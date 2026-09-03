# backtalk: talk to your Claude Code agent out loud.
# Copyright (C) 2026 Akhil
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Session log — terminal print + timestamped append to logs/backtalk.log.

Exists because the hardest voice bug ever hit here (the off-by-one
interrupt desync) had to be diagnosed from source, because the session
only printed to a terminal window nobody saved. Every load-bearing line
([you], replies, interrupts, drain/rebuild events, TTS fallbacks) goes
through log() so the next gremlin comes with receipts.
"""
import datetime
import sys
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "backtalk.log"


def _init_console():
    """Ask a Windows console for UTF-8 before anything is printed at it.

    Windows consoles default to a legacy codepage (cp1252 on a UK/US
    install), so a UTF-8 em-dash arrives as mojibake: the startup banner
    rendered as "[backtalk] up a<TM>" instead of "up --". Fixing the
    banner's own characters would not have been a fix, because the
    agent's REPLIES are printed here too and can contain anything at all.

    errors="replace" on the streams means a character the terminal
    genuinely cannot draw degrades to "?" rather than raising mid
    sentence and taking the voice down. No-ops everywhere but Windows.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_init_console()


def log(line: str):
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        # Last resort if the console refused UTF-8: readable beats fatal.
        print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        # encoding pinned on purpose. The default is the platform's, which
        # on Windows is that same legacy codepage -- so the log file kept
        # its own permanently corrupted copy of every line the console had
        # already mangled, and the receipts this module exists to produce
        # were unreadable exactly where they were most needed.
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {line}\n")
    except Exception:
        pass  # a broken log file must never take the voice down
