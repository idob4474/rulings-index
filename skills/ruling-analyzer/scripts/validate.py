#!/usr/bin/env python3
"""Check a ruling card (JSON) against the full text of the ruling before it is shown.

  python3 validate.py card.json fulltext.txt
  python3 validate.py card.json fulltext.txt --fix   # first fix mechanical slips in card.json, then check
  python3 validate.py card.json                       # schema and writing rules only, no text checks

Prints one line per problem. ERROR lines must be fixed, WARN lines are for review.
Exit code 0 when there are no errors, 1 when there are, 2 on bad input.

--fix rewrites card.json for slips that have one right answer and prints a FIXED line for each.
ASCII quote marks become ״ (׳ inside the quote), a geresh after a Hebrew letter becomes ׳, a dash
between numbers becomes a hyphen, a spaced long dash or a semicolon becomes a comma, a copied
prep marker ⟦...⟧ becomes a pin [[...]], and doubled spaces are collapsed. Colons and anything
that needs rewording are left as errors.

What it checks
  schema       the card schema of ספריית ההלכות
  writing      no " : ; — – anywhere except source URLs, balanced ==, ** and [[ ]]
  keys         three distinct holding indexes
  pins         every [[pin]] points to an opinion that exists and to paragraphs that exist in it
  quote        the quote appears word for word in the text, in the opinion it is attributed to
  facts        docket, date and judges in the card appear in the text, every opinion has a justice entry
Standard library only.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

FORBIDDEN = re.compile(r'[":;—–]')
PIN = re.compile(r"\[\[(.+?)\]\]")
NUM_LINE = re.compile(r"(?m)^[ \t\u00a0\u200e\u200f]*(\d{1,3})[ \t\u00a0]*\.(?:[ \t\u00a0]+\S|[ \t\u00a0]*$)")  # "5. text" or "5." alone on its line
TITLE = (r"(?:כב(?:וד|['׳])\s+)?(?:ה?שופט(?:ת)?|ה?נשיא(?:ה)?|המי?שנה[\s\-]+לנשיא(?:ה)?|סגנ?(?:ית)?[\s\-]+ה?נשיא(?:ה)?"
         r"|ממלא(?:ת)?\s+מקום\s+ה?נשיא(?:ה)?)")
# a header line, like השופט י' עמית: or המשנה לנשיא (בדימ') א' ריבלין:  A parenthesis with digits is a citation, not a title
HEADER = re.compile(r"^\s*" + TITLE + r"\s*(?:\([^)\d]{1,20}\)\s*)?([^:\n()\d]{2,40}?)\s*(?:\([^)\d]{1,20}\)\s*)?:\s*$")
TITLE_START = re.compile(r"^\s*" + TITLE + r"(?:\s|$)")
LETTER_LINE = re.compile(r"^[ \t\u00a0\u200e\u200f]*([א-ת]{1,3})[׳']?[ \t\u00a0]*\.(?:[ \t\u00a0]+\S|[ \t\u00a0]*$)")  # "כה." paragraphs
PARA_WORD = r"(?:פס(?:קה|קאות|['׳])|פסקאות)"
PIN_PARA = re.compile(r"^(?:" + TITLE + r"\s+)?(.*?)[\s,]*" + PARA_WORD + r"\s*([\dא-ת].*)$")
PIN_OPINION = re.compile(r"^(?:(?:סוף|תחילת|ראש)\s+)?חוו(?:ת|ות)\s+(?:ה?דעת|דעתו|דעתה)\s+(?:של\s+)?(?:" + TITLE + r"\s+)?(.+)$")
PIN_PAGE = re.compile(r"(?:^|\s)עמ['׳]\s*\d")
QUOTES = "\"'`״׳“”„‘’‚«»"
DOCKET = re.compile(r"(\d{1,6})\s*/\s*(\d{2,4})|(\d{3,6})-(\d{2})-(\d{2})")
INITIAL = re.compile(r"^[א-ת][׳']$|^[א-ת]$")

errors, warns, notes = [], [], []
BODY_WORDS = []  # the normalized words of the ruling, for names whose opinion header was not found
PANEL = []  # name tokens of the judges listed at the top of the ruling (כבוד השופט ...)


def err(path, msg):
    errors.append(f"ERROR {path} {msg}")


def warn(path, msg):
    warns.append(f"WARN {path} {msg}")


# ---------- helpers ----------

def norm(s):
    """Text for comparison: no niqqud or quote marks, punctuation as spaces, single spaces."""
    s = unicodedata.normalize("NFC", str(s)).replace("־", " ")
    s = re.sub(r"[֑-ׇ]", "", s)
    s = re.sub("[" + re.escape(QUOTES) + "]", "", s)
    s = re.sub(r"[‎‏‪-‮﻿]", "", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def name_tokens(s):
    toks = [t for t in norm(re.sub(r"\([^)]*\)", " ", s)).split() if not INITIAL.match(t)]
    return [t for t in toks if t not in {"השופט", "השופטת", "הנשיא", "הנשיאה", "המשנה", "לנשיא", "לנשיאה", "כבוד", "כב"}]


def contains_seq(hay, needle):
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def walk(v, path=()):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, path + (i,))
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from walk(x, path + (k,))


def p(path):
    return ".".join(str(x) for x in path) or "card"


def compress(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out) or "none"


# ---------- schema ----------

def is_str(v):
    return isinstance(v, str) and v.strip() != ""


def need_str(c, key, pinned=False, path=None):
    path = path or key
    v = c.get(key) if isinstance(c, dict) else None
    if not is_str(v):
        err(path, "is required and must be a non-empty string")
        return False
    if pinned and not PIN.search(v):
        err(path, "has no pin [[...]]")
    return True


def need_list(c, key, lo=0, path=None):
    path = path or key
    v = c.get(key)
    if not isinstance(v, list):
        err(path, "is required and must be a list")
        return []
    if len(v) < lo:
        err(path, f"needs at least {lo} items, has {len(v)}")
    return v


def check_schema(c):
    if not isinstance(c.get("course"), str) or not re.fullmatch(r"[a-z0-9_-]+", c.get("course") or ""):
        err("course", "must be a course id like torts or corp (use other when there is no course)")
    for k in ("docket", "name", "short", "eyebrow", "aka", "cite", "status", "decision"):
        need_str(c, k)
    if is_str(c.get("docket")) and not DOCKET.search(c["docket"]):
        warn("docket", "has no case number like ע״א 8489/12 or ת״א 58416-04-19, the text check cannot confirm it")
    one = c.get("oneLine")
    if need_str(c, "oneLine") and not (re.match(r"^==[^=][\s\S]*?==", one) and PIN.search(one)):
        err("oneLine", "must open with the holding wrapped in ==...== and carry a pin")
    for i, m in enumerate(need_list(c, "meta", 1)):
        if not (isinstance(m, list) and len(m) == 2 and all(is_str(x) for x in m)):
            err(f"meta.{i}", "must be [label, value]")
    for i, b in enumerate(need_list(c, "background", 1)):
        if not is_str(b):
            err(f"background.{i}", "must be a non-empty string")
        elif not PIN.search(b):
            err(f"background.{i}", "has no pin [[...]]")
    for i, q in enumerate(need_list(c, "questions", 1)):
        if not is_str(q):
            err(f"questions.{i}", "must be a non-empty string")
    hs = need_list(c, "holdings", 3)
    for i, h in enumerate(hs):
        if not (isinstance(h, list) and len(h) == 2 and all(is_str(x) for x in h)):
            err(f"holdings.{i}", "must be [title, text]")
        elif not PIN.search(h[1]):
            err(f"holdings.{i}.1", "has no pin [[...]]")
    cl = c.get("clause")
    if cl is not None:
        if not isinstance(cl, dict) or not is_str(cl.get("label")) or not isinstance(cl.get("items"), list) or not cl["items"]:
            err("clause", "must be {label, items[, after]} with at least one item")
    for i, j in enumerate(need_list(c, "justices")):
        if not isinstance(j, dict):
            err(f"justices.{i}", "must be {name, tag, theory, text[, solo]}")
            continue
        for k in ("name", "tag", "theory"):
            need_str(j, k, path=f"justices.{i}.{k}")
        need_str(j, "text", pinned=True, path=f"justices.{i}.text")
    q = c.get("quote")
    if q is not None and (not isinstance(q, dict) or not is_str(q.get("text")) or not is_str(q.get("src"))):
        err("quote", "must be {text, src[, label]}")
    ex = c.get("exam")
    if not isinstance(ex, dict):
        err("exam", "is required")
    else:
        need_str(ex, "pathLabel", path="exam.pathLabel")
        need_str(ex, "write", pinned=True, path="exam.write")
        path = ex.get("path")
        if not isinstance(path, list) or not path or not all(is_str(x) for x in path):
            err("exam.path", "must be a non-empty list of steps")
            path = []
        h = ex.get("here")
        if not isinstance(h, int) or isinstance(h, bool) or not 0 <= h < len(path):
            err("exam.here", f"must be an index into exam.path (0 to {max(len(path) - 1, 0)})")
        if not isinstance(ex.get("traps", []), list):
            err("exam.traps", "must be a list")
    for i, r in enumerate(need_list(c, "related")):
        if not (isinstance(r, list) and len(r) in (3, 4) and all(is_str(x) for x in r[:3])):
            err(f"related.{i}", "must be [name, keyword, text] and the text should open with the docket, like ע״א 243/83.")
    for i, pr in enumerate(need_list(c, "practice")):
        if not (isinstance(pr, dict) and is_str(pr.get("q")) and isinstance(pr.get("a"), list) and pr["a"]):
            err(f"practice.{i}", "must be {q, a[]} with at least one answer point")
    for i, s in enumerate(need_list(c, "sources", 1)):
        if isinstance(s, list):
            if not (len(s) == 2 and is_str(s[0]) and re.match(r"^https?://\S+$", s[1] or "")):
                err(f"sources.{i}", "must be text or [text, url]")
        elif not is_str(s):
            err(f"sources.{i}", "must be text or [text, url]")

    keys = c.get("keys")
    n = len(hs)
    if not (isinstance(keys, list) and len(keys) == 3 and all(isinstance(k, int) and not isinstance(k, bool) for k in keys)):
        err("keys", "must be 3 holding indexes, like [0, 3, 5]")
    else:
        if len(set(keys)) != 3:
            err("keys", "must be distinct")
        for i, k in enumerate(keys):
            if not 0 <= k < n:
                err(f"keys.{i}", f"{k} is not a holding index (0 to {n - 1})")

    for path, s in walk(c):
        is_url = len(path) == 3 and path[0] == "sources" and path[2] == 1
        if not is_url:
            m = FORBIDDEN.search(s)
            if m:
                ch = m.group(0)
                hint = " (use ״ or ׳ for Hebrew abbreviations and inner quotes)" if ch == '"' else ""
                err(p(path), f"forbidden character {ch!r} in ...{s[max(0, m.start() - 15):m.start() + 15]}...{hint}")
        if "⟦" in s or "⟧" in s:
            err(p(path), "has a prep marker ⟦...⟧. Write the pin as [[...]] (--fix does it)")
        if s.count("==") % 2:
            err(p(path), "has an unbalanced ==")
        if s.count("**") % 2:
            err(p(path), "has an unbalanced **")
        if s.count("[[") != s.count("]]"):
            err(p(path), "has an unbalanced [[ ]]")

    # recommended counts
    def rng(name, v, lo, hi):
        if isinstance(v, list) and not lo <= len(v) <= hi:
            warn(name, f"has {len(v)} items, expected {lo} to {hi}")
    rng("background", c.get("background"), 3, 5)
    rng("questions", c.get("questions"), 2, 4)
    rng("holdings", hs, 5, 9)
    rng("practice", c.get("practice"), 2, 3)
    for i, h in enumerate(hs):
        if isinstance(h, list) and h and is_str(h[0]):
            w = len(h[0].split())
            if not 2 <= w <= 4:
                warn(f"holdings.{i}.0", f"title has {w} words, expected 2 to 4")


# ---------- full text ----------

GEM = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400]))
FINAL = str.maketrans("ךםןףץ", "כמנפצ")


def gematria(s):
    return sum(GEM.get(ch, 0) for ch in s.translate(FINAL))


def heb_label(n):
    """25 -> כה, 15 -> טו, 16 -> טז."""
    out, rest = "", n
    for v, ch in ((400, "ת"), (300, "ש"), (200, "ר"), (100, "ק")):
        while rest >= v:
            out, rest = out + ch, rest - v
    if rest in (15, 16):
        return out + {15: "טו", 16: "טז"}[rest]
    for v, ch in ((90, "צ"), (80, "פ"), (70, "ע"), (60, "ס"), (50, "נ"), (40, "מ"), (30, "ל"), (20, "כ"), (10, "י")):
        if rest >= v:
            out, rest = out + ch, rest - v
            break
    return out + ("אבגדהוזחט"[rest - 1] if rest else "")


def label_value(tok):
    """'25' -> 25, 'כה' or 'כ״ה' -> 25, anything else -> None."""
    t = re.sub(r"[׳'\"״]", "", tok)
    if t.isdigit():
        return int(t)
    if re.fullmatch(r"[א-ת]{1,3}", t) and heb_label(gematria(t)) == t.translate(FINAL):
        return gematria(t)
    return None


def heb_plain(s):
    """A line for header matching, without niqqud and with maqaf as a hyphen."""
    return re.sub(r"[\u0591-\u05bd\u05bf-\u05c7]", "", s.replace("\u05be", "-"))


def join_broken(lines, i, end, stop):
    """Join line i with the short pieces after it, as Word exports break a name over lines
    (ס / ' / ג / ' / ובראן). A piece glues to the previous one when it follows it directly and
    has no leading space, otherwise a space goes between. Returns (joined text, next line)."""
    joined, j, pieces, gap = heb_plain(lines[i]).strip(), i + 1, 0, False
    while j < end and j <= i + 10 and pieces < 6:
        raw = heb_plain(lines[j])
        piece = raw.strip()
        if piece and stop(piece):
            break
        j += 1
        if not piece:
            gap = True
            continue
        glue = not gap and not raw[:1].isspace() or piece[0] in "'׳)"
        joined += piece if glue else " " + piece
        pieces, gap = pieces + 1, False
        if piece.endswith(":"):
            break
    return joined, j


def find_headers(lines, start=0):
    """[(line index, label)] of opinion headers. A header broken over a few short lines
    (הנשיא א / ' / גרוניס:) is joined. Panel lines that open with כבוד are never joined."""
    out, i, n = [], start, len(lines)
    while i < n:
        line = heb_plain(lines[i])
        h = HEADER.match(line)
        if h and len(line.strip()) <= 60:
            out.append((i, h.group(1).strip()))
            i += 1
            continue
        st = line.strip()
        if (TITLE_START.match(line) and len(st) <= 40 and not st.endswith(":") and not st.startswith("כב")
                and not re.search(r"[.,;!?]", st)):
            joined, j = join_broken(lines, i, n, lambda x: len(x) > 30 or bool(HEADER.match(x)))
            h = HEADER.match(joined)
            if h and len(joined) <= 60:
                out.append((i, h.group(1).strip()))
                i = j
                continue
        i += 1
    return out


def find_panel(lines, start, end):
    """Name tokens of the panel, from the lines that open with כבוד before the first opinion.
    Broken lines (כבוד הנשיא א / ' / גרוניס) are joined."""
    panel, i = [], start
    while i < end:
        st = heb_plain(lines[i]).strip()
        if re.match(r"^כב(?:וד|['׳])\s+" + TITLE, st):
            joined, j = join_broken(lines, i, end, lambda x: x.startswith("כב") or len(x) > 30 or ":" in x)
            toks = name_tokens(re.sub(r"^כב(?:וד|['׳])\s+" + TITLE, "", joined))
            if toks:
                panel.append(toks)
            i = j
            continue
        i += 1
    return panel


def sequence(nums):
    """Split numbered lines [(line, value)] into sure paragraphs and the rest.

    The paragraphs are the longest run 1, 2, 3 ... in line order. A number is sure when every
    longest run puts it on the same line. A list inside a quote or numbering that starts over
    gives a number two possible lines, and then it is left unmarked.
    """
    if not nums:
        return [], []
    occ = {}
    for i, v in nums:
        occ.setdefault(v, []).append(i)
    v0 = 1 if 1 in occ else min(occ)
    fwd = {v0: list(occ[v0])}
    v = v0
    while v + 1 in occ:
        prev = min(fwd[v])
        nxt = [i for i in occ[v + 1] if i > prev]
        if not nxt:
            break
        fwd[v + 1] = nxt
        v += 1
    top = v
    feas = {top: fwd[top]}
    for v in range(top - 1, v0 - 1, -1):
        last = max(feas[v + 1])
        feas[v] = [i for i in fwd[v] if i < last]
    good = [(feas[v][0], v) for v in range(v0, top + 1) if len(feas[v]) == 1]
    taken = {i for i, _ in good}
    return good, sorted((i, v) for i, v in nums if i not in taken)


def numbered(lines, a0, a1):
    """Numbered paragraph lines of one opinion, [(line, value, label)], and their kind.
    Digits (5.) or Hebrew letters (כה.), whichever gives the longer run."""
    digits, letters = [], []
    for i in range(a0, a1 + 1):
        m = NUM_LINE.match(lines[i])
        if m:
            digits.append((i, int(m.group(1)), m.group(1)))
            continue
        m = LETTER_LINE.match(lines[i])
        if m and label_value(m.group(1)) is not None:
            letters.append((i, label_value(m.group(1)), m.group(1)))
    run_d = len(sequence([(i, v) for i, v, _ in digits])[0])
    run_l = len(sequence([(i, v) for i, v, _ in letters])[0])
    return (letters, "letters") if run_l > run_d and run_l >= 3 else (digits, "digits")


def compress_kind(nums, kind):
    s = compress(nums)
    return re.sub(r"\d+", lambda m: heb_label(int(m.group(0))), s) if kind == "letters" and nums else s


class Opinion:
    def __init__(self, label, start):
        self.label = label
        self.tokens = name_tokens(label)
        self.start = start
        self.end = None
        self.paras = []  # (value, offset)
        self.kind = "digits"


def parse_text(raw):
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # header written by rulings-index lookup.py
    m = re.match(r"\ufeff?מקור.*?\n={20,}\n", text, re.S)
    body_start = m.end() if m else 0
    lines = text.split("\n")
    offs, pos = [], 0
    for line in lines:
        offs.append(pos)
        pos += len(line) + 1
    heads = find_headers(lines, text[:body_start].count("\n"))
    ops = []
    for k, (i, label) in enumerate(heads):
        last = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(lines) - 1
        o = Opinion(label, offs[i])
        o.end = offs[last] + len(lines[last])
        items, o.kind = numbered(lines, i, last)
        o.paras = [(v, offs[j]) for j, v, _ in items]
        ops.append(o)
    # merge repeated headers of the same judge
    merged = {}
    for o in ops:
        key = " ".join(o.tokens)
        if key in merged:
            merged[key].paras += o.paras
            merged[key].spans.append((o.start, o.end))
        else:
            o.spans = [(o.start, o.end)]
            merged[key] = o
    return text, body_start, list(merged.values())


def find_judge(ops, name):
    toks = name_tokens(name)
    hits = [o for o in ops if contains_seq(o.tokens, toks)]
    return hits[0] if len(hits) == 1 else (None if not hits else hits)


def para_numbers(spec):
    """'5-6' -> [5, 6], '5, 8' -> [5, 8], '5 ו-7' -> [5, 7], 'כה-כז' -> [25, 26, 27].
    None when the spec is not a clean list."""
    spec = spec.strip().rstrip(".")
    parts = re.split(r"\s*,\s*|\s+ו-?\s*|\s+", spec)
    out = []
    for part in filter(None, parts):
        ends = [label_value(x) for x in re.split(r"\s*-\s*", part)]
        if not 1 <= len(ends) <= 2 or None in ends:
            return None
        a, b = min(ends), max(ends)
        if b - a > 30:
            return None
        out += range(a, b + 1)
    return out or None


def unseen_judge(where, who, ops):
    """A judge with no detected opinion header. With a known panel, an error unless the judge sat on it.
    Without one, an error only when the name is nowhere in the text."""
    toks = name_tokens(who)
    if PANEL:
        if any(contains_seq(t, toks) for t in PANEL):
            warn(where, f"the opinion header of {who} was not detected, so this pin was not checked. Check it by hand. Opinions found {judges_list(ops)}")
        else:
            err(where, f"{who} is not on the panel of this ruling. Panel {', '.join(' '.join(t) for t in PANEL)}")
        return
    if contains_seq(BODY_WORDS, toks):
        warn(where, f"the opinion header of {who} was not detected, so this pin was not checked. Check it by hand. Opinions found {judges_list(ops)}")
    else:
        err(where, f"no opinion of {who} in the text. Opinions found {judges_list(ops)}")


def check_pins(c, ops):
    count = 0
    for path, s in walk(c):
        for pin in PIN.findall(s):
            count += 1
            where = f"{p(path)} [[{pin}]]"
            if PIN_PAGE.search(pin):
                warn(where, "page reference, not checked automatically. Check it against the text by hand")
                continue
            mo = PIN_OPINION.match(pin)
            mp = PIN_PARA.match(pin)
            if mo:
                if not ops:
                    warn(where, "no judge headers were found in the text, opinion pin not checked")
                    continue
                j = find_judge(ops, mo.group(1))
                if j is None:
                    unseen_judge(where, mo.group(1), ops)
                elif isinstance(j, list):
                    warn(where, f"{mo.group(1)} matches more than one opinion")
                continue
            if mp:
                who, nums = mp.group(1).strip(" ,"), para_numbers(mp.group(2))
                if nums is None:
                    warn(where, "paragraph numbers could not be read, use a form like פס׳ 5 or פס׳ 5-6")
                    continue
                if not ops:
                    continue  # checked against the whole text below
                if not who:
                    if len(ops) > 1:
                        warn(where, "no judge name in a ruling with several opinions, write the name before פס׳")
                    pool = sorted({n for o in ops for n, _ in o.paras})
                    missing = [n for n in nums if n not in pool]
                    if missing:
                        err(where, f"paragraph {compress(missing)} not found in any opinion")
                    continue
                j = find_judge(ops, who)
                if j is None:
                    unseen_judge(where, who, ops)
                    continue
                if isinstance(j, list):
                    warn(where, f"{who} matches more than one opinion")
                    continue
                have = {n for n, _ in j.paras}
                if not have:
                    err(where, f"the opinion of {who} has no numbered paragraphs, cite it as חוות דעת {who}")
                    continue
                missing = [n for n in nums if n not in have]
                if missing:
                    err(where, f"paragraph {compress_kind(missing, j.kind)} not found in the opinion of {who} (paragraphs {compress_kind(have, j.kind)})")
                continue
            warn(where, "unknown pin format, not checked. Use שם פס׳ N, חוות דעת שם or עמ׳ N")
    return count


def check_pins_without_headers(c, text, start):
    have = {int(n) for n in NUM_LINE.findall(text[start:])}
    for path, s in walk(c):
        for pin in PIN.findall(s):
            mp = PIN_PARA.match(pin)
            if mp and not PIN_PAGE.search(pin) and not PIN_OPINION.match(pin):
                nums = para_numbers(mp.group(2))
                if nums:
                    missing = [n for n in nums if n not in have]
                    if missing:
                        err(f"{p(path)} [[{pin}]]", f"paragraph {compress(missing)} not found in the text (paragraphs {compress(have)})")


def judges_list(ops):
    return ", ".join(" ".join(o.tokens) for o in ops) or "none"


def norm_with_map(text):
    """norm() over the whole text, plus a map from each normalized char back to the original offset."""
    out, idx = [], []
    prev_space = True
    for i, ch in enumerate(unicodedata.normalize("NFC", text)):
        if ch == "־":
            ch = " "
        if "֑" <= ch <= "ׇ" or ch in QUOTES or ch in "‎‏﻿" or "‪" <= ch <= "‮":
            continue
        if not (ch.isalnum() or ch == "_"):
            ch = " "
        if ch == " ":
            if prev_space:
                continue
            prev_space = True
        else:
            prev_space = False
        out.append(ch)
        idx.append(i)
    return "".join(out), idx


def check_quote(c, text, ops):
    q = c.get("quote")
    if not isinstance(q, dict) or not is_str(q.get("text")):
        return
    ntext, idx = norm_with_map(text)
    chunks = [norm(x) for x in re.split(r"\.\.\.|…", q["text"])]
    chunks = [x for x in chunks if x]
    pos, first = 0, None
    for ch in chunks:
        k = ntext.find(ch, pos)
        if k < 0:
            # find where it breaks, to point at the word that differs
            words, good = ch.split(), 0
            for n in range(1, len(words) + 1):
                if ntext.find(" ".join(words[:n]), pos) >= 0:
                    good = n
                else:
                    break
            hint = " ".join(words[max(0, good - 3):good + 3])
            err("quote.text", f"not found word for word in the text. It breaks around ...{hint}... Copy it again from the text")
            return
        first = k if first is None else first
        pos = k + len(ch)
    if not ops or first is None:
        return
    off = idx[first]
    owner = next((o for o in ops for a, b in o.spans if a <= off < b), None)
    src = q.get("src") or ""
    named = [o for o in ops if contains_seq(name_tokens(src), o.tokens[-1:])]
    if owner is None:
        warn("quote", "the quote is in the text but before the first opinion (summary or headnote?)")
        return
    if named and owner not in named:
        err("quote.src", f"the quote is in the opinion of {' '.join(owner.tokens)}, not {' '.join(named[0].tokens)}")
        return
    m = re.search(PARA_WORD + r"\s*(\d{1,3})", src)
    if m and owner.paras:
        before = [n for n, at in owner.paras if at <= off]
        if before and before[-1] != int(m.group(1)):
            warn("quote.src", f"the quote seems to be in paragraph {before[-1]} of {' '.join(owner.tokens)}, not {m.group(1)}")


def check_facts(c, text, start, ops):
    body = text[start:]
    flat = norm(body)
    d = DOCKET.search(c.get("docket") or "")
    if d:
        if d.group(1):
            pat = rf"(?<!\d){d.group(1)}\s*[/-]\s*{d.group(2)}(?!\d)"
        else:
            pat = rf"(?<!\d){d.group(3)}\s*-\s*{d.group(4)}\s*-\s*{d.group(5)}(?!\d)"
        if not re.search(pat, body):
            err("docket", f"{d.group(0)} does not appear in the text. Is this the right file?")
    for k, v in c.get("meta") or []:
        if not is_str(v):
            continue
        if k.strip() == "ניתן":
            m = re.fullmatch(r"\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})\s*", v)
            if m:
                dd, mm, yy = (int(x) for x in m.groups())
                pat = rf"(?<!\d)0?{dd}\.0?{mm}\.(?:{yy}|{yy % 100:02d}|20{yy % 100:02d})(?!\d)"
                if not re.search(pat, body):
                    warn(f"meta.{k}", f"the date {v} does not appear in the text")
        if k.strip() in ("הרכב", "שופטים"):
            for nm in re.split(r",|\sו(?=[א-ת])", re.sub(r"\([^)]*\)", "", v)):
                toks = name_tokens(nm)
                if toks and not contains_seq(flat.split(), toks):
                    warn(f"meta.{k}", f"{' '.join(toks)} does not appear in the text")
    js = [j for j in c.get("justices") or [] if isinstance(j, dict) and is_str(j.get("name"))]
    for i, j in enumerate(js):
        if ops:
            if find_judge(ops, j["name"]) is None:
                unseen_judge(f"justices.{i}.name", j["name"], ops)
        elif not contains_seq(flat.split(), name_tokens(j["name"])):
            warn(f"justices.{i}.name", f"{j['name']} does not appear in the text")
    for o in ops:
        if js and not any(contains_seq(o.tokens, name_tokens(j["name"])) for j in js):
            warn("justices", f"the text has an opinion of {' '.join(o.tokens)} but the card has no entry for it")


# ---------- --fix ----------

HEB_L = "א-ת"


def fix_text(s, in_quote=False):
    t = re.sub(r"\[\[\s*⟦([^⟧]+)⟧\s*\]\]", r"[[\1]]", s)
    t = re.sub(r"⟦([^⟧]+)⟧", r"[[\1]]", t)
    t = re.sub(rf'(?<=[{HEB_L}])"(?=[{HEB_L}])', "״", t)
    t = t.replace('"', "׳" if in_quote else "״")
    t = re.sub(rf"(?<=[{HEB_L}])'", "׳", t)
    t = re.sub(r"(?<=\d)\s*[–—]\s*(?=\d)", "-", t)
    t = re.sub(r"\s+[–—]\s+", ", ", t)
    t = re.sub(r"\s*;\s*", ", ", t)
    t = re.sub(r",\s*$", ".", t)
    t = re.sub(r"[ \t]{2,}", " ", t).strip()
    return t


def fix_card(c):
    fixed = []

    def go(v, path):
        if isinstance(v, str):
            is_url = len(path) == 3 and path[0] == "sources" and path[2] == 1
            if is_url:
                return v
            in_quote = path[:2] == ("quote", "text")
            if in_quote and v[:1] == '"' and v[-1:] == '"':
                v = "״" + v[1:-1] + "״"
            new = fix_text(v, in_quote)
            if new != v:
                i = next((k for k in range(min(len(v), len(new))) if v[k] != new[k]), min(len(v), len(new)))
                fixed.append(f"FIXED {p(path)} ...{v[max(0, i - 12):i + 12]}... -> ...{new[max(0, i - 12):i + 12]}...")
            return new
        if isinstance(v, list):
            return [go(x, path + (i,)) for i, x in enumerate(v)]
        if isinstance(v, dict):
            return {k: go(x, path + (k,)) for k, x in v.items()}
        return v

    return go(c, ()), fixed


def main():
    args = [a for a in sys.argv[1:] if a != "--fix"]
    do_fix = "--fix" in sys.argv[1:]
    if len(args) not in (1, 2):
        print(__doc__)
        sys.exit(2)
    sys.argv = [sys.argv[0]] + args
    try:
        card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR card {sys.argv[1]} is not valid JSON. {e}")
        sys.exit(2)
    if not isinstance(card, dict):
        print("ERROR card must be a JSON object")
        sys.exit(2)
    if do_fix:
        card, fixed = fix_card(card)
        if fixed:
            Path(sys.argv[1]).write_text(json.dumps(card, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        notes.extend(fixed)
    check_schema(card)
    pins = sum(len(PIN.findall(s)) for _, s in walk(card))
    if len(sys.argv) == 3:
        raw = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
        text, start, ops = parse_text(raw)
        BODY_WORDS[:] = norm(text[start:]).split()
        lines = text.split("\n")
        first = text[:ops[0].start].count("\n") if ops else len(lines)
        PANEL[:] = find_panel(lines, text[:start].count("\n"), first)
        if PANEL:
            notes.append("PANEL " + ", ".join(" ".join(t) for t in PANEL))
        if len(text) - start < 2000:
            warn("text", f"only {len(text) - start} characters. Is this the full text?")
        if ops:
            notes.append("OPINIONS " + " | ".join(f"{' '.join(o.tokens)} (paragraphs {compress_kind([n for n, _ in o.paras], o.kind)})" for o in ops))
        else:
            warn("text", "no judge headers like השופט י׳ עמית: were found, pins are checked against the whole text")
        check_facts(card, text, start, ops)
        check_pins(card, ops)
        if not ops:
            check_pins_without_headers(card, text, start)
        check_quote(card, text, ops)
    else:
        warn("text", "no full text given, pins and quote were not checked")
    for line in notes + errors + warns:
        print(line)
    print(f"RESULT {len(errors)} errors, {len(warns)} warnings, {pins} pins")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
