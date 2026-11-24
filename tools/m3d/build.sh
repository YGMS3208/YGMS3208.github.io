#!/usr/bin/env bash
# Rebuild the 3D viewer bundle after editing src.js (needs Node; run once: npm install).
# The bundle is committed, so the site pipeline itself does not need Node.
set -e
cd "$(dirname "$0")"
npx esbuild src.js --bundle --format=esm --minify --target=es2020 --legal-comments=eof --outfile=m3d.bundle.js
ls -l m3d.bundle.js
