@echo off
rem fullstack-agent: give your AI a full stack. memory, voice, face, hands.
rem Copyright (C) 2026 Jared Rhodenizer
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

rem Pulls the newest version of every installed piece, and of this repo.
rem Your files live outside the repos, so updates never touch them. If git
rem reports a conflict on a config you edited, your edit wins.

rem cmd reads a .bat by byte offset, so a script that pulls a new copy of
rem ITSELF mid-run gets garbled from that point on. Relaunch from a copy
rem before doing any work.
rem
rem The copy lives in this program's own folder under LOCALAPPDATA and NOT
rem in the system temp directory. Identical protection, and it stops the
rem script reading like something stashing an executable where nobody
rem looks. Reviewers read repos too, and copy-to-temp-then-run is the
rem shape people are trained to distrust.
rem
rem Invoked WITHOUT `call` deliberately: cmd hands control to the copy and
rem never returns here, so not one further byte of this file is read after
rem the pull rewrites it. If the copy cannot be made, execution falls
rem through to :run below and does the work in place.
if "%~1"=="__run__" goto run
if not defined LOCALAPPDATA goto run
set "RUNDIR=%LOCALAPPDATA%\fullstack-agent"
if not exist "%RUNDIR%\" mkdir "%RUNDIR%" >nul 2>nul
copy /y "%~f0" "%RUNDIR%\update-run.bat" >nul
"%RUNDIR%\update-run.bat" __run__ "%~dp0"

:run
setlocal
rem Where the work happens. Normally the relaunched copy is handed the
rem original folder as %2. On the fallback path above (no LOCALAPPDATA,
rem or the copy could not be made) there is no %2, so resolve to this
rem file's own folder instead of cd-ing to nowhere.
set "HOME_DIR=%~2"
if not defined HOME_DIR set "HOME_DIR=%~dp0"
cd /d "%HOME_DIR%.."
for %%r in (fullstack-agent ai-memory-vault backtalk barehands ai-visualizer) do (
  if exist "%%r\.git\" call :one "%%r"
)
echo update complete.
rem Resolve the real Desktop folder (OneDrive redirection moves it off
rem %USERPROFILE%\Desktop); fall back to the classic path if the query fails.
set "DESKTOP_DIR="
for /f "delims=" %%d in ('powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')" 2^>nul') do set "DESKTOP_DIR=%%d"
if not defined DESKTOP_DIR set "DESKTOP_DIR=%USERPROFILE%\Desktop"
if not exist "%DESKTOP_DIR%\Update *" echo Tip: want a desktop Update icon that does this on a double-click? Open your agent and ask for one.
exit /b 0

:one
echo == %~1
rem show what is arriving BEFORE applying it
git -C "%~1" fetch -q origin 2>nul
git -C "%~1" log --oneline "..@{u}" 2>nul
rem one-time migration (2026-08): the per-piece configs moved out of git
rem tracking so an update can never collide with personal settings. If
rem this clone still tracks one, lift it aside, pull, put it back as-is.
set CFG=
if "%~1"=="backtalk" set CFG=backtalk.json
if "%~1"=="barehands" set CFG=barehands.json
if "%~1"=="ai-visualizer" set CFG=ai-visualizer.json
set MIGRATE=0
if not defined CFG goto pull
if not exist "%~1\%CFG%" goto pull
git -C "%~1" ls-files --error-unmatch "%CFG%" >nul 2>nul
if errorlevel 1 goto pull
copy /y "%~1\%CFG%" "%~1\%CFG%.mine" >nul
git -C "%~1" checkout -- "%CFG%"
set MIGRATE=1
:pull
git -C "%~1" pull --ff-only
if "%MIGRATE%"=="1" if exist "%~1\%CFG%.mine" move /y "%~1\%CFG%.mine" "%~1\%CFG%" >nul
exit /b 0
