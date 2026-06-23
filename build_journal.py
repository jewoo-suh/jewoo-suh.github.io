#!/usr/bin/env python3
"""
Build the Journal: turn journal/posts/*.md into styled static HTML.

Usage:
    python build_journal.py

Each post is a Markdown file in journal/posts/ with a small front-matter block:

    ---
    title: My trip to Beppu
    date: 2026-06-20
    teaser: One line shown on the Journal index.
    location: Beppu, Japan        # optional
    ---
    Body in **Markdown**. Images: ![alt](img/photo.jpg)  (put files in journal/img/)

Running this regenerates journal/index.html and one journal/<slug>.html per post.
No em-dashes are introduced (the 'smarty' extension is deliberately not used).
"""
import os
import re
import glob
import html
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(HERE, "journal", "posts")
OUT_DIR = os.path.join(HERE, "journal")

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def parse_front_matter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block = text[3:end].strip()
            body = text[end + 4:].lstrip("\n")
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
    return meta, body


def fmt_date(iso):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
    if not m:
        return iso or ""
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{d} {MONTHS[mo]} {y}"


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Jewoo Suh</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="../assets/style.css" />
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml" />
</head>
<body>
"""

INDEX_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Journal | Jewoo Suh</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="../assets/style.css" />
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml" />
</head>
<body>
"""


def build():
    posts = []
    for path in glob.glob(os.path.join(POSTS_DIR, "*.md")):
        slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            meta, body = parse_front_matter(f.read())
        md = markdown.Markdown(extensions=["extra", "sane_lists"])
        body_html = md.convert(body)
        posts.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": meta.get("date", ""),
            "teaser": meta.get("teaser", ""),
            "location": meta.get("location", ""),
            "body": body_html,
        })

    posts.sort(key=lambda p: p["date"], reverse=True)

    # individual post pages
    for p in posts:
        loc = f' &nbsp;&middot;&nbsp; {html.escape(p["location"])}' if p["location"] else ""
        page = HEAD.format(title=html.escape(p["title"]))
        page += (
            f'  <div class="breadcrumb">\n'
            f'    <a href="../index.html">Jewoo Suh</a>\n    <span>/</span>\n'
            f'    <a href="index.html">Journal</a>\n    <span>/</span>\n'
            f'    {html.escape(p["title"])}\n  </div>\n\n'
            f'  <h1 class="page-title">{html.escape(p["title"])}</h1>\n'
            f'  <div class="post-meta">{fmt_date(p["date"])}{loc}</div>\n\n'
            f'  <div class="post-prose">\n{p["body"]}\n  </div>\n\n'
            f'  <a class="page-link" href="index.html">&larr; All entries</a>\n\n'
            f'</body>\n</html>\n'
        )
        with open(os.path.join(OUT_DIR, p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)

    # index
    idx = INDEX_HEAD
    idx += (
        '  <div class="breadcrumb">\n'
        '    <a href="../index.html">Jewoo Suh</a>\n    <span>/</span>\n    Journal\n  </div>\n\n'
        '  <h1 class="page-title">Journal</h1>\n'
        '  <p class="journal-intro">Occasional notes, diary entries, and travel.</p>\n\n'
        '  <div class="journal-list">\n'
    )
    if not posts:
        idx += '    <p class="journal-teaser">No entries yet.</p>\n'
    for p in posts:
        loc = f' &nbsp;&middot;&nbsp; {html.escape(p["location"])}' if p["location"] else ""
        idx += (
            f'    <a class="journal-entry" href="{p["slug"]}.html">\n'
            f'      <div class="journal-date">{fmt_date(p["date"])}{loc}</div>\n'
            f'      <div class="journal-body">\n'
            f'        <h2 class="journal-title">{html.escape(p["title"])}</h2>\n'
            f'        <p class="journal-teaser">{html.escape(p["teaser"])}</p>\n'
            f'      </div>\n    </a>\n'
        )
    idx += '  </div>\n\n</body>\n</html>\n'
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)

    print(f"Built {len(posts)} post(s) + index into journal/")


if __name__ == "__main__":
    build()
