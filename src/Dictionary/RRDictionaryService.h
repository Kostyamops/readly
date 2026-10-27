#import <Foundation/Foundation.h>
#import "RRWordEntry.h"

@interface RRDictionaryService : NSObject

/**
 * Синглтон сервиса словаря
 */
+ (instancetype)sharedService;

/**
 * Инициализация и открытие базы данных по указанному пути.
 * Режим: SQLITE_OPEN_READONLY для экономии памяти и защиты данных.
 */
- (BOOL)openDatabaseWithPath:(NSString *)path error:(NSError **)error;

/**
 * Нормализация слова встроенным системным морфологическим анализатором iOS 9.
 * (например: "running" -> "run", "knives" -> "knife", "went" -> "go")
 */
- (NSString *)lemmatizeWord:(NSString *)rawWord;

/**
 * Поиск перевода слова.
 * Реализует двухфазный поиск:
 * 1. Прямой поиск точного совпадения.
 * 2. Если не найдено — лемматизация и повторный поиск.
 */
- (RRWordEntry *)lookupWord:(NSString *)word;

/**
 * Закрытие соединения с базой данных и освобождение дескрипторов.
 */
- (void)closeDatabase;

@end
