"""Flag the parts of a Markdown answer that slow a scanning reader down.

Usage:
    python3 scan_check.py FILE [FILE ...]
    python3 scan_check.py - < draft.md

Flags sentences over 25 words, paragraphs over 3 sentences, and em-dashes.
Prints nothing and exits 0 when the text is clean. Code blocks and table borders are skipped.
"""

import re
import sys
from pathlib import Path

# ---------- Constants ----------

MAX_WORDS = 25  # longest sentence allowed, from SKILL.md step 3
MAX_SENTENCES = 3  # longest paragraph allowed, from SKILL.md step 3
EM_DASH = "—"
CODE_FENCE = "```"  # opens and closes a code block
NEW_BLOCK = re.compile(r"^\s*(#|[-*+] |\d+\. |\||$)")  # a heading, list item, table row or blank line
QUOTE = re.compile(r"^\s*>\s?")  # a > quote marker, stripped so quoted text is still checked
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")  # a sentence ends at . ! or ? before a space
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")  # [text](url): only the text counts
INLINE_CODE = re.compile(r"`[^`]*`")  # `code` counts as one word
MARKUP = re.compile(r"[*_#]|\[!\w+\]")  # bold, headings, callout labels
WORD = re.compile(r"[A-Za-z0-9][\w'%.-]*")  # a word, or a number like 15.0%
TABLE_BORDER = re.compile(r"^\|?[\s|:-]+\|?$")  # the |---|---| line under a table header
SHOWN = 80  # characters of a flagged sentence shown


def blocks(text):
    """(first line number, text, is_paragraph) for each paragraph, list item or table cell."""
    start, lines, in_code = 0, [], False
    all_lines = text.splitlines()
    skip = 0
    if all_lines and all_lines[0].strip() == "---":  # skip YAML frontmatter
        skip = next((i + 1 for i, l in enumerate(all_lines[1:], 1) if l.strip() == "---"), 0)
    for number, raw in enumerate(all_lines, 1):
        if number <= skip:
            continue
        line = QUOTE.sub("", raw)
        if line.strip().startswith(CODE_FENCE):
            in_code = not in_code
            continue
        if in_code or TABLE_BORDER.match(line.strip()):
            continue
        if NEW_BLOCK.match(line) or not lines:  # this line starts a new block
            if lines:
                yield start, " ".join(lines), is_paragraph
            start, lines = number, []
            is_paragraph = not NEW_BLOCK.match(line)
        if line.lstrip().startswith("|"):  # each table cell is its own text
            yield from ((number, cell, False) for cell in line.split("|"))
        elif line.strip():
            lines.append(line.strip())
    if lines:
        yield start, " ".join(lines), is_paragraph


def problems(text):
    """(line number, message) for each problem found in the text."""
    found = []
    for number, block, is_paragraph in blocks(text):
        if EM_DASH in block:
            found.append((number, "em-dash: use a comma or a period"))
        plain = MARKUP.sub("", INLINE_CODE.sub("code", LINK.sub(r"\1", block))).strip()
        sentences = [s for s in SENTENCE_END.split(plain) if WORD.search(s)]
        if is_paragraph and len(sentences) > MAX_SENTENCES:
            found.append((number, f"{len(sentences)} sentences in one paragraph: split it or use bullets"))
        for sentence in sentences:
            words = len(WORD.findall(sentence))
            if words > MAX_WORDS:
                found.append((number, f"{words} words: {sentence[:SHOWN]}"))
    return found


def main(paths):
    total = 0
    for path in paths or ["-"]:
        text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        name = "stdin" if path == "-" else path
        for number, message in problems(text):
            print(f"{name}:{number}: {message}")
            total += 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
