#!/usr/bin/env python3
"""Build dist/primer.html and dist/cheat-sheet.html from content/, diagrams/,
demo/output/ and the two stylesheets.

Both pages are build artifacts: edit the sources, then run `python3 build.py`.
The cheat sheet has one source, content/99-cheat-sheet.md. It becomes the last
section of the primer and, on its own, the printable one-page cheat-sheet.html.
The build is deterministic (no timestamps, no randomness, sorted inputs), so
unchanged sources always give a byte-identical file.

Placeholders understood in content/*.md:
  {{diagram:name}}   a figure from diagrams/figures.py (on its own line)
  {{output:name}}    captured command output from demo/output/name.txt (own line)
  {{fig:name}}       "Figure N", linked to that figure
  {{h:name}}         a 7-character demo hash from demo/output/hashes.json
  ::: why  ... :::   a "Why this matters forensically" callout
  ::: box Title ... :::   a titled box
"""
import html
import json
import pathlib
import re
import sys

import markdown

from diagrams import FIGURES

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT, OUTPUT, DIST = ROOT / "content", ROOT / "demo" / "output", ROOT / "dist"
HASHES = json.loads((OUTPUT / "hashes.json").read_text(encoding="utf-8"))


def md(text):
    return markdown.Markdown(extensions=["tables", "md_in_html", "sane_lists", "smarty"],
                             output_format="html").convert(text)


def callouts(text):
    """Turn ':::' fences into titled <div> blocks that still contain Markdown."""
    out = []
    for line in text.split("\n"):
        m = re.fullmatch(r":::\s*(why|box)\s*(.*)", line.strip())
        if m:
            kind, title = m.group(1), m.group(2) or "Why this matters forensically"
            out.append(f'<div class="callout {kind}" markdown="1">\n'
                       f'<p class="callout-title">{html.escape(title)}</p>\n')
        elif line.strip() == ":::":
            out.append("\n</div>")
        else:
            out.append(line)
    return "\n".join(out)


def render_output(name):
    path = OUTPUT / f"{name}.txt"
    if not path.exists():
        sys.exit(f"build.py: no captured output '{name}' (run demo/make_demo.sh?)")
    lines = []
    raws = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
    for i, raw in enumerate(raws):
        line = html.escape(raw.rstrip().replace("\t", "  "), quote=False)
        lines.append(f'<span class="cmd">{line}</span>' if raw.startswith("$ ") else line)
        # a command that printed nothing: say so, since silence is often the finding
        if raw.startswith("$ ") and (i + 1 == len(raws) or raws[i + 1].startswith("$ ")):
            lines.append('<span class="none">(no output)</span>')
    return '<pre class="term"><code>' + "\n".join(lines) + "</code></pre>"


