#import <Foundation/Foundation.h>
#import "RRBookModel.h"

@interface RREpubParser : NSObject

/**
 * Распаковывает (при необходимости) и парсит файл книги .epub.
 * Возвращает готовую модель RRBookModel со всеми главами.
 */
+ (RRBookModel *)parseEpubAtPath:(NSString *)epubFilePath error:(NSError **)error;

@end
