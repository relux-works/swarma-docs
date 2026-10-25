#!/usr/bin/env python3
"""Render a declarative diagram (TOML) to SVG in the house style.

    python3 scripts/diagram-kit/render.py SRC.toml OUT.svg [--theme THEME.toml]
        [--png OUT.png] [--report] [--require-fit normal|tall] [--graphviz-any]

Layouts: "stack" (vertical flow with trust-boundary groups, paired arrows,
side lanes and notes beside an element), "sequence" (participant containers,
lifelines, numbered messages, alt and opt frames, section dividers, notes over
or beside a participant) and "graph" (components, states and trees placed by
Graphviz `dot`, with start and end states and notes beside a node).

Every source and theme is checked against a schema before anything is drawn:
unknown keys, wrong types, unknown references and values outside an enum are
refused with a DiagramError that names the offending key. After drawing, a
geometry lint reads the SVG back and refuses the render when an arrow runs
through a label or a foreign box, when labels and boxes overlap, when text
spills out of its box or crosses a boundary, when a label sits away from its
arrow, or when anything lies outside the viewBox.

Needs Python 3.11+ (tomllib). The graph layout needs Graphviz `dot` at the
pinned version GRAPHVIZ_PIN, because another version places nodes differently;
--png needs `rsvg-convert`. Text is measured with the PT Sans and PT Mono
metrics in metrics.json and every text run carries its own position, so the
same source and theme give the same SVG byte for byte: on every machine for
stack and sequence, on every machine with the pinned Graphviz for graph. The
fonts are needed only to view or rasterise the SVG. The style guide is
editorial/diagram-style.ru.md.
"""
import argparse
import json
import math
import pathlib
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

HERE = pathlib.Path(__file__).resolve().parent
GRAPHVIZ_PIN = "14.0.4"
SVG_NS = "{http://www.w3.org/2000/svg}"


class DiagramError(Exception):
    pass


# ---------------------------------------------------------------- svg output

def fmt(v):
    s = f"{v:.1f}"
    s = s[:-2] if s.endswith(".0") else s
    return "0" if s == "-0" else s


def el(tag, body=None, **attrs):
    """One SVG element. Every attribute value goes through quoteattr; numbers
    are formatted with fmt. Keyword names map `stroke_width` to `stroke-width`
    and `class_` to `class`."""
    out = []
    for k, v in attrs.items():
        if v is None:
            continue
        name = k.rstrip("_").replace("_", "-")
        if isinstance(v, bool):
            raise TypeError(f"boolean SVG attribute {name}")
        val = fmt(v) if isinstance(v, (int, float)) else str(v)
        out.append(f" {name}={quoteattr(val)}")
    a = "".join(out)
    return f"<{tag}{a}/>" if body is None else f"<{tag}{a}>{body}</{tag}>"


# ---------------------------------------------------------------- schemas

ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
FONT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]*$")
DASH_RE = re.compile(r"^[0-9. ]+$")
ROLES = ("human", "agent", "service", "store", "key", "external", "alert", "neutral")


def _type(v):
    return {bool: "a boolean", int: "an integer", float: "a number", str: "a string",
            list: "an array", dict: "a table"}.get(type(v), type(v).__name__)


def t_text(path, v):
    if not isinstance(v, str):
        raise DiagramError(f"{path}: must be a string, got {_type(v)}")
    bad = [c for c in v if ord(c) < 32 and c != "\n"]
    if bad:
        raise DiagramError(f"{path}: control character {bad[0]!r} is not allowed")


def t_id(path, v):
    if not isinstance(v, str) or not ID_RE.match(v):
        raise DiagramError(f"{path}: must be an identifier (a Latin letter, then letters, digits or _), got {v!r}")


def t_bool(path, v):
    if not isinstance(v, bool):
        raise DiagramError(f"{path}: must be true or false, got {_type(v)}")


def t_true(path, v):
    if v is not True:
        raise DiagramError(f"{path}: must be true")


def t_step(path, v):
    if isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 99:
        raise DiagramError(f"{path}: must be an integer from 1 to 99, got {v!r}")


def t_enum(*values):
    def check(path, v):
        if v not in values:
            raise DiagramError(f"{path}: must be one of {', '.join(values)}, got {v!r}")
    return check


def t_role(path, v):
    if v not in ROLES:
        raise DiagramError(f"{path}: unknown role {v!r}; known: {', '.join(ROLES)}")


def t_ids(path, v):
    if not isinstance(v, list) or not v:
        raise DiagramError(f"{path}: must be a non-empty array of identifiers")
    for i, x in enumerate(v):
        t_id(f"{path}[{i}]", x)


def t_ranks(path, v):
    if not isinstance(v, list):
        raise DiagramError(f"{path}: must be an array of arrays of node identifiers")
    for i, r in enumerate(v):
        t_ids(f"{path}[{i}]", r)
        if len(r) < 2:
            raise DiagramError(f"{path}[{i}]: a rank lists at least two nodes")


