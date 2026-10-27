#import <Foundation/Foundation.h>
#import "RRBookModel.h"

@interface RREpubParser : NSObject

/**
 * Распаковывает и парсит EPUB книгу.
 * Возвращает RRBookModel с упорядоченными главами и абсолютными путями.
 */
+ (RRBookModel *)parseEpubAtPath:(NSString *)epubFilePath error:(NSError **)error;

@end
