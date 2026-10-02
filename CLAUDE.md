# Notes for Claude

This repo builds https://ygms3208.github.io/ (自動車製造工程図鑑). Work on the `source` branch; `main` holds only generated files and is written by `deploy.sh`.

- Build: `cd build && npm install && python3 mk_site_tpl.py && python3 site.py` → `../out`. Publish: `./deploy.sh "summary"`.
- Never change an existing slug in `data/slugs.tsv` or an OP number in `build/state/opnums.json`. If a URL must change, add `old new` to `build/state/redirects.txt`.
- `build/state/urls.json` holds publish/modify dates; commit it with every deploy.
- A page is indexable only if it has real written content (see `index` rules in `site.py`); add prose in `data/content/` to promote a method or equipment page.
- UI code lives in `build/template.html` (+ `site_views.js` for site-only views); `mk_site_tpl.py` derives the render template. Runtime JS for visitors is `build/site_app.js`.
- Content rules: public, general knowledge only; no customer or employer information; maker names are examples only; no ads.
- Machine-tool atlas (/machine-tools/): prose in `data/mt/*.md` (`@type/@component/@automation/@guide slug` blocks), drawings in `build/il_mt.py` (`@mt(slug)`), views in `build/site_views_mt.js`. Slugs there are URLs too — never rename.
