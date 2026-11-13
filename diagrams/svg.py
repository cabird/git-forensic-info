"""Tiny SVG helper shared by every figure.

One visual vocabulary for the whole primer:
  blob   = page with a folded corner, blue
  tree   = folder, green
  commit = rounded pill, amber
  tag    = label, purple
  changed = red outline;  unchanged / same hash = grey
Arrows always point from the object that holds a hash to the object it names.
Boxes are sized from their text, so labels cannot spill out of their shapes.
"""
from html import escape

W = 736
SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
INK, MUTED, RED, GREY = "#1b1b1b", "#555555", "#c62828", "#8c8c88"

KINDS = {
    "blob": {"fill": "#e8f1fb", "stroke": "#1f5fa8"},
    "tree": {"fill": "#e7f4e4", "stroke": "#2c6e2f"},
    "commit": {"fill": "#fdf0d3", "stroke": "#99610a"},
    "tag": {"fill": "#f2e9fa", "stroke": "#6b3fa0"},
}
STATES = {
    "changed": {"fill": "#fde7e4", "stroke": RED, "sw": 2.4},
    "same": {"fill": "#f0f0ee", "stroke": GREY, "sw": 1.2},
    "ghost": {"fill": "#ffffff", "stroke": GREY, "sw": 1.2, "dash": "5 4"},
}
KIND_LABEL = {"blob": "blob (file contents)", "tree": "tree (directory)",
              "commit": "commit", "tag": "annotated tag"}
STATE_LABEL = {"changed": "new hash", "same": "same hash as before"}

# Conservative per-character widths (in em) so estimates err on the wide side
# whatever system font the reader has.
_NARROW, _MID, _WIDE = set("iljI.,:;'|!"), set("ftr()[]/ -"), set("mwMW@")


def text_width(s, size=13, mono=False, bold=False):
    if mono:
        return len(s) * size * 0.61
    w = 0.0
    for ch in s:
        if ch in _NARROW:
            w += 0.31
        elif ch in _MID:
            w += 0.40
        elif ch in _WIDE:
            w += 0.92
        elif ch.isupper() or ch.isdigit():
            w += 0.68
        else:
            w += 0.59
    return w * size * (1.07 if bold else 1.0)


def fmt(n):
    """Stable, compact number formatting for deterministic output."""
    s = f"{n:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w / 2, y + h / 2

    def top(self, dx=0): return (self.cx + dx, self.y)
    def bottom(self, dx=0): return (self.cx + dx, self.y + self.h)
    def left(self, dy=0): return (self.x, self.cy + dy)
    def right(self, dy=0): return (self.x + self.w, self.cy + dy)


def shape(kind, x, y, w, h, style):
    """The outline for one object type, as SVG markup."""
    sw = fmt(style.get("sw", 1.5))
    dash = f' stroke-dasharray="{style["dash"]}"' if "dash" in style else ""
    paint = f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="{sw}" stroke-linejoin="round"{dash}'
    X, Y, R, B = fmt(x), fmt(y), fmt(x + w), fmt(y + h)
    if kind == "blob":
        e = 10
        return (f'<path d="M{X},{Y} H{fmt(x + w - e)} L{R},{fmt(y + e)} V{B} H{X} Z" {paint}/>'
                f'<path d="M{fmt(x + w - e)},{Y} V{fmt(y + e)} H{R}" fill="none" stroke="{style["stroke"]}" stroke-width="{sw}"/>')
    if kind == "tree":
        return f'<path d="M{X},{fmt(y - 6)} H{fmt(x + 24)} L{fmt(x + 30)},{Y} H{R} V{B} H{X} Z" {paint}/>'
    if kind == "tag":
        return (f'<path d="M{fmt(x + 12)},{Y} H{R} V{B} H{fmt(x + 12)} L{X},{fmt(y + h / 2)} Z" {paint}/>'
                f'<circle cx="{fmt(x + 12)}" cy="{fmt(y + h / 2)}" r="2.2" fill="{style["stroke"]}"/>')
    if kind == "commit":
        return f'<rect x="{X}" y="{Y}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(min(h / 2, 15))}" {paint}/>'
    return f'<rect x="{X}" y="{Y}" width="{fmt(w)}" height="{fmt(h)}" rx="6" {paint}/>'


