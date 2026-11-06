@echo off
rem fullstack-agent (ChatGPT fork): memory, chat, face, hands.
rem Copyright (C) 2026 Jared Rhodenizer — ChatGPT adaptations by contributors
rem SPDX-License-Identifier: AGPL-3.0-or-later
rem
rem   start.bat          face (if installed) — keeps window open
rem   start.bat chat     ChatGPT typed chat
rem   start.bat hands    barehands board
rem   start.bat voice    same as chat (ChatGPT; no Claude backtalk)

setlocal
set "TOOLBOX=%~dp0"
set "MODE=%~1"
if "%MODE%"=="" set "MODE=all"

set "PATH=%USERPROFILE%\.local\bin;%PATH%"
cd /d "%TOOLBOX%.."

if /I "%MODE%"=="chat" goto :chat
if /I "%MODE%"=="voice" goto :chat

if exist "ai-visualizer\" if /I not "%MODE%"=="hands" (
  echo   face:  starting
  start "agent face" cmd /c "cd /d ai-visualizer && run.bat"
)

if exist "barehands\" if /I "%MODE%"=="hands" (
  echo   hands: starting
  start "agent hands" cmd /c "cd /d barehands && run.bat"
)

if /I "%MODE%"=="hands" goto :eof
if /I "%MODE%"=="all" if not exist "ai-visualizer\" goto :chat
if /I "%MODE%"=="all" (
  echo   Face started. For ChatGPT chat, run: start.bat chat
  pause
  goto :eof
)

goto :eof

:chat
echo   chatgpt: starting typed chat
cd /d "%TOOLBOX%chatgpt"
set "PY="
if exist "%LocalAppData%\Programs\Python\Python314\python.exe" set "PY=%LocalAppData%\Programs\Python\Python314\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PY=%LocalAppData%\Programs\Python\Python313\python.exe"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo   No Python found. Install Python 3 from python.org ^(not the Store stub^).
  pause
  exit /b 1
)
"%PY%" -c "import certifi" 2>nul || "%PY%" -m pip install -r requirements.txt
"%PY%" chat.py
if errorlevel 1 pause
endlocal
