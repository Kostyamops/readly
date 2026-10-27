#import "AppDelegate.h"
#import "RRReaderViewController.h"
#import "RRDictionaryService.h"
#import "RREpubParser.h"
#import "Constants.h"

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
    self.window.backgroundColor = [UIColor whiteColor];
    
    // 1. Инициализация базы данных словаря
    NSString *dictPath = [[NSBundle mainBundle] pathForResource:@"dictionary" ofType:@"sqlite"];
    if (dictPath) {
        NSError *dictError = nil;
        BOOL ok = [[RRDictionaryService sharedService] openDatabaseWithPath:dictPath error:&dictError];
        if (ok) {
            NSLog(@"[RetroReader] База словаря успешно подключена: %@", dictPath);
        } else {
            NSLog(@"[RetroReader] Ошибка открытия словаря: %@", dictError);
        }
    } else {
        NSLog(@"[RetroReader] Внимание: dictionary.sqlite не найден в бандле!");
    }
    
    // 2. Загрузка демонстрационной книги sample.epub
    NSString *epubPath = [[NSBundle mainBundle] pathForResource:@"sample" ofType:@"epub"];
    RRBookModel *book = nil;
    if (epubPath) {
        NSError *epubError = nil;
        book = [RREpubParser parseEpubAtPath:epubPath error:&epubError];
        if (book) {
            NSLog(@"[RetroReader] Книга успешно загружена: '%@', глав: %lu", book.title, (unsigned long)book.chapters.count);
        } else {
            NSLog(@"[RetroReader] Ошибка парсинга книги: %@", epubError);
        }
    } else {
        NSLog(@"[RetroReader] Внимание: sample.epub не найден в бандле!");
    }
    
    // 3. Создание экрана чтения
    RRReaderViewController *readerVC = [[RRReaderViewController alloc] initWithBook:book];
    self.window.rootViewController = readerVC;
    [self.window makeKeyAndVisible];
    
    return YES;
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
    // Освобождаем кэш при сворачивании для предотвращения Jetsam kill на 512 МБ
    [[NSURLCache sharedURLCache] removeAllCachedResponses];
}

@end
