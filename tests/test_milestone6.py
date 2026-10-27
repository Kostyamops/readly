import unittest
import os
import subprocess
import zipfile

class TestMilestone6(unittest.TestCase):
    """
    TDD Tests for Milestone 6: Memory Optimization & Release Packaging (Issues #73 - #78)
    """

    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.appdelegate_m = os.path.join(self.project_dir, "src", "Core", "AppDelegate.m")
        self.reader_m = os.path.join(self.project_dir, "src", "Reader", "RRReaderViewController.m")
        self.sample_epub = os.path.join(self.project_dir, "resources", "sample.epub")
        self.dict_sqlite = os.path.join(self.project_dir, "resources", "dictionary.sqlite")
        self.makefile = os.path.join(self.project_dir, "Makefile")
        self.sdk_path = os.path.expanduser("~/theos/sdks/iPhoneOS9.3.sdk")

    def test_01_appdelegate_memory_and_lifecycle(self):
        """[M6-TASK-6.1.1.1, 6.1.1.3] Verify AppDelegate memory flushing and startup integration"""
        with open(self.appdelegate_m, "r", encoding="utf-8") as f:
            content = f.read()

        # Database and EPUB initialization
        self.assertIn("openDatabaseWithPath:", content)
        self.assertIn("parseEpubAtPath:", content)
        self.assertIn("initWithBook:", content)

        # Background cache flush
        self.assertIn("applicationDidEnterBackground:", content)
        self.assertIn("[NSURLCache sharedURLCache] removeAllCachedResponses", content)

        # Memory warning cache flush
        self.assertIn("applicationDidReceiveMemoryWarning:", content)

    def test_02_reader_memory_and_dom_unloading(self):
        """[M6-TASK-6.1.1.1, 6.1.1.2] Verify DOM unloading and didReceiveMemoryWarning in Reader"""
        with open(self.reader_m, "r", encoding="utf-8") as f:
            content = f.read()

        # Memory warning in controller
        self.assertIn("didReceiveMemoryWarning", content)
        self.assertIn("[NSURLCache sharedURLCache] removeAllCachedResponses", content)

        # DOM clearing on chapter change for iPad 2 memory protection
        self.assertIn("document.body.innerHTML", content)

    def test_03_sample_epub_data_integrity(self):
        """[M6-TASK-6.1.2.1] Verify resources/sample.epub is a valid EPUB structure"""
        self.assertTrue(os.path.isfile(self.sample_epub), f"Missing {self.sample_epub}")
        self.assertGreater(os.path.getsize(self.sample_epub), 500)

        with zipfile.ZipFile(self.sample_epub, "r") as zf:
            names = zf.namelist()
            self.assertIn("mimetype", names)
            self.assertIn("META-INF/container.xml", names)
            self.assertTrue(any(n.endswith(".opf") for n in names))

    def test_04_bundle_resource_configuration(self):
        """[M6-TASK-6.1.2.2] Verify resources directory configured in Makefile"""
        with open(self.makefile, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("RetroReader_RESOURCE_DIRS = resources", content)
        self.assertTrue(os.path.isfile(self.dict_sqlite))
        self.assertTrue(os.path.isfile(self.sample_epub))

    def test_05_appdelegate_clang_compilation(self):
        """[M6-TASK-6.1.1.1 - 6.1.1.3] Verify AppDelegate.m compiles cleanly for armv7 iOS 9.3"""
        if not os.path.isdir(self.sdk_path):
            self.skipTest("iOS 9.3 SDK not found locally")

        cmd = [
            "clang", "-fsyntax-only", "-fobjc-arc",
            "-target", "armv7-apple-ios9.3",
            "-isysroot", self.sdk_path,
            "-I", os.path.join(self.project_dir, "src", "Core"),
            "-I", os.path.join(self.project_dir, "src", "Dictionary"),
            "-I", os.path.join(self.project_dir, "src", "Epub"),
            "-I", os.path.join(self.project_dir, "src", "Reader"),
            "-I", os.path.join(self.project_dir, "src", "Popover"),
            "-I", os.path.join(self.project_dir, "src", "Storage"),
            "-I", os.path.join(self.project_dir, "src", "Library"),
            self.appdelegate_m
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"AppDelegate.m compilation failed:\n{res.stderr}")

if __name__ == "__main__":
    unittest.main()
