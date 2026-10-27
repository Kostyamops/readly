#import "RRBookShelfViewController.h"
#import "RRBookStorageManager.h"
#import "RRBookModel.h"
#import "RRReaderViewController.h"

@interface RRBookShelfViewController ()

@property (nonatomic, strong) UIView *headerBar;
@property (nonatomic, strong) UILabel *lblHeaderTitle;
@property (nonatomic, strong) UILabel *lblEmptyState;

@end

@implementation RRBookShelfViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor colorWithRed:0.96 green:0.95 blue:0.93 alpha:1.0];
    self.books = [NSMutableArray array];
    
    // 1. Верхняя панель заголовка
    CGFloat screenW = self.view.bounds.size.width > 0 ? self.view.bounds.size.width : 1024;
    self.headerBar = [[UIView alloc] initWithFrame:CGRectMake(0, 0, screenW, 54)];
    self.headerBar.backgroundColor = [UIColor colorWithWhite:0.97 alpha:0.95];
    self.headerBar.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
    
    self.lblHeaderTitle = [[UILabel alloc] initWithFrame:CGRectMake(20, 14, screenW - 40, 28)];
    self.lblHeaderTitle.font = [UIFont boldSystemFontOfSize:20.0];
    self.lblHeaderTitle.textColor = [UIColor colorWithWhite:0.15 alpha:1.0];
    self.lblHeaderTitle.text = @"📚 Моя библиотека";
    [self.headerBar addSubview:self.lblHeaderTitle];
    [self.view addSubview:self.headerBar];
    
    // 2. Таблица книг
    CGFloat tableY = 54;
    CGFloat tableH = self.view.bounds.size.height - tableY;
    self.tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, tableY, screenW, tableH) style:UITableViewStylePlain];
    self.tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    self.tableView.backgroundColor = [UIColor clearColor];
    self.tableView.dataSource = self;
    self.tableView.delegate = self;
    self.tableView.rowHeight = 90.0;
    self.tableView.tableFooterView = [[UIView alloc] initWithFrame:CGRectZero];
    [self.view addSubview:self.tableView];
    
    // 3. Заглушка пустого состояния
    self.lblEmptyState = [[UILabel alloc] initWithFrame:CGRectMake(40, 200, screenW - 80, 100)];
    self.lblEmptyState.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
    self.lblEmptyState.numberOfLines = 0;
    self.lblEmptyState.textAlignment = NSTextAlignmentCenter;
    self.lblEmptyState.font = [UIFont systemFontOfSize:16.0];
    self.lblEmptyState.textColor = [UIColor colorWithWhite:0.5 alpha:1.0];
    self.lblEmptyState.text = @"В библиотеке пока нет книг.\nЗагрузите .epub файл через iTunes File Sharing\nили откройте через меню «Поделиться».";
    self.lblEmptyState.hidden = YES;
    [self.view addSubview:self.lblEmptyState];
    
    // 4. Подписка на уведомление об обновлении библиотеки
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(handleLibraryNotification:)
                                                 name:RRBooksLibraryDidChangeNotification
                                               object:nil];
    
    [self reloadBooks];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self reloadBooks];
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
}

- (void)handleLibraryNotification:(NSNotification *)note {
    dispatch_async(dispatch_get_main_queue(), ^{
        [self reloadBooks];
    });
}

- (void)reloadBooks {
    NSArray *all = [[RRBookStorageManager sharedManager] loadAllBooks];
    [self.books removeAllObjects];
    if (all) {
        [self.books addObjectsFromArray:all];
    }
    
    self.lblHeaderTitle.text = [NSString stringWithFormat:@"📚 Моя библиотека (%ld)", (long)self.books.count];
    self.lblEmptyState.hidden = (self.books.count > 0);
    [self.tableView reloadData];
}

#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.books.count;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    static NSString *cellID = @"RRBookCell";
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:cellID];
    if (!cell) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:cellID];
        cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
        cell.backgroundColor = [UIColor colorWithWhite:1.0 alpha:0.7];
        cell.textLabel.font = [UIFont boldSystemFontOfSize:17.0];
        cell.textLabel.textColor = [UIColor colorWithRed:0.12 green:0.12 blue:0.14 alpha:1.0];
        cell.detailTextLabel.font = [UIFont systemFontOfSize:14.0];
        cell.detailTextLabel.textColor = [UIColor colorWithWhite:0.45 alpha:1.0];
        cell.imageView.contentMode = UIViewContentModeScaleAspectFit;
    }
    
    RRBookModel *book = self.books[indexPath.row];
    cell.textLabel.text = book.title ?: @"Без названия";
    
    NSString *author = book.author ?: @"Автор не указан";
    NSInteger chapterCount = book.chapters.count;
    cell.detailTextLabel.text = [NSString stringWithFormat:@"%@ • %ld глав", author, (long)chapterCount];
    
    if (book.coverImagePath && [[NSFileManager defaultManager] fileExistsAtPath:book.coverImagePath]) {
        cell.imageView.image = [UIImage imageWithContentsOfFile:book.coverImagePath];
    } else {
        cell.imageView.image = nil;
    }
    
    return cell;
}

#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    [tableView deselectRowAtIndexPath:indexPath animated:YES];
    
    RRBookModel *book = self.books[indexPath.row];
    RRReaderViewController *readerVC = [[RRReaderViewController alloc] initWithBook:book];
    
    if (self.navigationController) {
        [self.navigationController pushViewController:readerVC animated:YES];
    } else {
        [self presentViewController:readerVC animated:YES completion:nil];
    }
}

- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    return YES;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        RRBookModel *book = self.books[indexPath.row];
        [[RRBookStorageManager sharedManager] deleteBook:book error:nil];
        [self.books removeObjectAtIndex:indexPath.row];
        [tableView deleteRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationFade];
        self.lblHeaderTitle.text = [NSString stringWithFormat:@"📚 Моя библиотека (%ld)", (long)self.books.count];
        self.lblEmptyState.hidden = (self.books.count > 0);
    }
}

@end
