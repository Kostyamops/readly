import unittest
import os
import subprocess
import shutil

class TestMilestone5(unittest.TestCase):
    """
    TDD Tests for Milestone 5: Popover Translation UI (Issues #65 - #72)
    """

    def setUp(self):
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.popover_h = os.path.join(self.project_dir, "src", "Popover", "RRTranslationViewController.h")
        self.popover_m = os.path.join(self.project_dir, "src", "Popover", "RRTranslationViewController.m")
        self.reader_m = os.path.join(self.project_dir, "src", "Reader", "RRReaderViewController.m")
        self.sdk_path = os.path.expanduser("~/theos/sdks/iPhoneOS9.3.sdk")

    def test_01_popover_files_exist(self):
        """[M5-TASK-5.1.1.1] Verify RRTranslationViewController.h and .m exist"""
        self.assertTrue(os.path.isfile(self.popover_h), f"Missing {self.popover_h}")
        self.assertTrue(os.path.isfile(self.popover_m), f"Missing {self.popover_m}")

    def test_02_popover_header_declarations(self):
        """[M5-TASK-5.1.1.1 - 5.1.1.4] Verify properties and initialization method"""
        with open(self.popover_h, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("RRTranslationViewController : UIViewController", content)
        self.assertIn("RRWordEntry", content)
        self.assertIn("lblWord", content)
        self.assertIn("lblTranscription", content)
        self.assertIn("lblPos", content)
        self.assertIn("txtTranslation", content)
        self.assertIn("initWithWordEntry:", content)

    def test_03_popover_implementation_details(self):
        """[M5-TASK-5.1.1.1 - 5.1.1.4] Verify preferredContentSize and UI configuration"""
        with open(self.popover_m, "r", encoding="utf-8") as f:
            content = f.read()

        # Preferred content size 300x160
        self.assertIn("CGSizeMake(300, 160)", content)
        # Font checks
        self.assertIn("boldSystemFontOfSize:19", content)
        self.assertIn("italicSystemFontOfSize:13", content)
        # Badge corner radius
        self.assertIn("cornerRadius", content)
        self.assertIn("masksToBounds", content)
        # UITextView non-editable
        self.assertIn("editable = NO", content)
        self.assertIn("selectable = NO", content)
        # Dismiss tap gesture recognizer
        self.assertIn("handleDismissTap:", content)
        self.assertIn("dismissViewControllerAnimated", content)

    def test_04_reader_popover_presentation_binding(self):
        """[M5-TASK-5.1.2.1 - 5.1.2.3] Verify modalPresentationStyle, sourceView, sourceRect, permittedArrowDirections"""
        with open(self.reader_m, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("UIModalPresentationPopover", content)
        self.assertIn("popoverPresentationController", content)
        self.assertIn("sourceView = self.webView", content)
        self.assertIn("sourceRect", content)
        self.assertIn("permittedArrowDirections", content)
        self.assertIn("UIPopoverArrowDirectionUp", content)
        self.assertIn("UIPopoverArrowDirectionDown", content)

    def test_05_adaptive_presentation_style_none(self):
        """[M5-TASK-5.1.2.4] Verify adaptivePresentationStyleForPresentationController returns UIModalPresentationNone"""
        with open(self.reader_m, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("adaptivePresentationStyleForPresentationController", content)
        self.assertIn("UIModalPresentationNone", content)

    def test_06_popover_clang_compilation(self):
        """Verify armv7 compilation with iOS 9.3 SDK"""
        if not os.path.isdir(self.sdk_path):
            self.skipTest("iOS 9.3 SDK not found locally")

        test_harness = f"""
        #import <UIKit/UIKit.h>
        #import "{self.popover_h}"
        #import "{os.path.join(self.project_dir, 'src', 'Reader', 'RRReaderViewController.h')}"

        int main(int argc, char *argv[]) {{
            @autoreleasepool {{
                RRWordEntry *entry = [[RRWordEntry alloc] initWithWord:@"rabbit"
                                                         transcription:@"[ˈræbɪt]"
                                                          partOfSpeech:@"n."
                                                           translation:@"кролик"];
                RRTranslationViewController *vc = [[RRTranslationViewController alloc] initWithWordEntry:entry];
                (void)vc.view;
                
                RRReaderViewController *reader = [[RRReaderViewController alloc] initWithBook:nil];
                UIModalPresentationStyle style = [reader adaptivePresentationStyleForPresentationController:nil];
                if (style != UIModalPresentationNone) return 1;
            }}
            return 0;
        }}
        """
        harness_path = "/tmp/test_popover_harness.m"
        with open(harness_path, "w", encoding="utf-8") as f:
            f.write(test_harness)

        cmd = [
            "clang",
            "-target", "armv7-apple-ios9.3",
            "-isysroot", self.sdk_path,
            "-fobjc-arc",
            "-I", os.path.join(self.project_dir, "src", "Core"),
            "-I", os.path.join(self.project_dir, "src", "Dictionary"),
            "-I", os.path.join(self.project_dir, "src", "Epub"),
            "-I", os.path.join(self.project_dir, "src", "Reader"),
            "-I", os.path.join(self.project_dir, "src", "Popover"),
            "-c", harness_path,
            "-o", "/tmp/test_popover_harness.o"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"Clang compilation failed: {res.stderr}")

        if os.path.exists(harness_path):
            os.remove(harness_path)
        if os.path.exists("/tmp/test_popover_harness.o"):
            os.remove("/tmp/test_popover_harness.o")

if __name__ == "__main__":
    unittest.main()
