# 自動車製造工程図鑑 公開・SEO方針（決定版）

討議参加：テクニカルSEO／コンテンツSEO／構造化データ・SNS・AI検索／表示速度・国際化・アクセシビリティ（2ラウンド）
ユーザー決定：GitHub Pages（無料）／運営者はハンドルネーム「Machine Tool Scout」＋経歴概要（工作機械商社で10年以上）／日本語で公開、英語版は後から／CC BY-NC 4.0／AI学習用クローラーは拒否

## 1. 公開基盤
- リポジトリ `YGMS3208.github.io`（ユーザーサイト）で https://ygms3208.github.io/ のルートに公開。robots.txt・Search Console（アドレス変更ツール含む）がルートで使える。
- 公開ブランチ `main` は生成物のみ（毎回1コミットに置き換え、履歴を膨らませない）。ビルドスクリプトとデータは `source` ブランチ。
- GitHubのユーザー名は変更しない（旧URLが転送されずに消えるため）。canonicalのホストは小文字。
- 将来の独自ドメイン化：新旧両方をSearch Consoleで確認 → GitHubで設定（自動301）→ ベースURLを差し替えて再ビルド → アドレス変更ツール。
- コミットの作成者名に実名・私用メールを出さない。

## 2. ページとURL（英数字スラッグ・末尾スラッシュ・ルート＝日本語／英語は将来 /en/ に同スラッグ）
| 種類 | URL | インデックス |
|---|---|---|
| トップ | / | ○ |
| 系統 | /systems/ , /systems/{sys}/ | ○ |
| 部品 | /parts/{part}/（系統名を含めない） | ○（81件） |
| 工程 | 部品ページ内の見出し /parts/{part}/#op40 ＋詳細画面 /parts/{part}/op40/ | 詳細画面は noindex（canonicalは自分自身）。本文300字以上＋専用図解＋管理ポイント3項目以上で昇格 |
| 加工法 | /methods/ , /methods/{slug}/ | 「〜とは」本文（1,200字以上）を書いた約11件のみ○、他は noindex |
| 設備 | /equipment/ , /equipment/group/{slug}/（17）, /equipment/{slug}/（253） | グループは○。個別は「手書き説明200字以上」のものだけ○（初日は主要40〜60件を加筆） |
| 材料 | /materials/{slug}/ | noindex（内容が一覧中心のため） |
| 比較 | /powertrain/（5方式はタブ） | ○ |
| 工程マップ | /map/ | ○ |
| 運営者・方針 | /about/ | ○（ProfilePage） |
| 検索 | /search/ | noindex |
- OP番号はデータに固定して保存（並び順から計算しない。途中追加はOP35など）。
- 旧URLは redirects.txt から meta refresh＋canonical のHTMLを生成。公開URL一覧 urls.lock と比べ、転送先なしで消えたURLがあればビルド失敗。
- noindexページを robots.txt でブロックしない。全URLを404.htmlで受ける「SPAハック」はしない。専用の404.htmlを置く。
- インデックス数は書いた量で決める（初日は約180件が目安）。研削などは「〜とは（加工法）」「〜の種類（グループ）」「機種名（設備）」で役割とタイトルを書き分けて共食いを防ぐ。

## 3. 生成方式
- ページごとの静的HTML。本文は既存のJS描画関数をビルド時にヘッドレスChromiumで実行して取り出す（UIを1系統に保つ）。headはPythonで生成。
- 取り出し条件を固定：ライトテーマ・reduced-motion・固定幅。2回ビルドして一致を確認。
- 配信ページにJSONデータやSPAは載せない。実行時JSは外部1本（defer・ハッシュ付きファイル名）：検索（索引JSONを開いた時に読み込み）、パワートレインのタブ、カルーセル、比較表の絞り込み。
- パワートレインの5状態は文章・表を静的に出力し、図解だけ `<template>` に入れる。タブは role=tab/tabpanel/aria-controls。
- 設備一覧は17グループのハブに分割（1ページに全253件の図を並べない）。
- 自動検査：JS無効でh1・本文・リンクがあること／`#`始まりのルーティングリンク0件／title重複なし／canonicalが自分自身／SVGのid重複なし／CSSはgzip後15KB以下。
- 更新日は「データから計算した内容ハッシュ」が変わった日。画面表示・JSON-LD・sitemapのlastmodを一致させる。

