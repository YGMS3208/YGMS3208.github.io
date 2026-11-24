#!/usr/bin/env bash
# Regenerate the whole site from the base commit. Run from anywhere: bash tools/pipeline.sh
# Needs Python 3.9+ with fonttools and brotli (pip install fonttools brotli).
set -e
cd "$(dirname "$0")"
python3 build.py | tail -2        # reset the generated site to the base commit, design + motion layer, fonts, home page
python3 practice.py                # machine pages: spec meeting items, how to use, cautions, Q&A
python3 products.py                # machine elements and dies industry, parts / operations / equipment, menus, search, sitemaps
python3 guides.py                  # guides (torque chart, interference, guideways, coolant, maintenance) and the physical-AI page
python3 glossary.py > /dev/null    # glossary, term pages, in-text term links
python3 seo.py                     # shared CSS file, update dates only where the text changed
git -C .. reset -q                 # build.py checks out the base commit into the index; leave the index matching HEAD
