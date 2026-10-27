#import "RRReaderViewController.h"
#import "RRDictionaryService.h"
#import "RRTranslationViewController.h"
#import "Constants.h"

@interface RRReaderViewController ()

@property (nonatomic, strong) UIWebView *webView;
@property (nonatomic, strong) UIView *headerBar;
@property (nonatomic, strong) UILabel *lblBookTitle;
@property (nonatomic, strong) UIView *footerBar;
@property (nonatomic, strong) UILabel *lblPageInfo;
@property (nonatomic, copy) NSString *injectedCSS;
@property (nonatomic, copy) NSString *injectedJS;
@property (nonatomic, assign) BOOL isBarsVisible;
@property (nonatomic, copy) NSString *lastShownWord;
@property (nonatomic, assign) NSTimeInterval lastShownTimestamp;

@end

@implementation RRReaderViewController

- (instancetype)initWithBook:(RRBookModel *)book {
    self = [super initWithNibName:nil bundle:nil];
    if (self) {
        _book = book;
        _currentChapterIndex = 0;
        _currentPageIndex = 0;
        _totalPagesInChapter = 1;
        _isBarsVisible = YES;
        
        NSString *cssPath = [[NSBundle mainBundle] pathForResource:@"reader_style" ofType:@"css"];
        if (cssPath) {
            _injectedCSS = [NSString stringWithContentsOfFile:cssPath encoding:NSUTF8StringEncoding error:nil];
        }
        
        NSString *jsPath = [[NSBundle mainBundle] pathForResource:@"reader_bridge" ofType:@"js"];
        if (jsPath) {
            _injectedJS = [NSString stringWithContentsOfFile:jsPath encoding:NSUTF8StringEncoding error:nil];
        }
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor colorWithRed:0.97 green:0.96 blue:0.93 alpha:1.0];
    
    // 1. Полноэкранный UIWebView
    self.webView = [[UIWebView alloc] initWithFrame:self.view.bounds];
    self.webView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    self.webView.delegate = self;
    self.webView.backgroundColor = [UIColor clearColor];
    self.webView.opaque = NO;
    
    // Отключение лишнего системного оверхеда для iPad 2 (512 MB RAM)
    self.webView.scrollView.bounces = NO;
    self.webView.scrollView.scrollEnabled = NO;
    self.webView.dataDetectorTypes = UIDataDetectorTypeNone;
    
    [self.view addSubview:self.webView];
    
    // 2. Верхняя и нижняя панели
    [self setupBars];
    
    // 3. Жесты листания
    UISwipeGestureRecognizer *swipeLeft = [[UISwipeGestureRecognizer alloc] initWithTarget:self action:@selector(handleSwipe:)];
    swipeLeft.direction = UISwipeGestureRecognizerDirectionLeft;
    swipeLeft.delegate = self;
    [self.webView addGestureRecognizer:swipeLeft];
    
    UISwipeGestureRecognizer *swipeRight = [[UISwipeGestureRecognizer alloc] initWithTarget:self action:@selector(handleSwipe:)];
    swipeRight.direction = UISwipeGestureRecognizerDirectionRight;
    swipeRight.delegate = self;
    [self.webView addGestureRecognizer:swipeRight];
    
    // 3.1. Жест одиночного тапа для быстрого вызова перевода слова
    UITapGestureRecognizer *singleTap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleSingleTap:)];
    singleTap.numberOfTapsRequired = 1;
    singleTap.cancelsTouchesInView = NO;
    singleTap.delegate = self;
    [self.webView addGestureRecognizer:singleTap];
    
    // 4. Загрузка первой главы
    if (self.book.chapters.count > 0) {
        [self loadChapterAtIndex:0];
    }
}