## 4. タイトル・本文
- title：32字前後＋「｜自動車製造工程図鑑」。H1は主題名のみ。descriptionはデータから全ページ固有に生成。
  - 部品：「{部品}の製造工程｜{主要工程}など{n}工程と設備を図解」
  - 設備：「{設備}とは｜仕組みと自動車部品での使われ方」
  - 加工法：「{加工法}とは｜種類・原理と自動車部品での使い方」
  - 比較：「EVとエンジン車の部品・製造工程の違い｜必要な設備を比較」
- 冒頭に主語入りの定義文1〜2文。数値は「本図鑑の分類で数えた数」と明記。図の内容は figcaption と本文でも文章にする。
- 部品ページ内に工程ごとの見出し（h3）と説明、設備へのリンク（リンク文言は内容が分かる語に）。
- 狙わないもの：メーカー名での検索、価格、「おすすめ」、メーカー比較・ランキング、釣りタイトル、定型文の量産。
- 顧客現場で知った情報は書かない。記述は公開情報で裏付けられる一般論に限る。

## 5. 構造化データ・SNS
- 全ページ：WebSite＋Person（ハンドル名、url＝/about/、sameAsは同名SNSがあれば）を @id で参照。社名は書かない。
- index対象の部品・系統・設備・加工法・比較・材料：Article（image＝OG画像、author、datePublished、dateModified、about）。一覧：ItemList。/about/：ProfilePage。比較CSV：Dataset。
- noindexページは BreadcrumbList のみ（昇格時に Article が自動で付く）。
- 使わない：FAQPage、HowTo、Product、Review、AggregateRating、SearchAction。画面にない内容をJSON-LDに書かない。
- OGP：summary_large_image。index対象ページごとに1200×630のJPEG（名前＋数字＋図解）を生成。noindexページは所属する部品・グループの画像を流用し、og:title/descriptionは固有に。メーカーのロゴは使わない。
- 画像検索向けの代表PNGを<img>で出すのは第2段階（初日はインラインSVG＋OG画像）。
- 利用条件は CC BY-NC 4.0（運営者の決定）。/about/・JSON-LD license・フッターで一致させる。

## 6. クローラー・登録
- robots.txt：検索エンジンとAI検索は許可、AIの学習用クローラー（GPTBot・Google-Extended・CCBot・ClaudeBot など）は拒否（運営者の決定）＋sitemap。llms.txt は sitemap と同じデータから自動生成（index対象のみ）。
- Search Console と Bing Webmaster Tools に登録（ユーザー作業、確認用metaタグはビルドで挿入）。IndexNowは第2段階。
- favicon（48pxの倍数）を置く。

## 7. 表示速度・アクセシビリティ
- doctype・charset・viewport・`<html lang="ja">` を全ページに。英字ラベルに lang="en"。
- Google Fontsをやめ自サイト配信（unicode-range分割のうち使用文字を含む分割だけ、swap、フォールバックのメトリクス調整）。中国などGoogle Fontsが届かない地域でも表示が止まらない。
- CSSは各ページにインライン（gzip後15KB上限）。LCP（h1）にフェードをかけない。カウントアップは画面外の要素だけ。
- `--muted` をAA基準（4.5:1以上）に。h1は1つ、見出しレベルを飛ばさない。遷移はすべて `<a href>`。無限ループ装飾は reduced-motion で停止。
- hreflang は英語版を追加するときに双方向で入れる（今は入れない）。言語による自動リダイレクトはしない。

## 8. 公開後の監査で追加した対応
- 設備ページの代表メーカーは件数を出さず五十音・アルファベット順に並べ、「推奨や順位ではない」と明記（順位付けに見えるのを防ぐ）。
- 本文はOS標準の日本語フォント、見出しだけ Zen Kaku Gothic New（太字1ウェイト）にしてフォントの通信量を削減。
- 一覧系ページのh1は主題名（例：自動車の部品一覧（系統別））にし、キャッチコピーは表示用の大見出しとして残す。
- 色のコントラストをAA基準に調整、英字ラベルに lang="en"。
