@echo off
rem fullstack-agent: give your AI a full stack — memory, voice, face, hands.
rem Copyright (C) 2026 Akhil
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU Affero General Public License as published
rem by the Free Software Foundation, either version 3 of the License, or
rem (at your option) any later version.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
rem GNU Affero General Public License for more details.
rem
rem You should have received a copy of the GNU Affero General Public License
rem along with this program. If not, see <https://www.gnu.org/licenses/>.
rem
rem SPDX-License-Identifier: AGPL-3.0-or-later

rem Starts the agent's pieces. Each server gets its own window;
rem close the windows (or this one for the voice) to stop.
rem   start.bat          everything installed
rem   start.bat voice    the voice and the face (no hands)
rem   start.bat hands    the voice and the hands board (no face)
cd /d "%~dp0"

set "PATH=%USERPROFILE%\.local\bin;%PATH%"

rem ---- Ensure Ollama is running -----------------------------------------
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:11434' -UseBasicParsing -TimeoutSec 2).StatusCode; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
  echo   ollama: not running, starting in background...
  start /B "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve >nul 2>&1
  ping 127.0.0.1 -n 3 >nul
) else (
  echo   ollama: online
)

if exist "ai-visualizer\" if not "%1"=="hands" (
  echo   face:  starting
  start "agent face" cmd /c "cd ai-visualizer && run.bat"
)

rem Both servers are started through their own run.bat, which finds a
rem working interpreter and holds its window if anything goes wrong.
if exist "barehands\" if not "%1"=="voice" (
  echo   hands: starting
  start "agent hands" cmd /c "cd barehands && run.bat"
)

if exist "backtalk\" (
  echo   voice: starting in this window. Close it to hang up.
  cd backtalk
  rem Self-repair: reconcile the voice line's packages before launch
  rem (fast when current; heals a half-installed environment).
  echo   voice: checking packages. The FIRST run downloads models
  echo          and can take several minutes. It is not stuck.
  uv sync --inexact
  if errorlevel 1 (
    echo.
    echo   The voice line's packages could not be installed, so it never
    echo   started. The reason is in the output above.
    echo.
    pause
    exit /b 1
  )
  uv run python -m backtalk.main
  if errorlevel 1 (
    echo.
    echo   The voice line stopped with an error. The message is above.
    echo   The log lives in backtalk\logs\backtalk.log
    pause
  )
)
