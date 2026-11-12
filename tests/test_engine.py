"""Engine on local pages (headless, throwaway profile): snapshot, name guard, fill, upload, secrets hidden.
Needs Google Chrome and the agent-browser binary (python -m abkit setup)."""

import pathlib
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from abkit.engine import Browser, BrowserError  # noqa: E402
from abkit.guard import find  # noqa: E402

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.b = Browser(profile_dir=cls.tmp.name, headless=True, session="abop-test")
        cls.b.start()

    @classmethod
    def tearDownClass(cls):
        cls.b.close(force=True)
        time.sleep(1)
        cls.tmp.cleanup()

    def open(self, name):
        self.b.open((FIX / name).as_uri())
        return self.b.snapshot()

    def test_only_https(self):
        with self.assertRaises(BrowserError):
            Browser(headless=False).open("http://example.com")

    def test_secrets_never_read(self):
        snap = self.open("login.html")
        values = " ".join(e.get("value", "") for e in snap["elements"])
        for secret in ("S3cret-Pass", "4111111111111111", "918273", "tok-ABCDEF123"):
            self.assertNotIn(secret, values)
        self.assertIn("anh-nam", values)

    def test_click_refused_when_name_changed(self):
        snap = self.open("rename_button.html")
        btn = find(snap, kind="click")[0]
        self.b.eval("document.getElementById('b').textContent = 'Xóa tài khoản'")  # page changes after the snapshot
        with self.assertRaises(BrowserError):
            self.b.click(btn["id"], expect_name=btn["name"])

    def test_upload_and_fill(self):
        snap = self.open("upload_form.html")
        self.b.upload(find(snap, kind="upload")[0]["id"], FIX / "second_page.html")
        snap = self.b.snapshot()
        self.b.fill(find(snap, kind="fill")[0]["id"], "Mô tả có dấu tiếng Việt")
        snap = self.b.snapshot()
        self.assertEqual(find(snap, kind="fill")[0]["value"], "Mô tả có dấu tiếng Việt")
        post = find(snap, kind="click", names=("Đăng",))[0]
        self.assertFalse(post["disabled"])  # enabled only after a file was chosen


if __name__ == "__main__":
    unittest.main()
