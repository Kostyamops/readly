#import <Foundation/Foundation.h>
#import "RRDictionaryService.h"
#import "RRZipExtractor.h"
#import "RREpubParser.h"

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSLog(@"==================================================");
        NSLog(@"[TEST SUITE] Запуск тестов ядра RetroReader...");
        NSLog(@"==================================================");
        
        NSString *rootDir = [[NSFileManager defaultManager] currentDirectoryPath];
        NSString *dictPath = [rootDir stringByAppendingPathComponent:@"resources/dictionary.sqlite"];
        NSString *epubPath = [rootDir stringByAppendingPathComponent:@"resources/sample.epub"];
        
        // ----------------------------------------------------
        // ТЕСТ 1: Инициализация и поиск в SQLite словаре
        // ----------------------------------------------------
        NSLog(@"[TEST 1] Проверка RRDictionaryService...");
        RRDictionaryService *dict = [RRDictionaryService sharedService];
        NSError *dictError = nil;
        BOOL opened = [dict openDatabaseWithPath:dictPath error:&dictError];
        NSCAssert(opened, @"Ошибка открытия базы словаря: %@", dictError);
        NSLog(@"  -> База словаря успешно открыта: %@", dictPath);
        
        // Прямой поиск
        RRWordEntry *appleEntry = [dict lookupWord:@"apple"];
        NSCAssert(appleEntry != nil, @"Слово 'apple' должно быть найдено!");
        NSLog(@"  -> Найдено 'apple': %@ | %@", appleEntry.transcription, appleEntry.translation);
        
        // Поиск с пунктуацией и разным регистром
        RRWordEntry *punctEntry = [dict lookupWord:@"\"Rabbit!\","];
        NSCAssert(punctEntry != nil, @"Слово 'Rabbit' с пунктуацией должно быть найдено!");
        NSLog(@"  -> Найдено '\"Rabbit!\",': %@", punctEntry.translation);
        
        // Лемматизация (running -> run)
        RRWordEntry *lemmaEntry = [dict lookupWord:@"running"];
        NSCAssert(lemmaEntry != nil, @"Форма 'running' должна лемматизироваться в 'run'!");
        NSLog(@"  -> Лемматизация 'running' -> '%@': %@", lemmaEntry.word, lemmaEntry.translation);
        
        NSLog(@"[TEST 1 PASSED] Словарь и морфология работают корректно!\n");
        
        // ----------------------------------------------------
        // ТЕСТ 2: Распаковка ZIP (EPUB) через RRZipExtractor
        // ----------------------------------------------------
        NSLog(@"[TEST 2] Проверка RRZipExtractor...");
        NSString *testExtractDir = [NSTemporaryDirectory() stringByAppendingPathComponent:@"RetroReaderTestExtract"];
        [[NSFileManager defaultManager] removeItemAtPath:testExtractDir error:nil];
        
        NSError *zipError = nil;
        BOOL zipOk = [RRZipExtractor unzipFileAtPath:epubPath toDestination:testExtractDir error:&zipError];
        NSCAssert(zipOk, @"Ошибка распаковки sample.epub: %@", zipError);
        
        NSString *containerXml = [testExtractDir stringByAppendingPathComponent:@"META-INF/container.xml"];
        NSCAssert([[NSFileManager defaultManager] fileExistsAtPath:containerXml], @"META-INF/container.xml должен существовать!");
        NSLog(@"  -> sample.epub успешно распакован в %@", testExtractDir);
        NSLog(@"[TEST 2 PASSED] Архиватор работает корректно!\n");
        
        // ----------------------------------------------------
        // ТЕСТ 3: Полный парсинг EPUB через RREpubParser
        // ----------------------------------------------------
        NSLog(@"[TEST 3] Проверка RREpubParser...");
        NSError *parseError = nil;
        RRBookModel *book = [RREpubParser parseEpubAtPath:epubPath error:&parseError];
        NSCAssert(book != nil, @"Книга должна успешно распарситься: %@", parseError);
        
        NSLog(@"  -> Название: '%@'", book.title);
        NSLog(@"  -> Автор: '%@'", book.author);
        NSLog(@"  -> Количество глав: %lu", (unsigned long)book.chapters.count);
        
        NSCAssert([book.title isEqualToString:@"Alice's Adventures in Wonderland"], @"Неверное название книги!");
        NSCAssert([book.author isEqualToString:@"Lewis Carroll"], @"Неверный автор!");
        NSCAssert(book.chapters.count == 2, @"Должно быть ровно 2 главы!");
        
        for (RRChapterModel *chapter in book.chapters) {
            NSLog(@"    * %@ -> %@", chapter.chapterId, chapter.relativeHtmlPath);
            NSCAssert([[NSFileManager defaultManager] fileExistsAtPath:chapter.absoluteHtmlPath], @"Файл главы должен физически существовать!");
        }
        
        NSLog(@"[TEST 3 PASSED] Парсер EPUB работает идеально!\n");
        
        NSLog(@"==================================================");
        NSLog(@"[ALL TESTS PASSED] Все тесты ядра успешно пройдены!");
        NSLog(@"==================================================");
    }
    return 0;
}
