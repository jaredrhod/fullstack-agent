#!/bin/bash
# ai-visualizer — update to the newest version, showing what changed first.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Your ai-visualizer.json is yours: nothing in this script can touch or overwrite it.
# Safe to run any time; when nothing is new it just says so.

main() {
  cd "$(dirname "$0")" || exit 1
  CFG="ai-visualizer.json"

  if [ ! -d .git ]; then
    # this folder arrived as a zip: wire it to updates, once, keeping the config
    [ -f "$CFG" ] && cp "$CFG" "$CFG.mine"
    git init -q -b main
    git remote add origin https://github.com/jaredrhod/ai-visualizer
    git fetch -q origin
    git reset -q --hard origin/main
    git branch -q --set-upstream-to=origin/main main
    [ -f "$CFG.mine" ] && mv "$CFG.mine" "$CFG"
    echo "wired this folder to updates."
  fi

  git fetch -q origin
  git log --oneline "..@{u}" 2>/dev/null | sed "s/^/  new: /"

  # one-time migration: the config moved out of git tracking. If git here
  # still tracks the old copy, lift yours aside, let the pull retire the
  # tracked one, then put yours back exactly as it was.
  MIGRATE=0
  if git ls-files --error-unmatch "$CFG" >/dev/null 2>&1 && [ -f "$CFG" ]; then
    cp "$CFG" "$CFG.mine" && git checkout -q -- "$CFG" && MIGRATE=1
  fi

  git pull --ff-only || echo "  (couldn't fast-forward; your local edits win.)"

  if [ "$MIGRATE" = 1 ] && [ -f "$CFG.mine" ]; then
    mv "$CFG.mine" "$CFG"
  fi
  echo "update complete."
}
main "$@"
