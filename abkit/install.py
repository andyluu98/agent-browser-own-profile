"""Where things live, and the one-time download of the agent-browser binary.

The binary is pinned to one version and checked against the SHA-256 published on its GitHub release, so a
student always runs exactly the build this repo was tested with. Nothing else is installed: no pip, no npm.
"""

import hashlib
import os
import pathlib
import platform
import shutil
import sys
import urllib.request

VERSION = "0.42.0"
RELEASE = f"https://github.com/vercel-labs/agent-browser/releases/download/v{VERSION}/"
# sha256 digests from the GitHub release v0.42.0 (read 12/11/2026)
ASSETS = {
    ("Windows", "AMD64"): ("agent-browser-win32-x64.exe",
                           "8209f42e604d012f789caa14ae73a57200925608409fa09427b0fd6e4f3adf15"),
    ("Darwin", "arm64"): ("agent-browser-darwin-arm64",
                          "b1b2946c95d218b035262483f2c6193e0f216c155c903bcc532ce47e29d8e72d"),
    ("Darwin", "x86_64"): ("agent-browser-darwin-x64",
                           "802883bc38519e550525f74bb3e7ca692029082bdd2b7c235c26167b130c8d66"),
}


def home():
    """Fixed folder for the binary, Chrome profile, output and logs: plugin updates never touch it."""
    if os.environ.get("ABOP_HOME"):
        return pathlib.Path(os.environ["ABOP_HOME"])
    if sys.platform == "win32":
        return pathlib.Path(os.environ["LOCALAPPDATA"]) / "agent-browser-own-profile"
    if sys.platform == "darwin":
        return pathlib.Path.home() / "Library" / "Application Support" / "agent-browser-own-profile"
    return pathlib.Path.home() / ".local" / "share" / "agent-browser-own-profile"


def default_profile():
    return pathlib.Path(os.environ.get("ABOP_PROFILE") or home() / "chrome")


def _asset():
    key = (platform.system(), platform.machine())
    if key not in ASSETS:
        raise RuntimeError(f"chưa hỗ trợ máy {key[0]} {key[1]} (có: Windows x64, macOS)")
    return ASSETS[key]


def agent_browser_path():
    """The pinned binary in home()/bin; ABOP_AGENT_BROWSER overrides it (for development)."""
    if os.environ.get("ABOP_AGENT_BROWSER"):
        return pathlib.Path(os.environ["ABOP_AGENT_BROWSER"])
    name, _ = _asset()
    exe = home() / "bin" / (f"agent-browser-{VERSION}" + (".exe" if name.endswith(".exe") else ""))
    return exe if exe.is_file() else setup()  # first run downloads it


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def setup():
    """Download the pinned binary once and verify it. Returns its path."""
    name, digest = _asset()
    target = home() / "bin" / (f"agent-browser-{VERSION}" + (".exe" if name.endswith(".exe") else ""))
    if target.is_file() and sha256(target) == digest:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    print(f"Đang tải agent-browser {VERSION} (khoảng 19 MB)...")
    with urllib.request.urlopen(RELEASE + name, timeout=120) as r, open(part, "wb") as f:
        shutil.copyfileobj(r, f)
    got = sha256(part)
    if got != digest:
        part.unlink()
        raise RuntimeError("file tải về không khớp mã kiểm tra SHA-256, đã bỏ. Thử lại sau.")
    part.replace(target)
    if sys.platform != "win32":
        target.chmod(0o755)
    print(f"Đã tải và kiểm tra: {target}")
    return target
