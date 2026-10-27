#import <Foundation/Foundation.h>
#import "RRWordEntry.h"

@interface RRDictionaryService : NSObject

/**
 * Синглтон словарного сервиса
 */
+ (instancetype)sharedService;

/**
 * Открытие базы SQLite в режиме SQLITE_OPEN_READONLY
 */
- (BOOL)openDatabaseWithPath:(NSString *)path error:(NSError **)error;

/**
 * Очистка слова от краевых знаков пунктуации (запятые, кавычки, скобки)
 */
- (NSString *)cleanWord:(NSString *)rawWord;

/**
 * Приведение слова к нормальной форме через системный NSLinguisticTagger
 */
- (NSString *)lemmatizeWord:(NSString *)rawWord;

/**
 * Двухфазный поиск слова (точное совпадение -> лемма)
 */
- (RRWordEntry *)lookupWord:(NSString *)word;

/**
 * Закрытие соединения с базой и освобождение стейтментов
 */
- (void)closeDatabase;

@end
