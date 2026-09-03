#!/bin/bash
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
# backtalk installer — environment, engines, models. Run once.
# Safe to re-run; every step skips what's already done.
set -e
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "== backtalk install =="

# --- uv (the Python environment manager) ---
if ! command -v uv >/dev/null 2>&1; then
  echo "-- uv not found. It's the fast Python manager this uses."
  read -r -p "   Install it now? [Y/n] " a
  if [ "$a" = "n" ] || [ "$a" = "N" ]; then
    echo "   Install uv yourself (https://docs.astral.sh/uv/) and re-run."
    exit 1
  fi
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# --- espeak-ng (the one system library: the voice engine phonemizes
#     through it; its pip-bundled build is broken, the system package is
#     the supported path) ---
if ! command -v espeak-ng >/dev/null 2>&1 && \
   [ ! -e /opt/homebrew/lib/libespeak-ng.dylib ] && \
   [ ! -e /usr/local/lib/libespeak-ng.dylib ] && \
   [ ! -e /usr/lib/x86_64-linux-gnu/libespeak-ng.so.1 ]; then
  echo "-- installing espeak-ng (the voice engine needs it)"
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then brew install espeak-ng
      else echo "   Homebrew not found — install it (https://brew.sh), then re-run."; exit 1; fi ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then sudo apt-get install -y espeak-ng
      elif command -v dnf >/dev/null 2>&1; then sudo dnf install -y espeak-ng
      elif command -v pacman >/dev/null 2>&1; then sudo pacman -S --noconfirm espeak-ng
      else echo "   Install espeak-ng with your package manager, then re-run."; exit 1; fi ;;
    *) echo "   Unknown platform — install espeak-ng manually, then re-run."; exit 1 ;;
  esac
else
  echo "-- espeak-ng: already present"
fi

# --- Linux audio headers (sounddevice needs PortAudio) ---
if [ "$(uname -s)" = "Linux" ] && ! ldconfig -p 2>/dev/null | grep -q portaudio; then
  echo "-- installing PortAudio (mic + speaker access)"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y libportaudio2 portaudio19-dev
  fi
fi

# --- the Python environment ---
echo "-- creating the environment (first run downloads ~900MB of packages)"
uv venv .venv -q 2>/dev/null || true
uv pip install --python .venv/bin/python -q -e .

# --- prefetch the models so the first conversation doesn't wait ---
if [ "$1" != "--no-models" ]; then
  echo "-- downloading the speech models (first run only, ~1GB total)"
  .venv/bin/python - <<'PY'
import warnings; warnings.filterwarnings("ignore")
from backtalk.ears import warm as warm_ears
from backtalk.mouth import warm as warm_mouth
warm_ears()
warm_mouth()
print("-- models ready")
PY
fi

echo ""
echo "== backtalk installed =="
echo ""
echo "Next:"
echo "  1. Point it at your agent: edit backtalk.json (agent_dir + name),"
echo "     or open this folder in Claude Code and say:"
echo "         read backtalk.md and set me up"
echo "  2. ./run.sh — hold the key, talk, let go."
echo ""
echo "macOS: the FIRST run will ask for Microphone permission, and the"
echo "hold-to-talk key needs Input Monitoring for your terminal app"
echo "(System Settings -> Privacy & Security -> Input Monitoring)."
