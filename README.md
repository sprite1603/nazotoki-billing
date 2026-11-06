# 謎解き代金の請求ページ

Notion の「謎解き予定」データベースから **受取チェック OFF** の公演を取得し、
メンバーごとの請求額と請求文を GitHub Pages で表示します。

- 1人あたり = 金額 ÷ 人数（1円未満切り上げ）。立て替えた人には請求しない
- 金額・メンバー未入力の公演は「請求に含めていない公演」に表示
- GitHub Actions が 3 時間ごと（と main への push 時）に Notion から取得して再公開
- 取得データ（data.json）はリポジトリには保存されず、Pages の公開物にのみ含まれます

## セットアップ
1. https://www.notion.so/my-integrations でインテグレーションを作成し、トークンを控える
2. Notion の「謎解き予定」右上「…」→「接続」でそのインテグレーションを追加
3. このリポジトリの Settings → Secrets and variables → Actions に `NOTION_TOKEN` を登録
4. Settings → Pages の Source を **GitHub Actions** にする
5. Actions タブ →「Notion から取得して Pages に公開」→ Run workflow

すぐ反映したいときは 5 の手動実行を使ってください。
