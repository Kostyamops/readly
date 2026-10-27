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
    [self.webView addGestureRecognizer:swipeLeft];
    
    UISwipeGestureRecognizer *swipeRight = [[UISwipeGestureRecognizer alloc] initWithTarget:self action:@selector(handleSwipe:)];
    swipeRight.direction = UISwipeGestureRecognizerDirectionRight;
    [self.webView addGestureRecognizer:swipeRight];
    
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
    if ([url.scheme isEqualToString:kRRReaderBridgeScheme]) {
        if ([url.host isEqualToString:kRRReaderActionWordTap]) {
            [self handleWordTapURL:url];
            return NO;
        }
    }
    return YES;
}

#pragma mark - Перехват слова из URL и вызов всплывающего перевода

- (void)handleWordTapURL:(NSURL *)url {
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
    
    if (!word || word.length == 0) return;
    
    CGRect wordRect = CGRectMake(x, y, w > 10 ? w : 40, h > 10 ? h : 20);
    NSLog(@"[RetroReader] Tapped word: '%@', rect: %@", word, NSStringFromCGRect(wordRect));
    
    // Поиск слова в локальной SQLite базе с лемматизацией
    RRWordEntry *entry = [[RRDictionaryService sharedService] lookupWord:word];
    if (!entry) {
        entry = [[RRWordEntry alloc] initWithWord:word
                                     transcription:@""
                                      partOfSpeech:@""
                                       translation:@"Перевод не найден в локальном словаре."];
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
