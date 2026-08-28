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

# Pulls the newest version of every installed piece, and of this repo.
# Your own files (your AGENTS.md/KIMI.md, your vault, your configs) live outside
# the repos' tracked files, so updates never touch them. If git reports a
# conflict on a config you edited, your edit wins; keep your version.

HERE="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$(dirname "$HERE")"

main() {
  for repo in fullstack-kimi kimi-memory-vault kimi-voice kimi-barehands kimi-visualizer; do
    [ -d "$HOME_DIR/$repo/.git" ] || continue
    echo "== $repo"
    git -C "$HOME_DIR/$repo" fetch -q origin 2>/dev/null
    git -C "$HOME_DIR/$repo" log --oneline "..@{u}" 2>/dev/null | sed "s/^/   new: /"

    CFG=""
    case "$repo" in
      kimi-voice) CFG="kimi-voice.json" ;;
      kimi-barehands) CFG="kimi-barehands.json" ;;
      kimi-visualizer) CFG="kimi-visualizer.json" ;;
    esac
    MIGRATE=0
    if [ -n "$CFG" ] && [ -f "$HOME_DIR/$repo/$CFG" ] && \
       git -C "$HOME_DIR/$repo" ls-files --error-unmatch "$CFG" >/dev/null 2>&1; then
      cp "$HOME_DIR/$repo/$CFG" "$HOME_DIR/$repo/$CFG.mine" && \
        git -C "$HOME_DIR/$repo" checkout -q -- "$CFG" && MIGRATE=1
    fi
    git -C "$HOME_DIR/$repo" pull --ff-only || \
      echo "   (couldn't fast-forward; your local edits win.)"
    if [ "$MIGRATE" = 1 ] && [ -f "$HOME_DIR/$repo/$CFG.mine" ]; then
      mv "$HOME_DIR/$repo/$CFG.mine" "$HOME_DIR/$repo/$CFG"
    fi
  done
  echo "update complete."
}
main "$@"
