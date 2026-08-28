#!/bin/bash
# fullstack-kimi: give your AI a full stack — memory, voice, face, hands.
# Copyright (C) 2026 Jared Rhodenizer
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

# Starts the agent's pieces, in the right order:
#   kimi-visualizer (the face, opens in your browser)
#   kimi-barehands  (the hands, URL printed; open it when you want the board)
#   kimi-voice      (the voice, runs in this terminal; Ctrl-C stops EVERYTHING)
# Pieces you didn't install are skipped automatically.
#
#   ./start.sh          everything installed
#   ./start.sh voice    the voice and the face (no hands)
#   ./start.sh hands    the voice and the hands board (no face)

HERE="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$(dirname "$HERE")"
MODE="${1:-all}"
PIDS=()

cleanup() {
  trap - EXIT INT TERM
  for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done
  echo
  echo "agent stopped."
}
trap cleanup EXIT INT TERM

echo "fullstack-kimi: starting from $HOME_DIR"

if [ -d "$HOME_DIR/kimi-visualizer" ] && [ "$MODE" != "hands" ]; then
  (cd "$HOME_DIR/kimi-visualizer" && exec python3 server.py) &
  PIDS+=($!)
  echo "  face:  starting (your browser opens on the visualizer)"
fi

if [ -d "$HOME_DIR/kimi-barehands" ] && [ "$MODE" != "voice" ]; then
  (cd "$HOME_DIR/kimi-barehands" && exec python3 server.py) &
  PIDS+=($!)
  echo "  hands: starting (open the printed URL in Chrome when you want the board)"
fi

if [ -d "$HOME_DIR/kimi-voice" ]; then
  echo "  voice: starting (hold your talk key and speak; Ctrl-C here stops everything)"
  cd "$HOME_DIR/kimi-voice" && ./run.sh
else
  echo
  echo "No voice installed; servers are up. Ctrl-C stops everything."
  wait
fi
