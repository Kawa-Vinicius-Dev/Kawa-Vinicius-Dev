"""Daily live data -> data/status.json.

- Trilha Backend Java: exercise folders in protocolo-carrasco-java (public API).
- Fluxo de Gestão: one HTTP ping to $PROD_URL (a repo secret). The URL is never written anywhere.
  Without PROD_URL (e.g. a local run) the ping is skipped and the history is kept as is.
"""
import json
import os
import re
import time
from datetime import datetime, timezone

import requests

TRILHA_REPO = "Kawa-Vinicius-Dev/protocolo-carrasco-java"
TRILHA_TOTAL = 247
KEEP = 90  # daily checks kept for the uptime figure
PATH = "data/status.json"


def count_exercises():
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {}
    r = requests.get(f"https://api.github.com/repos/{TRILHA_REPO}/git/trees/HEAD?recursive=1", headers=headers, timeout=30)
    r.raise_for_status()
    return sum(1 for t in r.json()["tree"]
               if t["type"] == "tree" and re.fullmatch(r"src/exercicios/[^/]+/exercicio\d+", t["path"]))


def ping(url):
    t0 = time.monotonic()
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "kawa-profile-status"})
        # any answer below 500 means the server is running (a login-protected API replies 401/403)
        return {"up": r.status_code < 500, "code": r.status_code, "ms": round((time.monotonic() - t0) * 1000)}
    except requests.RequestException:
        return {"up": False, "code": None, "ms": None}


if __name__ == "__main__":
    try:
        data = json.load(open(PATH, encoding="utf-8"))
    except FileNotFoundError:
        data = {"checks": []}

    data["trilha"] = {"feitos": count_exercises(), "total": TRILHA_TOTAL}
    if os.environ.get("PROD_URL"):
        check = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), **ping(os.environ["PROD_URL"])}
        data["checks"] = (data["checks"] + [check])[-KEEP:]
        print("prod:", "up" if check["up"] else "DOWN", check["code"], check["ms"])
    else:
        print("PROD_URL not set - skipping ping")

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print("trilha:", data["trilha"])
