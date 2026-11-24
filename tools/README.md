# tools — サイトの生成スクリプト

サイト（このリポジトリのルート以下の HTML・sitemap・検索インデックスなど）は、ここにあるスクリプトで生成している。
基準コミット `5ca5a0e` の状態に戻してから、上から順に手を加えていく方式。**同じ入力なら毎回同じ出力になる。**

## 実行

```bash
pip install fonttools brotli   # 初回だけ
bash tools/pipeline.sh
```

実行すると、`tools/` と `CLAUDE.md` 以外の生成物は直前のコミットの状態にいったん戻されてから作り直される。
サイトの HTML を手で直しても次の実行で消えるので、**変更は必ずここのスクリプトかデータに入れる**こと。

## ファイル

| ファイル | 役割 |
|---|---|
| `pipeline.sh` | 全体の実行順 |
| `build.py` | 基準コミットへのリセット、デザイン層（`atlas.css`）と動き（`atlas.js`）の適用、明朝体サブセットの生成、トップページ |
| `atlas.css` / `atlas.js` | 全ページ共通のデザインと動き。動きのルールは `CLAUDE.md` の表を参照 |
| `practice.py` + `practice_data.py` + `qa_data.py` | 工作機械ページの「仕様打ち合わせ」「使用方法」「気を付けること」「想定問答」 |
| `products.py` + `products_data.py` | 機械要素・金型の業界、部品・工程・設備ページ、メニュー、検索、sitemap、llms.txt |
| `drawings.py` + `iso.py` | 新しい部品・設備の等角図（SVG）を描くライブラリと図 |
| `gear_guide.py` | 歯車の解説ページ |
| `guides.py` | ガイド（トルク線図、干渉図、案内面、クーラント、保全基準）とフィジカルAIのページ |
| `glossary.py` + `glossary_data.py` | 用語辞典、用語ページ、本文中の用語リンク |
| `callouts.py` + `callout_parts.json` | 構造図の番号ごとに、指す部品（分解の部品番号）を固定する。部品番号は図を `class="el"` で区切った順（0 始まり）。最初の部品に引出線の点が付いて動く |
| `seo.py` | 共通 CSS の外部ファイル化、本文が変わったページだけ更新日を今日（日本時間）にする |
| `extra_chars.txt` | 明朝体サブセットに含める追加の文字（スクリプトが更新する） |
| `font/` | Zen Old Mincho（SIL Open Font License 1.1、`OFL-LICENSE.txt`） |

## ページを追加するとき

- 部品・工程・設備: `products_data.py` にデータを足す（図は `drawings.py`）。
- 工作機械の実務情報・想定問答: `practice_data.py` / `qa_data.py`。
- ガイド: `guides.py`。用語: `glossary_data.py`。
- 共通の見た目や動きを変えるとき: `atlas.css` / `atlas.js`。そのうえで `CLAUDE.md` のルール表を更新する。
- 実行後は 1440px とスマホ幅で表示を確認してから、`main` に push する。

更新日（`dateModified`・表示の「更新」・sitemap の `lastmod`）は、直前のコミットと比べて本文が変わったページだけが今日の日付になる。
日付を指定したいときは `SITE_DATE=2026-12-01 bash tools/pipeline.sh` のように実行する。