def t_num(path, v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
        raise DiagramError(f"{path}: must be a non-negative number, got {v!r}")


def t_pos(path, v):
    t_num(path, v)
    if v == 0:
        raise DiagramError(f"{path}: must be greater than zero")


def t_dash(path, v):
    if not isinstance(v, str) or not DASH_RE.match(v) or not re.search(r"[0-9]", v):
        raise DiagramError(f"{path}: must match ^[0-9. ]+$ (dash lengths), got {v!r}")


def t_color(path, v):
    if not isinstance(v, str) or not COLOR_RE.match(v):
        raise DiagramError(f"{path}: must be a colour #rrggbb, got {v!r}")


def t_font(path, v):
    if not isinstance(v, str) or not FONT_RE.match(v):
        raise DiagramError(f"{path}: must be a font family name, got {v!r}")


def check_table(path, value, fields, required=()):
    if not isinstance(value, dict):
        raise DiagramError(f"{path}: must be a table, got {_type(value)}")
    for k in value:
        if k not in fields:
            raise DiagramError(f"{path}.{k}: unknown key; known: {', '.join(fields)}")
    for k in required:
        if k not in value:
            raise DiagramError(f"{path}: missing key {k!r}")
    for k, v in value.items():
        fields[k](f"{path}.{k}", v)


def check_map(path, value, fields, required=()):
    """A table of named entries (nodes, groups), each a table."""
    if not isinstance(value, dict):
        raise DiagramError(f"{path}: must be a table of named entries, got {_type(value)}")
    for k, v in value.items():
        t_id(f"{path}.{k}", k)
        check_table(f"{path}.{k}", v, fields, required)


def check_list(path, value, fields, required=()):
    if not isinstance(value, list):
        raise DiagramError(f"{path}: must be an array of tables, got {_type(value)}")
    for i, v in enumerate(value):
        check_table(f"{path}[{i}]", v, fields, required)


SPACE_SCHEMA = {k: t_num for k in (
    "pad", "box_pad_x", "box_pad_y", "box_radius", "box_stroke", "box_max_width", "node_text_width",
    "seq_node_width", "min_box_width", "group_pad", "group_radius", "group_stroke", "group_label_gap",
    "letter_spacing", "gap_min", "label_max_width", "seq_label_width", "seq_self_width", "pair_min_dx",
    "lane", "arrow_stroke", "arrow_head", "step_radius", "line_height", "seq_column_gap", "seq_row_gap",
    "graph_nodesep", "graph_ranksep", "note_width", "note_gap")}
SPACE_SCHEMA.update(group_dash=t_dash, frame_dash=t_dash, opt_dash=t_dash)
for _k in ("line_height", "step_radius", "arrow_head", "note_width", "seq_node_width", "seq_label_width",
           "seq_self_width", "label_max_width", "node_text_width", "box_max_width", "min_box_width"):
    SPACE_SCHEMA[_k] = t_pos


def bounded(check, limit):
    """A finite value can still be absurd: 1e308 px renders an `inf` figure."""
    def t(path, v):
        check(path, v)
        if v > limit:
            raise DiagramError(f"{path}: must be at most {fmt(limit)}, got {v!r}")
    return t


# Pixels up to 2000, the em and ratio keys up to 4, Graphviz inches up to 20.
SPACE_LIMITS = {k: 2000 for k, t in SPACE_SCHEMA.items() if t in (t_num, t_pos)}
SPACE_LIMITS.update(line_height=4, letter_spacing=4, graph_nodesep=20, graph_ranksep=20)
for _k, _limit in SPACE_LIMITS.items():
    SPACE_SCHEMA[_k] = bounded(SPACE_SCHEMA[_k], _limit)

THEME_SCHEMA = {
    "font": {"sans": t_font, "mono": t_font, "fallback": t_font},
    "size": {k: bounded(t_pos, 200) for k in ("title", "caption", "name", "text", "label", "protocol", "group", "step",
                                 "note")},
    "space": SPACE_SCHEMA,
    "print": {k: bounded(t_pos, 2000) for k in ("box_width_mm", "box_height_mm", "tall_height_mm", "min_print_pt")},
    "color": {k: t_color for k in ("background", "ink", "text", "muted", "line", "lifeline", "note_fill",
                                    "note_stroke")},
}
ROLE_SCHEMA = {"stroke": t_color, "fill": t_color, "label": t_color}


def check_theme(theme, path="theme"):
    sections = dict(THEME_SCHEMA)
    sections["role"] = None
    check_table(path, theme, {k: (lambda p, v: None) for k in sections}, required=list(sections))
    for name, schema in THEME_SCHEMA.items():
        check_table(f"{path}.{name}", theme[name], schema, required=list(schema))
    roles = theme["role"]
    if not isinstance(roles, dict):
        raise DiagramError(f"{path}.role: must be a table")
    for r in roles:
        if r not in ROLES:
            raise DiagramError(f"{path}.role.{r}: unknown role; the roles are fixed: {', '.join(ROLES)}")
    for r in ROLES:
        if r not in roles:
            raise DiagramError(f"{path}.role: missing role {r!r}")
        check_table(f"{path}.role.{r}", roles[r], ROLE_SCHEMA, required=list(ROLE_SCHEMA))


TOP = {"layout": t_enum("stack", "sequence", "graph"), "alt": t_text, "title": t_text, "caption": t_text,
       "theme": lambda p, v: None}
NODE = {"role": t_role, "name": t_text, "text": t_text, "badge": t_text, "style": t_enum("solid", "dashed"),
        "group": t_id}
LINK = {"from": t_id, "to": t_id, "step": t_step, "label": t_text, "style": t_enum("solid", "dashed"),
        "color": t_role}
SIDE = t_enum("left", "right")

SCHEMAS = {
    "stack": {
        "top": dict(TOP, nodes=None, groups=None, links=None),
        "node": dict(NODE, compact=t_bool, note=t_text, note_side=SIDE),
        "group": {"label": t_text, "role": t_role, "parent": t_id, "note": t_text, "note_side": SIDE},
        "link": dict(LINK, via=t_text, side=SIDE),
    },
    "sequence": {
        "top": dict(TOP, nodes=None, groups=None, seq=None),
        "node": NODE,
        "group": {"label": t_text, "role": t_role},
    },
    "graph": {
        "top": dict(TOP, nodes=None, groups=None, links=None, direction=t_enum("TB", "LR", "BT", "RL"),
                    splines=t_enum("spline", "polyline"), same_rank=t_ranks, uniform_width=t_bool),
        "node": dict(NODE, column=t_id, shape=t_enum("box", "start", "end"), note=t_text),
        "group": {"label": t_text, "role": t_role, "parent": t_id},
        "link": dict(LINK, via=t_text, constraint=t_bool),
    },
}

SEQ_KINDS = ("from", "alt", "opt", "else", "end", "note", "divider")
SEQ_SCHEMA = {
    "from": dict(LINK),
    "alt": {"alt": t_text},
    "opt": {"opt": t_text},
    "else": {"else": t_text},
    "end": {"end": t_true},
    "note": {"note": t_text, "over": t_ids, "on": t_id, "side": SIDE},
    "divider": {"divider": t_text},
}


def seq_kind(path, it):
    if not isinstance(it, dict):
        raise DiagramError(f"{path}: must be a table")
    kinds = [k for k in SEQ_KINDS if k in it]
    if len(kinds) != 1:
        raise DiagramError(f"{path}: needs exactly one of {', '.join(SEQ_KINDS)}"
                           + (f"; got {', '.join(kinds)}" if kinds else ""))
    return "msg" if kinds[0] == "from" else kinds[0]


def validate(d, layout):
    """Check the source against the layout's schema and resolve references.
    Raises DiagramError naming the first offending key."""
    sch = SCHEMAS[layout]
    top = {k: (v or (lambda p, x: None)) for k, v in sch["top"].items()}
    check_table("source", d, top, required=["layout", "nodes"])
    nodes = d["nodes"]
    check_map("nodes", nodes, sch["node"])
    if not nodes:
        raise DiagramError(f"nodes: a {layout} layout needs at least one node")
    groups = d.get("groups", {})
    check_map("groups", groups, sch["group"])

    # Groups: known parents, no cycles, at most two levels, no empty group.
    for gid, g in groups.items():
        if "parent" in g and g["parent"] not in groups:
            raise DiagramError(f"groups.{gid}.parent: unknown group {g['parent']!r}")
    for gid in groups:
        seen, cur = [], gid
        while cur:
            if cur in seen:
                raise DiagramError(f"groups.{gid}.parent: parents form a cycle ({' -> '.join(seen + [cur])})")
            seen.append(cur)
            cur = groups[cur].get("parent")
        if len(seen) > 2:
            raise DiagramError(f"groups.{gid}: nesting is limited to two levels ({' in '.join(seen)})")
    for nid, n in nodes.items():
        if "group" in n and n["group"] not in groups:
            raise DiagramError(f"nodes.{nid}.group: unknown group {n['group']!r}")
        shape = n.get("shape", "box")
        if shape == "box" and "name" not in n:
            raise DiagramError(f"nodes.{nid}: missing key 'name'")
        if shape != "box":
            extra = [k for k in ("name", "text", "badge", "note", "style") if k in n]
            if extra:
                raise DiagramError(f"nodes.{nid}.{extra[0]}: a {shape} state is drawn as a dot and has no "
                                   f"{extra[0]}")
    used = set()
    for n in nodes.values():
        g = n.get("group")
        while g:
            used.add(g)
            g = groups[g].get("parent")
    for gid in groups:
        if gid not in used:
            raise DiagramError(f"groups.{gid}: has no nodes")

    if layout == "sequence":
        items = d.get("seq", [])
        if not isinstance(items, list):
            raise DiagramError("seq: must be an array of tables")
        for i, it in enumerate(items):
            path = f"seq[{i}]"
            kind = seq_kind(path, it)
            fields = SEQ_SCHEMA["from" if kind == "msg" else kind]
            check_table(path, it, fields, required=["from", "to"] if kind == "msg" else [])
            refs = [it[k] for k in ("from", "to", "on") if k in it] + list(it.get("over", []))
            for r in refs:
                if r not in nodes:
                    raise DiagramError(f"{path}: sequence item names unknown node {r!r}")
            if kind == "note":
                if "over" in it and "on" in it:
                    raise DiagramError(f"{path}: a note is either over participants or on one participant, "
                                       f"not both")
                if "side" in it and "on" not in it:
                    raise DiagramError(f"{path}.side: side places a note beside the participant named in 'on'")
                if len(it.get("over", [])) > 2:
                    raise DiagramError(f"{path}.over: names the first and the last participant, at most two")
        return

    links = d.get("links", [])
    check_list("links", links, sch["link"], required=["from", "to"])
    for i, l in enumerate(links):
        for key in ("from", "to"):
            ep = l[key]
            if ep not in nodes and not (layout == "stack" and ep in groups):
                what = "neither a node nor a group" if layout == "stack" else "not a node"
                raise DiagramError(f"links[{i}].{key}: link endpoint {ep!r} is {what}")
        if l["from"] == l["to"]:
            raise DiagramError(f"links[{i}]: from and to are the same element; a loop has no layout here")
    if layout == "graph":
        for i, rank in enumerate(d.get("same_rank", [])):
            for x in rank:
                if x not in nodes:
                    raise DiagramError(f"same_rank[{i}]: unknown node {x!r}")


# ---------------------------------------------------------------- text metrics

class Metrics:
    def __init__(self, path):
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.tables = {}
        for face, t in raw.items():
            self.tables[face] = (dict(zip(t["widths"], t["advances"])), t["default"])

    def face_for(self, ch, face):
        """PT Sans has no arrows; they come from PT Mono, as the renderer will draw them."""
        table, _ = self.tables[face]
        if ch in table or not face.startswith("sans"):
            return face
        mono = "mono-bold" if face.endswith("bold") else "mono"
        return mono if ch in self.tables[mono][0] else face

    def width(self, text, face, size, spacing=0.0):
        total = 0
        for ch in text:
            table, default = self.tables[self.face_for(ch, face)]
            total += table.get(ch, default)
        return total * size / 1000 + spacing * size * len(text)


SHORT_WORD = re.compile(r"^[A-Za-zА-Яа-яЁё]{1,2}$")


class Text:
    """Inline markup: `code` is set in the mono face. A line break in the
    source is kept. Lines wrap at spaces; a one- or two-letter word (в, и, на)
    stays with the next word, and the last line of a paragraph is never a lone
    word when the line above can give one."""

    def __init__(self, kit, raw, size, bold=False, color=None):
        self.kit, self.size, self.bold, self.color = kit, size, bold, color
        self.raw = raw or ""
        self.base = "sans-bold" if bold else "sans"
        self.space = kit.m.width(" ", self.base, size)
        self.paragraphs = [self._words(p) for p in self.raw.split("\n")] if self.raw else []
        self.lines = [list(p) for p in self.paragraphs]

    def _words(self, paragraph):
        mono = "mono-bold" if self.bold else "mono"
        words, cur = [], []
        for i, part in enumerate(paragraph.split("`")):
            face = mono if i % 2 else self.base
            for j, chunk in enumerate(part.split(" ")):
                if j > 0:
                    words.append(cur)
                    cur = []
                if chunk:
                    cur.append((chunk, face))
        words.append(cur)
        words = [w for w in words if w]
        out, pending = [], None
        for k, w in enumerate(words):
            if pending:
                w = pending + [(" ", self.base)] + w
                pending = None
            short = len(w) == 1 and w[0][1] == self.base and SHORT_WORD.match(w[0][0])
            if short and k < len(words) - 1:
                pending = w
                continue
            out.append(w)
        return out

    def word_width(self, word):
        return sum(self.kit.m.width(t, f, self.size) for t, f in word)

    def line_width(self, line):
        return sum(self.word_width(w) for w in line) + self.space * max(0, len(line) - 1)

    def natural_width(self):
        return max((self.line_width(p) for p in self.paragraphs), default=0)

    def greedy(self, words, max_width):
        lines, line, width = [], [], 0
        for w in words:
            ww = self.word_width(w)
            if line and width + self.space + ww > max_width + 0.5:
                lines.append(line)
                line, width = [], 0
            if line:
                width += self.space
            line.append(w)
            width += ww
        lines.append(line)
        return lines

    def balanced(self, words, max_width):
        """Greedy wrap, then the narrowest measure that keeps the line count."""
        pl = self.greedy(words, max_width)
        n = len(pl)
        if n > 1:
            lo, hi = max_width / n, max_width
            while hi - lo > 2:
                mid = (lo + hi) / 2
                if len(self.greedy(words, mid)) > n:
                    lo = mid
                else:
                    hi = mid
            pl = self.greedy(words, hi)
        return pl

    def unwidow(self, pl, max_width):
        if len(pl) >= 2 and len(pl[-1]) == 1 and len(pl[-2]) >= 3:
            cand = [pl[-2][-1]] + pl[-1]
            if self.line_width(cand) <= max_width + 0.5:
                pl = pl[:-2] + [pl[-2][:-1], cand]
        return pl

    def wrap(self, max_width, balance=True):
        self.lines = []
        for words in self.paragraphs:
            pl = self.balanced(words, max_width) if balance else self.greedy(words, max_width)
            self.lines.extend(self.unwidow(pl, max_width))
        return self

    @property
    def line_height(self):
        return self.size * self.kit.s["line_height"]

    @property
    def height(self):
        return len(self.lines) * self.line_height if self.raw else 0

    @property
    def width(self):
        return max((self.line_width(l) for l in self.lines), default=0)

    def svg(self, x, y, anchor="middle", color=None):
        """y is the top of the first line; x is the anchor point."""
        out = []
        color = color or self.color or self.kit.c["ink"]
        for i, line in enumerate(self.lines):
            w = self.line_width(line)
            x0 = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
            base = y + i * self.line_height + self.size * 0.95
            runs = []
            for j, word in enumerate(line):
                if j:
                    runs.append((" ", self.base))
                runs.extend(word)
            if runs:
                out.append(self.kit.text_line(runs, x0, base, self.size, color))
        return "\n".join(out)


# ---------------------------------------------------------------- kit

def load_theme(theme_path=None):
    path = theme_path or HERE / "theme.toml"
    try:
        theme = tomllib.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise DiagramError(f"theme {path}: {e}")
    check_theme(theme)
    return theme


def apply_override(theme, over):
    """A source may set [theme.space] keys only; each one is type-checked."""
    if not isinstance(over, dict):
        raise DiagramError("theme: must be a table")
    unknown = set(over) - {"space"}
    if unknown:
        raise DiagramError("theme: a diagram may override only [theme.space]; colours and fonts live in the theme")
    check_table("theme.space", over.get("space", {}), SPACE_SCHEMA)
    out = dict(theme)
    out["space"] = dict(theme["space"], **over.get("space", {}))
    return out


class Kit:
    def __init__(self, theme):
        self.t = theme
        self.c = theme["color"]
        self.s = theme["space"]
        self.z = theme["size"]
        self.m = Metrics(HERE / "metrics.json")
        f = theme["font"]
        self.fam = {
            "sans": f"{f['sans']}, {f['fallback']}",
            "mono": f"{f['mono']}, monospace",
        }

    def role(self, name):
        return self.t["role"][name]

    def text(self, raw, size, bold=False, color=None):
        return Text(self, raw, size, bold, color)

    def text_line(self, runs, x, base, size, color, spacing=0.0):
        # Merge neighbouring runs of one face, then emit one <text> with tspans.
        merged = []
        for t, face in runs:
            for ch in t:
                eff = self.m.face_for(ch, face)
                if merged and merged[-1][1] == eff:
                    merged[-1][0] += ch
                else:
                    merged.append([ch, eff])
        # Every run after the first gets its own x from our metrics: renderers
        # drop spaces at tspan edges, and fixed positions keep the layout
        # identical wherever the SVG is drawn.
        spans = []
        cur = x
        for i, (t, face) in enumerate(merged):
            lead = len(t) - len(t.lstrip(" "))
            if lead:
                cur += self.m.width(" " * lead, face, size, spacing)
                t = t[lead:]
            w = self.m.width(t, face, size, spacing)
            body = t.rstrip(" ")
            fam = self.fam["mono" if face.startswith("mono") else "sans"]
            weight = "bold" if face.endswith("bold") else None
            if body:
                spans.append(el("tspan", escape(body), x=cur if (i or lead) else None, font_family=fam,
                                font_weight=weight))
            cur += w
        return el("text", "".join(spans), x=x, y=base, font_size=size, fill=color,
                  letter_spacing=(spacing * size) if spacing else None)

    def spaced_label(self, raw, x, y, size, color, anchor="start"):
        """Uppercase label with letter spacing (groups, protocols). y is the top."""
        sp = self.s["letter_spacing"]
        out = []
        lh = size * self.s["line_height"]
        for i, line in enumerate(raw.upper().split("\n")):
            w = self.m.width(line, "sans-bold", size, sp) - sp * size
            x0 = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
            out.append(self.text_line([(line, "sans-bold")], x0, y + i * lh + size * 0.95, size, color, sp))
        return "\n".join(out)

    def spaced_size(self, raw, size):
        sp = self.s["letter_spacing"]
        lines = raw.upper().split("\n")
        w = max(self.m.width(l, "sans-bold", size, sp) - sp * size for l in lines)
        return w, len(lines) * size * self.s["line_height"]

    def arrow(self, points, color=None, dashed=False, head=True, meta=None):
        d = "M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x, y in points)
        return self.path_arrow(d, points[-2], points[-1], color or self.c["line"], dashed, head, meta)

    def path_arrow(self, d, before, tip, color, dashed, head=True, meta=None):
        s = self.s
        meta = meta or {}
        dash = "6 5" if dashed else None
        out = []
        if head:
            # Shorten the line so it does not poke through the arrow head.
            ang = math.atan2(tip[1] - before[1], tip[0] - before[0])
            h = s["arrow_head"]
            back = (tip[0] - math.cos(ang) * h * 0.6, tip[1] - math.sin(ang) * h * 0.6)
            d = d[: d.rfind(" ", 0, d.rfind(" "))] + f" {fmt(back[0])} {fmt(back[1])}"
        out.append(el("path", d=d, fill="none", stroke=color, stroke_width=s["arrow_stroke"],
                      stroke_dasharray=dash, class_="edge", **meta))
        if head:
            p1 = (tip[0] - math.cos(ang) * h + math.sin(ang) * h * 0.45,
                  tip[1] - math.sin(ang) * h - math.cos(ang) * h * 0.45)
            p2 = (tip[0] - math.cos(ang) * h - math.sin(ang) * h * 0.45,
                  tip[1] - math.sin(ang) * h + math.cos(ang) * h * 0.45)
            pts = " ".join(f"{fmt(a)},{fmt(b)}" for a, b in (tip, p1, p2))
            out.append(el("polygon", points=pts, fill=color))
        return "\n".join(out)

    def connector(self, a, b, src, dst):
        """Dashed line from an element to its note."""
        return el("path", d=f"M {fmt(a[0])} {fmt(a[1])} L {fmt(b[0])} {fmt(b[1])}", fill="none",
                  stroke=self.c["note_stroke"], stroke_width=1.5, stroke_dasharray="4 4", class_="connector",
                  data_from=src, data_to=dst)

    # Step label: circled number, then a bold label, wrapped.
    def step_label(self, step, label, max_width=None):
        max_width = max_width or self.s["label_max_width"]
        mark = self.step_mark_width(step) if step is not None else 0
        lead = (mark + 6) if step is not None else 0
        t = self.text(label or "", self.z["label"], bold=True).wrap(max(40, max_width - lead))
        w = lead + t.width if t.raw else mark
        h = max(t.height, 2 * self.s["step_radius"] if step is not None else 0)
        return {"step": step, "text": t, "w": w, "h": h, "lead": lead}

    def step_mark_width(self, step):
        """A one-digit step sits in a circle; a longer number in a pill of the
        same height."""
        r = self.s["step_radius"]
        return max(2 * r, self.m.width(str(step), "sans-bold", self.z["step"]) + 9)

    def step_label_svg(self, lab, x, y, color=None, edge=None):
        """x, y: top-left of the label block. With `edge` the block is grouped
        and tagged, so the lint can check it stays next to its arrow."""
        out = []
        r = self.s["step_radius"]
        t = lab["text"]
        if lab["step"] is not None:
            cy = y + (t.line_height / 2 if t.raw else r)
            mw = self.step_mark_width(lab["step"])
            cx = x + mw / 2
            if mw <= 2 * r:
                out.append(el("circle", cx=cx, cy=cy, r=r, fill=self.c["background"],
                              stroke=color or self.c["ink"], stroke_width=1.5, class_="step"))
            else:
                out.append(el("rect", x=x, y=cy - r, width=mw, height=2 * r, rx=r, fill=self.c["background"],
                              stroke=color or self.c["ink"], stroke_width=1.5, class_="step"))
            digit = str(lab["step"])
            dw = self.m.width(digit, "sans-bold", self.z["step"])
            out.append(self.text_line([(digit, "sans-bold")], cx - dw / 2, cy + self.z["step"] * 0.36,
                                      self.z["step"], color or self.c["ink"]))
        if t.raw:
            out.append(t.svg(x + lab["lead"], y, anchor="start", color=self.c["ink"]))
        body = "\n".join(out)
        if edge is not None:
            return el("g", "\n" + body + "\n", class_="label", data_edge=edge)
        return body

    # Box: bold name, optional badge, description.
    def box_model(self, node, width=None, wrap=None):
        s, z = self.s, self.z
        name = self.text(node.get("name", ""), z["name"], bold=True)
        desc = self.text(node.get("text", ""), z["text"], color=self.c["text"])
        badge = node.get("badge")
        badge_w = (self.m.width(badge, "sans-bold", z["step"] + 1) + 24) if badge else 0
        inner_nat = max(name.natural_width(), desc.natural_width(), badge_w)
        if width is None:
            inner = min(inner_nat, wrap or s["node_text_width"])
            name.wrap(inner)
            desc.wrap(inner)
            width = max(max(name.width, desc.width, badge_w) + 2 * s["box_pad_x"], s["min_box_width"])
        inner = width - 2 * s["box_pad_x"]
        name.wrap(inner)
        desc.wrap(inner)
        h = s["box_pad_y"] * 2 + name.height
        if badge:
            h += 8 + 24
        if desc.raw:
            h += 6 + desc.height
        return {"node": node, "name": name, "desc": desc, "badge": badge, "w": width, "h": h,
                "natural": inner_nat + 2 * s["box_pad_x"]}

    def box_svg(self, bm, x, y, nid):
        s, z = self.s, self.z
        node = bm["node"]
        role = self.role(node.get("role", "neutral"))
        out = [f"<!-- node {nid} -->"]
        out.append(el("rect", x=x, y=y, width=bm["w"], height=bm["h"], rx=s["box_radius"], fill=role["fill"],
                      stroke=role["stroke"], stroke_width=s["box_stroke"],
                      stroke_dasharray="7 5" if node.get("style") == "dashed" else None,
                      class_="box", data_id=nid))
        cx = x + bm["w"] / 2
        cy = y + s["box_pad_y"]
        out.append(bm["name"].svg(cx, cy - 2))
        cy += bm["name"].height
        if bm["badge"]:
            bw = self.m.width(bm["badge"], "sans-bold", z["step"] + 1) + 24
            cy += 8
            out.append(el("rect", x=cx - bw / 2, y=cy, width=bw, height=24, rx=12, fill=role["stroke"]))
            out.append(self.text_line([(bm["badge"], "sans-bold")], cx - (bw - 24) / 2, cy + 17, z["step"] + 1,
                                      self.c["background"]))
            cy += 24
        if bm["desc"].raw:
            out.append(bm["desc"].svg(cx, cy + 6, color=self.c["text"]))
        return "\n".join(out)

    def start_svg(self, x, y, d, nid):
        r = d / 2
        return (f"<!-- node {nid} -->\n"
                + el("circle", cx=x + r, cy=y + r, r=r, fill=self.c["line"], class_="box", data_id=nid))

    def end_svg(self, x, y, d, nid):
        """Final state: a ring around a dot."""
        r = d / 2
        return "\n".join([f"<!-- node {nid} -->",
                          el("circle", cx=x + r, cy=y + r, r=r - 1, fill=self.c["background"],
                             stroke=self.c["line"], stroke_width=2, class_="box", data_id=nid),
                          el("circle", cx=x + r, cy=y + r, r=r * 0.5, fill=self.c["line"])])

    def note_model(self, raw):
        t = self.text(raw, self.z["note"], color=self.c["text"]).wrap(self.s["note_width"] - 24)
        return {"t": t, "w": t.width + 24, "h": t.height + 20}

    def note_svg(self, nm, x, y, nid=None):
        return "\n".join([el("rect", x=x, y=y, width=nm["w"], height=nm["h"], rx=10, fill=self.c["note_fill"],
                             stroke=self.c["note_stroke"], stroke_width=1.2, class_="note", data_id=nid),
                          nm["t"].svg(x + nm["w"] / 2, y + 10, color=self.c["text"])])

    def group_plate(self, g, x, y, w, h, where="top-left"):
        """Top-left corner of the group label text and its plate rect."""
        s = self.s
        lw, lh = self.spaced_size(g["label"], self.z["group"])
        vert, horiz = where.split("-")
        lx = x + s["group_pad"] if horiz == "left" else x + w - s["group_pad"] - lw
        ly = y + s["group_label_gap"] + 2 if vert == "top" else y + h - s["group_label_gap"] - lh
        return (lx, ly), (lx - 6, ly - 2, lx + lw + 6, ly + lh)

    def group_svg(self, g, x, y, w, h, gid, labels=None, where="top-left"):
        """Frame of a group. With a `labels` list the label goes there, so the
        caller can draw it above the arrows."""
        s = self.s
        role = self.role(g.get("role", "neutral"))
        out = [f"<!-- group {gid} -->",
               el("rect", x=x, y=y, width=w, height=h, rx=s["group_radius"], fill="none", stroke=role["stroke"],
                  stroke_width=s["group_stroke"], stroke_dasharray=s["group_dash"], class_="group", data_id=gid)]
        if g.get("label"):
            # A background plate keeps the label legible where an arrow enters the group.
            (lx, ly), pr = self.group_plate(g, x, y, w, h, where)
            plate = "\n".join([f"<!-- group label {gid} -->",
                               el("rect", x=pr[0], y=pr[1], width=pr[2] - pr[0], height=pr[3] - pr[1],
                                  fill=self.c["background"], class_="plate"),
                               self.spaced_label(g["label"], lx, ly, self.z["group"], role["label"])])
            (labels if labels is not None else out).append(plate)
        return "\n".join(out)

    def header(self, d, width):
        """Optional title and caption above the figure; returns (svg, height)."""
        out, h = [], 0
        if d.get("title"):
            t = self.text(d["title"], self.z["title"], bold=True).wrap(width)
            out.append(t.svg(0, h, anchor="start"))
            h += t.height + 4
        if d.get("caption"):
            t = self.text(d["caption"], self.z["caption"], color=self.c["text"]).wrap(width)
            out.append(t.svg(0, h, anchor="start", color=self.c["text"]))
            h += t.height
        if out:
            h += 24
        return "\n".join(out), h

    def document(self, d, body, width, height):
        head, hh = self.header(d, width)
        pad = self.s["pad"]
        W, H = width + 2 * pad, height + hh + 2 * pad
        title = d.get("title") or d.get("alt") or ""
        parts = [el("svg", None, xmlns="http://www.w3.org/2000/svg", width=W, height=H,
                    viewBox=f"0 0 {fmt(W)} {fmt(H)}")[:-2] + ">"]
        if title:
            parts.append(el("title", escape(title)))
        # A white plate always: the figure reads the same on a dark page.
        parts.append(el("rect", width=W, height=H, fill=self.c["background"]))
        if head:
            parts.append(el("g", f"\n{head}\n", transform=f"translate({fmt(pad)} {fmt(pad)})"))
        parts.append(el("g", f"\n{body}\n", transform=f"translate({fmt(pad)} {fmt(pad + hh)})"))
        parts.append("</svg>\n")
        return "\n".join(parts)


class Bounds:
    def __init__(self):
        self.r = None

    def add(self, x0, y0, x1, y1):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        self.r = (x0, y0, x1, y1) if self.r is None else (
            min(self.r[0], x0), min(self.r[1], y0), max(self.r[2], x1), max(self.r[3], y1))

    def wrap(self, body):
        """Shift the body so its bounds start at 0, 0; returns (svg, w, h)."""
        x0, y0, x1, y1 = self.r
        if abs(x0) < 0.05 and abs(y0) < 0.05:
            return body, x1, y1
        return el("g", "\n" + body + "\n", transform=f"translate({fmt(-x0)} {fmt(-y0)})"), x1 - x0, y1 - y0


# ---------------------------------------------------------------- geometry helpers

def cubic(p0, p1, p2, p3, n=20):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return out


def densify(points, step=3.0):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) // step))
        out.extend((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1))
    return out


