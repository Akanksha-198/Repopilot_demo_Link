"""Readable before/after diff + short-text helpers for the Streamlit UI (pure functions, no Streamlit calls)."""
import difflib
import html
import re


def _split(text):
    return (text or "").splitlines()


def _esc(s):
    return html.escape(s).replace("$", "&#36;")


def _intraline(a, b):
    """Highlight exactly which characters changed inside a modified line."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if sm.ratio() < 0.4:
        return _esc(a), _esc(b)
    ha, hb = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        sa, sb = _esc(a[i1:i2]), _esc(b[j1:j2])
        if tag == "equal":
            ha.append(sa); hb.append(sb)
        else:
            if sa: ha.append(f"<mark>{sa}</mark>")
            if sb: hb.append(f"<mark>{sb}</mark>")
    return "".join(ha), "".join(hb)


def diff_stats(old, new):
    a, b = _split(old), _split(new)
    added = removed = hunks = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            hunks += 1
            removed += i2 - i1
            added += j2 - j1
    return {"added": added, "removed": removed, "hunks": hunks}


def _cell(kind, ln, marker, body):
    return f'<div class="dv-cell {kind}"><span class="ln">{ln}</span><span class="mk">{marker}</span><span class="tx">{body or " "}</span></div>'


_EMPTY = '<div class="dv-cell empty"></div>'


def render_diff(old, new, context=2, collapse_over=24):
    """Return one line of HTML: summary chips + aligned Before | After grid."""
    a, b = _split(old), _split(new)
    if not a and not b:
        return ""
    st_ = diff_stats(old, new)

    if st_["hunks"] == 0:
        summary = '<div class="dv-stats"><span class="dv-chip">Only whitespace or line-ending changes</span></div>'
    else:
        places = "place" if st_["hunks"] == 1 else "places"
        summary = (
            '<div class="dv-stats">'
            f'<span class="dv-chip">✏️ {st_["hunks"]} {places} changed</span>'
            f'<span class="dv-chip del">− {st_["removed"]} removed</span>'
            f'<span class="dv-chip add">+ {st_["added"]} added</span>'
            '</div>'
        )

    rows = []  # ("same", i, j, text) | ("chg", left, right)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                rows.append(("same", i1 + k + 1, j1 + k + 1, a[i1 + k]))
        else:
            for k in range(max(i2 - i1, j2 - j1)):
                left = (i1 + k + 1, a[i1 + k]) if i1 + k < i2 else None
                right = (j1 + k + 1, b[j1 + k]) if j1 + k < j2 else None
                rows.append(("chg", left, right))

    keep = [True] * len(rows)
    if len(rows) > collapse_over:
        keep = [False] * len(rows)
        for idx, r in enumerate(rows):
            if r[0] == "chg":
                for k in range(max(0, idx - context), min(len(rows), idx + context + 1)):
                    keep[k] = True

    out, skipped = [], 0

    def flush():
        nonlocal skipped
        if skipped:
            out.append(f'<div class="dv-gap">⋯ {skipped} unchanged line{"s" if skipped != 1 else ""} ⋯</div>')
            skipped = 0

    for idx, r in enumerate(rows):
        if not keep[idx]:
            skipped += 1
            continue
        flush()
        if r[0] == "same":
            t = _esc(r[3])
            out.append('<div class="dv-row">' + _cell("same", r[1], "", t) + _cell("same", r[2], "", t) + "</div>")
        else:
            left, right = r[1], r[2]
            if left and right:
                hl, hr = _intraline(left[1], right[1])
            else:
                hl = _esc(left[1]) if left else ""
                hr = _esc(right[1]) if right else ""
            lc = _cell("del", left[0], "−", hl) if left else _EMPTY
            rc = _cell("add", right[0], "+", hr) if right else _EMPTY
            out.append(f'<div class="dv-row">{lc}{rc}</div>')
    flush()

    head = ('<div class="dv-row dv-head"><div class="dv-h before">BEFORE · what is there now</div>'
            '<div class="dv-h after">AFTER · what RepoPilot proposes</div></div>')
    note = '<div class="dv-note">Dark highlights show exactly which characters changed.</div>'
    return f'{summary}<div class="dv">{head}{"".join(out)}</div>{note}'


# ---------------------------------------------------------------- short text helpers
def tidy(text):
    text = re.split(r"(?im)^[#*\s]*next steps", text or "")[0]                 # drop "Next steps / questions" tail
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*(.+?)\s*#*\s*$", r"**\1**", text)      # giant headings -> bold
    text = re.sub(r"(?m)^\s*(-{3,}|\*{3,}|_{3,})\s*$", "", text)               # horizontal rules
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def short_text(text, limit=420):
    """Return (short_markdown, was_cut)."""
    t = tidy(text)
    if len(t) <= limit:
        return t, False
    cut = t[:limit]
    m = max(cut.rfind(". "), cut.rfind("\n"))
    if m > limit * 0.5:
        cut = cut[: m + 1]
    if cut.count("**") % 2:
        cut += "**"
    if cut.count("`") % 2:
        cut += "`"
    return cut.rstrip() + " …", True


def plan_html(plan, max_steps=5, max_chars=110):
    items = []
    for n, step in enumerate((plan or [])[:max_steps], start=1):
        s = step.strip()
        s = s if len(s) <= max_chars else s[: max_chars - 1].rstrip() + "…"
        items.append(f'<div class="pl-step"><span class="pl-n">{n}</span><span class="pl-t">{html.escape(s)}</span></div>')
    return f'<div class="pl">{"".join(items)}</div>' if items else ""
