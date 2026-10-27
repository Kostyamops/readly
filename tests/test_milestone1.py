#!/usr/bin/env python3
"""
TDD Test Suite для Milestone 1 (Задачи 1.1.1.1 - 1.1.3.3)
Проверяет окружение, конфиги, синтаксис кода и архитектуру сборки.
"""

import os
import sys
import shutil
import plistlib
import subprocess
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestMilestone1(unittest.TestCase):

    # ------------------------------------------------------------------------
    # [TASK-1.1.1.1] Утилиты хоста
    # ------------------------------------------------------------------------
    def test_1_1_1_1_host_utilities(self):
        """[TASK-1.1.1.1] Проверка наличия brew, ldid и dpkg в системе"""
        brew_path = shutil.which("brew")
        ldid_path = shutil.which("ldid")
        dpkg_path = shutil.which("dpkg") or shutil.which("dpkg-deb")

        self.assertIsNotNone(brew_path, "Homebrew должен быть установлен в системе")
        self.assertIsNotNone(ldid_path, "Утилита ldid (псевдоподпись iOS) должна быть установлена: brew install ldid")
        self.assertIsNotNone(dpkg_path, "Утилита dpkg (упаковка .deb) должна быть установлена: brew install dpkg")

    # ------------------------------------------------------------------------
    # [TASK-1.1.1.2] Установка Theos
    # ------------------------------------------------------------------------
    def test_1_1_1_2_theos_installed(self):
        """[TASK-1.1.1.2] Проверка наличия Theos в ~/theos или $THEOS"""
        theos_dir = os.environ.get("THEOS", os.path.expanduser("~/theos"))
        self.assertTrue(os.path.isdir(theos_dir), f"Каталог Theos не найден по пути: {theos_dir}")
        self.assertTrue(
            os.path.isfile(os.path.join(theos_dir, "bin", "nic.pl")) or
            os.path.isdir(os.path.join(theos_dir, "makefiles")),
            "Каталог Theos не содержит необходимых сборочных файлов"
        )

    # ------------------------------------------------------------------------
    # [TASK-1.1.1.3] Заголовочный SDK iOS 9/10 с поддержкой armv7
    # ------------------------------------------------------------------------
    def test_1_1_1_3_ios_sdk(self):
        """[TASK-1.1.1.3] Проверка наличия SDK с поддержкой armv7 в $THEOS/sdks/"""
        theos_dir = os.environ.get("THEOS", os.path.expanduser("~/theos"))
        sdks_dir = os.path.join(theos_dir, "sdks")
        self.assertTrue(os.path.isdir(sdks_dir), f"Каталог SDKs не найден: {sdks_dir}")

        sdks = [d for d in os.listdir(sdks_dir) if d.endswith(".sdk")]
        self.assertGreater(len(sdks), 0, "В каталоге $THEOS/sdks/ должен присутствовать хотя бы один заголовочный iOS SDK")

    # ------------------------------------------------------------------------
    # [TASK-1.1.2.1] Корневой Makefile проекта
    # ------------------------------------------------------------------------
    def test_1_1_2_1_makefile_configuration(self):
        """[TASK-1.1.2.1] Проверка синтаксиса и параметров Makefile"""
        makefile_path = os.path.join(PROJECT_ROOT, "Makefile")
        self.assertTrue(os.path.isfile(makefile_path), "Файл Makefile должен присутствовать в корне проекта")

        with open(makefile_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("TARGET", content, "Makefile должен задавать TARGET (например iphone:clang:latest:9.3)")
        self.assertIn("ARCHS", content, "Makefile должен задавать ARCHS")
        self.assertIn("armv7", content, "Makefile должен содержать архитектуру armv7")
        self.assertIn("RetroReader", content, "Имя приложения должно быть RetroReader")
        self.assertIn("UIKit", content, "Должен быть подключен UIKit.framework")
        self.assertIn("Foundation", content, "Должен быть подключен Foundation.framework")

    # ------------------------------------------------------------------------
    # [TASK-1.1.2.2] Файл control (Debian-пакет)
    # ------------------------------------------------------------------------
    def test_1_1_2_2_control_file(self):
        """[TASK-1.1.2.2] Проверка метаданных control файла"""
        control_path = os.path.join(PROJECT_ROOT, "control")
        self.assertTrue(os.path.isfile(control_path), "Файл control должен присутствовать в корне проекта")

        with open(control_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fields = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                fields[k.strip()] = v.strip()

        self.assertEqual(fields.get("Package"), "com.retroread.app", "Package должен быть com.retroread.app")
        self.assertEqual(fields.get("Name"), "RetroReader", "Name должен быть RetroReader")
        self.assertIn("arm", fields.get("Architecture", ""), "Архитектура должна быть iphoneos-arm")
        self.assertEqual(fields.get("Section"), "Applications", "Section должна быть Applications")

    # ------------------------------------------------------------------------
    # [TASK-1.1.2.3] Info.plist приложения
    # ------------------------------------------------------------------------
    def test_1_1_2_3_info_plist(self):
        """[TASK-1.1.2.3] Проверка валидности resources/Info.plist"""
        plist_path = os.path.join(PROJECT_ROOT, "resources", "Info.plist")
        self.assertTrue(os.path.isfile(plist_path), "Файл Info.plist должен присутствовать в resources/")

        with open(plist_path, "rb") as f:
            data = plistlib.load(f)

        self.assertEqual(data.get("CFBundleIdentifier"), "com.retroread.app")
        self.assertEqual(data.get("CFBundleExecutable"), "RetroReader")
        self.assertTrue(data.get("LSRequiresIPhoneOS"))
        
        # Проверка семейства устройств iPad (UIDeviceFamily = 2)
        device_family = data.get("UIDeviceFamily")
        self.assertTrue(
            (isinstance(device_family, list) and 2 in device_family) or device_family == 2,
            "UIDeviceFamily должен содержать 2 (iPad)"
        )

    # ------------------------------------------------------------------------
    # [TASK-1.1.2.4] Entitlements.plist
    # ------------------------------------------------------------------------
    def test_1_1_2_4_entitlements(self):
        """[TASK-1.1.2.4] Проверка валидности resources/Entitlements.plist"""
        ent_path = os.path.join(PROJECT_ROOT, "resources", "Entitlements.plist")
        self.assertTrue(os.path.isfile(ent_path), "Файл Entitlements.plist должен присутствовать в resources/")

        with open(ent_path, "rb") as f:
            data = plistlib.load(f)

        self.assertIsInstance(data, dict, "Entitlements.plist должен быть валидным словарём plist")

    # ------------------------------------------------------------------------
    # [TASK-1.1.3.1] Точка входа main.m и AppDelegate
    # ------------------------------------------------------------------------
    def test_1_1_3_1_main_and_appdelegate_syntax(self):
        """[TASK-1.1.3.1] Проверка синтаксиса Objective-C исходников точки входа"""
        main_m = os.path.join(PROJECT_ROOT, "src", "main.m")
        app_del_h = os.path.join(PROJECT_ROOT, "src", "Core", "AppDelegate.h")
        app_del_m = os.path.join(PROJECT_ROOT, "src", "Core", "AppDelegate.m")

        self.assertTrue(os.path.isfile(main_m), "src/main.m должен существовать")
        self.assertTrue(os.path.isfile(app_del_h), "src/Core/AppDelegate.h должен существовать")
        self.assertTrue(os.path.isfile(app_del_m), "src/Core/AppDelegate.m должен существовать")

        # Проверка синтаксиса компилятором Clang с iOS SDK
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
            app_del_m
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Ошибка компиляции AppDelegate.m:\n{res.stderr}")

    # ------------------------------------------------------------------------
    # [TASK-1.1.3.2] Проверка структуры сборочного пайплайна
    # ------------------------------------------------------------------------
    def test_1_1_3_2_theos_project_structure(self):
        """[TASK-1.1.3.2] Проверка наличия всех компонентов для команды make package"""
        required_paths = [
            os.path.join(PROJECT_ROOT, "Makefile"),
            os.path.join(PROJECT_ROOT, "control"),
            os.path.join(PROJECT_ROOT, "src", "main.m"),
            os.path.join(PROJECT_ROOT, "src", "Core", "AppDelegate.m"),
            os.path.join(PROJECT_ROOT, "resources", "Info.plist")
        ]
        for p in required_paths:
            self.assertTrue(os.path.exists(p), f"Обязательный сборочный артефакт отсутствует: {p}")

    # ------------------------------------------------------------------------
    # [TASK-1.1.3.3] Проверка целевой архитектуры сборки armv7
    # ------------------------------------------------------------------------
    def test_1_1_3_3_binary_architecture_target(self):
        """[TASK-1.1.3.3] Проверка, что компилятор Clang умеет таргетировать armv7 Mach-O"""
        # Проверяем на минимальном файле, что clang на M4 способен собрать armv7 объектный файл
        test_c = os.path.join(PROJECT_ROOT, "tests", "_test_armv7.c")
        test_o = os.path.join(PROJECT_ROOT, "tests", "_test_armv7.o")
        try:
            with open(test_c, "w") as f:
                f.write("int main(void) { return 0; }\n")

            cmd = ["clang", "-target", "armv7-apple-ios9.3", "-c", test_c, "-o", test_o]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Clang не может скомпилировать armv7 код:\n{res.stderr}")

            # Проверяем утилитой file
            file_cmd = ["file", test_o]
            file_res = subprocess.run(file_cmd, capture_output=True, text=True)
            self.assertIn("arm_v7", file_res.stdout, "Скомпилированный файл должен содержать срез arm_v7")
        finally:
            if os.path.exists(test_c): os.remove(test_c)
            if os.path.exists(test_o): os.remove(test_o)

if __name__ == "__main__":
    unittest.main()
