# healthkit-wakatime-log

iPhoneのHealthKitデータ（歩数・距離）とWakaTimeのコーディング時間をGitHub Actionsで自動記録するライフログシステムです。

## 仕組み

```
23:59 iPhoneショートカット自動実行
  ↓
HealthKitから歩数・距離を取得
  ↓
GitHub Gistを更新（データの中継地点）
  ↓
深夜0時 GitHub Actions起動
  ↓
Gist + WakaTime APIからデータ取得
  ↓
activity_tracking/daily-logs/YYYY-MM-DD.md を自動生成・コミット
```

## ディレクトリ構成

```
.
├── .github/
│   └── workflows/
│       ├── daily-log.yml       # GitHub Actions ワークフロー
│       └── scripts/
│           ├── generate_log.py # データ取得・ログ生成スクリプト
│           └── test_generate_log.py # テスト
└── activity_tracking/
    └── daily-logs/             # 日々の活動ログ（自動生成）
        └── YYYY-MM-DD.md
```

## セットアップ

### 1. GitHub Secretsの登録

リポジトリの Settings → Secrets and variables → Actions から以下を登録します。

| シークレット名     | 値                                           |
| ------------------ | -------------------------------------------- |
| `WAKATIME_API_KEY` | WakaTimeのAPIキー                            |
| `HEALTH_GIST_ID`   | 作成したGistのID                             |
| `GH_PAT`           | Personal Access Token（`gist` スコープ必須） |
| `GITHUB_USERNAME`  | GitHubのユーザー名                           |

`GITHUB_TOKEN` はGitHub Actionsが自動で提供するため登録不要です。

### 2. iOSショートカットの設定

毎日23:59にHealthKitのデータをGistに送信するショートカットを設定します。  
詳細は[Zenn記事](https://zenn.dev)を参照してください。

## ログの手動生成

`.env.example` をコピーして `.env` を作成し、各値を設定します。

```bash
cp .env.example .env
# .env を編集して各値を設定する
```

設定後、以下のコマンドで実行します。

```bash
# 前日分を生成（引数なし）
set -a && source .env && set +a && \
GITHUB_TOKEN=$(gh auth token) \
GH_PAT=$(gh auth token) \
python3 .github/workflows/scripts/generate_log.py

# 日付を指定する場合
set -a && source .env && set +a && \
GITHUB_TOKEN=$(gh auth token) \
GH_PAT=$(gh auth token) \
python3 .github/workflows/scripts/generate_log.py 2026-04-18
```

## テストの実行

```bash
python3 .github/workflows/scripts/test_generate_log.py
```

APIへの通信は発生しないため、環境変数の設定は不要です。

## 生成されるログの例

```markdown
# 2026年4月18日（土）

## 活動ログ
| カテゴリ         | 内容                   | 記録      |
|------------------|------------------------|-----------|
| 運動             | 歩数 15062歩 / 10.61km  |           |
| コーディング時間 | WakaTime               | 2h 45m    |
| プログラミング   | GitHubコミット数        | 5 commits |
|  └              | fix bug                |           |
|  └              | add feature            |           |
```
