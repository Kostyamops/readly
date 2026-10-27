#!/usr/bin/env python3
"""
TDD Test Suite для Milestone 2: Офлайн-словарь и морфология (NLP Engine)
Покрывает задачи: [M2-TASK-2.1.1.1] - [M2-TASK-2.2.2.5] (Issues #18 - #30).
"""

import os
import sys
import sqlite3
import subprocess
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")
DICT_PATH = os.path.join(RESOURCES_DIR, "dictionary.sqlite")
BUILDER_SCRIPT = os.path.join(PROJECT_ROOT, "tools", "dict_builder", "build_dict.py")

class TestMilestone2(unittest.TestCase):

    # ------------------------------------------------------------------------
    # [TASK-2.1.1.1 - 2.1.1.3] Скрипт сборки словаря и структура данных
    # ------------------------------------------------------------------------
    def test_2_1_1_builder_script_exists(self):
        """[TASK-2.1.1.1 - 2.1.1.3] Проверка наличия и запускаемости скрипта генератора словаря"""
        self.assertTrue(os.path.isfile(BUILDER_SCRIPT), "Скрипт tools/dict_builder/build_dict.py должен существовать")

        # Запускаем скрипт сборки базы данных
        res = subprocess.run([sys.executable, BUILDER_SCRIPT], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Ошибка при выполнении build_dict.py:\n{res.stderr}\n{res.stdout}")

    # ------------------------------------------------------------------------
    # [TASK-2.1.2.1 - 2.1.2.4] Схема SQLite, индексы, PRAGMA и размер базы
    # ------------------------------------------------------------------------
    def test_2_1_2_sqlite_database_and_schema(self):
        """[TASK-2.1.2.1 - 2.1.2.4] Валидация SQLite базы: схема, индекс, PRAGMA и размер < 20 МБ"""
        self.assertTrue(os.path.isfile(DICT_PATH), "Файл resources/dictionary.sqlite должен существовать")

        # Размер не должен превышать 20 МБ для экономии flash-памяти iPad 2
        size_mb = os.path.getsize(DICT_PATH) / (1024 * 1024)
        self.assertLess(size_mb, 20.0, f"Размер базы слишком велик ({size_mb:.2f} МБ), лимит 20 МБ")

        conn = sqlite3.connect(DICT_PATH)
        cursor = conn.cursor()

        # Проверка таблицы words
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='words';")
        self.assertIsNotNone(cursor.fetchone(), "Таблица 'words' должна присутствовать в базе данных")

        # Проверка колонок: id, word, transcription, pos, translation
        cursor.execute("PRAGMA table_info(words);")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        self.assertIn("word", columns)
        self.assertIn("transcription", columns)
        self.assertIn("pos", columns)
        self.assertIn("translation", columns)

        # Проверка индекса по полю word с NOCASE
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_word_nocase';")
        idx_row = cursor.fetchone()
        self.assertIsNotNone(idx_row, "Индекс 'idx_word_nocase' должен существовать")
        self.assertIn("NOCASE", idx_row[0].upper(), "Индекс должен использовать COLLATE NOCASE")

        # Проверка размера страницы PRAGMA page_size = 4096
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        self.assertEqual(page_size, 4096, "PRAGMA page_size должна быть равна 4096 для iPad 2")

        # Проверка наличия базовых тестовых слов
        cursor.execute("SELECT translation FROM words WHERE word = 'apple';")
        row = cursor.fetchone()
        self.assertIsNotNone(row, "Слово 'apple' должно присутствовать в базе словаря")
        self.assertIn("яблоко", row[0].lower())

        conn.close()

    # ------------------------------------------------------------------------
    # [TASK-2.2.1.1 - 2.2.1.4] Модель RRWordEntry и Objective-C класс RRDictionaryService
    # ------------------------------------------------------------------------
    def test_2_2_1_dictionary_objc_classes_exist(self):
        """[TASK-2.2.1.1 - 2.2.1.4] Проверка наличия исходных файлов RRWordEntry и RRDictionaryService"""
        word_h = os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRWordEntry.h")
        word_m = os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRWordEntry.m")
        dict_h = os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRDictionaryService.h")
        dict_m = os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRDictionaryService.m")

        self.assertTrue(os.path.isfile(word_h), "src/Dictionary/RRWordEntry.h должен существовать")
        self.assertTrue(os.path.isfile(word_m), "src/Dictionary/RRWordEntry.m должен существовать")
        self.assertTrue(os.path.isfile(dict_h), "src/Dictionary/RRDictionaryService.h должен существовать")
        self.assertTrue(os.path.isfile(dict_m), "src/Dictionary/RRDictionaryService.m должен существовать")

    # ------------------------------------------------------------------------
    # [TASK-2.2.2.1 - 2.2.2.5] Компиляция и тестирование функционала словаря и морфологии
    # ------------------------------------------------------------------------
    def test_2_2_2_dictionary_service_integration(self):
        """[TASK-2.2.2.1 - 2.2.2.5] Тестирование C-API SQLite, cleanWord, lemmatizeWord и lookupWord через нативный runner"""
        runner_c = os.path.join(PROJECT_ROOT, "tests", "_test_dict_runner.m")
        runner_bin = os.path.join(PROJECT_ROOT, "tests", "_test_dict_runner")

        test_code = f"""
#import <Foundation/Foundation.h>
#import "RRDictionaryService.h"
#import "RRWordEntry.h"

int main(int argc, const char * argv[]) {{
    @autoreleasepool {{
        RRDictionaryService *service = [RRDictionaryService sharedService];
        NSString *dictPath = @"{DICT_PATH}";
        
        NSError *error = nil;
        BOOL ok = [service openDatabaseWithPath:dictPath error:&error];
        if (!ok || error) {{
            NSLog(@"[FAIL] Не удалось открыть базу: %@", error);
            return 1;
        }}
        
        // 1. Тест точного совпадения
        RRWordEntry *e1 = [service lookupWord:@"apple"];
        if (!e1 || ![e1.translation containsString:@"яблоко"]) {{
            NSLog(@"[FAIL] Прямой поиск 'apple' не сработал");
            return 2;
        }}
        
        // 2. Тест очистки пунктуации
        RRWordEntry *e2 = [service lookupWord:@"\\"apple!\\","];
        if (!e2 || ![e2.translation containsString:@"яблоко"]) {{
            NSLog(@"[FAIL] Очистка пунктуации 'apple' не сработала");
            return 3;
        }}
        
        // 3. Тест морфологии / лемматизации (running -> run)
        RRWordEntry *e3 = [service lookupWord:@"running"];
        if (!e3 || (![e3.translation containsString:@"бег"] && ![e3.word isEqualToString:@"run"])) {{
            NSLog(@"[FAIL] Лемматизация 'running' -> 'run' не сработала");
            return 4;
        }}
        
        // 4. Тест множественного числа (books -> book)
        RRWordEntry *e4 = [service lookupWord:@"books"];
        if (!e4 || (![e4.translation containsString:@"книга"] && ![e4.word isEqualToString:@"book"])) {{
            NSLog(@"[FAIL] Лемматизация множественного числа 'books' -> 'book' не сработала");
            return 5;
        }}
        
        // 5. Тест отсутствующего слова (должен вернуть nil без краша)
        RRWordEntry *e5 = [service lookupWord:@"xyzrandomwordnotexist"];
        if (e5 != nil) {{
            NSLog(@"[FAIL] Несуществующее слово должно возвращать nil");
            return 6;
        }}
        
        [service closeDatabase];
    }}
    return 0;
}}
"""

        try:
            with open(runner_c, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Компилируем нативный тест через clang под macOS host
            cmd = [
                "clang", "-fobjc-arc",
                "-I", os.path.join(PROJECT_ROOT, "src", "Dictionary"),
                "-framework", "Foundation",
                "-lsqlite3",
                os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRWordEntry.m"),
                os.path.join(PROJECT_ROOT, "src", "Dictionary", "RRDictionaryService.m"),
                runner_c,
                "-o", runner_bin
            ]
            compile_res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(compile_res.returncode, 0, f"Ошибка компиляции test_dict_runner:\n{compile_res.stderr}")

            # Запускаем тест
            run_res = subprocess.run([runner_bin], capture_output=True, text=True)
            self.assertEqual(run_res.returncode, 0, f"Тест словаря завершился с кодом {run_res.returncode}:\n{run_res.stderr}\n{run_res.stdout}")

        finally:
            if os.path.exists(runner_c): os.remove(runner_c)
            if os.path.exists(runner_bin): os.remove(runner_bin)

if __name__ == "__main__":
    unittest.main()