def main():
    files = sorted(CONTENT.glob("*.md"))
    sources = {f: f.read_text(encoding="utf-8") for f in files}

    # Figures are numbered in order of first appearance across the whole page.
    fig_no = {}
    for f in files:
        for name in re.findall(r"\{\{diagram:(\w+)\}\}", sources[f]):
            if name not in FIGURES:
                sys.exit(f"build.py: {f.name} uses unknown diagram '{name}'")
            fig_no.setdefault(name, len(fig_no) + 1)
    unused = sorted(set(FIGURES) - set(fig_no))
    if unused:
        sys.exit(f"build.py: diagrams never referenced from content: {', '.join(unused)}")

    def figure(m):
        name = m.group(1)
        svg, caption = FIGURES[name](HASHES)
        return (f'<figure id="fig-{name}"><div class="figure-scroll">{svg}</div>'
                f'<figcaption><strong>Figure {fig_no[name]}.</strong> {caption}</figcaption></figure>')

    def convert(text):
        def short_hash(m):
            if m.group(1) not in HASHES:
                sys.exit(f"build.py: unknown hash name '{m.group(1)}'")
            return HASHES[m.group(1)][:7]
        text = re.sub(r"\{\{h:([\w.]+)\}\}", short_hash, text)
        text = re.sub(r"\{\{fig:(\w+)\}\}",
                      lambda m: f'<a href="#fig-{m.group(1)}">Figure {fig_no[m.group(1)]}</a>', text)
        body = md(callouts(text))
        body = re.sub(r"<p>\{\{diagram:(\w+)\}\}</p>", figure, body)
        return re.sub(r"<p>\{\{output:([\w-]+)\}\}</p>", lambda m: render_output(m.group(1)), body)

    title, lede, sections, toc, number, sheet = "", "", [], [], 0, ""
    for f in files:
        heading, _, body = sources[f].partition("\n")
        name = heading.lstrip("# ").strip().replace("'", "\u2019")
        slug = re.sub(r"^\d+-", "", f.stem)
        if f.stem.startswith("00-"):                    # page title and introduction
            title, lede = name, convert(body)
        elif f.stem.startswith("99-"):                  # the cheat sheet: unnumbered, own print pages
            sheet = convert(body)
            sections.append(f'<section id="{slug}" class="cheatsheet"><h2>{html.escape(name)}</h2>\n'
                            f'<p class="sheet-note screen-only"><a href="cheat-sheet.html">Open the '
                            f'printable one-page version</a> (<a href="cheat-sheet.pdf">PDF</a>)</p>\n'
                            f'{sheet}\n</section>')
            toc.append(f'<li class="toc-extra"><a href="#{slug}">{html.escape(name)}</a></li>')
        else:
            number += 1
            sections.append(f'<section id="{slug}"><h2><span class="num">{number}</span> '
                            f'{html.escape(name)}</h2>\n{convert(body)}\n</section>')
            toc.append(f'<li><a href="#{slug}">{html.escape(name)}</a></li>')

    css = (ROOT / "style.css").read_text(encoding="utf-8").strip()
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
{css}
</style>
</head>
<body>
<header>
<h1>{html.escape(title)}</h1>
{lede}
<p class="sheet-note screen-only">Also available: <a href="primer.pdf">this primer as a PDF</a>, and the
<a href="cheat-sheet.html">one-page cheat sheet</a> (<a href="cheat-sheet.pdf">PDF</a>).</p>
</header>
<nav class="toc" aria-label="Contents">
<h2>Contents</h2>
<ol>
{chr(10).join(toc)}
</ol>
</nav>
<main>
{chr(10).join(sections)}
</main>
</body>
</html>
"""
    sheet_css = (ROOT / "cheat-sheet.css").read_text(encoding="utf-8").strip()
    sheet_page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Git Forensics Cheat Sheet</title>
<style>
{css}
{sheet_css}
</style>
</head>
<body class="sheet">
<main>
<section id="cheat-sheet" class="cheatsheet">
<h1>Git Forensics Cheat Sheet</h1>
<p class="sheet-note screen-only">Prints on one page (A4 or Letter); also as a
<a href="cheat-sheet.pdf">PDF</a>. From the primer <a href="primer.html">{html.escape(title)}</a>.</p>
{sheet}
<p class="sheet-note print-only">From the primer \u201c{html.escape(title)}\u201d.</p>
</section>
</main>
</body>
</html>
"""
    DIST.mkdir(exist_ok=True)
    (DIST / "primer.html").write_text(page, encoding="utf-8", newline="\n")
    (DIST / "cheat-sheet.html").write_text(sheet_page, encoding="utf-8", newline="\n")
    words = len(re.sub(r"<(pre|svg|style)\b.*?</\1>|<[^>]+>", " ", page, flags=re.S).split())
    print(f"wrote dist/primer.html: {len(page.encode('utf-8')) // 1024} KB, "
          f"{number} sections, {len(fig_no)} figures, about {words} words of prose")
    print(f"wrote dist/cheat-sheet.html: {len(sheet_page.encode('utf-8')) // 1024} KB")


if __name__ == "__main__":
    main()
