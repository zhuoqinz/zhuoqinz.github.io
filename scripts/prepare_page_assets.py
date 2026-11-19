"""Inline small homepage dependencies to avoid cold-start request waterfalls.

CSS/JS files remain the editable sources (and are still shared with the CV).
Run after changing those files. Image bytes, CSS rules and JS behavior are not
transformed. Keeping this deterministic also makes generated output verifiable.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"
CSS = ("assets/css/personal.css", "assets/css/personal-v2.css")
JS = ("assets/js/personal.js", "assets/js/academic.js")


def block(kind, paths):
    tag = "style" if kind == "styles" else "script"
    parts = []
    for path in paths:
        source = (ROOT / path).read_text(encoding="utf-8").rstrip()
        assert f"</{tag}" not in source.lower(), path
        parts.append(f'<{tag} data-source="{path}">\n{source}\n</{tag}>')
    return f"<!-- inline-{kind}:start -->\n" + "\n".join(parts) + f"\n<!-- inline-{kind}:end -->"


def build():
    html = PAGE.read_text(encoding="utf-8")
    # Keep the first paper eager and give it an early high-priority request.
    # Native lazy loading fetches nearby papers ahead of scrolling while distant
    # figures no longer compete with the portrait and first visible paper.
    paper_index = 0
    def paper_policy(match):
        nonlocal paper_index
        tag = match.group()
        if 'loading=' not in tag:
            return tag
        priority = "high" if paper_index == 0 else "auto"
        loading = "eager" if paper_index == 0 else "lazy"
        paper_index += 1
        tag = re.sub(r'fetchpriority="[^"]*"', f'fetchpriority="{priority}"', tag)
        return re.sub(r'loading="[^"]*"', f'loading="{loading}"', tag)
    html = re.sub(r'<img\b[^>]*>', paper_policy, html)
    assert paper_index == 5, paper_index
    html = re.sub(
        r'(<link rel="preload" as="image" type="image/avif"[^>]*?)(?: fetchpriority="[^"]*")?>',
        r'\1 fetchpriority="high">', html)
    for kind, paths, anchor in (("styles", CSS, "</head>"), ("scripts", JS, "</body>")):
        generated = block(kind, paths)
        marker = rf"<!-- inline-{kind}:start -->.*?<!-- inline-{kind}:end -->"
        if re.search(marker, html, re.S):
            html = re.sub(marker, lambda _: generated, html, flags=re.S)
        else:
            for path in paths:
                if kind == "styles":
                    pattern = rf'\s*<link rel="stylesheet" href="{re.escape(path)}(?:\?[^"]*)?">'
                else:
                    pattern = rf'\s*<script src="{re.escape(path)}(?:\?[^"]*)?" defer></script>'
                html, count = re.subn(pattern, "", html)
                assert count == 1, (path, count)
            html = html.replace(anchor, generated + "\n" + anchor, 1)
    PAGE.write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    build()
