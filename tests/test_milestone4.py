#!/usr/bin/env python3
"""
TDD Test Suite для Milestone 4: Читалка и перехват кликов (UIWebView + CSS + JS Bridge)
Покрывает задачи: [M4-TASK-4.1.1.1] - [M4-TASK-4.2.2.2] (Issues #48 - #64).
"""

import os
import sys
import subprocess
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
READER_DIR = os.path.join(PROJECT_ROOT, "src", "Reader")
ASSETS_DIR = os.path.join(READER_DIR, "Assets")

class TestMilestone4(unittest.TestCase):

    # ------------------------------------------------------------------------
    # [TASK-4.1.2.1 - 4.1.2.2] CSS-верстка страниц (CSS Multi-Column)
    # ------------------------------------------------------------------------
    def test_4_1_css_multi_column_rules(self):
        """[TASK-4.1.2.1 - 4.1.2.2] Проверка правил колоночной верстки и защиты от выделения в reader_style.css"""
        css_path = os.path.join(ASSETS_DIR, "reader_style.css")
        self.assertTrue(os.path.isfile(css_path), "src/Reader/Assets/reader_style.css должен существовать")

        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn("-webkit-column-width", css, "CSS должен содержать свойство -webkit-column-width")
        self.assertIn("-webkit-column-gap", css, "CSS должен содержать свойство -webkit-column-gap")
        self.assertIn("-webkit-user-select", css, "CSS должен отключать системное синее выделение текста")
        self.assertIn("-webkit-touch-callout", css, "CSS должен отключать системное контекстное меню iOS")
        self.assertIn("#book-container", css, "CSS должен задавать правила для контейнера #book-container")

    # ------------------------------------------------------------------------
    # [TASK-4.2.1.1 - 4.2.1.5] JavaScript Bridge (детекция клика и координат)
    # ------------------------------------------------------------------------
    def test_4_2_js_bridge_logic(self):
        """[TASK-4.2.1.1 - 4.2.1.5] Проверка логики JS-моста в reader_bridge.js"""
        js_path = os.path.join(ASSETS_DIR, "reader_bridge.js")
        self.assertTrue(os.path.isfile(js_path), "src/Reader/Assets/reader_bridge.js должен существовать")

        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("caretRangeFromPoint", js, "JS должен использовать caretRangeFromPoint для нахождения слова под пальцем")
        self.assertIn("expand('word')", js, "JS должен расширять диапазон до границы слова: range.expand('word')")
        self.assertIn("getBoundingClientRect", js, "JS должен вычислять экранные координаты слова через getBoundingClientRect()")
        self.assertIn("reader-bridge://wordTap", js, "JS должен отправлять кастомную URI-схему reader-bridge://wordTap")
        self.assertIn("RRScrollToPage", js, "JS должен содержать функцию RRScrollToPage для пагинации")

    # ------------------------------------------------------------------------
    # [TASK-4.1.1.1 - 4.2.2.2] Контроллер RRReaderViewController
    # ------------------------------------------------------------------------
    def test_4_3_reader_viewcontroller_files(self):
        """[TASK-4.1.1.1 - 4.2.2.2] Проверка наличия исходных файлов RRReaderViewController"""
        h_path = os.path.join(READER_DIR, "RRReaderViewController.h")
        m_path = os.path.join(READER_DIR, "RRReaderViewController.m")

        self.assertTrue(os.path.isfile(h_path), "src/Reader/RRReaderViewController.h должен существовать")
        self.assertTrue(os.path.isfile(m_path), "src/Reader/RRReaderViewController.m должен существовать")

    # ------------------------------------------------------------------------
    # Интеграционный тест: Компиляция RRReaderViewController под iOS 9.3 SDK
    # ------------------------------------------------------------------------
    def test_4_4_reader_viewcontroller_compilation(self):
        """[TASK-4.1.1 - 4.2.2] Проверка компиляции RRReaderViewController с заголовочным SDK iOS 9.3"""
        m_path = os.path.join(READER_DIR, "RRReaderViewController.m")
        theos_dir = os.environ.get("THEOS", os.path.expanduser("~/theos"))
        sdk_path = os.path.join(theos_dir, "sdks", "iPhoneOS9.3.sdk")

        cmd = [
            "clang", "-fsyntax-only", "-fobjc-arc",
            "-target", "armv7-apple-ios9.3",
            "-isysroot", sdk_path,
            "-I", os.path.join(PROJECT_ROOT, "src", "Core"),
            "-I", os.path.join(PROJECT_ROOT, "src", "Dictionary"),
            "-I", os.path.join(PROJECT_ROOT, "src", "Epub"),
            "-I", os.path.join(PROJECT_ROOT, "src", "Reader"),
            "-I", os.path.join(PROJECT_ROOT, "src", "Popover"),
            m_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Ошибка компиляции RRReaderViewController.m:\n{res.stderr}")

if __name__ == "__main__":
    unittest.main()
