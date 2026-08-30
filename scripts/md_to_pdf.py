"""Render a Markdown file to a clean, print-ready PDF via headless Chrome.

Usage: python scripts/md_to_pdf.py <input.md> <output.pdf> ["Doc Title"]

No LaTeX/pandoc needed — Markdown -> styled HTML -> Chrome --print-to-pdf.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1a1a20; max-width: 100%; margin: 0; }
h1 { font-size: 21pt; color: #4b0f82; margin: 0 0 4pt; line-height: 1.15; }
h2 { font-size: 14pt; color: #6a1bb0; margin: 18pt 0 6pt; border-bottom: 1.5px solid #e5d6f5;
  padding-bottom: 3pt; }
h3 { font-size: 11.5pt; color: #333; margin: 12pt 0 4pt; }
p, li { font-size: 10.5pt; }
a { color: #7a1fb8; text-decoration: none; }
code { background: #f3eefa; padding: 1px 4px; border-radius: 3px;
  font: 9pt ui-monospace, "SF Mono", Menlo, Consolas, monospace; color: #5a1a8a; }
pre { background: #f6f3fb; border: 1px solid #e5d6f5; border-radius: 6px; padding: 10px 12px;
  overflow-x: auto; }
pre code { background: none; padding: 0; color: #2a2a30; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt; }
th, td { border: 1px solid #dcd3ea; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f3eefa; color: #4b0f82; font-weight: 700; }
blockquote { border-left: 3px solid #a100ff; background: #faf7fe; margin: 8pt 0;
  padding: 6pt 12pt; color: #444; }
strong { color: #1a1a20; }
hr { border: none; border-top: 1px solid #e5d6f5; margin: 14pt 0; }
h1, h2, h3 { page-break-after: avoid; }
table, pre, blockquote { page-break-inside: avoid; }
"""


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    html_body = markdown.markdown(
        src.read_text(), extensions=["tables", "fenced_code", "toc", "sane_lists"])
    html = (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>"
            f"<style>{CSS}</style></head><body>{html_body}</body></html>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        tmp = f.name
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", f"file://{tmp}"],
                   check=True, capture_output=True)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