def path_points(d):
    """Sample a path made of M, L and C commands."""
    toks = d.replace(",", " ").split()
    pts, i, cur = [], 0, None
    while i < len(toks):
        c = toks[i]
        if c in ("M", "L"):
            cur = (float(toks[i + 1]), float(toks[i + 2]))
            pts.append(cur)
            i += 3
        elif c == "C":
            p = [(float(toks[i + 1 + 2 * j]), float(toks[i + 2 + 2 * j])) for j in range(3)]
            pts.extend(cubic(cur, *p))
            cur = p[2]
            i += 7
        else:
            raise ValueError(f"path command {c!r}")
    return densify(pts)


def grow(r, s):
    return (r[0] - s, r[1] - s, r[2] + s, r[3] + s)


def hit(r, p):
    return r[0] < p[0] < r[2] and r[1] < p[1] < r[3]


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def within(a, b, tol=0.0):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


def rect_dist(r, p):
    dx = max(r[0] - p[0], 0, p[0] - r[2])
    dy = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dy)


# ---------------------------------------------------------------- stack layout

def layout_stack(kit, d, opts):
    s, z = kit.s, kit.z
    nodes = d["nodes"]
    groups = d.get("groups", {})
    links = d.get("links", [])
    order = list(nodes)
    gp = s["group_pad"]

    def chain(gid):
        out = []
        while gid:
            out.append(gid)
            gid = groups[gid].get("parent")
        return out[::-1]

    chains = [chain(nodes[n].get("group")) for n in order]
    # A group must be one contiguous run of the stack.
    seen_closed = set()
    for i, ch in enumerate(chains):
        prev = chains[i - 1] if i else []
        seen_closed |= {g for g in prev if g not in ch}
        for g in ch:
            if g in seen_closed:
                raise DiagramError(f"group {g} is split; list its nodes next to each other")
    idx = {n: i for i, n in enumerate(order)}
    members = {g: [i for i, ch in enumerate(chains) if g in ch] for g in groups}

    def endpoint_index(ep, other):
        if ep in idx:
            return idx[ep]
        m = members[ep]
        return m[-1] if other > m[-1] else m[0] if other < m[0] else m[0]

    def rough_index(ep):
        return idx[ep] if ep in idx else members[ep][0]

    gap_links, side_links = {}, []
    for k, l in enumerate(links):
        a = endpoint_index(l["from"], rough_index(l["to"]))
        b = endpoint_index(l["to"], a)
        if a == b:
            raise DiagramError(f"links[{k}]: a link between a group and its own node has no layout")
        if abs(a - b) == 1 and not l.get("side"):
            gap_links.setdefault(min(a, b), []).append((k, l, a < b))
        else:
            if l.get("via"):
                raise DiagramError(f"links[{k}].via: a protocol label sits between a pair of arrows between "
                                   f"neighbours; this link runs in a side lane")
            side_links.append((k, l, a, b))

    def top(i):
        return chains[i][0] if chains[i] else None

    # Lanes: a side link whose endpoints share a top-level group runs inside
    # it. Shorter lanes run closer to the boxes, so lanes nest without crossing.
    lanes = {}
    for k, l, a, b in side_links:
        owner = top(a) if top(a) and top(a) == top(b) else None
        lanes.setdefault(owner, []).append((k, l, a, b, l.get("side", "right")))
    for owner in lanes:
        lanes[owner].sort(key=lambda x: abs(x[2] - x[3]))

    def lanes_of(owner, side):
        return [x for x in lanes.get(owner, []) if x[4] == side]

    notes = []
    for n in order:
        if nodes[n].get("note"):
            notes.append(("node", n, nodes[n].get("note_side", "right")))
    for g in groups:
        if groups[g].get("note"):
            notes.append(("group", g, groups[g].get("note_side", "right")))
    for kind, key, side in notes:
        if lanes_of(None, side):
            other = "left" if side == "right" else "right"
            raise DiagramError(f"{kind}s.{key}.note: the {side} side carries a return lane; "
                               f"set note_side = \"{other}\"")

    label_h = z["group"] * s["line_height"]
    group_top_h = s["group_label_gap"] + label_h + gp * 0.6

    def place(reserve):
        """Horizontal and vertical pass for given lane reserves inside groups."""
        models = {n: kit.box_model(nodes[n], wrap=s["box_max_width"] - 2 * s["box_pad_x"]) for n in order}
        content = 320
        for i, n in enumerate(order):
            t = top(i)
            extra = (reserve.get((t, "right"), 0) + reserve.get((t, "left"), 0)) if t else 0
            content = max(content, min(models[n]["natural"], s["box_max_width"]) + 2 * gp * len(chains[i]) + extra)
        for gid, g in groups.items():
            if g.get("label"):
                lw, _ = kit.spaced_size(g["label"], z["group"])
                depth = len(chain(gid)) - 1
                content = max(content, lw + 2 * gp * (depth + 1) + 12)

        def span(i):
            depth = len(chains[i])
            t = top(i)
            x0, x1 = gp * depth, content - gp * depth
            if t:
                x0 += reserve.get((t, "left"), 0)
                x1 -= reserve.get((t, "right"), 0)
            return x0, x1

        for i, n in enumerate(order):
            x0, x1 = span(i)
            compact = nodes[n].get("compact", nodes[n].get("role") == "human")
            w = min(models[n]["natural"], x1 - x0) if compact else x1 - x0
            models[n] = kit.box_model(nodes[n], width=max(w, s["min_box_width"]))
            models[n]["x"] = (x0 + x1 - models[n]["w"]) / 2

        gap_layout = {}
        for gi, items in gap_links.items():
            labs = [(k, l, down, kit.step_label(l.get("step"), l.get("label", ""))) for k, l, down in items]
            via = next((l.get("via") for _, l, _, _ in labs if l.get("via")), None)
            vw, vh = kit.spaced_size(via, z["protocol"]) if via else (0, 0)
            free = max(s["gap_min"], max([lab["h"] for *_, lab in labs] + [vh]) + 28)
            gap_layout[gi] = (labs, via, vw, vh, free)

        y = 0
        box_y, gap_free, group_y0, group_y1 = {}, {}, {}, {}
        for i, n in enumerate(order):
            prev = chains[i - 1] if i else []
            cur = chains[i]
            if i:
                closing = [g for g in prev if g not in cur]
                opening = [g for g in cur if g not in prev]
                y_free0 = y
                for g in reversed(closing):
                    y += gp * 0.8
                    group_y1[g] = y
                free = gap_layout.get(i - 1, (None, None, 0, 0, s["gap_min"]))[4]
                if closing or opening:
                    free = max(free, 48)
                y_free_start = y
                y += free
                for g in opening:
                    group_y0[g] = y
                    y += group_top_h
                gap_free[i - 1] = (y_free0, y_free_start, y, y_free_start + free)
            else:
                for g in cur:
                    group_y0[g] = y
                    y += group_top_h
            box_y[n] = y
            y += models[n]["h"]
        for g in reversed(chains[-1]):
            y += gp * 0.8
            group_y1[g] = y
        return dict(models=models, content=content, gap_layout=gap_layout, box_y=box_y, gap_free=gap_free,
                    group_y0=group_y0, group_y1=group_y1, height=y)

    # Attachment heights on box sides: lanes sharing a side are spread so an
    # outer lane attaches further out than an inner one and they never cross.
    attach = {}
    for owner, items in lanes.items():
        for side in ("right", "left"):
            for li, (k, l, a, b, _) in enumerate(x for x in items if x[4] == side):
                dist = li if owner else 100 + li
                attach.setdefault((min(a, b), side), []).append((k, False, dist))
                attach.setdefault((max(a, b), side), []).append((k, True, dist))
    # A note's connector takes its own place on the box side, below the lanes.
    for kind, key, side in notes:
        if kind == "node":
            attach.setdefault((idx[key], side), [])
    frac = {}
    for (i, side), lst in attach.items():
        ups = sorted((x for x in lst if x[1]), key=lambda x: x[2])
        downs = sorted((x for x in lst if not x[1]), key=lambda x: -x[2])
        seq = ups + downs
        has_note = any(kind == "node" and idx[key] == i and s_ == side for kind, key, s_ in notes)
        n = len(seq) + (1 if has_note else 0)
        for j, (k, _, _) in enumerate(seq):
            frac[(k, i)] = (j + 1) / (n + 1)
        if has_note:
            frac[("note", i, side)] = n / (n + 1)

    def lane_labels(P):
        out = {}
        for items in lanes.values():
            for k, l, a, b, _ in items:
                na, nb = order[a], order[b]
                ya = P["box_y"][na] + P["models"][na]["h"] * frac[(k, a)]
                yb = P["box_y"][nb] + P["models"][nb]["h"] * frac[(k, b)]
                out[k] = (ya, yb, kit.step_label(l.get("step"), l.get("label", ""),
                                                 max_width=max(60, abs(yb - ya) - 20)))
        return out

    def reserves(labels):
        res = {}
        for owner in lanes:
            if owner is None:
                continue
            for side in ("right", "left"):
                mine = lanes_of(owner, side)
                if mine:
                    res[(owner, side)] = 14 + sum(max(s["lane"], 8 + labels[k][2]["h"] + 10)
                                                  for k, *_ in mine)
        return res

    reserve = {(o, side): 14 + len(lanes_of(o, side)) * s["lane"]
               for o in lanes if o for side in ("right", "left") if lanes_of(o, side)}
    P = place(reserve)
    labels = lane_labels(P)
    need = reserves(labels)
    if need != reserve:
        P = place(need)
        labels = lane_labels(P)
        reserve = need
    models, content, box_y = P["models"], P["content"], P["box_y"]
    group_y0, group_y1 = P["group_y0"], P["group_y1"]
    height = P["height"]

    def group_rect(gid):
        depth = len(chain(gid)) - 1
        t = chain(gid)[0]
        x0, x1 = gp * depth, content - gp * depth
        if depth > 0:
            x0 += reserve.get((t, "left"), 0)
            x1 -= reserve.get((t, "right"), 0)
        return x0, group_y0[gid], x1, group_y1[gid]

    bb = Bounds()
    bb.add(0, 0, content, height)
    body, group_labels = [], []
    for gid in groups:
        x0, y0, x1, y1 = group_rect(gid)
        body.append(kit.group_svg(groups[gid], x0, y0, x1 - x0, y1 - y0, gid, group_labels))
    for n in order:
        m = models[n]
        body.append(kit.box_svg(m, m["x"], box_y[n], n))

    def edge_y(ep, i, bottom):
        if ep in groups:
            return group_y1[ep] if bottom else group_y0[ep]
        n = order[i]
        return box_y[n] + (models[n]["h"] if bottom else 0)

    # Gap links: a single arrow, or a request and answer pair with the
    # protocol between them.
    for gi, (labs, via, vw, vh, free) in P["gap_layout"].items():
        a, b = order[gi], order[gi + 1]
        ax0, ax1 = models[a]["x"], models[a]["x"] + models[a]["w"]
        bx0, bx1 = models[b]["x"], models[b]["x"] + models[b]["w"]
        cx = (max(ax0, bx0) + min(ax1, bx1)) / 2
        _, f0, _, f_end = P["gap_free"][gi]
        mid = (f0 + f_end) / 2
        n_links = len(labs)
        dx = max(s["pair_min_dx"], vw / 2 + 16)
        if n_links == 1:
            xs = [cx]
        elif n_links == 2:
            xs = [cx - dx, cx + dx]
        else:
            xs = [cx - dx * (n_links - 1) + 2 * dx * j for j in range(n_links)]
        ordered = sorted(labs, key=lambda x: (not x[2], x[0]))
        for j, (k, l, down, lab) in enumerate(ordered):
            x = xs[j]
            top_ep, bot_ep = (l["from"], l["to"]) if down else (l["to"], l["from"])
            y_top = edge_y(top_ep, gi, True)
            y_bot = edge_y(bot_ep, gi + 1, False)
            color = kit.role(l["color"])["stroke"] if l.get("color") else None
            pts = [(x, y_top), (x, y_bot)] if down else [(x, y_bot), (x, y_top)]
            body.append(f"<!-- link {l['from']} -> {l['to']} -->")
            body.append(kit.arrow(pts, color=color, dashed=l.get("style") == "dashed",
                                  meta={"data_from": l["from"], "data_to": l["to"], "data_edge": f"e{k}"}))
            left = x < cx
            ly = mid - lab["h"] / 2
            lx = x - 12 - lab["w"] if left else x + 12
            body.append(kit.step_label_svg(lab, lx, ly, edge=f"e{k}"))
            bb.add(lx, ly, lx + lab["w"], ly + lab["h"])
        if via:
            vx = cx if n_links >= 2 else cx - 14
            anchor = "middle" if n_links >= 2 else "end"
            body.append(kit.spaced_label(via, vx, mid - vh / 2, z["protocol"], kit.c["muted"], anchor))
            x0 = vx - vw / 2 if anchor == "middle" else vx - vw
            bb.add(x0, mid - vh / 2, x0 + vw, mid + vh / 2)

    # Side links. Lanes go outwards from the boxes; each label sits on the
    # outer side of its lane.
    for owner, items in lanes.items():
        for side in ("right", "left"):
            mine = [x for x in items if x[4] == side]
            if not mine:
                continue
            sgn = 1 if side == "right" else -1
            if owner is None:
                lx = content + 18 if side == "right" else -18
            else:
                x0g, _, x1g, _ = group_rect(owner)
                base = (x1g - gp - reserve[(owner, "right")]) if side == "right" else (x0g + gp + reserve[(owner, "left")])
                lx = base + sgn * 14
            for k, l, a, b, _ in mine:
                ya, yb, lab = labels[k]
                na, nb = order[a], order[b]
                ma, mb = models[na], models[nb]
                xa = ma["x"] + (ma["w"] if side == "right" else 0)
                xb = mb["x"] + (mb["w"] if side == "right" else 0)
                color = kit.role(l["color"])["stroke"] if l.get("color") else None
                body.append(f"<!-- side link {l['from']} -> {l['to']} -->")
                body.append(kit.arrow([(xa, ya), (lx, ya), (lx, yb), (xb, yb)], color=color,
                                      dashed=l.get("style", "dashed" if owner else "solid") == "dashed",
                                      meta={"data_from": l["from"], "data_to": l["to"], "data_edge": f"e{k}"}))
                cy = (ya + yb) / 2
                tx = lx + 8 + lab["h"] if side == "right" else lx - 8
                body.append(el("g", "\n" + kit.step_label_svg(lab, 0, -lab["h"]) + "\n",
                               transform=f"translate({fmt(tx)} {fmt(cy + lab['w'] / 2)}) rotate(-90)",
                               class_="label", data_edge=f"e{k}"))
                bb.add(tx - lab["h"], cy - lab["w"] / 2, tx, cy + lab["w"] / 2)
                bb.add(lx, ya, lx, yb)
                lx += sgn * max(s["lane"], 8 + lab["h"] + 10)

    # Notes beside an element, on a dashed connector.
    placed = {"right": [], "left": []}
    note_items = []
    for kind, key, side in notes:
        if kind == "node":
            m = models[key]
            ex = m["x"] + m["w"] if side == "right" else m["x"]
            cy = box_y[key] + m["h"] * frac[("note", idx[key], side)]
            raw = nodes[key]["note"]
        else:
            x0, y0, x1, y1 = group_rect(key)
            ex = x1 if side == "right" else x0
            cy = (y0 + y1) / 2
            raw = groups[key]["note"]
        note_items.append((cy, kind, key, side, ex, kit.note_model(raw)))
    edge_x = {"right": bb.r[2], "left": bb.r[0]}
    for cy, kind, key, side, ex, nm in sorted(note_items, key=lambda x: x[0]):
        ny = max(0, cy - nm["h"] / 2, *(b + 10 for b in placed[side]))
        placed[side].append(ny + nm["h"])
        nx = edge_x[side] + s["note_gap"] if side == "right" else edge_x[side] - s["note_gap"] - nm["w"]
        nid = f"note_{key}"
        body.append(f"<!-- note {key} -->")
        body.append(kit.note_svg(nm, nx, ny, nid))
        jy = min(max(cy, ny + 10), ny + nm["h"] - 10)
        body.append(kit.connector((ex, cy), (nx if side == "right" else nx + nm["w"], jy), key, nid))
        bb.add(nx, ny, nx + nm["w"], ny + nm["h"])

    return bb.wrap("\n".join(body + group_labels))


