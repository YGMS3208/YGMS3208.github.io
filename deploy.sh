#!/usr/bin/env bash
# Build the site and publish it to the `main` branch (GitHub Pages serves main).
# Run from a clone that has the `source` branch checked out:  ./deploy.sh "変更の要約"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MSG="${1:-サイトを更新}"

cd "$ROOT/build"
[ -d node_modules/@fontsource ] || npm install --no-audit --no-fund
python3 mk_site_tpl.py
python3 site.py                       # fails loudly on lost URLs, broken links, thin pages

cd "$ROOT"
git add -A build/state data build
git commit -qm "$MSG" || true         # page dates / op numbers live in build/state
git push -q origin source

git fetch -q origin main || true
if [ ! -d "$ROOT/_pub/.git" ] && [ ! -f "$ROOT/_pub/.git" ]; then
  git worktree add -f "$ROOT/_pub" main 2>/dev/null || git worktree add -f "$ROOT/_pub" -b main origin/main
fi
cd "$ROOT/_pub"
git checkout -q main && git reset -q --hard origin/main 2>/dev/null || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$ROOT/out/." .
git add -A
git commit -qm "$MSG" && git push -q origin main && echo "published" || echo "nothing to publish"