- (void)setupBars {
    CGFloat screenW = self.view.bounds.size.width > 0 ? self.view.bounds.size.width : kRRIpadScreenWidth;
    CGFloat screenH = self.view.bounds.size.height > 0 ? self.view.bounds.size.height : kRRIpadScreenHeight;
    
    // Верхняя панель
    self.headerBar = [[UIView alloc] initWithFrame:CGRectMake(0, 0, screenW, 40)];
    self.headerBar.backgroundColor = [UIColor colorWithWhite:0.96 alpha:0.92];
    self.headerBar.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
    
    self.lblBookTitle = [[UILabel alloc] initWithFrame:CGRectMake(20, 10, screenW - 40, 24)];
    self.lblBookTitle.font = [UIFont systemFontOfSize:14.0];
    self.lblBookTitle.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
    self.lblBookTitle.textAlignment = NSTextAlignmentCenter;
    self.lblBookTitle.text = self.book.title ?: @"RetroReader";
    [self.headerBar addSubview:self.lblBookTitle];
    [self.view addSubview:self.headerBar];
    
    // Нижняя панель
    self.footerBar = [[UIView alloc] initWithFrame:CGRectMake(0, screenH - 36, screenW, 36)];
    self.footerBar.backgroundColor = [UIColor colorWithWhite:0.96 alpha:0.92];
    self.footerBar.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
    
    self.lblPageInfo = [[UILabel alloc] initWithFrame:CGRectMake(20, 6, screenW - 40, 24)];
    self.lblPageInfo.font = [UIFont systemFontOfSize:13.0];
    self.lblPageInfo.textColor = [UIColor colorWithWhite:0.4 alpha:1.0];
    self.lblPageInfo.textAlignment = NSTextAlignmentCenter;
    self.lblPageInfo.text = @"Загрузка...";
    [self.footerBar addSubview:self.lblPageInfo];
    [self.view addSubview:self.footerBar];
}

#pragma mark - Загрузка главы и подготовка DOM

- (void)loadChapterAtIndex:(NSInteger)chapterIndex {
    if (chapterIndex < 0 || chapterIndex >= self.book.chapters.count) {
        return;
    }
    
    self.currentChapterIndex = chapterIndex;
    self.currentPageIndex = 0;
    
    // Очистка предыдущего DOM содержимого для минимизации расхода памяти WebKit на iPad 2
    [self.webView stringByEvaluatingJavaScriptFromString:@"if (document.body) { document.body.innerHTML = ''; }"];
    
    RRChapterModel *chapter = self.book.chapters[chapterIndex];
    NSString *htmlPath = chapter.absoluteHtmlPath;
    
    NSError *error = nil;
    NSString *rawHtml = [NSString stringWithContentsOfFile:htmlPath encoding:NSUTF8StringEncoding error:&error];
    if (!rawHtml) {
        rawHtml = [NSString stringWithContentsOfFile:htmlPath encoding:NSISOLatin1StringEncoding error:nil];
    }
    if (!rawHtml) return;
    
    NSMutableString *preparedHtml = [NSMutableString stringWithString:rawHtml];
    
    // Инъекция CSS стилей
    NSString *styleTag = [NSString stringWithFormat:@"<style>%@</style>", self.injectedCSS ?: @""];
    NSRange headRange = [preparedHtml rangeOfString:@"</head>" options:NSCaseInsensitiveSearch];
    if (headRange.location != NSNotFound) {
        [preparedHtml insertString:styleTag atIndex:headRange.location];
    } else {
        [preparedHtml insertString:styleTag atIndex:0];
    }
    
    // Оборачивание содержимого <body> в <div id="book-container">
    NSRange bodyOpen = [preparedHtml rangeOfString:@"<body" options:NSCaseInsensitiveSearch];
    if (bodyOpen.location != NSNotFound) {
        NSRange bodyCloseTag = [preparedHtml rangeOfString:@">" options:0 range:NSMakeRange(bodyOpen.location, preparedHtml.length - bodyOpen.location)];
        if (bodyCloseTag.location != NSNotFound) {
            NSUInteger insertPos = bodyCloseTag.location + 1;
            [preparedHtml insertString:@"<div id=\"book-container\">" atIndex:insertPos];
        }
    }
    
    NSRange bodyEnd = [preparedHtml rangeOfString:@"</body>" options:NSCaseInsensitiveSearch];
    if (bodyEnd.location != NSNotFound) {
        NSString *jsScript = [NSString stringWithFormat:@"</div><script>%@</script>", self.injectedJS ?: @""];
        [preparedHtml insertString:jsScript atIndex:bodyEnd.location];
    }
    
    NSURL *baseURL = [NSURL fileURLWithPath:[htmlPath stringByDeletingLastPathComponent] isDirectory:YES];
    [self.webView loadHTMLString:preparedHtml baseURL:baseURL];
}

