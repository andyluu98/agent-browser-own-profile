@echo off
rem Launcher for Windows. Needs only Python 3.11+ (standard library, nothing to pip install).
rem The agent-browser binary, Chrome profile, output and logs live in %LOCALAPPDATA%\agent-browser-own-profile.
setlocal
set "ROOT=%~dp0"
set "PYCMD="
where py >nul 2>nul && py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD (
  where python >nul 2>nul && python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul && set "PYCMD=python"
)
if not defined PYCMD (
  echo CHUA CO PYTHON 3.11+: cai tai https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) roi chay lai.
  exit /b 1
)
set "PYTHONPATH=%ROOT%"
set "PYTHONIOENCODING=utf-8"
%PYCMD% -m abkit %*
