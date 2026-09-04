#!/usr/bin/env python3
"""Split the Codex course index.html into per-unit Markdown files.

Usage:
    .venv/bin/python scripts/export_units.py \
        /path/to/course-1-14/index.html knowledge/codex-course
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}


def clean(text: str) -> str:
    """Collapse HTML whitespace artifacts into single spaces."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def inline(node: Tag) -> str:
    """Render inline markdown for a text-bearing node."""
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name == "strong" or name == "b":
            parts.append(f"**{clean(inline(child))}**")
        elif name == "em" or name == "i":
            parts.append(f"*{clean(inline(child))}*")
        elif name == "code":
            parts.append(f"`{child.get_text()}`")
        elif name == "a":
            href = child.get("href", "")
            text = clean(inline(child))
            parts.append(f"[{text}]({href})" if text else f"<{href}>")
        elif name == "img":
            alt = child.get("alt", "")
            parts.append(f"![{alt}]({child.get('src', '')})" if alt else "")
        elif name == "br":
            parts.append("\n")
        else:
            parts.append(inline(child))
    return "".join(parts)


def walk(node: Tag, out: list[str]) -> None:
    """Render block-level markdown for a container node."""
    for child in node.children:
        if isinstance(child, NavigableString):
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()

        if name in HEADINGS:
            text = clean(inline(child))
            out.append(f"{'#' * HEADINGS[name]} {text}\n")
        elif name == "p":
            text = clean(inline(child))
            out.append(f"{text}\n" if text else "")
        elif name in ("ul", "ol"):
            prefix = "-" if name == "ul" else "1."
            for li in child.find_all("li", recursive=False):
                text = clean(inline(li))
                out.append(f"{prefix} {text}\n")
            out.append("")
        elif name == "blockquote":
            text = clean(inline(child))
            out.append(f"> {text}\n")
        elif name == "pre":
            code = child.get_text().strip("\n")
            out.append("```\n" + code + "\n```\n")
        elif name == "code":
            out.append(f"`{child.get_text()}`\n")
        elif name == "hr":
            out.append("---\n")
        elif name == "img":
            alt = child.get("alt", "")
            out.append(f"![{alt}]({child.get('src', '')})\n")
        elif name == "header":
            # skip unit header: its h1 duplicates the title we prepend
            continue
        elif name in ("article", "section", "div", "main", "body", "figure", "figcaption", "footer", "table", "tr", "td", "th"):
            walk(child, out)
        else:
            # fallback: inline the unknown tag, then recurse into its blocks
            out.append(f"{clean(inline(child))}\n")
            walk(child, out)


def slugify(title: str, idx: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title).strip("-").lower()
    return f"{idx:02d}-{slug}"


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    html = src.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    sections = soup.find_all("section", class_="course-unit")
    print(f"found {len(sections)} units")
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, sec in enumerate(sections, start=1):
        uid = sec.get("id", f"unit-{idx}")
        title = sec.get("data-title", uid)
        unit_type = sec.get("data-unit-type", "source")

        lines: list[str] = [f"# {title}\n", f"\n> unit: {uid} | type: {unit_type}\n"]
        walk(sec, lines)

        text = "\n".join(lines)
        text = re.sub(r"[ \t]+$", "", text, flags=re.M)  # trailing spaces
        text = re.sub(r"\n{3,}", "\n\n", text)  # collapse blank runs
        text = text.strip() + "\n"

        name = slugify(title, idx)
        target = out_dir / f"{name}.md"
        target.write_text(text, encoding="utf-8")
        print(f"  {target.name}")


if __name__ == "__main__":
    main()
