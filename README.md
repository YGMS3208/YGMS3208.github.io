# 自動車製造工程図鑑（AUTOMOTIVE ATLAS）— ソース

公開サイト: https://ygms3208.github.io/

このブランチ（`source`）はサイトを生成するためのデータとスクリプトです。公開されているのは `main` ブランチ（生成物）で、GitHub Pages がそのまま配信します。

## 構成

| 場所 | 中身 |
|---|---|
| `data/01_plant.txt` 〜 `10_misc.txt` | 系統・部品・工程・設備のデータ |
| `data/cats.txt` | 設備（253分類）と説明 |
| `data/content/` | 加工法の解説（methods_*.md）と設備の解説（equipment_*.md） |
| `data/mt/` | 工作機械図鑑（/machine-tools/）の本文：機種（types_*.md）・構成部品・自動化・ガイド |
| `build/il_mt.py` | 工作機械図鑑の図解（構造図・部品図・自動化の図） |
| `data/slugs.tsv` | すべてのページの英語URL（**一度公開したら変えない**） |
| `build/state/urls.json` | 公開済みURL・公開日・更新日（内容のハッシュが変わった日だけ更新日が進む） |
| `build/state/opnums.json` | 工程番号（OP10など）。並び順から計算し直さない |
| `build/state/redirects.txt` | URLを変えた・消したときの転送（`旧URL 新URL`） |
| `build/site_config.json` | ベースURL、運営者名、Search Console の確認コードなど |

## 更新のしかた

1. `data/` の内容を直す（部品や工程の追加・修正、解説文の加筆）。
2. 新しい部品・設備を足したら `data/slugs.tsv` に英語URLを1行追加する。
3. `./deploy.sh "変更の要約"` を実行する（ビルド → 検査 → `source` と `main` に push）。

ビルドは次の場合に止まります。公開済みURLが転送なしで消えた／内部リンク切れ／h1が1つでない／title重複／内容が薄いページを検索対象にした／CSSが大きすぎる。

必要なもの: Python 3、Playwright（Chromium）、Node.js（フォント取得用に `npm install`）。

## 方針（SEO）

- 1ページ1URLの静的HTML。本文・リンク・構造化データはすべてHTMLに直接書き込み、JavaScriptは検索・タブ・カルーセルだけに使う。
- 検索結果に出すのは本文の充実したページだけ（部品・系統・解説を書いた加工法と設備・設備分類・比較など）。工程の詳細画面や解説未執筆の設備は `noindex,follow`。解説文を追加すると自動で検索対象になり、sitemap にも載る。
- AIの学習用クローラーは robots.txt で拒否、検索エンジンとAI検索は許可。
- 文章と図解は CC BY-NC 4.0。
