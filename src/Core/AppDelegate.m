#import "AppDelegate.h"
#import "RRDictionaryService.h"
#import "RREpubParser.h"
#import "RRReaderViewController.h"

@interface AppDelegate ()

@property (nonatomic, strong) RRReaderViewController *readerViewController;

@end

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
    self.window.backgroundColor = [UIColor colorWithRed:0.97 green:0.96 blue:0.93 alpha:1.0];

    // 1. Инициализация и открытие базы словаря SQLite (SQLITE_OPEN_READONLY)
    NSString *dictPath = [[NSBundle mainBundle] pathForResource:@"dictionary" ofType:@"sqlite"];
    if (dictPath) {
        NSError *dictError = nil;
        BOOL opened = [[RRDictionaryService sharedService] openDatabaseWithPath:dictPath error:&dictError];
        if (opened) {
            NSLog(@"[RetroReader] Dictionary database opened successfully from: %@", dictPath);
        } else {
            NSLog(@"[RetroReader] Failed to open dictionary database: %@", dictError);
        }
    } else {
        NSLog(@"[RetroReader] Warning: dictionary.sqlite not found in bundle");
    }

    // 2. Распаковка и парсинг встроенной книги sample.epub
    NSString *epubPath = [[NSBundle mainBundle] pathForResource:@"sample" ofType:@"epub"];
    RRBookModel *book = nil;
    if (epubPath) {
        NSError *epubError = nil;
        book = [RREpubParser parseEpubAtPath:epubPath error:&epubError];
        if (book) {
            NSLog(@"[RetroReader] Book '%@' loaded with %ld chapters", book.title, (long)book.chapters.count);
        } else {
            NSLog(@"[RetroReader] Failed to parse EPUB: %@", epubError);
        }
    }

    // 3. Создание читалки и установка в rootViewController
    self.readerViewController = [[RRReaderViewController alloc] initWithBook:book];
    self.window.rootViewController = self.readerViewController;
    [self.window makeKeyAndVisible];

    return YES;
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
    // Сброс кэша при сворачивании приложения для предотвращения Jetsam выгрузки на iPad 2 (512 MB RAM)
    [[NSURLCache sharedURLCache] removeAllCachedResponses];
    NSLog(@"[RetroReader] Cleared NSURLCache on applicationDidEnterBackground");
}

- (void)applicationDidReceiveMemoryWarning:(UIApplication *)application {
    // Агрессивный сброс кэша при нехватке оперативной памяти
    [[NSURLCache sharedURLCache] removeAllCachedResponses];
    NSLog(@"[RetroReader] Cleared NSURLCache on applicationDidReceiveMemoryWarning");
}

- (void)applicationWillTerminate:(UIApplication *)application {
    [[RRDictionaryService sharedService] closeDatabase];
}

@end
