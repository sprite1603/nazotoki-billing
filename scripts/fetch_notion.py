#!/usr/bin/env python3
"""Notion「謎解き予定」から受取チェック OFF の公演を取得し site/data.json に書き出す。

GitHub Actions から実行される想定。環境変数 NOTION_TOKEN が必要。
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "371b37adbf34809ba194d9dfd55d8f2b")
NOTION_VERSION = "2022-06-28"
JST = timezone(timedelta(hours=9))
OUT = Path(__file__).resolve().parent.parent / "site" / "data.json"


def query(token, body):
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        method="POST",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion API エラー ({e.code}): {e.read().decode(errors='replace')}")


def to_jst_date(s):
    if not s:
        return None
    if "T" not in s:
        return s
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(JST).date().isoformat()


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("NOTION_TOKEN が設定されていません")

    events, cursor = [], None
    while True:
        body = {
            "filter": {"property": "受取チェック", "checkbox": {"equals": False}},
            "sorts": [{"property": "日付", "direction": "ascending"}],
            "page_size": 100,
        }
        if cursor:
            body["start_cursor"] = cursor
        data = query(token, body)
        for page in data["results"]:
            p = page["properties"]
            events.append({
                "title": "".join(t["plain_text"] for t in p["公演名"]["title"]).strip() or "(無題)",
                "date": to_jst_date((p["日付"].get("date") or {}).get("start")),
                "amount": p["金額"]["number"],
                "people": p["人数"]["number"],
                "members": [m["name"] for m in p["メンバー"]["multi_select"]],
            })
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "updated": datetime.now(JST).isoformat(timespec="minutes"),
        "events": events,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(events)} 件を書き出しました → {OUT}")


if __name__ == "__main__":
    main()
