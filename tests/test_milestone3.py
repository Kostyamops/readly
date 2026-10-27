#!/usr/bin/env python3
"""
TDD Test Suite для Milestone 3: Движок парсинга и распаковки EPUB (EPUB Engine)
Покрывает задачи: [M3-TASK-3.1.1.1] - [M3-TASK-3.2.2.6] (Issues #31 - #44).
"""

import os
import sys
import zipfile
import shutil
import tempfile
import subprocess
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_EPUB = os.path.join(PROJECT_ROOT, "src", "Epub")

class TestMilestone3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем временный валидный EPUB архив для TDD-тестов
        cls.temp_dir = tempfile.mkdtemp(prefix="retroread_test_epub_")
        cls.test_epub_path = os.path.join(cls.temp_dir, "test_book.epub")

        mimetype = "application/epub+zip"
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""

        content_opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>TDD Alice in Wonderland</dc:title>
        <dc:creator>Lewis Carroll</dc:creator>
        <dc:language>en</dc:language>
    </metadata>
    <manifest>
        <item id="c1" href="chap1.xhtml" media-type="application/xhtml+xml"/>
        <item id="c2" href="chap2.xhtml" media-type="application/xhtml+xml"/>
    </manifest>
    <spine>
        <itemref idref="c1"/>
        <itemref idref="c2"/>
    </spine>
</package>"""

        chap1_html = "<html><body><h1>Chapter 1</h1><p>Down the rabbit hole.</p></body></html>"
        chap2_html = "<html><body><h1>Chapter 2</h1><p>The pool of tears.</p></body></html>"

        with zipfile.ZipFile(cls.test_epub_path, "w") as z:
            z.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
            z.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)
            z.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)
            z.writestr("OEBPS/chap1.xhtml", chap1_html, compress_type=zipfile.ZIP_DEFLATED)
            z.writestr("OEBPS/chap2.xhtml", chap2_html, compress_type=zipfile.ZIP_DEFLATED)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    # ------------------------------------------------------------------------
    # [TASK-3.1.1.1 - 3.1.1.4] Класс RRZipExtractor
    # ------------------------------------------------------------------------
    def test_3_1_1_zip_extractor_files_exist(self):
        """[TASK-3.1.1.1 - 3.1.1.4] Проверка наличия исходных файлов RRZipExtractor"""
        h_path = os.path.join(SRC_EPUB, "RRZipExtractor.h")
        m_path = os.path.join(SRC_EPUB, "RRZipExtractor.m")
        self.assertTrue(os.path.isfile(h_path), "src/Epub/RRZipExtractor.h должен существовать")
        self.assertTrue(os.path.isfile(m_path), "src/Epub/RRZipExtractor.m должен существовать")

    # ------------------------------------------------------------------------
    # [TASK-3.2.2.1 - 3.2.2.2] Модели RRChapterModel и RRBookModel
    # ------------------------------------------------------------------------
    def test_3_2_models_exist(self):
        """[TASK-3.2.2.1 - 3.2.2.2] Проверка наличия моделей RRChapterModel и RRBookModel"""
        chap_h = os.path.join(SRC_EPUB, "RRChapterModel.h")
        chap_m = os.path.join(SRC_EPUB, "RRChapterModel.m")
        book_h = os.path.join(SRC_EPUB, "RRBookModel.h")
        book_m = os.path.join(SRC_EPUB, "RRBookModel.m")

        self.assertTrue(os.path.isfile(chap_h), "src/Epub/RRChapterModel.h должен существовать")
        self.assertTrue(os.path.isfile(chap_m), "src/Epub/RRChapterModel.m должен существовать")
        self.assertTrue(os.path.isfile(book_h), "src/Epub/RRBookModel.h должен существовать")
        self.assertTrue(os.path.isfile(book_m), "src/Epub/RRBookModel.m должен существовать")

    # ------------------------------------------------------------------------
    # [TASK-3.2.2.6] Парсер RREpubParser
    # ------------------------------------------------------------------------
    def test_3_2_parser_files_exist(self):
        """[TASK-3.2.2.6] Проверка наличия файлов RREpubParser"""
        parser_h = os.path.join(SRC_EPUB, "RREpubParser.h")
        parser_m = os.path.join(SRC_EPUB, "RREpubParser.m")
        self.assertTrue(os.path.isfile(parser_h), "src/Epub/RREpubParser.h должен существовать")
        self.assertTrue(os.path.isfile(parser_m), "src/Epub/RREpubParser.m должен существовать")

    # ------------------------------------------------------------------------
    # [TASK-3.1.1 - 3.2.2] Интеграционный тест: потоковая распаковка и парсинг EPUB
    # ------------------------------------------------------------------------
    def test_3_3_zip_and_epub_parsing_integration(self):
        """[TASK-3.1.1 - 3.2.2] Компиляция и тестирование распаковки и XML-парсинга через нативный тест"""
        runner_c = os.path.join(PROJECT_ROOT, "tests", "_test_epub_runner.m")
        runner_bin = os.path.join(PROJECT_ROOT, "tests", "_test_epub_runner")

        test_code = f"""
