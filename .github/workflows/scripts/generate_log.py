import os, requests, datetime, json, sys


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        print(f"❌ 環境変数 {name} が設定されていません。GitHub Secrets を確認してください。")
        sys.exit(1)
    return value


def fetch_wakatime(api_key: str, date: str) -> str:
    """WakaTime APIからコーディング時間を取得して "Xh Ym" 形式で返す"""
    try:
        waka = requests.get(
            "https://wakatime.com/api/v1/users/current/summaries",
            params={"start": date, "end": date},
            auth=(api_key, ""),
            timeout=10
        ).json()
        coding_sec = waka["data"][0]["grand_total"]["total_seconds"] if waka.get("data") else 0
    except Exception:
        coding_sec = 0
    return f"{int(coding_sec // 3600)}h {int((coding_sec % 3600) // 60)}m"


def fetch_github_commits(token: str, date: str, github_username: str) -> tuple:
    """GitHub Search APIからコミット数とメッセージ一覧を返す（JST基準）"""
    try:
        end = f"{(datetime.date.fromisoformat(date) + datetime.timedelta(days=1)).isoformat()}T00:00:00+09:00"
        commits = requests.get(
            "https://api.github.com/search/commits",
            params={"q": f"author:{github_username} committer-date:{date}T00:00:00+09:00..{end}", "per_page": 50},
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github.cloak-preview"},
            timeout=10
        ).json()
        count = commits.get("total_count", 0)
        messages = [item["commit"]["message"].splitlines()[0] for item in commits.get("items", [])]
    except Exception:
        count = "—"
        messages = []
    return count, messages


def fetch_health(gist_id: str, pat: str) -> tuple:
    """GistからHealthKitデータ（歩数・距離）を取得して返す"""
    try:
        gist = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers={"Authorization": f"Bearer {pat}"},
            timeout=10
        ).json()
        health_raw = list(gist["files"].values())[0]["content"]
        health = json.loads(health_raw)
        steps = health.get("steps", "—")
        distance = round(health.get("distance_km", 0), 2) if health.get("distance_km") is not None else "—"
    except Exception:
        steps = "—"
        distance = "—"
    return steps, distance


def format_date_ja(date: str) -> str:
    """YYYY-MM-DD を 2026年4月20日（月）形式に変換する"""
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    d = datetime.date.fromisoformat(date)
    return f"{d.year}年{d.month}月{d.day}日（{weekdays[d.weekday()]}）"


def build_markdown(date: str, steps, distance, coding_str: str, commit_count, commit_messages: list) -> str:
    """活動ログのMarkdown文字列を生成して返す（ファイル書き込みはしない）"""
    commit_rows = "".join(f"| &nbsp;&nbsp;└ | {msg} | |\n" for msg in commit_messages)
    return f"""# {format_date_ja(date)}

## 活動ログ
| カテゴリ | 内容 | 記録 |
|---------|------|------|
| 運動 | 歩数 {steps}歩 / {distance}km | |
| コーディング時間 | WakaTime | {coding_str} |
| プログラミング | GitHubコミット数 | {commit_count} commits |
{commit_rows}"""


def main():
    jst = datetime.timezone(datetime.timedelta(hours=9))
    today = sys.argv[1] if len(sys.argv) > 1 else (
        (datetime.datetime.now(jst) - datetime.timedelta(days=1)).date().isoformat()
    )

    github_token    = get_required_env("GITHUB_TOKEN")
    gh_pat          = get_required_env("GH_PAT")
    wakatime_key    = get_required_env("WAKATIME_API_KEY")
    gist_id         = get_required_env("HEALTH_GIST_ID")
    github_username = get_required_env("GITHUB_USERNAME")

    coding_str             = fetch_wakatime(wakatime_key, today)
    commit_count, messages = fetch_github_commits(github_token, today, github_username)
    steps, distance        = fetch_health(gist_id, gh_pat)
    md                     = build_markdown(today, steps, distance, coding_str, commit_count, messages)

    os.makedirs("activity_tracking/daily-logs", exist_ok=True)
    with open(f"activity_tracking/daily-logs/{today}.md", "w") as f:
        f.write(md)

    print(f"✅ Log generated for {today}")


if __name__ == "__main__":
    main()
