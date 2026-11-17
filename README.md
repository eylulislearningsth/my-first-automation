# Daily viral news

Every morning a GitHub Action collects the stories that are blowing up worldwide and saves them here.

- **Top headlines** come from Google News Top Stories.
- **What the world is reading** comes from Wikipedia's most-viewed articles of the previous day, which is a good signal of what actually went viral.

Each day gets its own file in the [`news/`](news) folder, and the latest list is shown below.

<!-- NEWS:START -->
_The first list appears here after the workflow runs._
<!-- NEWS:END -->

## How it works

- `viral_news.py` fetches both sources and writes the Markdown.
- `.github/workflows/daily.yml` runs it every day at 06:00 UTC, whenever you push, and whenever you click **Run workflow** in the **Actions** tab.
- The workflow commits the results back to the repo, so run `git pull` before you change anything yourself.
