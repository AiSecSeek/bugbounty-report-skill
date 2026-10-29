#!/usr/bin/env python3
"""upload_github.py — заливает проект bugbounty-report-skill в GitHub-репозиторий.

Токен берётся из env GH_TOKEN (нужны права repo + workflow).
Создаёт репозиторий, если его нет, затем заливает/обновляет все файлы
через Contents API (один commit на файл).

Запуск:
    GH_TOKEN=ghp_xxx python3 upload_github.py [--repo NAME] [--private]
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
REPO_DEFAULT = "bugbounty-report-skill"
BRANCH = "main"

# Файлы проекта (относительно папки со скриптом)
FILES = [
    "README.md",
    "research.md",
    "LICENSE",
    "SKILL.md",
    "scripts/generate_report.py",
    "examples/finding-xss-example.json",
    "examples/report-hackerone.md",
    "examples/report-bugcrowd.md",
    "examples/report-intigriti.md",
    "examples/report-yeswehack.md",
]

DESCRIPTION = (
    "Bug bounty report skill: HackerOne / Bugcrowd / Intigriti / YesWeHack "
    "formats, severity mapping (CVSS/VRT), JSON -> Markdown report generator"
)


def req(method: str, path: str, data=None, token: str = ""):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(API + path, data=body, method=method)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    r.add_header("Accept", "application/vnd.github+json")
    r.add_header("User-Agent", "bugbounty-report-skill-uploader")
    if body is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read() or b"{}")
        except Exception:
            payload = {}
        return e.code, payload
    except Exception as e:  # noqa: BLE001
        return -1, {"message": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--private", action="store_true", help="создать приватный репо")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("FAIL: нет GH_TOKEN в окружении")
        return 1

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1) проверка токена
    st, me = req("GET", "/user", token=token)
    print("auth:", st, me.get("login", me.get("message")))
    if st != 200:
        return 1
    login = me["login"]

    # 2) репозиторий: есть или создать
    st, repo = req("GET", f"/repos/{login}/{args.repo}", token=token)
    if st == 200:
        print("repo exists:", repo.get("html_url"))
    elif st == 404:
        st, repo = req(
            "POST",
            "/user/repos",
            {
                "name": args.repo,
                "description": DESCRIPTION,
                "private": args.private,
                "auto_init": False,
                "has_issues": True,
            },
            token=token,
        )
        print("create repo:", st, repo.get("html_url") or repo.get("message"))
        if st != 201:
            return 1
    else:
        print("FAIL: проверка репо:", json.dumps(repo)[:300])
        return 1

    # 3) заливка файлов
    ok, fail = 0, 0
    for fname in FILES:
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            print("skip (not found):", fname)
            continue
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        st, cur = req("GET", f"/repos/{login}/{args.repo}/contents/{fname}", token=token)
        sha = cur.get("sha") if st == 200 else None
        payload = {
            "message": "Add " + fname,
            "content": b64,
            "branch": BRANCH,
        }
        if sha:
            payload["sha"] = sha
        st, res = req("PUT", f"/repos/{login}/{args.repo}/contents/{fname}", payload, token=token)
        if st in (200, 201):
            ok += 1
            print("OK:", fname)
        else:
            fail += 1
            print("FAIL:", fname, "->", st, json.dumps(res)[:200])

    print(f"\nDone: {ok} OK, {fail} FAIL")
    print(f"Repo: https://github.com/{login}/{args.repo}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