#pragma mark - UIWebViewDelegate

- (void)webViewDidFinishLoad:(UIWebView *)webView {
    NSString *pagesStr = [self.webView stringByEvaluatingJavaScriptFromString:@"window.RRGetTotalPages ? window.RRGetTotalPages() : 1;"];
    NSInteger pages = [pagesStr integerValue];
    self.totalPagesInChapter = pages > 0 ? pages : 1;
    [self updatePageDisplay];
}

- (BOOL)webView:(UIWebView *)webView
shouldStartLoadWithRequest:(NSURLRequest *)request
 navigationType:(UIWebViewNavigationType)navigationType {
    NSURL *url = request.URL;
    if ([url.scheme caseInsensitiveCompare:kRRReaderBridgeScheme] == NSOrderedSame) {
        if ([url.host caseInsensitiveCompare:kRRReaderActionWordTap] == NSOrderedSame) {
            [self handleWordTapURL:url];
            return NO;
        }
    }
    return YES;
}

#pragma mark - Перехват слова и вызов всплывающего перевода

- (void)handleSingleTap:(UITapGestureRecognizer *)gesture {
    if (gesture.state == UIGestureRecognizerStateEnded) {
        CGPoint pt = [gesture locationInView:self.webView];
        NSLog(@"[RetroReader] Native tap gesture at: (%f, %f)", pt.x, pt.y);
        
        // Синхронный вызов JS для мгновенного определения слова под пальцем
        NSString *js = [NSString stringWithFormat:@"window.RRGetWordAt ? window.RRGetWordAt(%f, %f) : '';", pt.x, pt.y];
        NSString *resultJson = [self.webView stringByEvaluatingJavaScriptFromString:js];
        
        NSLog(@"[RetroReader] Tap JS result: '%@'", resultJson);
        
        if (resultJson && resultJson.length > 2) {
            NSData *data = [resultJson dataUsingEncoding:NSUTF8StringEncoding];
            NSDictionary *dict = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
            if ([dict isKindOfClass:[NSDictionary class]]) {
                NSString *word = dict[@"word"];
                CGFloat x = [dict[@"x"] doubleValue];
                CGFloat y = [dict[@"y"] doubleValue];
                CGFloat w = [dict[@"w"] doubleValue];
                CGFloat h = [dict[@"h"] doubleValue];
                
                if (word.length > 0) {
                    CGRect rect = CGRectMake(x, y, w, h);
                    [self showPopoverForWord:word rect:rect];
                    return;
                }
            }
        }
    }
}

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    return YES;
}

- (void)showPopoverForWord:(NSString *)word rect:(CGRect)wordRect {
    if (!word || word.length == 0) return;
    
    NSTimeInterval now = [[NSDate date] timeIntervalSince1970];
    if ([word isEqualToString:self.lastShownWord] && (now - self.lastShownTimestamp < 0.4)) {
        return; // Дебаунс дубликатов
    }
    self.lastShownWord = word;
    self.lastShownTimestamp = now;
    
    // Коррекция и защита координат для стрелочки попапа
    if (wordRect.size.width < 10) wordRect.size.width = 40;
    if (wordRect.size.height < 10) wordRect.size.height = 20;
    if (CGRectIsEmpty(wordRect) || CGRectIsNull(wordRect) || wordRect.origin.x < 0 || wordRect.origin.y < 0) {
        CGFloat screenW = self.view.bounds.size.width > 0 ? self.view.bounds.size.width : kRRIpadScreenWidth;
        CGFloat screenH = self.view.bounds.size.height > 0 ? self.view.bounds.size.height : kRRIpadScreenHeight;
        wordRect = CGRectMake(screenW / 2.0 - 20, screenH / 2.0 - 10, 40, 20);
    }
    
    NSLog(@"[RetroReader] Presenting translation for: '%@', rect: %@", word, NSStringFromCGRect(wordRect));
    
    // Поиск слова в локальной SQLite базе с лемматизацией
    RRWordEntry *entry = [[RRDictionaryService sharedService] lookupWord:word];
    if (!entry) {
        entry = [[RRWordEntry alloc] initWithWord:word
                                     transcription:@""
                                      partOfSpeech:@""
                                       translation:@"Перевод не найден в локальном словаре."];
    }
    
    // Если уже открыт попап перевода, закрываем предыдущий перед открытием нового
    if (self.presentedViewController) {
        [self.presentedViewController dismissViewControllerAnimated:NO completion:nil];
    }
    
    // Инициализация и показ компактного бабла перевода
    RRTranslationViewController *popoverVC = [[RRTranslationViewController alloc] initWithWordEntry:entry];
    popoverVC.modalPresentationStyle = UIModalPresentationPopover;
    
    UIPopoverPresentationController *popPresenter = popoverVC.popoverPresentationController;
    popPresenter.delegate = self;
    popPresenter.sourceView = self.webView;
    popPresenter.sourceRect = wordRect;
    popPresenter.permittedArrowDirections = UIPopoverArrowDirectionUp | UIPopoverArrowDirectionDown;
    
    [self presentViewController:popoverVC animated:YES completion:nil];
}

