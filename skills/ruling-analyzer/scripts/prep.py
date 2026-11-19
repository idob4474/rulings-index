#!/usr/bin/env python3
"""Prepare the full text of a ruling for reading in one pass.

  python3 prep.py ruling.txt -o clean.txt

Writes a clean copy of the text and prints a map of it.
  clean copy   boilerplate of Nevo and of the court site removed, blank lines collapsed, and a marker
               before every opinion and every numbered paragraph, like ⟦עמית פס׳ 5⟧ or ⟦חוות דעת שהם⟧.
               The marker is the pin to write in the card for what follows it.
  map          the opinions in order, with their lines and paragraphs, and every numbered line that
               was left without a marker because it breaks the sequence or repeats (a quoted statute,
               a list inside a quote, numbering that starts over). Those are checked by hand.
Markers are added only where the numbering is unambiguous. Quotes are copied without them.
Standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import find_headers, numbered, sequence, name_tokens, compress_kind  # noqa: E402

BOILER = re.compile(
    r"העותק כפוף לשינויי עריכה|נוסח מסמך זה כפוף לשינויי ניסוח|בעניין עריכה ושינויים במסמכי פסיקה|"
    r"נבו הוצאה לאור|www\.nevo\.co\.il|מרכז מידע,? טל|www\.court\.gov\.il|^\s*\d{6,9}\s*$|^\s*[_*=\-]{5,}\s*$")
INVISIBLE = re.compile(r"[‎‏‪-‮﻿]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text")
    ap.add_argument("-o", "--out", default="clean.txt")
    a = ap.parse_args()
    raw = Path(a.text).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")

    # header written by rulings-index lookup.py
    start, source = 0, None
    if lines and lines[0].lstrip("﻿").startswith("מקור"):
        for i, l in enumerate(lines[:12]):
            if re.fullmatch(r"={20,}", l.strip()):
                start, source = i + 1, " | ".join(x.strip() for x in lines[:i] if x.strip())
                break

    # a Word style block (<!-- ... -->) that some converted rulings carry is dropped
    style = set()
    k = start
    while k < len(lines):
        if lines[k].strip().startswith("<!--"):
            e = next((x for x in range(k, min(len(lines), k + 5000)) if "-->" in lines[x]), None)
            if e is not None and any("{" in lines[x] or "mso-" in lines[x] for x in range(k, e + 1)):
                style.update(range(k, e + 1))
                k = e + 1
                continue
        k += 1

    # opinions by judge headers, then paragraphs per judge. Only numbers on the one possible line get a marker
    heads = [(i, " ".join(name_tokens(label)) or label) for i, label in find_headers(lines, start)]
    segs = []  # (judge, first line, last line)
    for k, (i, who) in enumerate(heads):
        segs.append((who, i, (heads[k + 1][0] if k + 1 < len(heads) else len(lines)) - 1))
    if not segs:
        segs = [("", start, len(lines) - 1)]
    marks, report, items, kinds = {}, [], {}, {}
    for who, a0, a1 in segs:
        got, kind = numbered(lines, a0, a1)
        items.setdefault(who, []).extend(got)
        kinds.setdefault(who, kind)
    for who, got in items.items():
        label = {i: lab for i, _, lab in got}
        good, unsure = sequence([(i, v) for i, v, _ in got])
        for i, v in good:
            marks[i] = f"⟦{who + ' ' if who else ''}פס׳ {label[i]}⟧"
        report.append((who, [v for _, v in good], [(i, label[i]) for i, _ in unsure]))

    # clean copy with markers
    out, removed, blank = [], 0, 0
    line_of = {}
    head_at = {i: who for who, i, _ in segs if who}
    for i in range(start, len(lines)):
        l = INVISIBLE.sub("", lines[i]).rstrip()
        if i in style or BOILER.search(l):
            removed += 1
            continue
        if not l.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        if i in marks:
            line_of[i] = len(out) + 1
            out.append(marks[i] + " " + l.strip())
        else:
            line_of[i] = len(out) + 1
            out.append(l)
        if i in head_at:
            out.append(f"⟦חוות דעת {head_at[i]}⟧")
    clean = "\n".join(out).strip("\n") + "\n"
    Path(a.out).write_text(clean, encoding="utf-8")

    # map
    def ln(i):
        return line_of.get(i) or line_of.get(min((k for k in line_of if k >= i), default=i), i)

    print(f"TEXT {a.out} {clean.count(chr(10))} lines, {len(clean)} characters. {removed} boilerplate lines removed")
    if source:
        print(f"SOURCE {source}")
    first = segs[0][1] if segs[0][0] else None
    if first is not None and first > start:
        print(f"PREAMBLE lines 1-{ln(first) - 1}. Parties, counsel and any summary. Good for names and dates, never a pin")
    if segs[0][0] == "":
        print("OPINIONS no judge headers found. Markers carry the paragraph only, add the judge's name in a ruling with several opinions")
    else:
        print("OPINIONS")
        for who, a0, a1 in segs:
            r = next(x for x in report if x[0] == who)
            paras = f"paragraphs {compress_kind(r[1], kinds[who])}" if r[1] else f"no numbered paragraphs, pin ⟦חוות דעת {who}⟧"
            print(f"  {who}  lines {ln(a0)}-{ln(a1)}  {paras}")
    for who, _, unsure in report:
        if unsure:
            listed = ", ".join(f"{n} (line {ln(i)})" for i, n in unsure)
            print(f"UNMARKED {who or 'text'} {listed}. Quoted text or numbering that starts over. Check before citing")
    print("Read the clean copy in full. The marker before a passage is its pin. Quotes are copied without markers")


if __name__ == "__main__":
    main()
