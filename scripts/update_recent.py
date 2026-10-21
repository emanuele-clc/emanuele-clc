"""Rewrite the "Latest activity" block of README.md with the most recently pushed repos."""

import json
import os
import re
import urllib.request
from datetime import datetime

USER = "emanuele-clc"
LIMIT = 5
# Personal or not-yet-public-facing repos that shouldn't be advertised on the profile
EXCLUDE = {USER, "deutsch", "football-opposition-report", "app_meteo"}

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=100",
    headers={"Accept": "application/vnd.github+json"},
)
token = os.environ.get("GITHUB_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")

with urllib.request.urlopen(req) as resp:
    repos = json.load(resp)

lines = []
for repo in repos:
    if repo["fork"] or repo["private"] or repo["name"] in EXCLUDE:
        continue
    pushed = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y")
    desc = f" – {repo['description']}" if repo["description"] else ""
    lines.append(f"- 🔨 **[{repo['name']}]({repo['html_url']})**{desc} <sub>(updated {pushed})</sub>")
    if len(lines) == LIMIT:
        break

block = "<!--RECENT:START-->\n" + "\n".join(lines) + "\n<!--RECENT:END-->"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

new = re.sub(r"<!--RECENT:START-->.*?<!--RECENT:END-->", lambda _: block, readme, flags=re.S)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new)