# ---------------------------------------------------------------- sequence layout

def layout_sequence(kit, d, opts):
    s, z = kit.s, kit.z
    nodes = d["nodes"]
    groups = d.get("groups", {})
    items = d.get("seq", [])
    ids = list(nodes)
    col = {n: i for i, n in enumerate(ids)}
    models = {n: kit.box_model(nodes[n], wrap=s["seq_node_width"]) for n in ids}
    gof = [nodes[n].get("group") for n in ids]
    gp = s["group_pad"]
    for g in groups:
        cols = [i for i, x in enumerate(gof) if x == g]
        if cols != list(range(cols[0], cols[-1] + 1)):
            raise DiagramError(f"groups.{g}: list its participants next to each other")
    loop_w, loop_gap = 32, 12  # self-message loop width and gap to its label
    border_margin = 8          # free space between a plate or note and a container border

    def same(i, j):
        return 0 <= j < len(ids) and gof[j] is not None and gof[j] == gof[i]

    def alone(a):
        """The participant is the only member of its container."""
        return gof[a] is not None and not same(a, a - 1) and not same(a, a + 1)

    def self_left(a):
        """A self-message loops right, except in the last column and where a
        container border is on the right and a neighbour of the same
        container on the left. A participant alone in its container always
        loops right: the container widens under the label instead."""
        if alone(a):
            return False
        if a == len(ids) - 1 and a > 0:
            return True
        return gof[a] is not None and not same(a, a + 1) and same(a, a - 1)

    # Column gaps start from the header widths and the containers, and widen
    # for message labels.
    gaps = []
    for i in range(len(ids) - 1):
        g = models[ids[i]]["w"] / 2 + models[ids[i + 1]]["w"] / 2 + s["seq_column_gap"]
        if gof[i] != gof[i + 1]:
            g += (gp if gof[i] else 0) + (gp if gof[i + 1] else 0)
        gaps.append(g)
    prepared = []
    frames = []
    for k, it in enumerate(items):
        kind = seq_kind(f"seq[{k}]", it)
        if kind == "msg":
            a, b = col[it["from"]], col[it["to"]]
            wrap = s["seq_self_width"] if a == b else s["seq_label_width"]
            lab = kit.step_label(it.get("step"), it.get("label", ""), max_width=wrap)
            prepared.append(("msg", it, a, b, lab))
            need = loop_w + loop_gap + lab["w"] + 30
            if a == b and alone(a):
                pass  # the container widens under the label below
            elif a == b and not self_left(a) and a < len(ids) - 1:
                gaps[a] = max(gaps[a], need)
            elif a == b and a > 0:
                # The last column loops to the left, so the figure does not grow sideways.
                gaps[a - 1] = max(gaps[a - 1], need)
            elif a != b:
                lo, hi = min(a, b), max(a, b)
                deficit = lab["w"] + 40 - sum(gaps[lo:hi])
                if deficit > 0:
                    gaps[hi - 1] += deficit
        elif kind in ("alt", "opt"):
            frames.append(kind)
            prepared.append((kind, it, None, None, kit.text(it[kind], z["note"], bold=True).wrap(10_000)))
        elif kind == "else":
            if not frames:
                raise DiagramError(f"seq[{k}]: else outside alt")
            if frames[-1] != "alt":
                raise DiagramError(f"seq[{k}]: else belongs to alt; an opt frame has one branch")
            prepared.append(("else", it, None, None, kit.text(it["else"], z["note"], bold=True).wrap(10_000)))
        elif kind == "end":
            if not frames:
                raise DiagramError(f"seq[{k}]: end outside alt or opt")
            frames.pop()
            prepared.append(("end", it, None, None, None))
        elif kind == "note":
            if "on" in it:
                a, side, nm = col[it["on"]], it.get("side", "right"), kit.note_model(it["note"])
                if gof[a] is not None:
                    # The note stays inside the participant's container: it
                    # moves to the side of a neighbour from the same container.
                    fits = {"right": same(a, a + 1), "left": same(a, a - 1)}
                    if not fits[side]:
                        side = "left" if side == "right" else "right"
                    if not fits[side]:
                        raise DiagramError(f"seq[{k}]: the note on {it['on']} would cover the border of "
                                           f"{gof[a]}; a container needs a second participant to hold it")
                    i = a if side == "right" else a - 1
                    gaps[i] = max(gaps[i], nm["w"] + 10 + border_margin)
                prepared.append(("note_on", it, a, side, nm))
            else:
                over = [col[x] for x in it.get("over", [ids[0], ids[-1]])]
                lo, hi = min(over), max(over)
                # A note over participants on both sides of a container border
                # would hide that border; it goes under the containers instead.
                inside = set(gof[lo:hi + 1])
                cross = any(g in inside and (len(inside) > 1 or any(x == g for x in gof[:lo] + gof[hi + 1:]))
                            for g in groups)
                prepared.append(("note", it, lo, hi, "foot" if cross else None))
        elif kind == "divider":
            if frames:
                raise DiagramError(f"seq[{k}]: a divider cannot sit inside {frames[-1]}")
            prepared.append(("divider", it, None, None, kit.text(it["divider"], z["note"], bold=True).wrap(10_000)))
    if frames:
        raise DiagramError(f"{frames[-1]} without end")
    foot_at = next((k for k, p in enumerate(prepared) if p[0] == "note" and p[4] == "foot"), None)
    if foot_at is not None and any(p[0] != "note" or p[4] != "foot" for p in prepared[foot_at:]):
        raise DiagramError(f"seq: the note {prepared[foot_at][1]['note'][:30]!r} spans a container border; "
                           "narrow its `over` to one side or put it after the last message")

    def positions():
        xs = [0.0]
        for g in gaps:
            xs.append(xs[-1] + g)
        return xs

    # Containers must fit their label.
    xs = positions()
    ext = {}
    for g, grp in groups.items():
        cols = [i for i, x in enumerate(gof) if x == g]
        c0, c1 = cols[0], cols[-1]
        lw = (kit.spaced_size(grp["label"], z["group"])[0] if grp.get("label") else 0) + 2 * gp + 12
        have = xs[c1] + models[ids[c1]]["w"] / 2 - xs[c0] + models[ids[c0]]["w"] / 2 + 2 * gp
        deficit = lw - have
        if deficit > 0:
            if c1 > c0:
                for i in range(c0, c1):
                    gaps[i] += deficit / (c1 - c0)
            else:
                ext[g] = deficit
                if c1 < len(ids) - 1:
                    gaps[c1] += deficit
    # A container with one participant also widens under the labels of that
    # participant's self-messages, so a label never sits on its border.
    for g in groups:
        cols = [i for i, x in enumerate(gof) if x == g]
        if len(cols) != 1:
            continue
        a = cols[0]
        half = models[ids[a]]["w"] / 2 + gp
        for kind, it, a2, b2, lab in prepared:
            if kind != "msg" or a2 != a or b2 != a:
                continue
            need = loop_w + loop_gap + lab["w"] + 4 + border_margin - half
            if need > ext.get(g, 0):
                ext[g] = need
        if a < len(ids) - 1:
            nxt = gp if gof[a + 1] else 0
            want = half + ext.get(g, 0) + nxt + s["seq_column_gap"] + models[ids[a + 1]]["w"] / 2
            gaps[a] = max(gaps[a], want)
    xs = positions()

    def borders(xs):
        """Container border x positions, each with the column it moves with."""
        out = []
        for g in groups:
            cols = [i for i, x in enumerate(gof) if x == g]
            c0, c1 = cols[0], cols[-1]
            out.append((xs[c0] - models[ids[c0]]["w"] / 2 - gp, c0))
            out.append((xs[c1] + models[ids[c1]]["w"] / 2 + gp + ext.get(g, 0), c1))
        return out

    def segments(a, b, xs):
        """Stretches of a message between the container borders it crosses."""
        lo, hi = min(a, b), max(a, b)
        pts = sorted([(xs[lo], lo)] + [(x, c) for x, c in borders(xs) if xs[lo] < x < xs[hi]] + [(xs[hi], hi)])
        return [(p, q, cp, cq) for (p, cp), (q, cq) in zip(pts, pts[1:])]

    def clear_x(want, w, lo, hi):
        """Left edge nearest to `want` for a plate of width `w` inside
        [lo, hi] that keeps clear of every container border."""
        free = [(lo, hi)]
        for x, _ in borders(xs):
            free = [part for p, q in free for part in ((p, min(q, x - border_margin)), (max(p, x + border_margin), q))
                    if part[1] > part[0]]
        best = None
        for p, q in free:
            if q - p >= w:
                x = min(max(want, p), q - w)
                if best is None or abs(x - want) < abs(best - want):
                    best = x
        # Nothing fits: the plate starts after the last border, and the
        # caller widens what holds it.
        return best if best is not None else (free[-1][0] if free else want)

    # A message label crossing a container border sits between two borders,
    # never on one: the gap of the longest stretch that can grow widens until
    # the label fits there.
    for _ in range(4 * len(prepared) + 4):
        grown = False
        for kind, it, a, b, lab in prepared:
            if kind != "msg" or a == b:
                continue
            segs = segments(a, b, xs)
            need = lab["w"] + 8 + 2 * border_margin
            if len(segs) == 1 or any(q - p >= need for p, q, _, _ in segs):
                continue
            free = [sg for sg in segs if sg[2] < sg[3]]
            p, q, cp, cq = max(free, key=lambda sg: sg[1] - sg[0])
            gaps[cq - 1] += need - (q - p)
            xs, grown = positions(), True
        if not grown:
            break

    band = (s["group_label_gap"] + z["group"] * s["line_height"] + gp * 0.6) if groups else 0
    head_h = max(m["h"] for m in models.values())

    # Vertical pass: rows carry their horizontal extent so frames can wrap them.
    y = band + head_h + 24
    rows, done_frames, open_frames = [], [], []
    for kind, it, a, b, extra in prepared:
        if kind == "msg":
            lab = extra
            if a == b:
                hgt = max(lab["h"], 16) + 10
                left = self_left(a)
                e = (xs[a] - loop_w - loop_gap - lab["w"] - 4, xs[a]) if left else \
                    (xs[a], xs[a] + loop_w + loop_gap + lab["w"] + 4)
                rows.append(("self", it, a, lab, y, e))
                y += hgt + 8 + s["seq_row_gap"]
            else:
                y_arrow = y + lab["h"] + 8
                rows.append(("msg", it, (a, b), lab, y_arrow, (min(xs[a], xs[b]), max(xs[a], xs[b]))))
                y = y_arrow + s["seq_row_gap"] + 8
        elif kind in ("alt", "opt"):
            open_frames.append({"kind": kind, "y0": y, "label": extra, "rows": [], "elses": [],
                                "depth": len(open_frames)})
            y += extra.height + 18
            continue
        elif kind == "else":
            open_frames[-1]["elses"].append((y + 4, extra))
            y += extra.height + 22
            continue
        elif kind == "end":
            f = open_frames.pop()
            f["y1"] = y
            done_frames.append(f)
            y += 14
            continue
        elif kind == "note" and extra == "foot":
            continue
        elif kind == "note":
            t = kit.text(it["note"], z["note"], color=kit.c["text"])
            t.wrap(max(xs[b] - xs[a] + 88, 240))
            w = max(xs[b] - xs[a] + 120, t.width + 32)
            cx = (xs[a] + xs[b]) / 2
            rows.append(("note", it, None, {"t": t, "w": w, "h": t.height + 24}, y, (cx - w / 2, cx + w / 2)))
            y += t.height + 24 + s["seq_row_gap"]
        elif kind == "note_on":
            nm, side = extra, b
            x0 = xs[a] + 10 if side == "right" else xs[a] - 10 - nm["w"]
            rows.append(("note", it, None, nm, y, (x0, x0 + nm["w"])))
            y += nm["h"] + s["seq_row_gap"]
        elif kind == "divider":
            rows.append(("divider", it, None, extra, y, None))
            y += extra.height + 10 + s["seq_row_gap"] + 8
            continue
        for f in open_frames:
            f["rows"].append(rows[-1])
    bottom = y + 6

    lo_x = min(xs[i] - models[n]["w"] / 2 for i, n in enumerate(ids))
    hi_x = max(xs[i] + models[n]["w"] / 2 for i, n in enumerate(ids))
    body = []

    # Participant containers, behind everything.
    box_bottom = bottom + 8 if groups else bottom
    group_labels = []
    for g, grp in groups.items():
        cols = [i for i, x in enumerate(gof) if x == g]
        c0, c1 = cols[0], cols[-1]
        x0 = xs[c0] - models[ids[c0]]["w"] / 2 - gp
        x1 = xs[c1] + models[ids[c1]]["w"] / 2 + gp + ext.get(g, 0)
        body.append(kit.group_svg(grp, x0, 0, x1 - x0, box_bottom, g, group_labels))
        lo_x, hi_x = min(lo_x, x0), max(hi_x, x1)
    body.extend(group_labels)
    fy = box_bottom + 12
    for kind, it, a, b, extra in prepared:
        if kind == "note" and extra == "foot":
            t = kit.text(it["note"], z["note"], color=kit.c["text"])
            t.wrap(max(xs[b] - xs[a] + 88, 240))
            w = max(xs[b] - xs[a] + 120, t.width + 32)
            cx = (xs[a] + xs[b]) / 2
            rows.append(("note", it, None, {"t": t, "w": w, "h": t.height + 24}, fy, (cx - w / 2, cx + w / 2)))
            fy += t.height + 24 + s["seq_row_gap"]
    foot_bottom = fy - s["seq_row_gap"] if fy > box_bottom + 12 else box_bottom

    for i, n in enumerate(ids):
        body.append(el("line", x1=xs[i], y1=band + models[n]["h"], x2=xs[i], y2=bottom, stroke=kit.c["lifeline"],
                       stroke_width=1.5, stroke_dasharray="4 5"))

    # Frames: alt dashed, opt dotted, wrapping their rows; condition labels
    # sit on a plate above the lifelines.
    plates = []
    # Geometry first, innermost frames first, so an outer frame can grow
    # around an inner one that grew for its label.
    for f in sorted(done_frames, key=lambda f: -f["depth"]):
        ex = [r[5] for r in f["rows"] if r[5]] or [(xs[0], xs[-1])]
        inset = 14 * f["depth"]
        x0 = min(e[0] for e in ex) - 44 + inset
        x1 = max(e[1] for e in ex) + 24 - inset
        x1 = max(x1, x0 + max([f["label"].width] + [t.width for _, t in f["elses"]]) + 40)
        for g in done_frames:
            if g["depth"] > f["depth"] and f["y0"] <= g["y0"] and g["y1"] <= f["y1"]:
                x1 = max(x1, g["x1"] + 14)
        # Condition labels keep clear of container borders; a frame too
        # narrow for that grows to the right.
        labels = [(f["y0"] + 8, f["label"])] + [(ey + 6, et) for ey, et in f["elses"]]
        f["placed"] = []
        for ly, lt in labels:
            px = clear_x(x0 + 8, lt.width + 12, x0 + 8, x1 - 8)
            x1 = max(x1, px + lt.width + 12 + 8)
            f["placed"].append((px, ly, lt))
        # A frame edge never runs along a container border.
        for b, _ in borders(xs):
            if abs(x0 - b) < border_margin:
                x0 = b - border_margin
            if abs(x1 - b) < border_margin:
                x1 = b + border_margin
        f["x0"], f["x1"] = x0, x1
    for f in sorted(done_frames, key=lambda f: f["depth"]):
        x0, x1 = f["x0"], f["x1"]
        lo_x, hi_x = min(lo_x, x0), max(hi_x, x1)
        opt = f["kind"] == "opt"
        body.append(f"<!-- frame {f['kind']} -->")
        body.append(el("rect", x=x0, y=f["y0"], width=x1 - x0, height=f["y1"] - f["y0"], rx=10, fill="none",
                       stroke=kit.c["muted"], stroke_width=2 if opt else 1.5,
                       stroke_dasharray=s["opt_dash"] if opt else s["frame_dash"],
                       stroke_linecap="round" if opt else None, class_="frame", data_kind=f["kind"]))
        for ey, et in f["elses"]:
            body.append(el("line", x1=x0, y1=ey, x2=x1, y2=ey, stroke=kit.c["muted"], stroke_width=1.2,
                           stroke_dasharray="4 4"))
        for px, ly, lt in f["placed"]:
            plates.append(el("rect", x=px, y=ly - 1, width=lt.width + 12, height=lt.height + 2,
                             fill=kit.c["background"], class_="plate"))
            plates.append(lt.svg(px + 6, ly, anchor="start", color=kit.c["muted"]))
    body.extend(plates)

    for i, n in enumerate(ids):
        m = models[n]
        body.append(kit.box_svg(m, xs[i] - m["w"] / 2, band, n))

    for kind, it, ab, lab, yy, e in rows:
        if kind == "divider":
            continue
        lo_x, hi_x = min(lo_x, e[0]), max(hi_x, e[1])

    for k, (kind, it, ab, lab, yy, e) in enumerate(rows):
        color = kit.role(it["color"])["stroke"] if it.get("color") else None
        dashed = it.get("style") == "dashed"
        if kind == "msg":
            a, b = ab
            xa, xb = xs[a], xs[b]
            sgn = 1 if xb > xa else -1
            body.append(f"<!-- message {it['from']} -> {it['to']} -->")
            body.append(kit.arrow([(xa + sgn * 2, yy), (xb - sgn * 2, yy)], color=color, dashed=dashed,
                                  meta={"data_from": it["from"], "data_to": it["to"], "data_edge": f"m{k}"}))
            segs = segments(a, b, xs)
            fit = [sg for sg in segs if sg[1] - sg[0] >= lab["w"] + 8 + 2 * border_margin] or segs
            p, q, _, _ = max(fit, key=lambda sg: sg[1] - sg[0])
            lx, ly = (p + q) / 2 - lab["w"] / 2, yy - lab["h"] - 7
            body.append(el("rect", x=lx - 4, y=ly - 1, width=lab["w"] + 8, height=lab["h"] + 2,
                           fill=kit.c["background"], class_="plate"))
            body.append(kit.step_label_svg(lab, lx, ly, edge=f"m{k}"))
        elif kind == "self":
            x = xs[ab]
            hgt = max(lab["h"], 16) + 10
            y0 = yy + 4
            body.append(f"<!-- self {it['from']} -->")
            sgn = -1 if e[1] == x else 1
            body.append(kit.arrow([(x + sgn * 2, y0), (x + sgn * loop_w, y0), (x + sgn * loop_w, y0 + hgt),
                                   (x + sgn * 3, y0 + hgt)], color=color, dashed=dashed,
                                  meta={"data_from": it["from"], "data_to": it["to"], "data_edge": f"m{k}"}))
            lx = x + loop_w + loop_gap if sgn > 0 else x - loop_w - loop_gap - lab["w"]
            ly = y0 + (hgt - lab["h"]) / 2
            body.append(el("rect", x=lx - 4, y=ly - 1, width=lab["w"] + 8, height=lab["h"] + 2,
                           fill=kit.c["background"], class_="plate"))
            body.append(kit.step_label_svg(lab, lx, ly, edge=f"m{k}"))
        elif kind == "note":
            x0, x1 = e
            body.append("<!-- note -->")
            body.append(el("rect", x=x0, y=yy, width=x1 - x0, height=lab["h"], rx=10, fill=kit.c["note_fill"],
                           stroke=kit.c["note_stroke"], stroke_width=1.2, class_="note"))
            body.append(lab["t"].svg((x0 + x1) / 2, yy + (lab["h"] - lab["t"].height) / 2, color=kit.c["text"]))
        elif kind == "divider":
            t = lab
            h = t.height + 10
            cy = yy + h / 2
            cx = (xs[0] + xs[-1]) / 2
            w = t.width + 28
            # The pill moves to the nearest place clear of every container border.
            cx = clear_x(cx - w / 2, w, lo_x, hi_x) + w / 2
            body.append("<!-- divider -->")
            body.append(el("line", x1=lo_x, y1=cy, x2=hi_x, y2=cy, stroke=kit.c["muted"], stroke_width=1.2))
            body.append(el("rect", x=cx - w / 2, y=yy, width=w, height=h, rx=h / 2, fill=kit.c["note_fill"],
                           stroke=kit.c["muted"], stroke_width=1.2, class_="plate"))
            body.append(t.svg(cx, yy + 5, color=kit.c["ink"]))

    bb = Bounds()
    bb.add(lo_x, 0, hi_x, foot_bottom)
    return bb.wrap("\n".join(body))


