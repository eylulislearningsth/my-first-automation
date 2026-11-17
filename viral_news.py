"""Save today's viral news to a Markdown file.

Two free sources, no account or API key needed:
  1. Google News "Top stories" (international English edition)
  2. Wikipedia's most-read articles from yesterday (what the world clicked on)

Output:
  news/YYYY-MM-DD.md   one file per day
  README.md            the latest list is copied between the NEWS markers
"""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

HOW_MANY_HEADLINES = 10
HOW_MANY_WIKI = 10
HEADERS = {"User-Agent": "my-first-automation/1.0 (GitHub Actions learning project)"}

GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en&gl=US&ceid=US:en"
WIKI_TOP = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{y}/{m}/{d}"

# Wikipedia pages that are always popular but are not news
WIKI_SKIP = re.compile(r"^(Main_Page$|-$|Special:|Wikipedia:|Portal:|File:|Help:|Template:|Category:|Talk:|User:)")


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def top_headlines():
    root = ET.fromstring(fetch(GOOGLE_NEWS_RSS))
    items = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        source = item.findtext("source", "").strip()
        # Google adds " - Source" at the end of titles; drop it since we show the source separately
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)]
        items.append((title, link, source))
        if len(items) == HOW_MANY_HEADLINES:
            break
    return items


def wiki_most_read():
    day = datetime.now(timezone.utc) - timedelta(days=1)
    url = WIKI_TOP.format(y=day.year, m=f"{day.month:02d}", d=f"{day.day:02d}")
    data = json.loads(fetch(url))
    results = []
    for a in data["items"][0]["articles"]:
        name = a["article"]
        if WIKI_SKIP.match(name):
            continue
        results.append((name.replace("_", " "), f"https://en.wikipedia.org/wiki/{name}", a["views"]))
        if len(results) == HOW_MANY_WIKI:
            break
    return results


def build_markdown(today):
    lines = [f"## Viral news for {today}", ""]

    lines.append("### Top headlines worldwide")
    try:
        for i, (title, link, source) in enumerate(top_headlines(), 1):
            src = f" ({source})" if source else ""
            lines.append(f"{i}. [{title}]({link}){src}")
    except Exception as e:  # keep going even if one source is down
        lines.append(f"_Could not load headlines today: {e}_")
    lines.append("")

    lines.append("### What the world was reading on Wikipedia yesterday")
    try:
        for i, (name, link, views) in enumerate(wiki_most_read(), 1):
            lines.append(f"{i}. [{name}]({link}) ({views:,} views)")
    except Exception as e:
        lines.append(f"_Could not load Wikipedia stats today: {e}_")
    lines.append("")

    return "\n".join(lines)


def update_readme(md):
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    new = re.sub(
        r"<!-- NEWS:START -->.*<!-- NEWS:END -->",
        f"<!-- NEWS:START -->\n{md}\n<!-- NEWS:END -->",
        readme,
        flags=re.DOTALL,
    )
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new)


if __name__ == "__main__":
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md = build_markdown(today)

    os.makedirs("news", exist_ok=True)
    with open(f"news/{today}.md", "w", encoding="utf-8") as f:
        f.write(md)

    update_readme(md)
    print(md)
