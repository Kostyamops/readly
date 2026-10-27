#import <Foundation/Foundation.h>
#import "RRBookModel.h"

extern NSString * const RRBooksLibraryDidChangeNotification;

@interface RRBookStorageManager : NSObject

+ (instancetype)sharedManager;

/**
 * Путь к папке Documents/Books
 */
- (NSString *)booksDirectoryPath;

/**
 * Загружает все доступные книги из Documents/Books, Documents и ресурсов бандла.
 */
- (NSArray<RRBookModel *> *)loadAllBooks;

/**
 * Импортирует .epub файл из переданного внешнего URL (Safari, Mail, AirDrop, Inbox).
 * Возвращает постоянный абсолютный путь к импортированному файлу.
 */
- (NSString *)importEpubFromURL:(NSURL *)url error:(NSError **)error;

/**
 * Удаляет книгу из хранилища и очищает кэш распакованных глав.
 */
- (BOOL)deleteBook:(RRBookModel *)book error:(NSError **)error;

@end
