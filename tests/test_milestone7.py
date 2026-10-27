import os
import sys
import subprocess
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

class TestMilestone7(unittest.TestCase):
    """
    TDD Test Suite for Milestone 7: Custom EPUBs, Library Shelf, Reader Settings
    Covers [M7-TASK-7.1.1.1] - [M7-TASK-7.3.1.3] (Issues #79 - #86).
    """

    def setUp(self):
        self.theos_dir = os.environ.get("THEOS", os.path.expanduser("~/theos"))
        self.sdk_path = os.path.join(self.theos_dir, "sdks", "iPhoneOS9.3.sdk")

    def test_7_1_info_plist_document_types(self):
        """[M7-TASK-7.1.1.1] Verify Info.plist has CFBundleDocumentTypes and UIFileSharingEnabled"""
        plist_path = os.path.join(PROJECT_ROOT, "resources", "Info.plist")
        with open(plist_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("UIFileSharingEnabled", content)
        self.assertIn("CFBundleDocumentTypes", content)
        self.assertIn("org.idpf.epub-container", content)
        self.assertIn("UTImportedTypeDeclarations", content)

    def test_7_2_appdelegate_open_url_handlers(self):
        """[M7-TASK-7.1.1.2] Verify AppDelegate.m handles incoming openURL"""
        appdel_path = os.path.join(SRC_DIR, "Core", "AppDelegate.m")
        with open(appdel_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("openURL", content)
        self.assertIn("RRBookStorageManager", content)
        self.assertIn("handleIncomingURL:", content)

    def test_7_3_book_storage_manager(self):
        """[M7-TASK-7.1.1.3] Verify RRBookStorageManager exists and has required methods"""
        h_path = os.path.join(SRC_DIR, "Storage", "RRBookStorageManager.h")
        m_path = os.path.join(SRC_DIR, "Storage", "RRBookStorageManager.m")
        self.assertTrue(os.path.isfile(h_path))
        self.assertTrue(os.path.isfile(m_path))

        with open(h_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("sharedManager", content)
        self.assertIn("loadAllBooks", content)
        self.assertIn("importEpubFromURL:", content)
        self.assertIn("deleteBook:", content)

    def test_7_4_book_shelf_view_controller(self):
        """[M7-TASK-7.2.1.1 - 7.2.1.2] Verify RRBookShelfViewController exists and conforms to UITableView delegates"""
        h_path = os.path.join(SRC_DIR, "Library", "RRBookShelfViewController.h")
        m_path = os.path.join(SRC_DIR, "Library", "RRBookShelfViewController.m")
        self.assertTrue(os.path.isfile(h_path))
        self.assertTrue(os.path.isfile(m_path))

        with open(h_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("UITableViewDataSource", content)
        self.assertIn("UITableViewDelegate", content)
        self.assertIn("reloadBooks", content)

    def test_7_5_reader_settings_and_popover(self):
        """[M7-TASK-7.3.1.1 - 7.3.1.2] Verify RRReaderSettings and RRSettingsViewController"""
        settings_h = os.path.join(SRC_DIR, "Reader", "RRReaderSettings.h")
        settings_vc_h = os.path.join(SRC_DIR, "Reader", "RRSettingsViewController.h")
        self.assertTrue(os.path.isfile(settings_h))
        self.assertTrue(os.path.isfile(settings_vc_h))

        with open(settings_h, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("fontSize", content)
        self.assertIn("fontFamily", content)
        self.assertIn("theme", content)

    def test_7_6_js_bridge_dynamic_styles(self):
        """[M7-TASK-7.3.1.3] Verify reader_bridge.js dynamic styling functions"""
        js_path = os.path.join(SRC_DIR, "Reader", "Assets", "reader_bridge.js")
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("RRSetFontSize", content)
        self.assertIn("RRSetFontFamily", content)
        self.assertIn("RRSetTheme", content)
        self.assertIn("RRApplySettings", content)

    def test_7_7_clang_compilation_armv7(self):
        """Verify clang compilation of new modules under armv7 iOS 9.3 SDK"""
        if not os.path.isdir(self.sdk_path):
            self.skipTest("iOS 9.3 SDK not found locally")

        sources = [
            os.path.join(SRC_DIR, "Storage", "RRBookStorageManager.m"),
            os.path.join(SRC_DIR, "Library", "RRBookShelfViewController.m"),
            os.path.join(SRC_DIR, "Reader", "RRReaderSettings.m"),
            os.path.join(SRC_DIR, "Reader", "RRSettingsViewController.m")
        ]

        for src in sources:
            cmd = [
                "clang", "-fsyntax-only", "-fobjc-arc",
                "-target", "armv7-apple-ios9.3",
                "-isysroot", self.sdk_path,
                "-I", os.path.join(SRC_DIR, "Core"),
                "-I", os.path.join(SRC_DIR, "Dictionary"),
                "-I", os.path.join(SRC_DIR, "Epub"),
                "-I", os.path.join(SRC_DIR, "Reader"),
                "-I", os.path.join(SRC_DIR, "Popover"),
                "-I", os.path.join(SRC_DIR, "Storage"),
                "-I", os.path.join(SRC_DIR, "Library"),
                src
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Compilation failed for {os.path.basename(src)}:\n{res.stderr}")

if __name__ == "__main__":
    unittest.main()