#import <Foundation/Foundation.h>
#import "RRZipExtractor.h"
#import "RRBookModel.h"
#import "RRChapterModel.h"
#import "RREpubParser.h"

int main(int argc, const char * argv[]) {{
    @autoreleasepool {{
        NSString *epubPath = @"{self.test_epub_path}";
        
        // 1. Тест распаковщика RRZipExtractor
        NSString *destExtractDir = [NSTemporaryDirectory() stringByAppendingPathComponent:@"TDD_Extract_Test"];
        [[NSFileManager defaultManager] removeItemAtPath:destExtractDir error:nil];
        
        NSError *unzipError = nil;
        BOOL unzipOk = [RRZipExtractor unzipFileAtPath:epubPath toDestination:destExtractDir error:&unzipError];
        if (!unzipOk || unzipError) {{
            NSLog(@"[FAIL] Ошибка распаковки ZIP: %@", unzipError);
            return 1;
        }}
        
        NSString *containerPath = [destExtractDir stringByAppendingPathComponent:@"META-INF/container.xml"];
        if (![[NSFileManager defaultManager] fileExistsAtPath:containerPath]) {{
            NSLog(@"[FAIL] META-INF/container.xml не найден после распаковки");
            return 2;
        }}
        
        // 2. Тест генерации кэша cacheDirectoryForBookPath
        NSString *cachePath = [RRZipExtractor cacheDirectoryForBookPath:epubPath];
        if (!cachePath || cachePath.length == 0 || ![cachePath containsString:@"Books"]) {{
            NSLog(@"[FAIL] Некорректный путь кэша: %@", cachePath);
            return 3;
        }}
        
        // 3. Тест парсера RREpubParser
        NSError *parseError = nil;
        RRBookModel *book = [RREpubParser parseEpubAtPath:epubPath error:&parseError];
        if (!book || parseError) {{
            NSLog(@"[FAIL] Ошибка парсинга EPUB: %@", parseError);
            return 4;
        }}
        
        if (![book.title isEqualToString:@"TDD Alice in Wonderland"]) {{
            NSLog(@"[FAIL] Неверный заголовок книги: '%@'", book.title);
            return 5;
        }}
        
        if (![book.author isEqualToString:@"Lewis Carroll"]) {{
            NSLog(@"[FAIL] Неверный автор: '%@'", book.author);
            return 6;
        }}
        
        if (book.chapters.count != 2) {{
            NSLog(@"[FAIL] Ожидалось 2 главы, найдено: %lu", (unsigned long)book.chapters.count);
            return 7;
        }}
        
        RRChapterModel *ch1 = book.chapters[0];
        RRChapterModel *ch2 = book.chapters[1];
        
        if (![ch1.chapterId isEqualToString:@"c1"] || ![ch2.chapterId isEqualToString:@"c2"]) {{
            NSLog(@"[FAIL] Нарушен порядок spine в главах");
            return 8;
        }}
        
        if (![[NSFileManager defaultManager] fileExistsAtPath:ch1.absoluteHtmlPath]) {{
            NSLog(@"[FAIL] Файл главы 1 физически не существует: %@", ch1.absoluteHtmlPath);
            return 9;
        }}
        
        [[NSFileManager defaultManager] removeItemAtPath:destExtractDir error:nil];
    }}
    return 0;
}}
"""
        try:
            with open(runner_c, "w", encoding="utf-8") as f:
                f.write(test_code)

            cmd = [
                "clang", "-fobjc-arc",
                "-I", SRC_EPUB,
                "-framework", "Foundation",
                "-lz",
                os.path.join(SRC_EPUB, "RRZipExtractor.m"),
                os.path.join(SRC_EPUB, "RRChapterModel.m"),
                os.path.join(SRC_EPUB, "RRBookModel.m"),
                os.path.join(SRC_EPUB, "RREpubParser.m"),
                runner_c,
                "-o", runner_bin
            ]
            compile_res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(compile_res.returncode, 0, f"Ошибка компиляции test_epub_runner:\n{compile_res.stderr}")

            run_res = subprocess.run([runner_bin], capture_output=True, text=True)
            self.assertEqual(run_res.returncode, 0, f"Тест EPUB завершился с кодом {run_res.returncode}:\n{run_res.stderr}\n{run_res.stdout}")

        finally:
            if os.path.exists(runner_c): os.remove(runner_c)
            if os.path.exists(runner_bin): os.remove(runner_bin)

if __name__ == "__main__":
    unittest.main()