class Canvas:
    def __init__(self, name, label, width=W):
        self.name, self.title, self.width = name, label, width
        self.back, self.items, self.height = [], [], 0
        self.colors = []

    def _grow(self, y):
        self.height = max(self.height, y)

    # -- text ---------------------------------------------------------------
    def text(self, x, y, s, size=13, anchor="middle", mono=False, bold=False,
             fill=INK, halo=False, italic=False):
        attrs = f'x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}" text-anchor="{anchor}" fill="{fill}"'
        if mono:
            attrs += f' font-family="{MONO}"'
        if bold:
            attrs += ' font-weight="600"'
        if italic:
            attrs += ' font-style="italic"'
        if halo:
            attrs += ' stroke="#ffffff" stroke-width="4" stroke-linejoin="round" paint-order="stroke"'
        self.items.append(f'<text {attrs} xml:space="preserve">{escape(s)}</text>')
        self._grow(y + 5)

    # -- nodes --------------------------------------------------------------
    def node(self, kind, cx, cy, lines, state=None, minw=0, pad=13):
        """An object drawn in its type's shape. lines: [(text, 'name'|'hash'|'note'), ...]"""
        specs = {"name": dict(size=13, bold=True), "hash": dict(size=12, mono=True),
                 "note": dict(size=12, italic=True)}
        pad += 6 if kind == "tag" else 0
        w = max([minw] + [text_width(t, specs[k]["size"], k == "hash", k == "name") + 2 * pad
                          for t, k in lines])
        h = 17 * len(lines) + 12
        x, y = cx - w / 2, cy - h / 2
        style = dict(KINDS.get(kind, {"fill": "#fff", "stroke": INK}))
        if state:
            style.update(STATES[state])
        self.items.append(shape(kind, x, y, w, h, style))
        ink = MUTED if state in ("same", "ghost") else INK
        tx = cx + (5 if kind == "tag" else 0)
        for i, (t, k) in enumerate(lines):
            self.text(tx, y + 6 + 17 * i + 13, t, fill=ink, **specs[k])
        self._grow(y + h)
        return Box(x, y, w, h)

    def card(self, kind, x, y, w, title, hash7, lines, note):
        """A large object card listing the object's real content, one field per line."""
        lh, top = 17, 30
        body = top + lh * len(lines) + 8
        h = body + 26
        self.items.append(shape(kind, x, y, w, h, KINDS[kind]))
        self.text(x + 16 + (6 if kind == "tag" else 0), y + 20, title, anchor="start", bold=True)
        self.text(x + w - 16, y + 20, hash7, anchor="end", mono=True, size=12)
        ys = {}
        for i, ln in enumerate(lines):
            ly = y + top + lh * i + 12
            ys[i] = ly - 4
            if ln:
                self.text(x + 16 + (6 if kind == "tag" else 0), ly, ln, anchor="start", mono=True, size=12)
        stroke = KINDS[kind]["stroke"]
        self.items.append(f'<path d="M{fmt(x + 12)},{fmt(y + body)} H{fmt(x + w - 12)}" stroke="{stroke}" '
                          f'stroke-width="1" stroke-opacity="0.35"/>')
        self.text(x + 16, y + body + 17, note, anchor="start", size=12, fill=MUTED)
        box = Box(x, y, w, h)
        box.line_y = ys
        return box

    def label(self, cx, cy, s, fill=INK, stroke=None, bold=False):
        """A plain outlined label for things that are not objects (branch names, badges)."""
        w = text_width(s, 12, bold=bold) + 16
        self.items.append(f'<rect x="{fmt(cx - w / 2)}" y="{fmt(cy - 10)}" width="{fmt(w)}" height="20" rx="4" '
                          f'fill="#ffffff" stroke="{stroke or fill}" stroke-width="1.2"/>')
        self.text(cx, cy + 4, s, size=12, fill=fill, bold=bold)
        return Box(cx - w / 2, cy - 10, w, 20)

    def region(self, x, y, w, h, fill="#f6f6f3", stroke=GREY, dash="6 4"):
        self.back.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="12" '
                         f'fill="{fill}" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="{dash}"/>')
        self._grow(y + h)

    # -- connectors -----------------------------------------------------------
    def _marker(self, color):
        if color not in self.colors:
            self.colors.append(color)
        return f"ah-{self.name}-{self.colors.index(color)}"

    def arrow(self, *pts, color=INK, dashed=False, label=None, lpos=0.5, ldx=0, ldy=-5,
              width=1.4, head=True, lanchor="middle"):
        """A straight or elbowed connector through pts; the arrowhead is at the last point."""
        d = "M" + " L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)
        extra = ' stroke-dasharray="5 4"' if dashed else ""
        if head:
            extra += f' marker-end="url(#{self._marker(color)})"'
        self.items.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{fmt(width)}"{extra}/>')
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            if len(pts) > 2:
                (x1, y1), (x2, y2) = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
            self.text(x1 + (x2 - x1) * lpos + ldx, y1 + (y2 - y1) * lpos + ldy, label,
                      size=12, fill=color if color != INK else MUTED, halo=True, anchor=lanchor)
        for _, y in pts:
            self._grow(y)

    def equals(self, p1, p2, label, color="#2c6e2f"):
        """A double line meaning 'these two hashes are equal'."""
        (x1, y1), (x2, y2) = p1, p2
        for dy in (-2.5, 2.5):
            self.items.append(f'<path d="M{fmt(x1)},{fmt(y1 + dy)} L{fmt(x2)},{fmt(y2 + dy)}" '
                              f'stroke="{color}" stroke-width="1.6"/>')
        self.text((x1 + x2) / 2, (y1 + y2) / 2 - 9, label, size=12, fill=color, bold=True, halo=True)

    # -- legend -----------------------------------------------------------------
    def legend(self, kinds=(), states=(), extra=()):
        y = self.height + 34
        x = 14
        self.items.append(f'<path d="M14,{fmt(y - 22)} H{self.width - 14}" stroke="#d9d9d4" stroke-width="1"/>')
        for k in kinds:
            self.items.append(shape(k, x, y - 8, 26, 16, KINDS[k]))
            self.text(x + 33, y + 4, KIND_LABEL[k], size=12, anchor="start", fill=MUTED)
            x += 33 + text_width(KIND_LABEL[k], 12) + 22
        for s in states:
            self.items.append(shape("box", x, y - 8, 26, 16, STATES[s]))
            self.text(x + 33, y + 4, STATE_LABEL[s], size=12, anchor="start", fill=MUTED)
            x += 33 + text_width(STATE_LABEL[s], 12) + 22
        for s in extra:
            self.text(x, y + 4, s, size=12, anchor="start", fill=MUTED)
            x += text_width(s, 12) + 22
        self._grow(y + 12)

    # -- output -------------------------------------------------------------------
    def render(self):
        h = int(self.height + 12)
        markers = "".join(
            f'<marker id="ah-{self.name}-{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="{c}"/></marker>'
            for i, c in enumerate(self.colors))
        return (f'<svg viewBox="0 0 {self.width} {h}" width="{self.width}" '
                f'height="{h}" role="img" aria-label="{escape(self.title, quote=True)}" font-family="{SANS}">'
                f'<title>{escape(self.title)}</title><defs>{markers}</defs>'
                + "".join(self.back) + "".join(self.items) + "</svg>")