# ---------------------------------------------------------------- graph layout

def graphviz_version():
    try:
        res = subprocess.run(["dot", "-V"], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise DiagramError("graph layout needs Graphviz `dot` on PATH")
    m = re.search(r"version (\S+)", res.stderr + res.stdout)
    return m.group(1) if m else "unknown"


def layout_graph(kit, d, opts):
    s, z = kit.s, kit.z
    nodes = d["nodes"]
    groups = d.get("groups", {})
    links = d.get("links", [])
    version = graphviz_version()
    if version != GRAPHVIZ_PIN and not opts.get("graphviz_any"):
        raise DiagramError(f"graph layout is pinned to Graphviz {GRAPHVIZ_PIN}, found {version}; another version "
                           f"places nodes differently and the SVG will not match the committed one. Install "
                           f"{GRAPHVIZ_PIN}, or pass --graphviz-any for a draft")
    direction = d.get("direction", "TB")
    models = {}
    for n, node in nodes.items():
        shape = node.get("shape", "box")
        if shape == "start":
            models[n] = {"w": 22, "h": 22}
        elif shape == "end":
            models[n] = {"w": 26, "h": 26}
        else:
            models[n] = kit.box_model(node)
    if d.get("uniform_width"):
        # One width per column reads as a column, as in the stack layout;
        # without columns every box gets the same width.
        any_col = any(nodes[n].get("column") for n in nodes)
        cols = {}
        for n, node in nodes.items():
            if node.get("shape", "box") == "box" and (node.get("column") or not any_col):
                cols.setdefault(node.get("column", ""), []).append(n)
        for ns in cols.values():
            w = max(models[n]["w"] for n in ns)
            for n in ns:
                models[n] = kit.box_model(nodes[n], width=w)
    notes = {n: kit.note_model(node["note"]) for n, node in nodes.items() if node.get("note")}
    labs = [kit.step_label(l.get("step"), l.get("label", "")) for l in links]
    vias = [l.get("via") for l in links]
    blocks = []
    for k, l in enumerate(links):
        lw, lh = labs[k]["w"], labs[k]["h"]
        if vias[k]:
            vw, vh = kit.spaced_size(vias[k], z["protocol"])
            lw, lh = max(lw, vw), lh + vh + 4
        blocks.append((lw, lh) if (labs[k]["text"].raw or labs[k]["step"] is not None or vias[k]) else None)

    def q(x):
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'

    def inch(v):
        return f"{v / 72:.4f}"

    def fixed_label(w, h):
        return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0" CELLSPACING="0"><TR>'
                f'<TD FIXEDSIZE="TRUE" WIDTH="{max(1, round(w))}" HEIGHT="{max(1, round(h))}"></TD></TR></TABLE>>')

    children = {}
    for gid, g in groups.items():
        children.setdefault(g.get("parent"), []).append(gid)

    def source(loc):
        lines = ["digraph G {",
                 f"  graph [rankdir={direction}, nodesep={fmt(s['graph_nodesep'])}, "
                 f"ranksep={fmt(s['graph_ranksep'])}, splines={d.get('splines', 'spline')}, "
                 f"compound=true, newrank=true, fontsize=1];",
                 '  node [shape=box, fixedsize=true, label="", margin=0];',
                 "  edge [arrowsize=0.6];"]

        def emit(parent, indent):
            for gid in children.get(parent, []):
                g = groups[gid]
                w, h = kit.spaced_size(g.get("label") or " ", z["group"])
                lines.append(f"{indent}subgraph {q('cluster_' + gid)} {{")
                lines.append(f"{indent}  label={fixed_label(w + 12, h + s['group_label_gap'])}; labeljust=l; "
                             f"labelloc={loc.get(gid, 't')}; margin={fmt(s['group_pad'])};")
                emit(gid, indent + "  ")
                lines.append(f"{indent}}}")
            for n, node in nodes.items():
                if node.get("group") == parent:
                    m = models[n]
                    colattr = f", group={q(node['column'])}" if node.get("column") else ""
                    lines.append(f"{indent}{q(n)} [width={inch(m['w'])}, height={inch(m['h'])}{colattr}];")
                    if n in notes:
                        lines.append(f"{indent}{q('note:' + n)} [width={inch(notes[n]['w'])}, "
                                     f"height={inch(notes[n]['h'])}];")

        emit(None, "  ")
        for rank in d.get("same_rank", []):
            lines.append("  { rank=same; " + "; ".join(q(x) for x in rank) + "; }")
        for j, n in enumerate(notes):
            lines.append(f"  {{ rank=same; {q(n)}; {q('note:' + n)}; }}")
            lines.append(f"  {q(n)} -> {q('note:' + n)} [id={q('n' + str(j))}, arrowhead=none];")
        for k, l in enumerate(links):
            attrs = [f"id={q('e' + str(k))}"]
            if blocks[k]:
                attrs.append(f"label={fixed_label(blocks[k][0] + 8, blocks[k][1] + 4)}")
            if l.get("constraint") is False:
                attrs.append("constraint=false")
            lines.append(f"  {q(l['from'])} -> {q(l['to'])} [{', '.join(attrs)}];")
        lines.append("}")
        return "\n".join(lines)

    def run(loc):
        res = subprocess.run(["dot", "-Tjson"], input=source(loc), capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise DiagramError("dot failed: " + res.stderr.strip())
        g = json.loads(res.stdout)
        bb = [float(v) for v in g["bb"].split(",")]
        H = bb[3]

        def pt(sx, sy):
            return float(sx) - bb[0], H - float(sy)

        L = {"clusters": {}, "pos": {}, "edges": {}, "notes": {}}
        for o in g.get("objects", []):
            name = o.get("name", "")
            if name.startswith("cluster_") and "bb" in o:
                x0, y0, x1, y1 = (float(v) for v in o["bb"].split(","))
                L["clusters"][name[len("cluster_"):]] = (x0 - bb[0], H - y1, x1 - bb[0], H - y0)
            elif "pos" in o:
                if name in nodes:
                    L["pos"][name] = pt(*o["pos"].split(","))
                elif name.startswith("note:"):
                    L["notes"][name[5:]] = pt(*o["pos"].split(","))
        for e in g.get("edges", []):
            eid = e.get("id", "")
            if not eid.startswith("e"):
                continue
            ctrl, end = [], None
            for p in e["pos"].split():
                if p.startswith("e,"):
                    end = pt(*p[2:].split(","))
                elif not p.startswith("s,"):
                    ctrl.append(pt(*p.split(",")))
            dpath = f"M {fmt(ctrl[0][0])} {fmt(ctrl[0][1])}"
            for i in range(1, len(ctrl) - 2, 3):
                dpath += " C " + " ".join(f"{fmt(a)} {fmt(b)}" for a, b in ctrl[i:i + 3])
            before, tip = (ctrl[-1], end) if end else (ctrl[-2], ctrl[-1])
            if end:
                dpath += f" L {fmt(end[0])} {fmt(end[1])}"
            lp = pt(*e["lp"].split(",")) if "lp" in e else None
            L["edges"][int(eid[1:])] = {"d": dpath, "before": before, "tip": tip, "lp": lp,
                                         "pts": path_points(dpath)}
        return L

    def box_rect(n, L):
        x, y = L["pos"][n]
        m = models[n]
        return (x - m["w"] / 2, y - m["h"] / 2, x + m["w"] / 2, y + m["h"] / 2)

    def note_rect(n, L):
        x, y = L["notes"][n]
        nm = notes[n]
        return (x - nm["w"] / 2, y - nm["h"] / 2, x + nm["w"] / 2, y + nm["h"] / 2)

    def label_spots(L):
        """Cluster label plates: top-left first, then the other corners of the
        band dot reserved. A plate must not cover an arrow or a box."""
        spots, blocked = {}, []
        boxes = [box_rect(n, L) for n in nodes] + [note_rect(n, L) for n in notes]
        for gid, r in L["clusters"].items():
            g = groups[gid]
            if not g.get("label"):
                continue
            vert = loc.get(gid, "t")
            corners = ["top-left", "top-right"] if vert == "t" else ["bottom-left", "bottom-right"]
            for where in corners:
                _, pr = kit.group_plate(g, r[0], r[1], r[2] - r[0], r[3] - r[1], where)
                gr = grow(pr, 3)
                if any(hit(gr, p) for e in L["edges"].values() for p in e["pts"]):
                    continue
                if any(overlap(pr, b) for b in boxes):
                    continue
                spots[gid] = where
                break
            else:
                blocked.append(gid)
        return spots, blocked

    loc = {}
    L = run(loc)
    spots, blocked = label_spots(L)
    if blocked:
        loc = {gid: "b" for gid in blocked}
        L2 = run(loc)
        spots2, blocked2 = label_spots(L2)
        if len(blocked2) < len(blocked):
            L, spots, blocked = L2, spots2, blocked2
        else:
            loc = {}
    for gid in blocked:
        spots[gid] = "top-left"  # the lint names the crossing

    # Edge labels: placed beside their own arrow, at the height (or, left to
    # right, the position) dot chose, on whichever side is free.
    boxes = [box_rect(n, L) for n in nodes] + [note_rect(n, L) for n in notes]
    plates = []
    for gid, where in spots.items():
        r = L["clusters"][gid]
        plates.append(kit.group_plate(groups[gid], r[0], r[1], r[2] - r[0], r[3] - r[1], where)[1])
    placed = []
    label_at = {}
    for k, e in sorted(L["edges"].items()):
        if not blocks[k] or not e["lp"]:
            continue
        bw, bh = blocks[k]
        lx, ly = e["lp"]
        # The label sits just beside the stretch of its arrow nearest to the
        # place dot reserved for it: to the side where the arrow runs along
        # the label, above or below where it runs across.
        qx, qy = min(e["pts"], key=lambda p: math.hypot(p[0] - lx, p[1] - ly))
        near = [p for p in e["pts"] if math.hypot(p[0] - qx, p[1] - qy) <= 25]
        xr = max(p[0] for p in near) - min(p[0] for p in near)
        yr = max(p[1] for p in near) - min(p[1] for p in near)
        if yr >= xr:
            band = [p[0] for p in e["pts"] if abs(p[1] - qy) <= bh / 2 + 2 and abs(p[0] - qx) <= 60]
            cands = [(max(band) + 8, qy - bh / 2), (min(band) - 8 - bw, qy - bh / 2)]
        else:
            band = [p[1] for p in e["pts"] if abs(p[0] - qx) <= bw / 2 + 2 and abs(p[1] - qy) <= 60]
            cands = [(qx - bw / 2, min(band) - 6 - bh), (qx - bw / 2, max(band) + 6)]
        cands.append((lx - bw / 2, ly - bh / 2))
        others = [p for j, o in L["edges"].items() if j != k for p in o["pts"]]

        def free(r):
            if any(overlap(grow(r, 2), b) for b in boxes + plates + placed):
                return False
            if any(hit(grow(r, 2), p) for p in others) or any(hit(grow(r, 1), p) for p in e["pts"]):
                return False
            for c in L["clusters"].values():
                if overlap(grow(r, 4), c) and not within(grow(r, 4), c):
                    return False
            return True

        chosen = cands[0]
        for cx, cy in cands:
            if free((cx, cy, cx + bw, cy + bh)):
                chosen = (cx, cy)
                break
        label_at[k] = chosen
        placed.append((chosen[0], chosen[1], chosen[0] + bw, chosen[1] + bh))

    bb = Bounds()
    body = [f"<!-- graphviz {version} -->"]
    group_labels = []
    for gid in L["clusters"]:
        x0, y0, x1, y1 = L["clusters"][gid]
        body.append(kit.group_svg(groups[gid], x0, y0, x1 - x0, y1 - y0, gid, group_labels,
                                  spots.get(gid, "top-left")))
        bb.add(x0, y0, x1, y1)
    for n in nodes:
        r = box_rect(n, L)
        shape = nodes[n].get("shape", "box")
        if shape == "start":
            body.append(kit.start_svg(r[0], r[1], models[n]["w"], n))
        elif shape == "end":
            body.append(kit.end_svg(r[0], r[1], models[n]["w"], n))
        else:
            body.append(kit.box_svg(models[n], r[0], r[1], n))
        bb.add(*r)
    for n in notes:
        r, b = note_rect(n, L), box_rect(n, L)
        nid = f"note_{n}"
        body.append(f"<!-- note {n} -->")
        body.append(kit.note_svg(notes[n], r[0], r[1], nid))
        if r[0] >= b[2]:
            a_pt, b_pt = (b[2], (b[1] + b[3]) / 2), (r[0], (b[1] + b[3]) / 2)
        elif r[2] <= b[0]:
            a_pt, b_pt = (b[0], (b[1] + b[3]) / 2), (r[2], (b[1] + b[3]) / 2)
        elif r[1] >= b[3]:
            a_pt, b_pt = ((b[0] + b[2]) / 2, b[3]), ((b[0] + b[2]) / 2, r[1])
        else:
            a_pt, b_pt = ((b[0] + b[2]) / 2, b[1]), ((b[0] + b[2]) / 2, r[3])
        body.append(kit.connector(a_pt, b_pt, n, nid))
        bb.add(*r)
    for k, e in sorted(L["edges"].items()):
        l = links[k]
        color = kit.role(l["color"])["stroke"] if l.get("color") else kit.c["line"]
        body.append(f"<!-- link {l['from']} -> {l['to']} -->")
        body.append(kit.path_arrow(e["d"], e["before"], e["tip"], color, l.get("style") == "dashed",
                                   meta={"data_from": l["from"], "data_to": l["to"], "data_edge": f"e{k}"}))
        for p in e["pts"]:
            bb.add(p[0], p[1], p[0], p[1])
        if k in label_at:
            x, y = label_at[k]
            lab = labs[k]
            parts = []
            if lab["text"].raw or lab["step"] is not None:
                parts.append(kit.step_label_svg(lab, x, y))
            if vias[k]:
                parts.append(kit.spaced_label(vias[k], x, y + lab["h"] + 4, z["protocol"], kit.c["muted"]))
            body.append(el("g", "\n" + "\n".join(parts) + "\n", class_="label", data_edge=f"e{k}"))
            bb.add(x, y, x + blocks[k][0], y + blocks[k][1])
    return bb.wrap("\n".join(body + group_labels))


LAYOUTS = {"stack": layout_stack, "sequence": layout_sequence, "graph": layout_graph}


# ---------------------------------------------------------------- geometry lint

def _transform(spec):
    m = (1, 0, 0, 1, 0, 0)
    for op, args in re.findall(r"(translate|rotate)\(([^)]*)\)", spec or ""):
        v = [float(x) for x in args.replace(",", " ").split()]
        if op == "translate":
            n = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        else:
            a = math.radians(v[0])
            n = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
        m = _mul(m, n)
    return m


def _mul(m, n):
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _apply(m, p):
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


def _box(m, x0, y0, x1, y1):
    pts = [_apply(m, p) for p in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def read_geometry(svg, kit):
    """Rectangles of boxes, plates, notes, groups, frames, texts and the
    sampled points of every arrow, in the SVG's own coordinates."""
    root = ET.fromstring(svg)
    G = {"W": float(root.get("width")), "H": float(root.get("height")), "boxes": [], "notes": [], "plates": [],
         "steps": [], "groups": [], "frames": [], "texts": [], "edges": [], "other": []}

    def num(e, k, default=0.0):
        v = e.get(k)
        return float(v) if v is not None else default

    def walk(node, m, edge):
        for e in node:
            tag = e.tag.replace(SVG_NS, "")
            cls = e.get("class")
            mm = _mul(m, _transform(e.get("transform")))
            if tag == "g":
                walk(e, mm, e.get("data-edge") if cls == "label" else edge)
            elif tag == "rect":
                r = _box(mm, num(e, "x"), num(e, "y"), num(e, "x") + num(e, "width"), num(e, "y") + num(e, "height"))
                item = {"r": r, "id": e.get("data-id"), "edge": edge}
                {"box": G["boxes"], "note": G["notes"], "plate": G["plates"], "group": G["groups"],
                 "frame": G["frames"], "step": G["steps"]}.get(cls, G["other"]).append(item)
            elif tag == "circle":
                cx, cy, rr = num(e, "cx"), num(e, "cy"), num(e, "r")
                item = {"r": _box(mm, cx - rr, cy - rr, cx + rr, cy + rr), "id": e.get("data-id"), "edge": edge}
                {"box": G["boxes"], "step": G["steps"]}.get(cls, G["other"]).append(item)
            elif tag == "path":
                pts = [_apply(mm, p) for p in path_points(e.get("d"))]
                if cls in ("edge", "connector"):
                    G["edges"].append({"pts": pts, "from": e.get("data-from"), "to": e.get("data-to"),
                                       "edge": e.get("data-edge"), "cls": cls})
                else:
                    G["other"].append({"r": (min(p[0] for p in pts), min(p[1] for p in pts),
                                             max(p[0] for p in pts), max(p[1] for p in pts))})
            elif tag == "line":
                G["other"].append({"r": _box(mm, num(e, "x1"), num(e, "y1"), num(e, "x2"), num(e, "y2"))})
            elif tag == "polygon":
                pts = [_apply(mm, tuple(float(v) for v in p.split(","))) for p in e.get("points").split()]
                G["other"].append({"r": (min(p[0] for p in pts), min(p[1] for p in pts),
                                         max(p[0] for p in pts), max(p[1] for p in pts))})
            elif tag == "text":
                size = num(e, "font-size")
                spacing = num(e, "letter-spacing") / size
                cur, x0, x1, content = num(e, "x"), None, None, []
                for sp in e.iter(SVG_NS + "tspan"):
                    if sp.get("x") is not None:
                        cur = float(sp.get("x"))
                    face = ("mono" if "Mono" in (sp.get("font-family") or "") else "sans") + \
                           ("-bold" if sp.get("font-weight") == "bold" else "")
                    w = kit.m.width(sp.text or "", face, size, spacing) - (spacing * size if spacing else 0)
                    x0 = cur if x0 is None else min(x0, cur)
                    x1 = cur + w if x1 is None else max(x1, cur + w)
                    cur += w + (spacing * size if spacing else 0)
                    content.append(sp.text or "")
                if x0 is None:
                    continue
                base = num(e, "y")
                G["texts"].append({"r": _box(mm, x0, base - 0.8 * size, x1, base + 0.22 * size),
                                   "s": "".join(content), "edge": edge})

    walk(root, (1, 0, 0, 1, 0, 0), None)
    return G


def lint(svg, kit):
    """Geometry problems of a rendered diagram, as readable strings."""
    G = read_geometry(svg, kit)
    probs = []
    view = (0, 0, G["W"], G["H"])

    def short(t):
        return repr(t if len(t) <= 32 else t[:30] + "…")

    def name(item):
        if "s" in item:
            return f"text {short(item['s'])}"
        return f"box {item['id']}" if item.get("id") else "element"

    for kind in ("boxes", "notes", "plates", "steps", "groups", "frames", "texts", "other"):
        for it in G[kind]:
            if not within(it["r"], view, 0.5):
                probs.append(f"{name(it)} lies outside the viewBox")
    for e in G["edges"]:
        if any(not hit(grow(view, 0.5), p) for p in e["pts"]):
            probs.append(f"arrow {e['from']} -> {e['to']} leaves the viewBox")

    # Text belongs to the box, note, plate or step circle around its centre;
    # it must stay inside. Text outside all of them is a free label.
    containers = [("box", b) for b in G["boxes"]] + [("note", n) for n in G["notes"]]
    free, on_plate = [], []
    for t in G["texts"]:
        c = ((t["r"][0] + t["r"][2]) / 2, (t["r"][1] + t["r"][3]) / 2)
        host = next(((k, b) for k, b in containers if hit(b["r"], c)), None)
        if host:
            if not within(t["r"], host[1]["r"], 1.5):
                probs.append(f"{name(t)} spills out of {host[0]} {host[1].get('id') or ''}".rstrip())
            continue
        plate = next((p for p in G["plates"] if hit(p["r"], c)), None)
        if plate:
            if not within(t["r"], plate["r"], 1.5):
                probs.append(f"{name(t)} spills out of its plate")
            on_plate.append(t)
            continue
        if any(hit(st["r"], c) for st in G["steps"]):
            continue
        free.append(t)
    steps = [st for st in G["steps"] if not any(within(st["r"], p["r"], 1) for p in G["plates"])]
    solid = [("box", b) for b in G["boxes"]] + [("note", n) for n in G["notes"]] + \
            [("plate", p) for p in G["plates"]] + [("step", st) for st in steps] + [("text", t) for t in free]
    for i in range(len(solid)):
        for j in range(i + 1, len(solid)):
            (ka, a), (kb, b) = solid[i], solid[j]
            # Only a label plate may hold another solid item (its step number).
            held = (ka == "plate" and within(b["r"], a["r"], 1)) or (kb == "plate" and within(a["r"], b["r"], 1))
            if overlap(grow(a["r"], -1), grow(b["r"], -1)) and not held:
                probs.append(f"{name(a) if ka != 'plate' else 'a label plate'} overlaps "
                             f"{name(b) if kb != 'plate' else 'a label plate'}")

    # Boxes, step numbers, free text, label plates, notes and divider pills
    # keep clear of boundary and frame lines: an opaque plate or note on a
    # container border hides the very point where data crosses it.
    for frame in G["groups"] + G["frames"]:
        for kind, items in (("box", G["boxes"]), ("step", steps), ("text", free), ("plate", G["plates"]),
                            ("note", G["notes"])):
            for item in items:
                r = grow(item["r"], 2)
                if overlap(r, frame["r"]) and not within(r, frame["r"]):
                    what = {"step": "a step number", "plate": "a label plate",
                            "note": "a note"}.get(kind) or name(item)
                    probs.append(f"{what} covers a boundary" if kind in ("plate", "note")
                                 else f"{what} crosses a boundary")

    # A frame edge does not run along a boundary line, where the two would
    # read as one.
    for frame in G["frames"]:
        f = frame["r"]
        for group in G["groups"]:
            g = group["r"]
            if min(f[3], g[3]) - max(f[1], g[1]) > 0 and \
                    any(abs(a - b) < 4 for a in (f[0], f[2]) for b in (g[0], g[2])):
                probs.append("a frame edge runs along a boundary")

    # Arrows do not run through labels, plates, notes or boxes other than their ends.
    for e in G["edges"]:
        ends = {e["from"], e["to"]}
        obstacles = [(grow(b["r"], -2), name(b)) for b in G["boxes"] if b.get("id") not in ends]
        obstacles += [(grow(n["r"], -2), "a note") for n in G["notes"] if n.get("id") not in ends]
        obstacles += [(grow(p["r"], -1), "a label plate") for p in G["plates"]]
        obstacles += [(grow(st["r"], -1), "a step number") for st in G["steps"]]
        obstacles += [(grow(t["r"], -1), name(t)) for t in free]
        for r, what in obstacles:
            if any(hit(r, p) for p in e["pts"]):
                kind = "connector" if e["cls"] == "connector" else "arrow"
                probs.append(f"{kind} {e['from']} -> {e['to']} runs through {what}")

    # Two lines never run on top of each other (ends excepted, where arrows
    # may meet at one point).
    cell = 3.0
    grids = []
    for e in G["edges"]:
        pts = e["pts"]
        trimmed = [p for p in pts if math.hypot(p[0] - pts[0][0], p[1] - pts[0][1]) > 15
                   and math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 15]
        grid = {}
        for p in trimmed:
            grid.setdefault((int(p[0] // cell), int(p[1] // cell)), []).append(p)
        grids.append((e, trimmed, grid))
    for i in range(len(grids)):
        for j in range(i + 1, len(grids)):
            ea, pa, _ = grids[i]
            eb, _, gb = grids[j]
            close = 0
            for p in pa:
                cx, cy = int(p[0] // cell), int(p[1] // cell)
                if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 2 for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                       for q in gb.get((cx + dx, cy + dy), ())):
                    close += 1
            if close >= 4:
                probs.append(f"lines {ea['from']} -> {ea['to']} and {eb['from']} -> {eb['to']} run on top of each other")

    # A label stays next to its own arrow.
    by_edge = {}
    for t in G["texts"] + G["steps"]:
        if t.get("edge"):
            r = t["r"]
            cur = by_edge.get(t["edge"])
            by_edge[t["edge"]] = r if cur is None else (min(cur[0], r[0]), min(cur[1], r[1]),
                                                         max(cur[2], r[2]), max(cur[3], r[3]))
    for e in G["edges"]:
        r = by_edge.get(e.get("edge"))
        if r is not None:
            gap = min(rect_dist(r, p) for p in e["pts"])
            if gap > 24:
                probs.append(f"label of {e['from']} -> {e['to']} sits {gap:.0f} px from its arrow")
    out = []
    for p in probs:
        if p not in out:
            out.append(p)
    return out


# ---------------------------------------------------------------- print budget

def print_report(svg, theme):
    """Text sizes, in points, once the figure is fitted into the book's figure
    box (96 px per inch, as WeasyPrint reads SVG). `fits` is judged on the
    smallest text the figure uses, not only on descriptions."""
    m = re.search(r'width="([0-9.]+)" height="([0-9.]+)"', svg)
    w_mm, h_mm = (float(v) * 25.4 / 96 for v in m.groups())
    pr = theme["print"]
    sizes = [float(v) for v in re.findall(r'font-size="([0-9.]+)"', svg)]
    smallest = min(sizes) if sizes else theme["size"]["text"]
    out = {"width_px": float(m.group(1)), "height_px": float(m.group(2)), "smallest_px": smallest}
    for name, box_h in (("normal", pr["box_height_mm"]), ("tall", pr["tall_height_mm"])):
        scale = min(1.0, pr["box_width_mm"] / w_mm, box_h / h_mm)
        out[name] = round(smallest * 0.75 * scale, 1)
        out[name + "_text"] = round(theme["size"]["text"] * 0.75 * scale, 1)
    out["fits"] = "normal" if out["normal"] >= pr["min_print_pt"] else \
        "tall" if out["tall"] >= pr["min_print_pt"] else "no"
    return out


# ---------------------------------------------------------------- entry points

def load_source(src):
    try:
        return tomllib.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise DiagramError(f"not valid TOML: {e}")
    except (OSError, UnicodeDecodeError) as e:
        raise DiagramError(f"cannot read: {e}")


def render(src, theme_path=None, graphviz_any=False, draft=None):
    theme = load_theme(theme_path)
    d = load_source(src)
    layout = d.get("layout")
    if layout not in LAYOUTS:
        raise DiagramError(f"source.layout: layout must be one of {', '.join(LAYOUTS)}")
    if "theme" in d:
        theme = apply_override(theme, d["theme"])
    validate(d, layout)
    kit = Kit(theme)
    body, w, h = LAYOUTS[layout](kit, d, {"graphviz_any": graphviz_any})
    svg = kit.document(d, body, w, h)
    problems = lint(svg, kit)
    if problems and draft is not None:
        draft.append(svg)
    if problems:
        more = f" (and {len(problems) - 8} more)" if len(problems) > 8 else ""
        raise DiagramError("geometry lint: " + "; ".join(problems[:8]) + more)
    return svg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--theme", type=pathlib.Path)
    ap.add_argument("--png", help="also write a PNG through rsvg-convert")
    ap.add_argument("--zoom", type=float, default=2.0, help="PNG zoom factor (default 2)")
    ap.add_argument("--report", action="store_true",
                    help="print the smallest text size the figure gets in the book (pt)")
    ap.add_argument("--require-fit", choices=("normal", "tall"),
                    help="exit 3 unless the smallest text stays legible in this figure box")
    ap.add_argument("--draft", action="store_true",
                    help="write the SVG even when the geometry lint refuses it (still exit 1), to look at it")
    ap.add_argument("--graphviz-any", action="store_true",
                    help=f"allow a Graphviz other than {GRAPHVIZ_PIN} (draft only; the SVG will differ)")
    a = ap.parse_args(argv)
    draft = [] if a.draft else None
    try:
        svg = render(a.src, a.theme, a.graphviz_any, draft)
    except DiagramError as e:
        print(f"render.py: {a.src}: {e}", file=sys.stderr)
        if draft:
            pathlib.Path(a.out).write_text(draft[0], encoding="utf-8")
            if a.png:
                subprocess.run(["rsvg-convert", "-z", str(a.zoom), a.out, "-o", a.png])
        return 1
    pathlib.Path(a.out).write_text(svg, encoding="utf-8")
    rc = 0
    if a.report or a.require_fit:
        r = print_report(svg, load_theme(a.theme))
        print(f"{a.out}: {fmt(r['width_px'])} x {fmt(r['height_px'])} px; smallest text "
              f"({fmt(r['smallest_px'])} px) {r['normal']} pt in the normal box, {r['tall']} pt in the tall box; "
              f"descriptions {r['normal_text']} / {r['tall_text']} pt; fits: {r['fits']}")
        if a.require_fit and (r["fits"] == "no" or (a.require_fit == "normal" and r["fits"] != "normal")):
            rc = 3
    if a.png:
        r = subprocess.run(["rsvg-convert", "-z", str(a.zoom), a.out, "-o", a.png])
        if r.returncode:
            return r.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
