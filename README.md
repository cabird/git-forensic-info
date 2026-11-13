# Git Internals for Software Forensics

A short primer on how Git stores code and history, what its hashes prove, and
how to use that in forensic work.

- **[Read the primer](https://cabird.github.io/git-forensic-info/)** · [PDF](https://cabird.github.io/git-forensic-info/dist/primer.pdf) (Letter)
- **[Printable cheat sheet](https://cabird.github.io/git-forensic-info/dist/cheat-sheet.html)** · [PDF](https://cabird.github.io/git-forensic-info/dist/cheat-sheet.pdf) (one page)

The web pages are single self-contained HTML files in [`dist/`](dist/), with no
external fonts, scripts or images. GitHub shows HTML files as source, so use
the links above to read them, or download the files and open them in any
browser, offline. The PDFs are in `dist/` too, and GitHub displays those
directly. The links are served by GitHub Pages from the `main` branch:
`index.html` redirects to the primer, and `.nojekyll` tells Pages to serve the
files as they are.

The HTML is a build artifact. Do not edit it by hand; edit the sources and
rebuild.

## Build

    pip install -r requirements.txt     # just the `markdown` library
    python3 build.py                    # writes dist/primer.html and dist/cheat-sheet.html

The build needs no network access and is deterministic: unchanged sources give
a byte-identical file.

The PDFs are a separate, optional step, because they need a headless browser:

    node make_pdf.js                    # writes dist/primer.pdf and dist/cheat-sheet.pdf (Letter)
    node make_pdf.js A4                 # the same, on A4

This needs Node and Playwright (`npm install playwright`). Run it after
`build.py` whenever the HTML changes, so the committed PDFs do not go stale.

## Layout

| Path | What it is |
|---|---|
| `content/*.md` | One Markdown file per section, numbered for order. `00-` is the title and introduction, `99-` is the cheat sheet (the one source for both the primer's last section and the standalone sheet) |
| `diagrams/figures.py` | One Python function per figure; each returns SVG and a caption |
| `diagrams/svg.py` | Shared drawing helper: shapes, colors, arrows, text sizing |
| `demo/make_demo.sh` | Builds the demo repositories and captures command output |
| `demo/output/` | Captured output and `hashes.json` (committed; read by the build) |
| `demo/pair-commits.sh` | Small read-only tool used in section 6; reusable on real repositories |
| `style.css` | Inlined into both pages at build time, including the print styles |
| `cheat-sheet.css` | Extra rules for the standalone cheat sheet only (page margins, heading) |
| `build.py` | Turns all of the above into `dist/primer.html` and `dist/cheat-sheet.html` |
| `make_pdf.js` | Optional: prints the two HTML pages to PDF with headless Chromium |

## Editing content

Edit the Markdown in `content/` and run `python3 build.py`. The first line of
each file (`# Title`) is the section title; numbering and the table of contents
are generated. Placeholders:

| Placeholder | Becomes |
|---|---|
| `{{diagram:name}}` | The figure `name` from `diagrams/figures.py`, numbered automatically (on its own line) |
| `{{output:name}}` | The captured output in `demo/output/name.txt` (on its own line) |
| `{{fig:name}}` | A link reading "Figure N" |
| `{{h:name}}` | A 7-character hash from `demo/output/hashes.json`, e.g. `{{h:fix}}` |
| `::: why` … `:::` | A "Why this matters forensically" callout |
| `::: box Title` … `:::` | A titled box |

To add a section, add a file with the next number. To reorder, renumber the files.

## Adding or changing a diagram

Figures are generated, never drawn by hand. Add a function to
`diagrams/figures.py` that builds a `Canvas`, returns `(svg, caption)`, and is
listed in `FIGURES`; then reference it with `{{diagram:its_name}}`. Use
`c.node()` for objects (boxes size themselves to their text), `c.arrow()` for
references, and `H["name"][:7]` for real demo hashes. Colors and shapes for
blob, tree, commit and tag live in `diagrams/svg.py`, so changing them there
restyles every figure. The build fails if a figure is unused or a placeholder
is unknown.

## Rebuilding the demo

    ./demo/make_demo.sh && python3 build.py

Every hash in the primer comes from this script. Names, emails, dates, the
signing key and the signing time are all fixed, so the hashes are identical on
every run. Requirements and fallbacks:

- **git** (developed with 2.43).
- **git-filter-repo** (`pip install git-filter-repo`) for the filtered copy.
  If it is missing, the script falls back to `git filter-branch`, which
  produces the same hashes. Set `DEMO_NO_FILTER_REPO=1` to force the fallback.
- **gpg** to sign the release commit with the throwaway key in `demo/keys/`
  (see the note there: it is a public demo key, not a secret). Without gpg the
  commit is left unsigned, so its hash, the tag's hash and the signature
  output will differ from the committed ones.

To add a command to the primer, add a `cap name DIR <<EOF … EOF` block to
`make_demo.sh`, rerun it, and reference `{{output:name}}` in the content. To
use a new hash in a figure or in prose, add it to the `H[...]` table in the
same script.

The working repositories are left in `demo/work/` (ignored by Git) so you can
explore them: `original`, `filtered`, `fresh` (a clean clone), `compare` and
`loose`.
