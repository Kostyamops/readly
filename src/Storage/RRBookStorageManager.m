#import "RRBookStorageManager.h"
#import "RREpubParser.h"

NSString * const RRBooksLibraryDidChangeNotification = @"RRBooksLibraryDidChangeNotification";

@implementation RRBookStorageManager

+ (instancetype)sharedManager {
    static RRBookStorageManager *instance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        instance = [[RRBookStorageManager alloc] init];
    });
    return instance;
}

- (NSString *)booksDirectoryPath {
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *docs = [paths firstObject];
    NSString *booksDir = [docs stringByAppendingPathComponent:@"Books"];
    
    NSFileManager *fm = [NSFileManager defaultManager];
    if (![fm fileExistsAtPath:booksDir]) {
        [fm createDirectoryAtPath:booksDir withIntermediateDirectories:YES attributes:nil error:nil];
    }
    return booksDir;
}

- (NSArray<RRBookModel *> *)loadAllBooks {
    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *booksDir = [self booksDirectoryPath];
    
    // 1. Проверяем наличие встроенного sample.epub, если в Books пусто
    NSString *sampleInBooks = [booksDir stringByAppendingPathComponent:@"sample.epub"];
    if (![fm fileExistsAtPath:sampleInBooks]) {
        NSString *bundleSample = [[NSBundle mainBundle] pathForResource:@"sample" ofType:@"epub"];
        if (bundleSample && [fm fileExistsAtPath:bundleSample]) {
            [fm copyItemAtPath:bundleSample toPath:sampleInBooks error:nil];
        }
    }
    
    // 2. Сканируем папку Books и корневую папку Documents (для файлов, сброшенных через iTunes File Sharing)
    NSMutableArray<NSString *> *epubPaths = [NSMutableArray array];
    
    NSArray *booksFiles = [fm contentsOfDirectoryAtPath:booksDir error:nil];
    for (NSString *file in booksFiles) {
        if ([[file pathExtension] caseInsensitiveCompare:@"epub"] == NSOrderedSame) {
            [epubPaths addObject:[booksDir stringByAppendingPathComponent:file]];
        }
    }
    
    NSArray *docPaths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *docs = [docPaths firstObject];
    NSArray *rootFiles = [fm contentsOfDirectoryAtPath:docs error:nil];
    for (NSString *file in rootFiles) {
        if ([[file pathExtension] caseInsensitiveCompare:@"epub"] == NSOrderedSame) {
            // Перемещаем файл из корня Documents в Documents/Books для порядка
            NSString *oldPath = [docs stringByAppendingPathComponent:file];
            NSString *newPath = [booksDir stringByAppendingPathComponent:file];
            if (![fm fileExistsAtPath:newPath]) {
                [fm moveItemAtPath:oldPath toPath:newPath error:nil];
                [epubPaths addObject:newPath];
            }
        }
    }
    
    // 3. Парсим каждую книгу
    NSMutableArray<RRBookModel *> *books = [NSMutableArray array];
    for (NSString *path in epubPaths) {
        NSError *err = nil;
        RRBookModel *book = [RREpubParser parseEpubAtPath:path error:&err];
        if (book) {
            [books addObject:book];
        } else {
            NSLog(@"[RRBookStorageManager] Ошибка парсинга книги %@: %@", path, err);
        }
    }
    
    return books;
}

- (NSString *)importEpubFromURL:(NSURL *)url error:(NSError **)error {
    if (!url || !url.isFileURL) {
        if (error) {
            *error = [NSError errorWithDomain:@"RRBookStorageManager"
                                         code:400
                                     userInfo:@{NSLocalizedDescriptionKey: @"Некорректный URL файла"}];
        }
        return nil;
    }
    
    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *sourcePath = [url path];
    if (![fm fileExistsAtPath:sourcePath]) {
        if (error) {
            *error = [NSError errorWithDomain:@"RRBookStorageManager"
                                         code:404
                                     userInfo:@{NSLocalizedDescriptionKey: @"Файл не найден"}];
        }
        return nil;
    }
    
    NSString *booksDir = [self booksDirectoryPath];
    NSString *fileName = [sourcePath lastPathComponent];
    NSString *destPath = [booksDir stringByAppendingPathComponent:fileName];
    
    // Предотвращение коллизии имен файлов
    if ([fm fileExistsAtPath:destPath]) {
        NSString *nameWithoutExt = [fileName stringByDeletingPathExtension];
        NSString *ext = [fileName pathExtension];
        NSString *uniqueName = [NSString stringWithFormat:@"%@_%ld.%@", nameWithoutExt, (long)[[NSDate date] timeIntervalSince1970], ext];
        destPath = [booksDir stringByAppendingPathComponent:uniqueName];
    }
    
    NSError *copyError = nil;
    BOOL success = [fm copyItemAtPath:sourcePath toPath:destPath error:&copyError];
    if (!success) {
        if (error) *error = copyError;
        return nil;
    }
    
    // Если файл находился во временной системной папке Inbox, удаляем его
    if ([sourcePath rangeOfString:@"/Inbox/"].location != NSNotFound) {
        [fm removeItemAtPath:sourcePath error:nil];
    }
    
    dispatch_async(dispatch_get_main_queue(), ^{
        [[NSNotificationCenter defaultCenter] postNotificationName:RRBooksLibraryDidChangeNotification object:destPath];
    });
    
    return destPath;
}

- (BOOL)deleteBook:(RRBookModel *)book error:(NSError **)error {
    if (!book) return NO;
    
    NSFileManager *fm = [NSFileManager defaultManager];
    
    // Удаляем файл epub
    if (book.epubFilePath && [fm fileExistsAtPath:book.epubFilePath]) {
        BOOL ok = [fm removeItemAtPath:book.epubFilePath error:error];
        if (!ok) return NO;
    }
    
    // Удаляем кэш распакованных данных
    if (book.baseFolderPath && [fm fileExistsAtPath:book.baseFolderPath]) {
        [fm removeItemAtPath:book.baseFolderPath error:nil];
    }
    
    dispatch_async(dispatch_get_main_queue(), ^{
        [[NSNotificationCenter defaultCenter] postNotificationName:RRBooksLibraryDidChangeNotification object:nil];
    });
    
    return YES;
}

@end