- (void)handleWordTapURL:(NSURL *)url {
    dispatch_async(dispatch_get_main_queue(), ^{
        NSURLComponents *components = [NSURLComponents componentsWithURL:url resolvingAgainstBaseURL:NO];
        NSString *word = nil;
        CGFloat x = 0, y = 0, w = 0, h = 0;
        
        for (NSURLQueryItem *item in components.queryItems) {
            if ([item.name isEqualToString:@"word"]) {
                word = item.value;
            } else if ([item.name isEqualToString:@"x"]) {
                x = [item.value doubleValue];
            } else if ([item.name isEqualToString:@"y"]) {
                y = [item.value doubleValue];
            } else if ([item.name isEqualToString:@"w"]) {
                w = [item.value doubleValue];
            } else if ([item.name isEqualToString:@"h"]) {
                h = [item.value doubleValue];
            }
        }
        
        if (word.length > 0) {
            CGRect wordRect = CGRectMake(x, y, w, h);
            [self showPopoverForWord:word rect:wordRect];
        }
    });
}

#pragma mark - UIPopoverPresentationControllerDelegate

- (UIModalPresentationStyle)adaptivePresentationStyleForPresentationController:(UIPresentationController *)controller {
    // Предотвращаем разворачивание попапа на весь экран iPad
    return UIModalPresentationNone;
}

#pragma mark - Пагинация и свайпы

- (void)handleSwipe:(UISwipeGestureRecognizer *)gesture {
    if (gesture.direction == UISwipeGestureRecognizerDirectionLeft) {
        [self nextPage];
    } else if (gesture.direction == UISwipeGestureRecognizerDirectionRight) {
        [self prevPage];
    }
}

- (void)nextPage {
    if (self.currentPageIndex + 1 < self.totalPagesInChapter) {
        self.currentPageIndex++;
        [self scrollToCurrentPage];
    } else if (self.currentChapterIndex + 1 < self.book.chapters.count) {
        [self loadChapterAtIndex:self.currentChapterIndex + 1];
    }
}

- (void)prevPage {
    if (self.currentPageIndex > 0) {
        self.currentPageIndex--;
        [self scrollToCurrentPage];
    } else if (self.currentChapterIndex > 0) {
        [self loadChapterAtIndex:self.currentChapterIndex - 1];
    }
}

- (void)scrollToCurrentPage {
    NSString *js = [NSString stringWithFormat:@"if (window.RRScrollToPage) { window.RRScrollToPage(%ld); }", (long)self.currentPageIndex];
    [self.webView stringByEvaluatingJavaScriptFromString:js];
    [self updatePageDisplay];
}

- (void)updatePageDisplay {
    RRChapterModel *chapter = nil;
    if (self.currentChapterIndex < self.book.chapters.count) {
        chapter = self.book.chapters[self.currentChapterIndex];
    }
    
    NSString *chapterTitle = chapter.title ?: [NSString stringWithFormat:@"Глава %ld", (long)(self.currentChapterIndex + 1)];
    self.lblPageInfo.text = [NSString stringWithFormat:@"%@ • Стр. %ld из %ld",
                             chapterTitle,
                             (long)(self.currentPageIndex + 1),
                             (long)self.totalPagesInChapter];
}

#pragma mark - Управление памятью

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    [[NSURLCache sharedURLCache] removeAllCachedResponses];
}

@end
