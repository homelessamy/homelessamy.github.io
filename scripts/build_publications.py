"""Render verified publication records into static HTML; no client JS required.

Run after editing publications.json. Use --check in CI to verify generated HTML.
An empty list produces no public section, heading, or placeholder.
"""
import argparse
import difflib
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = "    <!-- publications:start -->"
END = "    <!-- publications:end -->"
STATUSES = {"Preprint", "Under review", "In preparation", "Published"}


def render(records):
    entries = []
    for record in records:
        if record["status"] not in STATUSES:
            raise ValueError("Unknown publication status")
        if not isinstance(record["authors"], list) or not record["authors"]:
            raise ValueError("Each publication needs an author list")
        if not isinstance(record["year"], int) or not record["title"].strip():
            raise ValueError("Each publication needs a title and integer year")
        links = []
        for field in ("paper", "code", "project"):
            url = record.get(field)
            if not url:
                continue
            parsed = urlsplit(url)
            if not (parsed.scheme == "https" and parsed.netloc) and not (
                not parsed.scheme and not parsed.netloc and url.startswith("research/")
            ):
                raise ValueError("Use an HTTPS URL or a local research/ path")
            links.append(f'<a href="{escape(url, quote=True)}">{field.title()}</a>')
        authors = ", ".join(escape(author) for author in record["authors"])
        venue = escape(record.get("venue", ""))
        metadata = " · ".join(part for part in (venue, record["status"]) if part)
        entries.append(
            '<article class="publication">'
            f'<p class="meta">{authors}</p>'
            f'<h3>{escape(record["title"])}</h3>'
            f'<p class="meta">{metadata} · <time datetime="{record["year"]}">{record["year"]}</time></p>'
            + (f'<div class="publication-links">{"".join(links)}</div>' if links else "")
            + '</article>'
        )
    if not entries:
        return ""
    return ('    <section class="section secondary-section" id="publications" aria-labelledby="publications-title">\n'
            '      <h2 id="publications-title">Publications</h2>\n      <div>'
            + "\n".join(entries) + '</div>\n    </section>\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = (ROOT / "index.html").read_text()
    before, rest = content.split(START)
    _, after = rest.split(END)
    output = before + START + "\n" + render(json.loads((ROOT / "publications.json").read_text())) + END + after
    if args.check:
        if output != content:
            print("".join(difflib.unified_diff(content.splitlines(True), output.splitlines(True))))
            raise SystemExit("Run python scripts/build_publications.py")
        print("Publication HTML is current.")
    elif output != content:
        (ROOT / "index.html").write_text(output)
        print("Publication HTML updated.")
    else:
        print("Publication HTML already current.")
