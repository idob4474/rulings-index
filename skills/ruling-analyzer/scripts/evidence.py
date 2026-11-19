#!/usr/bin/env python3
"""Check that every claim in the card is found in the paragraph its pin points to.

  python3 evidence.py card.json ruling.txt                         # report, writes evidence.md
  python3 evidence.py card.json ruling.txt --verdicts skeptic.json # also enforce the skeptic's verdicts

validate.py checks that a pinned paragraph exists. This checks that it says what the card says.
Each card text is cut into claims, the text before each group of pins. Each pin is resolved to
its span in the ruling, and the claim's content words are looked up there, with Hebrew prefixes
and suffixes allowed (ו, ה, ב, ל, מ, ש, כ, ים, ות and so on). A claim with little in common with
its paragraph is LOW, and when another paragraph of the same judge fits much better it is named.

The overlap is a heuristic, so its lines are warnings. evidence.md holds every claim beside the
best matching excerpt of its paragraph, and it is the input of the skeptic review
(references/skeptic.md). With --verdicts, a claim the skeptic flagged must have been changed or
carry a written resolution, or it is an error.

Exit code 1 only with --verdicts and an unresolved flag. Standard library only.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import (PIN, PIN_OPINION, PIN_PAGE, PIN_PARA, PANEL, find_judge, find_panel,  # noqa: E402
                      heb_label, norm, p, para_numbers, parse_text, sequence, walk)

PREFIX = set("והבלמשכ")
SUFFIXES = ("יות", "ים", "ות", "יה", "ה", "ת", "ו", "י", "ם", "ן")
STOP = set("""
של את על אל עם כי אם לא גם או אך אבל זה זו זאת הוא היא הם הן יש אין כל כך לכן רק עוד בין לפי אשר מה מי כמו
היה היתה היו יהיה להיות אחר אחרת אחד אחת שני שתי עד מן כדי כאשר שלא אינו אינה אינם לו לה להם בו בה בהם
אותו אותה אותם עצמו עצמה ולא וגם או יותר פחות מאוד גם הזה הזו הזאת האלה אלה אלו שם כאן עליו עליה עליהם
בית משפט המשפט דין פסק פס השופט השופטת שופט שופטת חוות דעת דעתו דעתה קבע קבעה נקבע הלכה הכרטיס סעיף
""".split())
SHORT = 40          # pinned text with fewer content words (an opinion that only agrees) is not scored as LOW
LOW = 0.34          # below this share of content words found in the best window, the claim is LOW
MIN_WORDS = 4       # shorter claims are not scored
WINDOW = 800        # characters in a window of the ruling, the unit a claim is scored against
STEP = 200


def variants(w):
    """Forms of a Hebrew word for loose matching. ובית -> בית, המשפט -> משפט, הכרעות -> הכרע."""
    out = {w}
    if len(w) >= 4 and w[0] in PREFIX:
        out.add(w[1:])
        if len(w) >= 5 and w[1] in PREFIX:
            out.add(w[2:])
    for v in list(out):
        for s in SUFFIXES:
            if v.endswith(s) and len(v) - len(s) >= 3:
                out.add(v[: -len(s)])
                break
    return out


def words(text):
    return [w for w in norm(text).split() if len(w) >= 2 and not w.isdigit() or len(w) >= 3]


NAMES = set()  # surnames of the judges of the ruling, not content words in a claim


def content(text):
    out = []
    for w in words(text):
        if w in STOP or variants(w) & STOP:
            continue
        if variants(w) & NAMES:
            continue
        out.append(w)
    return out


def vocab(text):
    v = set()
    for w in words(text):
        v |= variants(w)
    return v


def coverage(claim_words, vocab_set):
    if not claim_words:
        return 1.0, []
    hit = [w for w in claim_words if variants(w) & vocab_set]
    return len(hit) / len(claim_words), hit


def claim_id(path, text, pins):
    h = hashlib.sha1(f"{p(path)}|{norm(text)}|{'|'.join(pins)}".encode("utf-8")).hexdigest()
    return h[:6]


def claims_of(card):
    """[(id, path, claim text, [pins])]. A claim is the text before a run of pins."""
    out = []
    for path, s in walk(card):
        if path and path[0] in ("quote", "sources", "keys"):
            continue
        pos, i = 0, 0
        ms = list(PIN.finditer(s))
        while i < len(ms):
            j = i
            while j + 1 < len(ms) and not s[ms[j].end():ms[j + 1].start()].strip():
                j += 1
            text = re.sub(r"==|\*\*", "", s[pos:ms[i].start()]).strip(" .,")
            pins = [m.group(1) for m in ms[i:j + 1]]
            if text:
                out.append((claim_id(path, text, pins), path, text, pins))
            pos, i = ms[j].end(), j + 1
    return out


class Ruling:
    def __init__(self, raw):
        self.text, self.start, self.ops = parse_text(raw)
        lines = self.text.split("\n")
        first = self.text[:self.ops[0].start].count("\n") if self.ops else len(lines)
        for t in [list(o.tokens) for o in self.ops] + find_panel(lines, self.text[:self.start].count("\n"), first):
            for w in t:
                NAMES.update(variants(w))
        self.spans = {}  # (opinion key, value) -> [(a, b)]
        self.sure = {}   # opinion key -> values in the running sequence 1, 2, 3 ...
        self._win = {}
        for o in self.ops:
            key = " ".join(o.tokens)
            good, _ = sequence([(off, v) for v, off in o.paras])
            self.sure[key] = sorted({v for _, v in good})
            cuts = sorted({off for off, _ in good} | {b for _, b in o.spans} | {a for a, _ in o.spans})
            top = max(b for _, b in o.spans)
            for v, off in o.paras:
                end = min([c for c in cuts if c > off] + [top])
                self.spans.setdefault((key, v), []).append((off, end))

    def windows(self, a, b):
        """Vocabularies of the windows of WINDOW characters that cover the span."""
        if (a, b) not in self._win:
            starts = list(range(a, max(a + 1, b - WINDOW + STEP), STEP))
            self._win[(a, b)] = [(s, vocab(self.text[s:min(b, s + WINDOW)])) for s in starts]
        return self._win[(a, b)]

    def score(self, spans, claim_words):
        """Share of the claim's words found in the best window of the spans, and that window.
        A claim pinned to several paragraphs (5-6, or two pins) may sum them up, so it also gets
        the union of the best window of each paragraph."""
        best, union = (-1.0, None), set()
        for a, b in spans:
            mine = (-1.0, set())
            for s, v in self.windows(a, b):
                sc, _ = coverage(claim_words, v)
                if sc > best[0]:
                    best = (sc, (s, min(b, s + WINDOW), a, b))
                if sc > mine[0]:
                    mine = (sc, v)
            union |= mine[1]
        if len(spans) > 1:
            sc, _ = coverage(claim_words, union)
            if sc > best[0]:
                best = (sc, best[1])
        return best

    def numbers_missing(self, spans, text):
        """Numbers in the claim (sums, percentages, dates, sections) that the pinned text does not have."""
        nums = {n.rstrip(".").replace(",", "") for n in re.findall(r"\d[\d,.]*\d|\d", text)}
        if not nums:
            return []
        hay = " ".join(self.text[a:b] for a, b in spans).replace(",", "")

        def found(n):
            if re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", hay):
                return True
            d = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", n)
            if not d:
                return False
            # the card writes 19.3.1995, a ruling often writes 19.3.95, 19.03.1995 or 19/3/95
            dd, mm, yy = (int(x) for x in d.groups())
            date = rf"(?<![\d./])0?{dd}[./]0?{mm}[./](?:{yy}|{yy % 100:02d})(?!\d)"
            return bool(re.search(date, hay))
        return sorted(n for n in nums if len(n) >= 2 and not found(n))

    def opinion_spans(self, o, tail=False):
        if tail:
            a, b = o.spans[-1]
            return [(max(a, b - 2500), b)]
        return list(o.spans)

    def resolve(self, pin):
        """[(a, b)] spans of the text the pin points to, or None when it cannot be resolved."""
        if PIN_PAGE.search(pin) or not self.ops:
            return None
        mo = PIN_OPINION.match(pin)
        if mo:
            j = find_judge(self.ops, mo.group(1))
            if not j or isinstance(j, list):
                return None
            return self.opinion_spans(j, tail=pin.strip().startswith("סוף"))
        mp = PIN_PARA.match(pin)
        if not mp:
            return None
        who, nums = mp.group(1).strip(" ,"), para_numbers(mp.group(2))
        if not nums:
            return None
        if who:
            j = find_judge(self.ops, who)
            if not j or isinstance(j, list):
                return None
            pool = [j]
        else:
            pool = self.ops
        out = []
        for o in pool:
            for n in nums:
                out += self.spans.get((" ".join(o.tokens), n), [])
        return out or None

    def judge_of(self, pin):
        mp = PIN_PARA.match(pin)
        if mp and mp.group(1).strip(" ,") and para_numbers(mp.group(2)):
            j = find_judge(self.ops, mp.group(1).strip(" ,"))
            return j if j and not isinstance(j, list) else None
        return None

    def excerpt(self, window):
        if not window:
            return ""
        s, e, a, b = window
        body = re.sub(r"\s+", " ", self.text[s:e]).strip()
        return ("..." if s > a else "") + body + ("..." if e < b else "")


def check(card, ruling):
    rows = []
    for cid, path, text, pins in claims_of(card):
        cw = content(text)
        spans, unresolved = [], []
        for pin in pins:
            got = ruling.resolve(pin)
            if got is None:
                unresolved.append(pin)
            else:
                spans += got
        row = {"id": cid, "path": p(path), "claim": text, "pins": pins, "words": len(cw), "unresolved": unresolved, "numbers": []}
        if not spans:
            row.update(score=None, excerpt="", hint=None)
            rows.append(row)
            continue
        score, window = ruling.score(spans, cw)
        # an opinion of a line or two (אני מסכים) has no words to match, so it is never LOW
        row["short"] = len(content(" ".join(ruling.text[a:b] for a, b in spans))) < SHORT
        # a related ruling's text opens with its own docket, which the citing paragraph often leaves out
        numtext = re.sub(r"^\s*[^\s.]{1,8}\s+\d{1,6}/\d{2,4}\.\s*", "", text) if path[0] == "related" else text
        row.update(score=score, excerpt=ruling.excerpt(window), hint=None, numbers=ruling.numbers_missing(spans, numtext))
        # a much better paragraph of the same judge?
        if score < LOW + 0.1 and len(cw) >= MIN_WORDS and len(pins) == 1:
            j = ruling.judge_of(pins[0])
            if j:
                key = " ".join(j.tokens)
                best = (0, None)
                for val in ruling.sure.get(key, []):
                    sc, _ = ruling.score(ruling.spans[(key, val)], cw)
                    if sc > best[0]:
                        best = (sc, val)
                if best[1] is not None and best[0] >= max(0.5, score + 0.3):
                    label = heb_label(best[1]) if j.kind == "letters" else str(best[1])
                    row["hint"] = (f"{key} פס׳ {label}", best[0])
        rows.append(row)
    return rows


def write_report(rows, path):
    out = ["# ראיות לכל טענה בכרטיס", "",
           "לכל טענה, מראה המקום שלה והקטע מהנוסח שמתאים לה הכי הרבה. זה הקלט של הבדיקה הספקנית.", ""]
    for r in rows:
        sc = "לא נבדק אוטומטית" if r["score"] is None else f"{round(r['score'] * 100)}% מהמילים נמצאו"
        out.append(f"## {r['id']} · {r['path']} · {' '.join('[[' + x + ']]' for x in r['pins'])} · {sc}")
        out.append(f"טענה. {r['claim']}")
        if r["unresolved"]:
            out.append(f"לא אותר בנוסח אוטומטית. {', '.join(r['unresolved'])}. מחפשים בנוסח בעצמכם.")
        if r.get("short"):
            out.append("מראה המקום הוא חוות דעת קצרה, בדרך כלל הסכמה בלבד. בודקים שהיא אכן מסכימה.")
        if r["excerpt"]:
            out.append(f"מהנוסח. {r['excerpt']}")
        if r["hint"]:
            out.append(f"אולי מתאים יותר. [[{r['hint'][0]}]], {round(r['hint'][1] * 100)}%")
        if r["numbers"]:
            out.append(f"מספרים שלא נמצאו בקטע המצוטט. {', '.join(r['numbers'])}")
        out.append("")
    Path(path).write_text("\n".join(out), encoding="utf-8")


def check_verdicts(rows, verdicts):
    errors, warns = [], []
    current = {r["id"]: r for r in rows}
    checked = set(verdicts.get("checked") or [])
    issues = verdicts.get("issues") or []
    covered = len(checked & set(current))
    if current and covered == 0:
        errors.append("VERDICT the skeptic verdicts do not match this card. Run the skeptic on the current evidence.md")
    elif current and covered < len(current) / 2:
        errors.append(f"VERDICT the skeptic checked {covered} of {len(current)} claims. Run it on the whole evidence.md")
    for cid in sorted(set(current) - checked):
        warns.append(f"VERDICT {cid} {current[cid]['path']} is new or changed after the skeptic review. Check it against the text yourself")
    for it in issues:
        cid, verdict = it.get("id"), (it.get("verdict") or "").upper()
        if verdict == "SUPPORTED":
            continue
        if cid in current:
            if it.get("resolution"):
                warns.append(f"VERDICT {cid} {current[cid]['path']} {verdict} kept, {it['resolution']}")
            else:
                errors.append(f"VERDICT {cid} {current[cid]['path']} the skeptic says {verdict}, {it.get('problem') or ''}. "
                              "Fix the claim or its pin, or write a resolution in skeptic.json")
    for g in verdicts.get("global") or []:
        if not g.get("resolution"):
            errors.append(f"VERDICT global, {g.get('problem')}. Fix it and write what was done as the resolution")
    return errors, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("card")
    ap.add_argument("text")
    ap.add_argument("-o", "--out", default="evidence.md")
    ap.add_argument("--verdicts")
    a = ap.parse_args()
    card = json.loads(Path(a.card).read_text(encoding="utf-8"))
    ruling = Ruling(Path(a.text).read_text(encoding="utf-8", errors="replace"))
    rows = check(card, ruling)
    write_report(rows, a.out)
    scored = [r for r in rows if r["score"] is not None and r["words"] >= MIN_WORDS]
    low = [r for r in scored if r["score"] < LOW and not r.get("short")]
    for r in low:
        hint = f" Maybe [[{r['hint'][0]}]] ({round(r['hint'][1] * 100)}%)" if r["hint"] else ""
        print(f"LOW {r['id']} {r['path']} {' '.join('[[' + x + ']]' for x in r['pins'])} "
              f"{round(r['score'] * 100)}% of the claim's words are in the paragraph.{hint}")
    for r in rows:
        if r["hint"] and r not in low:
            print(f"HINT {r['id']} {r['path']} [[{r['pins'][0]}]] fits {round(r['score'] * 100)}%, "
                  f"[[{r['hint'][0]}]] fits {round(r['hint'][1] * 100)}%")
    for r in rows:
        if r["numbers"]:
            print(f"NUMBER {r['id']} {r['path']} {' '.join('[[' + x + ']]' for x in r['pins'])} "
                  f"{', '.join(r['numbers'])} not found in the pinned text")
    unres = [r for r in rows if r["score"] is None]
    errors = []
    if a.verdicts:
        verdicts = json.loads(Path(a.verdicts).read_text(encoding="utf-8"))
        errors, warns = check_verdicts(rows, verdicts)
        for line in errors + warns:
            print(("ERROR " if line in errors else "WARN ") + line)
    avg = sum(r["score"] for r in scored) / len(scored) if scored else 0
    print(f"EVIDENCE {len(rows)} claims, {len(scored)} scored, average {round(avg * 100)}%, {len(low)} low, "
          f"{len(unres)} not resolved automatically. Report in {a.out}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
