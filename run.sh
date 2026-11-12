#!/bin/bash
# Launcher for macOS. Needs only Python 3.11+ (standard library, nothing to pip install).
# The agent-browser binary, Chrome profile, output and logs live in
# ~/Library/Application Support/agent-browser-own-profile.
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYCMD=""
for c in python3.13 python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    PYCMD="$c"; break
  fi
done
[ -n "$PYCMD" ] || { echo "CHƯA CÓ PYTHON 3.11+: cài tại https://www.python.org/downloads/macos/ rồi chạy lại."; exit 1; }
PYTHONPATH="$ROOT" exec "$PYCMD" -m abkit "$@"
