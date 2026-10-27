#import "AppDelegate.h"
#import "RRDictionaryService.h"
#import "RREpubParser.h"
#import "RRBookStorageManager.h"
#import "RRBookShelfViewController.h"
#import "RRReaderViewController.h"

@interface AppDelegate ()

@property (nonatomic, strong) UINavigationController *navigationController;
@property (nonatomic, strong) RRBookShelfViewController *shelfViewController;

@end

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
    self.window.backgroundColor = [UIColor colorWithRed:0.96 green:0.95 blue:0.93 alpha:1.0];

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

    // 2. Создание навигационного стека с книжной полкой
    self.shelfViewController = [[RRBookShelfViewController alloc] init];
    self.navigationController = [[UINavigationController alloc] initWithRootViewController:self.shelfViewController];
    [self.navigationController setNavigationBarHidden:YES animated:NO];
    self.window.rootViewController = self.navigationController;
    [self.window makeKeyAndVisible];

    // 3. Обработка файла при холодном старте через Open In
    NSURL *launchURL = launchOptions[UIApplicationLaunchOptionsURLKey];
    if (launchURL) {
        [self handleIncomingURL:launchURL];
    }

    return YES;
}

- (BOOL)application:(UIApplication *)app openURL:(NSURL *)url options:(NSDictionary *)options {
    return [self handleIncomingURL:url];
}

- (BOOL)application:(UIApplication *)application openURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {
    return [self handleIncomingURL:url];
}

- (BOOL)handleIncomingURL:(NSURL *)url {
    if (!url) return NO;
    
    NSLog(@"[RetroReader] Incoming file URL: %@", url);
    NSError *error = nil;
    NSString *savedPath = [[RRBookStorageManager sharedManager] importEpubFromURL:url error:&error];
    if (!savedPath) {
        NSLog(@"[RetroReader] Failed to import EPUB from %@: %@", url, error);
        return NO;
    }
    
    // Открываем импортированную книгу
    RRBookModel *book = [RREpubParser parseEpubAtPath:savedPath error:&error];
    if (book) {
        RRReaderViewController *readerVC = [[RRReaderViewController alloc] initWithBook:book];
        [self.navigationController pushViewController:readerVC animated:YES];
        return YES;
    }
    
    return NO;
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
