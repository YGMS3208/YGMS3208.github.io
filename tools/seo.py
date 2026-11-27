#!/usr/bin/env python3
"""Final step: shared CSS to one cached file, accurate lastmod/dateModified for pages whose text changed."""
import glob, hashlib, html, os, re, subprocess
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(SITE)
BASE = "5ca5a0e"; B = "https://ygms3208.github.io"
import datetime
# the update date stamped on pages whose text changed: today in Japan (override with SITE_DATE=YYYY-MM-DD)
_d = datetime.date.fromisoformat(os.environ["SITE_DATE"]) if os.environ.get("SITE_DATE") else datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()
DAY, DAY_J = _d.isoformat(), f"{_d.year}年{_d.month}月{_d.day}日"
pages = sorted(glob.glob("**/*.html", recursive=True))

# ---- 1. externalize the shared stylesheet ----
for f in glob.glob("assets/site.*.css"): os.remove(f)
home = open("index.html", encoding="utf-8").read()
common = re.search(r"<style>(.*?)</style>", home, re.S).group(1)
# the home page carries no page-only rules, so its whole style block is the shared sheet
h = hashlib.sha1(common.encode()).hexdigest()[:10]
css_path = f"assets/site.{h}.css"
open(css_path, "w", encoding="utf-8").write(common)
moved = 0
for p in pages:
    s = open(p, encoding="utf-8").read()
    m = re.search(r"<style>(.*?)</style>", s, re.S)
    if not m or not m.group(1).startswith(common): continue
    rest = m.group(1)[len(common):]
    rep = f'<link rel="stylesheet" href="/{css_path}">' + (f"<style>{rest}</style>" if rest else "")
    s = s[:m.start()] + rep + s[m.end():]
    open(p, "w", encoding="utf-8").write(s); moved += 1
print("css externalized on", moved, "pages ->", css_path, len(common) // 1024, "KB")

# ---- 2. lastmod / dateModified only where the visible text changed ----
def text(s):
    s = s[s.find("<main"):s.find("</main>")] if "<main" in s else s
    s = re.sub(r"<(script|style|svg)\b.*?</\1>", "", s, flags=re.S)
    return re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", s)))
# compare with the last published version (HEAD): unchanged pages keep their dates, changed or new pages get today
def text2(s): return text(re.sub(r"<time\b[^>]*>.*?</time>", "", s))
def head_of(p):
    r = subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None
def _jp(d):
    y, m, dd = d.split("-"); return f"{int(y)}年{int(m)}月{int(dd)}日"
DM = re.compile(r'"dateModified":"([0-9-]+)"'); UPD = re.compile(r'(更新 <time datetime=")([0-9-]+)(">)([^<]*)(</time>)')
prev_lastmod = {}
for sm in subprocess.run(["git", "ls-tree", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split():
    if sm.startswith("sitemap-") and sm.endswith(".xml"):
        prev_lastmod.update(re.findall(r"<loc>([^<]+)</loc><lastmod>([0-9-]+)</lastmod>", head_of(sm) or ""))
changed, dates = [], {}
for p in pages:
    if not p.endswith("index.html"): continue
    s = open(p, encoding="utf-8").read(); url = B + "/" + p[:-len("index.html")]
    old = head_of(p)
    if old is not None and text2(s) == text2(old):
        dm, up = DM.search(old), UPD.search(old)
        if dm: s = DM.sub(f'"dateModified":"{dm.group(1)}"', s)
        if up: s = UPD.sub(lambda m: m.group(1) + up.group(2) + m.group(3) + up.group(4) + m.group(5), s)
        if url in prev_lastmod: dates[url] = prev_lastmod[url]
        open(p, "w", encoding="utf-8").write(s)
        continue
    changed.append(p); dates[url] = DAY
    s = DM.sub(f'"dateModified":"{DAY}"', s)
    s = UPD.sub(lambda m: m.group(1) + DAY + m.group(3) + DAY_J + m.group(5), s)
    open(p, "w", encoding="utf-8").write(s)
# a page is never updated before it was published; give every article a datePublished
PUBT = re.compile(r'公開 <time datetime="([0-9-]+)">')
for p in pages:
    if not p.endswith("index.html"): continue
    s = open(p, encoding="utf-8").read(); s0 = s
    pm = PUBT.search(s)
    if not pm: continue
    pub = pm.group(1)
    up = UPD.search(s)
    if up and up.group(2) < pub:
        s = UPD.sub(lambda m: m.group(1) + pub + m.group(3) + _jp(pub) + m.group(5), s)
    dm = DM.search(s)
    if dm and dm.group(1) < pub: s = DM.sub(f'"dateModified":"{pub}"', s)
    if dm and '"datePublished"' not in s: s = s.replace(dm.group(0), f'"datePublished":"{pub}",' + DM.search(s).group(0), 1)
    url = B + "/" + p[:-len("index.html")]
    if url in dates and dates[url] < pub: dates[url] = pub
    if s != s0: open(p, "w", encoding="utf-8").write(s)
urls = {B + "/" + p[:-len("index.html")] for p in changed}
for sm in glob.glob("sitemap-*.xml"):
    x = open(sm, encoding="utf-8").read()
    x = re.sub(r"<url><loc>([^<]+)</loc><lastmod>([0-9-]+)</lastmod></url>", lambda m: f"<url><loc>{m.group(1)}</loc><lastmod>{dates.get(m.group(1), m.group(2))}</lastmod></url>", x)
    open(sm, "w", encoding="utf-8").write(x)
x = open("sitemap.xml", encoding="utf-8").read()
open("sitemap.xml", "w", encoding="utf-8").write(re.sub(r"<lastmod>[0-9-]+</lastmod>", f"<lastmod>{max(dates.values()) if dates else DAY}</lastmod>", x))
import tempfile; open(os.path.join(tempfile.gettempdir(), "changed_urls.txt"), "w").write("\n".join(sorted(urls)))
print("pages with changed text:", len(changed))
