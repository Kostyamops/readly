#import <Foundation/Foundation.h>

@interface RRZipExtractor : NSObject

/**
 * Распаковывает zip-архив (включая .epub) в целевую директорию.
 * Потоковое чтение через zlib.h (минимальное потребление RAM, без загрузки архива целиком).
 */
+ (BOOL)unzipFileAtPath:(NSString *)filePath
          toDestination:(NSString *)destinationPath
                  error:(NSError **)error;

/**
 * Возвращает уникальный путь к кэш-директории для данной книги в Library/Caches/Books/<hash>/
 */
+ (NSString *)cacheDirectoryForBookPath:(NSString *)filePath;

@end
