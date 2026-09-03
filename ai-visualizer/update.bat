@echo off
rem ai-visualizer -- updating has moved. This script does nothing now.
rem Copyright (C) 2026 Jared Rhodenizer
rem SPDX-License-Identifier: AGPL-3.0-or-later
rem
rem WHY THIS IS EMPTY, because the reason is worth knowing before anyone
rem puts it back.
rem
rem To update safely this script used to copy ITSELF into a folder under
rem LOCALAPPDATA and hand control to the copy. That was real protection
rem against a real bug: cmd reads a .bat by byte offset, so a script that
rem pulls a new version of itself mid-run gets garbled from that point on.
rem
rem It is also, precisely, what malicious software does -- write a copy of
rem yourself somewhere out of sight and run it. Antivirus scores the
rem behaviour and cannot see the intention, and Windows users were being
rem warned about this file. The protection was never worth that price
rem either: it only mattered on an update that changed this very script,
rem and by then the pull had already succeeded. The cost was a warning on
rem every machine; the benefit was a tidier error message on a rare day.
rem
rem The file is kept rather than deleted so an existing Desktop shortcut
rem still finds something here and prints the message below, instead of
rem failing with an error nobody can read.
rem
rem Nothing on macOS or Linux changed. update.sh wraps its work in a shell
rem function and calls it at the very end, so bash reads the whole script
rem into memory before running any of it. It never needed a copy of itself.
rem
rem If this folder has no .git yet because it arrived as a zip, an agent
rem can wire it up once, keeping ai-visualizer.json:
rem   git init -b main
rem   git remote add origin https://github.com/jaredrhod/ai-visualizer
rem   git fetch origin
rem   git reset --hard origin/main

echo.
echo   Updating has moved, and there is nothing here to run.
echo.
echo   Open a chat with your agent and say:
echo.
echo       update ai-visualizer and tell me what changed
echo.
echo   It does the same job, and it tells you what arrived.
echo.
pause
