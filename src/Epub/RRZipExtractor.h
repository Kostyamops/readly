#import <Foundation/Foundation.h>

@interface RRZipExtractor : NSObject

/**
 * Распаковывает zip/epub архив в целевую директорию.
 * Потоковое чтение кусками по 4 КБ через zlib.h (без перерасхода RAM на iPad 2).
 */
+ (BOOL)unzipFileAtPath:(NSString *)filePath
          toDestination:(NSString *)destinationPath
                  error:(NSError **)error;

/**
 * Возвращает уникальный путь к кэш-директории книги: Library/Caches/Books/<md5_hash>/
 */
+ (NSString *)cacheDirectoryForBookPath:(NSString *)filePath;

@end
