"""Browser engine: drives Chrome through the agent-browser CLI (Rust, Vercel Labs, Apache-2.0).

agent-browser keeps one Chrome open in a background daemon per --session, so every call below is a short
CLI run (tens of milliseconds) instead of a new Chrome. Only snapshot.js and the fixed snippets in this
file are ever evaluated in a page: no caller-supplied JavaScript.

Elements are addressed by the data-bok-id="eN" attribute that snapshot.js sets; before each click the
current name of the element is compared with the name seen in the snapshot (the page may have changed).
"""

import base64
import json
import os
import pathlib
import re
import subprocess
import time

from .install import agent_browser_path

SNAPSHOT_JS = pathlib.Path(__file__).with_name("snapshot.js").read_text(encoding="utf-8")
CALL_TIMEOUT_S = 40
OPEN_TIMEOUT_S = 60
ID_RE = re.compile(r"^e\d{1,4}$")
READ_LIMIT = 8000
KEEP_OPEN_MS = int(os.environ.get("ABOP_KEEP_OPEN_MS", 300000))  # 5 minutes; 0 = close after each command

# Fixed snippets. {sel} is only ever a validated [data-bok-id="eN"] selector.
NAME_JS = "(() => {{ const el = document.querySelector('{sel}'); " \
          "return el && typeof window.__bokName === 'function' ? window.__bokName(el) : null; }})()"
TEXT_JS = "(() => (document.body ? document.body.innerText : '').slice(0, %d))()" % READ_LIMIT
SCROLL_JS = "(() => {{ const el = document.querySelector('{sel}'); if (!el) return false; " \
            "let p = el; while (p && p !== document.body) {{ if (p.scrollHeight > p.clientHeight + 10 && " \
            "/(auto|scroll)/.test(getComputedStyle(p).overflowY)) break; p = p.parentElement; }} " \
            "(p && p !== document.body ? p : document.scrollingElement).scrollBy(0, {px}); return true; }})()"


class BrowserError(RuntimeError):
    pass


def find_chrome():
    """Google Chrome installed on this machine (Windows, macOS, Linux)."""
    candidates = []
    for base in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
        if base:
            candidates.append(pathlib.Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe")
    candidates += [pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                   pathlib.Path("/usr/bin/google-chrome"), pathlib.Path("/usr/bin/google-chrome-stable")]
    for c in candidates:
        if c.is_file():
            return str(c)
    raise RuntimeError("không thấy Google Chrome trên máy")


def sel(el_id):
    if not ID_RE.match(el_id or ""):
        raise BrowserError(f"mã phần tử không hợp lệ: {el_id!r}")
    return f'[data-bok-id="{el_id}"]'


class Browser:
    """One agent-browser session. profile_dir: persistent Chrome profile (logins kept).
    attach=True: the user's own running Chrome via --auto-connect (Chrome asks Allow)."""

    def __init__(self, profile_dir=None, headless=False, attach=False, session="abop", chrome=None):
        self.exe = str(agent_browser_path())
        self.profile_dir = str(profile_dir) if profile_dir else None
        self.headless = headless
        self.attach = attach
        self.session = session
        self.chrome = chrome
        self.version = None
        self.started = False

    # low level

    def _run(self, *args, timeout=CALL_TIMEOUT_S, launch=False):
        cmd = [self.exe, "--session", self.session, "--json"]
        if launch:  # launch options only matter on the command that starts the daemon
            if self.attach:
                cmd.append("--auto-connect")
            else:
                if not self.headless:
                    cmd.append("--headed")
                if self.profile_dir:
                    cmd += ["--profile", self.profile_dir]
                cmd += ["--executable-path", self.chrome or find_chrome()]
        cmd += [str(a) for a in args]
        # Chrome stays open between commands (the speed gain) and shuts itself after KEEP_OPEN_MS idle.
        env = {**os.environ, "AGENT_BROWSER_IDLE_TIMEOUT_MS": str(KEEP_OPEN_MS)}
        try:
            out = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace",
                                 timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            raise BrowserError(f"lệnh {args[0]} quá {timeout} giây")
        line = next((ln for ln in reversed(out.stdout.splitlines()) if ln.startswith("{")), None)
        if line is None:
            raise BrowserError((out.stderr or out.stdout or "agent-browser không trả lời").strip()[:300])
        reply = json.loads(line)
        if not reply.get("success"):
            raise BrowserError(str(reply.get("error") or "lỗi không rõ")[:300])
        return reply.get("data") or {}

    def eval(self, js):
        data = self._run("eval", "-b", base64.b64encode(js.encode("utf-8")).decode("ascii"))
        return data.get("result")

    # lifecycle

    def start(self):
        self.started = True
        self.version = "agent-browser"

    def close(self, force=False):
        """End of a command. Chrome is kept for the next command unless force or KEEP_OPEN_MS == 0."""
        if not self.started:
            return
        self.started = False
        if not force and KEEP_OPEN_MS and not self.attach:
            return
        try:
            self._run("close", timeout=20)
        except BrowserError:
            pass

    # actions

    def open(self, url):
        if not (url.startswith("https://") or (self.headless and url.startswith("file://"))):
            raise BrowserError("chỉ mở được địa chỉ https://")
        last = None
        for _ in range(2):  # the first page of a fresh Chrome is sometimes left on about:blank
            data = self._run("open", url, timeout=OPEN_TIMEOUT_S, launch=True)
            if data.get("url", "").startswith(("https://", "file://")):
                return {"title": data.get("title", ""), "url": data.get("url", "")}
            last = data
        raise BrowserError(f"không mở được {url} (dừng ở {last.get('url') if last else '?'})")

    def snapshot(self):
        snap = self.eval("(" + SNAPSHOT_JS + ")()")
        if not isinstance(snap, dict):
            raise BrowserError("không đọc được trang")
        return snap

    def read_text(self):
        return self.eval(TEXT_JS) or ""

    def current_name(self, el_id):
        return self.eval(NAME_JS.format(sel=sel(el_id)))

    def click(self, el_id, expect_name=None, expect_text=None):
        if expect_name is not None:
            now = self.current_name(el_id)
            if now is None:
                raise BrowserError("nút không còn trên trang")
            if now != expect_name:
                raise BrowserError(f"nút đã đổi tên ('{expect_name}' thành '{now}'), không bấm")
        self._run("scrollintoview", sel(el_id))
        return self._run("click", sel(el_id))

    def fill(self, el_id, text):
        self._run("click", sel(el_id))
        try:
            return self._run("fill", sel(el_id), "--", text)
        except BrowserError:  # rich editors (contenteditable) refuse fill: type real keystrokes instead
            self._run("press", "Control+a")
            return self._run("keyboard", "inserttext", text)

    def upload(self, el_id, path):
        return self._run("upload", sel(el_id), str(path), timeout=120)

    def scroll(self, el_id, times=5):
        for _ in range(times):
            self.eval(SCROLL_JS.format(sel=sel(el_id), px=600))
            time.sleep(0.3)
        time.sleep(1.5)  # time for the page to load the next batch
        return True

    def screenshot(self, path):
        return self._run("screenshot", str(path))
