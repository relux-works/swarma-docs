#!/usr/bin/env python3
"""Render a declarative diagram (TOML) to SVG in the house style.

    python3 scripts/diagram-kit/render.py SRC.toml OUT.svg [--theme THEME.toml] [--png OUT.png]

Layouts: "stack" (vertical flow with trust-boundary groups, paired arrows and
side lanes), "sequence" (lifelines, numbered messages, condition frames) and
"graph" (components, states and trees placed by Graphviz `dot`).

Needs Python 3.11+ (tomllib). The graph layout needs Graphviz `dot`; --png
needs `rsvg-convert`. Text is measured with the PT Sans and PT Mono metrics in
metrics.json, so the SVG is identical on every machine; the fonts themselves
are needed only to view or rasterise it. The style guide is
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
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent


class DiagramError(Exception):
    pass


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


def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Text:
    """Inline markup: `code` is set in the mono face. Lines wrap at spaces."""

    def __init__(self, kit, raw, size, bold=False, color=None):
        self.kit, self.size, self.bold = kit, size, bold
        self.color = color
        self.lines = []  # each line: list of (text, face)
        self.raw = raw or ""

    def _words(self, paragraph):
        base = "sans-bold" if self.bold else "sans"
        mono = "mono-bold" if self.bold else "mono"
        parts = paragraph.split("`")
        words, cur = [], []
        for i, part in enumerate(parts):
            face = mono if i % 2 else base
            chunks = part.split(" ")
            for j, chunk in enumerate(chunks):
                if j > 0:
                    words.append(cur)
                    cur = []
                if chunk:
                    cur.append((chunk, face))
        words.append(cur)
        return [w for w in words if w]

    def word_width(self, word):
        return sum(self.kit.m.width(t, f, self.size) for t, f in word)

    def natural_width(self):
        space = self.kit.m.width(" ", "sans", self.size)
        best = 0
        for paragraph in self.raw.split("\n"):
            words = self._words(paragraph)
            w = sum(self.word_width(x) for x in words) + space * max(0, len(words) - 1)
            best = max(best, w)
        return best

    def wrap(self, max_width, balance=True):
        """Greedy wrap, then narrow the measure while the line count holds, so
        the last line is not a lone word."""
        self._wrap(max_width)
        n = len(self.lines)
        if balance and n > 1 and len(self.raw.split("\n")) == 1:
            lo, hi = max_width / n, max_width
            while hi - lo > 2:
                mid = (lo + hi) / 2
                self._wrap(mid)
                if len(self.lines) > n:
                    lo = mid
                else:
                    hi = mid
            self._wrap(hi)
        return self

    def _wrap(self, max_width):
        space = self.kit.m.width(" ", "sans", self.size)
        self.lines = []
        for paragraph in self.raw.split("\n"):
            line, width = [], 0
            for word in self._words(paragraph):
                ww = self.word_width(word)
                if line and width + space + ww > max_width + 0.5:
                    self.lines.append(line)
                    line, width = [], 0
                if line:
                    line.append((" ", "sans-bold" if self.bold else "sans"))
                    width += space
                line.extend(word)
                width += ww
            self.lines.append(line)

    @property
    def line_height(self):
        return self.size * self.kit.t["space"]["line_height"]

    @property
    def height(self):
        return len(self.lines) * self.line_height if self.raw else 0

    def line_width(self, line):
        return sum(self.kit.m.width(t, f, self.size) for t, f in line)

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
            out.append(self.kit.text_line(line, x0, base, self.size, color))
        return "\n".join(out)


# ---------------------------------------------------------------- kit

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
        roles = self.t["role"]
        if name not in roles:
            raise DiagramError(f"unknown role {name!r}; known: {', '.join(roles)}")
        return roles[name]

    def text(self, raw, size, bold=False, color=None):
        return Text(self, raw, size, bold, color)

    def text_line(self, line, x, base, size, color, spacing=0.0):
        # Merge neighbouring runs of one face, then emit one <text> with tspans.
        runs = []
        for t, face in line:
            for ch in t:
                eff = self.m.face_for(ch, face)
                if runs and runs[-1][1] == eff:
                    runs[-1][0] += ch
                else:
                    runs.append([ch, eff])
        # Every run after the first gets its own x from our metrics: renderers
        # drop spaces at tspan edges, and fixed positions keep the layout
        # identical wherever the SVG is drawn.
        spans = []
        cur = x
        for i, (t, face) in enumerate(runs):
            w = self.m.width(t, face, size, spacing)
            lead = len(t) - len(t.lstrip(" "))
            if lead:
                cur += self.m.width(" " * lead, face, size, spacing)
                t = t[lead:]
                w = self.m.width(t, face, size, spacing)
            body = t.rstrip(" ")
            trail = self.m.width(t[len(body):], face, size, spacing)
            fam = self.fam["mono" if face.startswith("mono") else "sans"]
            weight = ' font-weight="bold"' if face.endswith("bold") else ""
            pos = f' x="{fmt(cur)}"' if i else ""
            if body:
                spans.append(f'<tspan{pos} font-family="{fam}"{weight}>{escape(body)}</tspan>')
            cur += w
        ls = f' letter-spacing="{fmt(spacing * size)}"' if spacing else ""
        return (f'<text x="{fmt(x)}" y="{fmt(base)}" font-size="{fmt(size)}" fill="{color}"{ls}>'
                + "".join(spans) + "</text>")

    def spaced_label(self, raw, x, y, size, color, anchor="start"):
        """Uppercase label with letter spacing (groups, protocols). y is the top."""
        sp = self.s["letter_spacing"]
        lines = raw.upper().split("\n")
        out = []
        lh = size * self.s["line_height"]
        for i, line in enumerate(lines):
            w = self.m.width(line, "sans-bold", size, sp) - sp * size
            x0 = {"middle": x - w / 2, "start": x, "end": x - w}[anchor]
            out.append(self.text_line([(line, "sans-bold")], x0, y + i * lh + size * 0.95, size, color, sp))
        return "\n".join(out)

    def spaced_size(self, raw, size):
        sp = self.s["letter_spacing"]
        lines = raw.upper().split("\n")
        w = max(self.m.width(l, "sans-bold", size, sp) - sp * size for l in lines)
        return w, len(lines) * size * self.s["line_height"]

    def arrow(self, points, color=None, dashed=False, head=True):
        color = color or self.c["line"]
        d = "M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x, y in points)
        return self.path_arrow(d, points[-2], points[-1], color, dashed, head)

    def path_arrow(self, d, before, tip, color, dashed, head=True):
        s = self.s
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        out = []
        if head:
            # Shorten the line so it does not poke through the arrow head.
            ang = math.atan2(tip[1] - before[1], tip[0] - before[0])
            h = s["arrow_head"]
            back = (tip[0] - math.cos(ang) * h * 0.6, tip[1] - math.sin(ang) * h * 0.6)
            d = d[: d.rfind(" ", 0, d.rfind(" "))] + f" {fmt(back[0])} {fmt(back[1])}"
            out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{fmt(s["arrow_stroke"])}"{dash}/>')
            p1 = (tip[0] - math.cos(ang) * h + math.sin(ang) * h * 0.45,
                  tip[1] - math.sin(ang) * h - math.cos(ang) * h * 0.45)
            p2 = (tip[0] - math.cos(ang) * h - math.sin(ang) * h * 0.45,
                  tip[1] - math.sin(ang) * h + math.cos(ang) * h * 0.45)
            out.append(f'<polygon points="{fmt(tip[0])},{fmt(tip[1])} {fmt(p1[0])},{fmt(p1[1])} '
                       f'{fmt(p2[0])},{fmt(p2[1])}" fill="{color}"/>')
        else:
            out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{fmt(s["arrow_stroke"])}"{dash}/>')
        return "\n".join(out)

    # Step label: circled number, then a bold label, wrapped.
    def step_label(self, step, label, max_width=None):
        max_width = max_width or self.s["label_max_width"]
        r = self.s["step_radius"]
        lead = (2 * r + 6) if step is not None else 0
        t = self.text(label or "", self.z["label"], bold=True).wrap(max_width - lead)
        w = lead + t.width
        h = max(t.height, 2 * r if step is not None else 0)
        return {"step": step, "text": t, "w": w, "h": h, "lead": lead}

    def step_label_svg(self, lab, x, y, color=None):
        """x, y: top-left of the label block."""
        out = []
        r = self.s["step_radius"]
        t = lab["text"]
        if lab["step"] is not None:
            cy = y + (t.line_height / 2 if t.raw else r)
            cx = x + r
            out.append(f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{self.c["background"]}" '
                       f'stroke="{color or self.c["ink"]}" stroke-width="1.5"/>')
            digit = str(lab["step"])
            dw = self.m.width(digit, "sans-bold", self.z["step"])
            out.append(self.text_line([(digit, "sans-bold")], cx - dw / 2, cy + self.z["step"] * 0.36,
                                      self.z["step"], color or self.c["ink"]))
        if t.raw:
            out.append(t.svg(x + lab["lead"], y, anchor="start", color=self.c["ink"]))
        return "\n".join(out)

    # Box: bold name, optional badge, description.
    def box_model(self, node, width=None, wrap=None):
        s, z = self.s, self.z
        name = self.text(node.get("name", ""), z["name"], bold=True)
        desc = self.text(node.get("text", ""), z["text"], color=self.c["text"])
        badge = node.get("badge")
        inner_nat = max(name.natural_width(), desc.natural_width(),
                        (self.m.width(badge, "sans-bold", z["step"] + 1) + 24) if badge else 0)
        if width is None:
            inner = min(inner_nat, wrap or s["node_text_width"])
            name.wrap(inner)
            desc.wrap(inner)
            badge_w = (self.m.width(badge, "sans-bold", z["step"] + 1) + 24) if badge else 0
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
        dash = ' stroke-dasharray="7 5"' if node.get("style") == "dashed" else ""
        out.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(bm["w"])}" height="{fmt(bm["h"])}" '
                   f'rx="{fmt(s["box_radius"])}" fill="{role["fill"]}" stroke="{role["stroke"]}" '
                   f'stroke-width="{fmt(s["box_stroke"])}"{dash}/>')
        cx = x + bm["w"] / 2
        cy = y + s["box_pad_y"]
        out.append(bm["name"].svg(cx, cy - 2))
        cy += bm["name"].height
        if bm["badge"]:
            bw = self.m.width(bm["badge"], "sans-bold", z["step"] + 1) + 24
            cy += 8
            out.append(f'<rect x="{fmt(cx - bw / 2)}" y="{fmt(cy)}" width="{fmt(bw)}" height="24" rx="12" '
                       f'fill="{role["stroke"]}"/>')
            out.append(self.text_line([(bm["badge"], "sans-bold")],
                                      cx - (bw - 24) / 2, cy + 17, z["step"] + 1, "#ffffff"))
            cy += 24
        if bm["desc"].raw:
            out.append(bm["desc"].svg(cx, cy + 6, color=self.c["text"]))
        return "\n".join(out)

    def start_svg(self, x, y, d, nid):
        r = d / 2
        return (f"<!-- node {nid} -->\n"
                f'<circle cx="{fmt(x + r)}" cy="{fmt(y + r)}" r="{fmt(r)}" fill="{self.c["line"]}"/>')

    def group_svg(self, g, x, y, w, h, gid, labels=None):
        """Frame of a group. With a `labels` list the label goes there, so the
        caller can draw it above the arrows."""
        s = self.s
        role = self.role(g.get("role", "neutral"))
        out = [f"<!-- group {gid} -->",
               f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{fmt(s["group_radius"])}" '
               f'fill="none" stroke="{role["stroke"]}" stroke-width="{fmt(s["group_stroke"])}" '
               f'stroke-dasharray="{s["group_dash"]}"/>']
        if g.get("label"):
            # A background plate keeps the label legible where an arrow enters the group.
            lw, lh = self.spaced_size(g["label"], self.z["group"])
            lx, ly = x + s["group_pad"], y + s["group_label_gap"] + 2
            plate = (f'<!-- group label {gid} -->\n'
                     f'<rect x="{fmt(lx - 6)}" y="{fmt(ly - 2)}" width="{fmt(lw + 12)}" height="{fmt(lh + 2)}" '
                     f'fill="{self.c["background"]}"/>\n'
                     + self.spaced_label(g["label"], lx, ly, self.z["group"], role["label"]))
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
            t = self.text(d["caption"], self.z["caption"], color=self.c["muted"]).wrap(width)
            out.append(t.svg(0, h, anchor="start", color=self.c["text"]))
            h += t.height
        if out:
            h += 24
        return "\n".join(out), h

    def document(self, d, body, width, height):
        head, hh = self.header(d, width)
        pad = self.s["pad"]
        W, H = width + 2 * pad, height + hh + 2 * pad
        title = escape(d.get("title") or d.get("alt") or "")
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(W)}" height="{fmt(H)}" '
                 f'viewBox="0 0 {fmt(W)} {fmt(H)}">']
        if title:
            parts.append(f"<title>{title}</title>")
        parts.append(f'<rect width="{fmt(W)}" height="{fmt(H)}" fill="{self.c["background"]}"/>')
        if head:
            parts.append(f'<g transform="translate({fmt(pad)} {fmt(pad)})">\n{head}\n</g>')
        parts.append(f'<g transform="translate({fmt(pad)} {fmt(pad + hh)})">\n{body}\n</g>')
        parts.append("</svg>\n")
        return "\n".join(parts)


# ---------------------------------------------------------------- stack layout

def layout_stack(kit, d):
    s = kit.s
    nodes = d.get("nodes", {})
    groups = d.get("groups", {})
    links = d.get("links", [])
    order = list(nodes)
    if not order:
        raise DiagramError("stack layout needs nodes")
    for gid, g in groups.items():
        if g.get("parent") and g["parent"] not in groups:
            raise DiagramError(f"group {gid}: unknown parent {g['parent']!r}")

    def chain(gid):
        out = []
        while gid:
            out.append(gid)
            gid = groups[gid].get("parent")
        return list(reversed(out))

    for nid, n in nodes.items():
        if n.get("group") and n["group"] not in groups:
            raise DiagramError(f"node {nid}: unknown group {n['group']!r}")
    chains = [chain(nodes[n].get("group")) for n in order]
    # A group must be one contiguous run of the stack.
    seen_closed = set()
    for i, ch in enumerate(chains):
        prev = chains[i - 1] if i else []
        for g in prev:
            if g not in ch:
                seen_closed.add(g)
        for g in ch:
            if g in seen_closed:
                raise DiagramError(f"group {g} is split; list its nodes next to each other")
    idx = {n: i for i, n in enumerate(order)}
    members = {g: [i for i, ch in enumerate(chains) if g in ch] for g in groups}

    def endpoint_index(ep, other_index):
        if ep in idx:
            return idx[ep]
        if ep in groups:
            m = members[ep]
            if not m:
                raise DiagramError(f"group {ep} has no nodes")
            return m[0] if other_index > m[-1] else m[-1] if other_index < m[0] else m[0]
        raise DiagramError(f"link endpoint {ep!r} is neither a node nor a group")

    def rough_index(ep):
        if ep in idx:
            return idx[ep]
        if ep in groups and members[ep]:
            return members[ep][0]
        raise DiagramError(f"link endpoint {ep!r} is neither a node nor a group")

    gap_links = {}
    side_links = []
    for k, l in enumerate(links):
        a = endpoint_index(l["from"], rough_index(l["to"]))
        b = endpoint_index(l["to"], a)
        if abs(a - b) == 1 and not l.get("side"):
            gap_links.setdefault(min(a, b), []).append((k, l, a < b))
        else:
            side_links.append((k, l, a, b))

    # Lanes: a side link whose endpoints share a top-level group runs inside it.
    def top(i):
        return chains[i][0] if chains[i] else None

    lanes = {}  # owner (top group or None) -> list of (k, link, a, b, side)
    for k, l, a, b in side_links:
        owner = top(a) if top(a) and top(a) == top(b) else None
        lanes.setdefault(owner, []).append((k, l, a, b, l.get("side", "right")))
    lane_w = s["lane"]

    def lanes_of(owner, side):
        return [x for x in lanes.get(owner, []) if x[4] == side]

    # Widths.
    gp = s["group_pad"]
    models = {n: kit.box_model(nodes[n], wrap=s["box_max_width"] - 2 * s["box_pad_x"]) for n in order}
    content = 0
    for i, n in enumerate(order):
        depth = len(chains[i])
        t = top(i)
        extra = (len(lanes_of(t, "right")) + len(lanes_of(t, "left"))) * lane_w if t else 0
        content = max(content, min(models[n]["natural"], s["box_max_width"]) + 2 * gp * depth + extra)
    content = max(content, 320)
    left_root = (18 + len(lanes_of(None, "left")) * lane_w) if lanes_of(None, "left") else 0
    right_root = (18 + len(lanes_of(None, "right")) * lane_w) if lanes_of(None, "right") else 0
    x_left = left_root  # left edge of the top-level column

    def span(i):
        """Horizontal span of the box column for entry i."""
        depth = len(chains[i])
        t = top(i)
        x0 = x_left + gp * depth
        x1 = x_left + content - gp * depth
        if t:
            x0 += len(lanes_of(t, "left")) * lane_w
            x1 -= len(lanes_of(t, "right")) * lane_w
        return x0, x1

    for i, n in enumerate(order):
        x0, x1 = span(i)
        compact = nodes[n].get("compact", nodes[n].get("role") == "human")
        w = min(models[n]["natural"], x1 - x0) if compact else x1 - x0
        models[n] = kit.box_model(nodes[n], width=max(w, s["min_box_width"]))
        models[n]["x"] = (x0 + x1 - models[n]["w"]) / 2

    # Gap label blocks.
    gap_layout = {}
    for gi, items in gap_links.items():
        labs = [(k, l, down, kit.step_label(l.get("step"), l.get("label", ""))) for k, l, down in items]
        via = next((l.get("via") for _, l, _, _ in labs if l.get("via")), None)
        vw, vh = kit.spaced_size(via, kit.z["protocol"]) if via else (0, 0)
        free = max(s["gap_min"], max([lab["h"] for *_, lab in labs] + [vh]) + 28)
        gap_layout[gi] = (labs, via, vw, vh, free)

    # Vertical pass.
    label_h = kit.z["group"] * s["line_height"]
    group_top_h = s["group_label_gap"] + label_h + s["group_pad"] * 0.6
    y = 0
    box_y = {}
    gap_free = {}
    group_y0 = {}
    group_y1 = {}
    for i, n in enumerate(order):
        prev = chains[i - 1] if i else []
        cur = chains[i]
        if i:
            closing = [g for g in prev if g not in cur]
            opening = [g for g in cur if g not in prev]
            y_free0 = y
            for g in reversed(closing):
                y += s["group_pad"] * 0.8
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
        y += s["group_pad"] * 0.8
        group_y1[g] = y
    height = y

    body = []
    group_labels = []
    # Groups first (behind boxes); their labels last (above arrows).
    for gid in groups:
        if gid not in group_y0:
            continue
        depth = len(chain(gid)) - 1
        t = chain(gid)[0]
        x0 = x_left + gp * depth
        x1 = x_left + content - gp * depth
        if depth > 0:
            x0 += len(lanes_of(t, "left")) * lane_w
            x1 -= len(lanes_of(t, "right")) * lane_w
        body.append(kit.group_svg(groups[gid], x0, group_y0[gid], x1 - x0, group_y1[gid] - group_y0[gid], gid,
                                  group_labels))

    for n in order:
        m = models[n]
        body.append(kit.box_svg(m, m["x"], box_y[n], n))

    def edge_y(ep, i, bottom):
        if ep in groups:
            return group_y1[ep] if bottom else group_y0[ep]
        n = order[i]
        return box_y[n] + (models[n]["h"] if bottom else 0)

    # Gap links.
    for gi, (labs, via, vw, vh, free) in gap_layout.items():
        a, b = order[gi], order[gi + 1]
        ax0, ax1 = models[a]["x"], models[a]["x"] + models[a]["w"]
        bx0, bx1 = models[b]["x"], models[b]["x"] + models[b]["w"]
        cx = (max(ax0, bx0) + min(ax1, bx1)) / 2
        _, f0, f1, f_end = gap_free[gi]
        mid = (f0 + f_end) / 2
        n_links = len(labs)
        dx = max(s["pair_min_dx"], vw / 2 + 16)
        if n_links == 1:
            xs = [cx]
        elif n_links == 2:
            xs = [cx - dx, cx + dx]
        else:
            step = 2 * dx
            xs = [cx - dx * (n_links - 1) + step * j for j in range(n_links)]
        ordered = sorted(labs, key=lambda x: (not x[2], x[0]))
        for j, (k, l, down, lab) in enumerate(ordered):
            x = xs[j]
            top_ep, bot_ep = (l["from"], l["to"]) if down else (l["to"], l["from"])
            y_top = edge_y(top_ep, gi, True)
            y_bot = edge_y(bot_ep, gi + 1, False)
            color = kit.role(l["color"])["stroke"] if l.get("color") else None
            pts = [(x, y_top), (x, y_bot)] if down else [(x, y_bot), (x, y_top)]
            body.append(f"<!-- link {l['from']} -> {l['to']} -->")
            body.append(kit.arrow(pts, color=color, dashed=l.get("style") == "dashed"))
            left = x < cx or (n_links > 2 and x <= cx)
            ly = mid - lab["h"] / 2
            if left:
                body.append(kit.step_label_svg(lab, x - 12 - lab["w"], ly))
            else:
                body.append(kit.step_label_svg(lab, x + 12, ly))
        if via:
            vx = cx if n_links >= 2 else cx - 14
            anchor = "middle" if n_links >= 2 else "end"
            body.append(kit.spaced_label(via, vx, mid - vh / 2, kit.z["protocol"], kit.c["muted"], anchor))

    # Side links.
    for owner, items in lanes.items():
        for side in ("right", "left"):
            mine = [x for x in items if x[4] == side]
            for li, (k, l, a, b, _) in enumerate(mine):
                na, nb = order[a], order[b]
                if owner is None:
                    if side == "right":
                        lx = x_left + content + 18 + lane_w * li
                    else:
                        lx = x_left - 18 - lane_w * li
                else:
                    gx1 = x_left + content - gp
                    gx0 = x_left + gp
                    nl = len(mine)
                    lx = gx1 - lane_w * (nl - li - 0.6) if side == "right" else gx0 + lane_w * (nl - li - 0.6)
                ma, mb = models[na], models[nb]
                ya = box_y[na] + ma["h"] * (0.42 if a < b else 0.58)
                yb = box_y[nb] + mb["h"] * (0.58 if a < b else 0.42)
                xa = ma["x"] + (ma["w"] if side == "right" else 0)
                xb = mb["x"] + (mb["w"] if side == "right" else 0)
                color = kit.role(l["color"])["stroke"] if l.get("color") else None
                body.append(f"<!-- side link {l['from']} -> {l['to']} -->")
                body.append(kit.arrow([(xa, ya), (lx, ya), (lx, yb), (xb, yb)], color=color,
                                      dashed=l.get("style", "dashed" if owner else None) == "dashed"))
                lab = kit.step_label(l.get("step"), l.get("label", ""), max_width=abs(yb - ya) - 20)
                cy = (ya + yb) / 2
                # Inside a group the label sits between the boxes and the lane, as
                # the lane is the group's edge; outside it sits on the outer side.
                outer = owner is None
                if side == "right":
                    tx = lx + 8 + lab["h"] if outer else lx - 8
                else:
                    tx = lx - 8 if outer else lx + 8 + lab["h"]
                body.append(f'<g transform="translate({fmt(tx)} {fmt(cy + lab["w"] / 2)}) rotate(-90)">')
                body.append(kit.step_label_svg(lab, 0, -lab["h"]))
                body.append("</g>")
    width = x_left + content + right_root
    return "\n".join(body + group_labels), width, height


# ---------------------------------------------------------------- sequence layout

def layout_sequence(kit, d):
    s, z = kit.s, kit.z
    nodes = d.get("nodes", {})
    items = d.get("seq", [])
    ids = list(nodes)
    if not ids:
        raise DiagramError("sequence layout needs nodes")
    col = {n: i for i, n in enumerate(ids)}
    models = {n: kit.box_model(nodes[n], wrap=min(s["node_text_width"], 220)) for n in ids}
    loop_w, loop_gap = 32, 12  # self-message loop width and gap to its label

    def need(n):
        if n not in col:
            raise DiagramError(f"sequence item names unknown node {n!r}")
        return col[n]

    # Column gaps start from the header widths and widen for message labels.
    gaps = [models[ids[i]]["w"] / 2 + models[ids[i + 1]]["w"] / 2 + s["seq_column_gap"]
            for i in range(len(ids) - 1)]
    prepared = []
    depth = 0
    for it in items:
        if "from" in it:
            a, b = need(it["from"]), need(it["to"])
            wrap = s["label_max_width"] - 40 if it["from"] == it["to"] else s["label_max_width"] + 60
            lab = kit.step_label(it.get("step"), it.get("label", ""), max_width=wrap)
            prepared.append(("msg", it, a, b, lab))
            if a == b and a < len(ids) - 1:
                gaps[a] = max(gaps[a], loop_w + loop_gap + lab["w"] + 30)
            elif a == b and a > 0:
                # The last column loops to the left, so the figure does not grow sideways.
                gaps[a - 1] = max(gaps[a - 1], loop_w + loop_gap + lab["w"] + 30)
            elif a != b:
                lo, hi = min(a, b), max(a, b)
                deficit = lab["w"] + 40 - sum(gaps[lo:hi])
                if deficit > 0:
                    gaps[hi - 1] += deficit
        elif "alt" in it:
            depth += 1
            prepared.append(("alt", it, None, None, kit.text(it["alt"], z["note"], bold=True).wrap(10_000)))
        elif "else" in it:
            if not depth:
                raise DiagramError("else outside alt")
            prepared.append(("else", it, None, None, kit.text(it["else"], z["note"], bold=True).wrap(10_000)))
        elif it.get("end"):
            if not depth:
                raise DiagramError("end outside alt")
            depth -= 1
            prepared.append(("end", it, None, None, None))
        elif "note" in it:
            over = [need(x) for x in it.get("over", [ids[0], ids[-1]])]
            prepared.append(("note", it, min(over), max(over), None))
        else:
            raise DiagramError(f"unknown sequence item {it}")
    if depth:
        raise DiagramError("alt without end")

    xs = [0.0]
    for g in gaps:
        xs.append(xs[-1] + g)
    head_h = max(m["h"] for m in models.values())

    # Vertical pass: rows carry their horizontal extent so frames can wrap them.
    y = head_h + 24
    rows, frames, open_frames = [], [], []
    for kind, it, a, b, extra in prepared:
        if kind == "msg":
            lab = extra
            if a == b:
                hgt = max(lab["h"], 16) + 10
                left = a == len(ids) - 1 and a > 0
                ext = (xs[a] - loop_w - loop_gap - lab["w"], xs[a]) if left else \
                    (xs[a], xs[a] + loop_w + loop_gap + lab["w"])
                rows.append(("self", it, a, lab, y, ext))
                y += hgt + 8 + s["seq_row_gap"]
            else:
                y_arrow = y + lab["h"] + 8
                lo, hi = min(xs[a], xs[b]), max(xs[a], xs[b])
                rows.append(("msg", it, (a, b), lab, y_arrow, (lo, hi)))
                y = y_arrow + s["seq_row_gap"] + 8
            for f in open_frames:
                f["rows"].append(rows[-1])
        elif kind == "alt":
            f = {"y0": y, "label": extra, "rows": [], "elses": [], "depth": len(open_frames)}
            open_frames.append(f)
            y += extra.height + 18
        elif kind == "else":
            open_frames[-1]["elses"].append((y + 4, extra))
            y += extra.height + 22
        elif kind == "end":
            f = open_frames.pop()
            f["y1"] = y
            frames.append(f)
            y += 14
        elif kind == "note":
            t = kit.text(it["note"], z["note"], color=kit.c["text"])
            t.wrap(max(xs[b] - xs[a] + 88, 240))
            w = max(xs[b] - xs[a] + 120, t.width + 32)
            cx = (xs[a] + xs[b]) / 2
            rows.append(("note", it, (a, b), t, y, (cx - w / 2, cx + w / 2)))
            y += t.height + 24 + s["seq_row_gap"]
    bottom = y + 6

    body = []
    for i, n in enumerate(ids):
        body.append(f'<line x1="{fmt(xs[i])}" y1="{fmt(models[n]["h"])}" x2="{fmt(xs[i])}" y2="{fmt(bottom)}" '
                    f'stroke="{kit.c["lifeline"]}" stroke-width="1.5" stroke-dasharray="4 5"/>')
    lo_x = min(xs[i] - models[n]["w"] / 2 for i, n in enumerate(ids))
    hi_x = max(xs[i] + models[n]["w"] / 2 for i, n in enumerate(ids))

    # Frames: dashed, wrapping their rows; condition labels sit on a plate
    # above the lifelines.
    plates = []
    for f in sorted(frames, key=lambda f: f["depth"]):
        ext = [r[5] for r in f["rows"]] or [(xs[0], xs[-1])]
        inset = 14 * f["depth"]
        x0 = min(e[0] for e in ext) - 44 + inset
        x1 = max(e[1] for e in ext) + 24 - inset
        x1 = max(x1, x0 + f["label"].width + 40)
        lo_x, hi_x = min(lo_x, x0), max(hi_x, x1)
        body.append("<!-- frame -->")
        body.append(f'<rect x="{fmt(x0)}" y="{fmt(f["y0"])}" width="{fmt(x1 - x0)}" '
                    f'height="{fmt(f["y1"] - f["y0"])}" rx="10" fill="none" stroke="{kit.c["muted"]}" '
                    f'stroke-width="1.5" stroke-dasharray="7 5"/>')
        labels = [(f["y0"] + 8, f["label"])]
        for ey, et in f["elses"]:
            body.append(f'<line x1="{fmt(x0)}" y1="{fmt(ey)}" x2="{fmt(x1)}" y2="{fmt(ey)}" '
                        f'stroke="{kit.c["muted"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
            labels.append((ey + 6, et))
        for ly, lt in labels:
            plates.append(f'<rect x="{fmt(x0 + 8)}" y="{fmt(ly - 1)}" width="{fmt(lt.width + 12)}" '
                          f'height="{fmt(lt.height + 2)}" fill="{kit.c["background"]}"/>')
            plates.append(lt.svg(x0 + 14, ly, anchor="start", color=kit.c["muted"]))
    body.extend(plates)

    for i, n in enumerate(ids):
        m = models[n]
        body.append(kit.box_svg(m, xs[i] - m["w"] / 2, 0, n))

    for kind, it, ab, lab, yy, ext in rows:
        color = kit.role(it["color"])["stroke"] if it.get("color") else None
        dashed = it.get("style") == "dashed"
        if kind == "msg":
            a, b = ab
            xa, xb = xs[a], xs[b]
            sgn = 1 if xb > xa else -1
            body.append(f"<!-- message {it['from']} -> {it['to']} -->")
            body.append(kit.arrow([(xa + sgn * 2, yy), (xb - sgn * 2, yy)], color=color, dashed=dashed))
            lx, ly = (xa + xb) / 2 - lab["w"] / 2, yy - lab["h"] - 7
            body.append(f'<rect x="{fmt(lx - 4)}" y="{fmt(ly - 1)}" width="{fmt(lab["w"] + 8)}" '
                        f'height="{fmt(lab["h"] + 2)}" fill="{kit.c["background"]}"/>')
            body.append(kit.step_label_svg(lab, lx, ly))
        elif kind == "self":
            x = xs[ab]
            hgt = max(lab["h"], 16) + 10
            y0 = yy + 4
            body.append(f"<!-- self {it['from']} -->")
            sgn = -1 if ext[1] == x else 1
            body.append(kit.arrow([(x + sgn * 2, y0), (x + sgn * loop_w, y0), (x + sgn * loop_w, y0 + hgt),
                                   (x + sgn * 3, y0 + hgt)], color=color, dashed=dashed))
            lx = x + loop_w + loop_gap if sgn > 0 else x - loop_w - loop_gap - lab["w"]
            body.append(kit.step_label_svg(lab, lx, y0 + (hgt - lab["h"]) / 2))
        elif kind == "note":
            x0, x1 = ext
            body.append("<!-- note -->")
            body.append(f'<rect x="{fmt(x0)}" y="{fmt(yy)}" width="{fmt(x1 - x0)}" height="{fmt(lab.height + 24)}" '
                        f'rx="10" fill="{kit.c["note_fill"]}" stroke="{kit.c["note_stroke"]}" stroke-width="1.2"/>')
            body.append(lab.svg((x0 + x1) / 2, yy + 12, color=kit.c["text"]))
        lo_x, hi_x = min(lo_x, ext[0]), max(hi_x, ext[1])

    svg = f'<g transform="translate({fmt(-lo_x)} 0)">\n' + "\n".join(body) + "\n</g>"
    return svg, hi_x - lo_x, bottom


# ---------------------------------------------------------------- graph layout

def layout_graph(kit, d):
    s, z = kit.s, kit.z
    nodes = d.get("nodes", {})
    groups = d.get("groups", {})
    links = d.get("links", [])
    if not nodes:
        raise DiagramError("graph layout needs nodes")
    models = {}
    for n, node in nodes.items():
        if node.get("shape") == "start":
            models[n] = {"w": 22, "h": 22, "node": node}
        else:
            models[n] = kit.box_model(node)
    if d.get("uniform_width"):
        # One width for every box reads as a column, as in the stack layout.
        w = max(m["w"] for n, m in models.items() if nodes[n].get("shape") != "start")
        for n, node in nodes.items():
            if node.get("shape") != "start":
                models[n] = kit.box_model(node, width=w)
    labs = [kit.step_label(l.get("step"), l.get("label", "")) for l in links]
    vias = [l.get("via") for l in links]

    def q(x):
        return '"' + str(x).replace('"', r"\"") + '"'

    def px(v):
        return f"{v / 72:.4f}"

    def fixed_label(w, h):
        return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0" CELLSPACING="0"><TR>'
                f'<TD FIXEDSIZE="TRUE" WIDTH="{max(1, round(w))}" HEIGHT="{max(1, round(h))}"></TD></TR></TABLE>>')

    lines = ["digraph G {",
             f'  graph [rankdir={d.get("direction", "TB")}, nodesep={s["graph_nodesep"]}, '
             f'ranksep={s["graph_ranksep"]}, splines={d.get("splines", "spline")}, '
             f'compound=true, newrank=true, fontsize=1];',
             '  node [shape=box, fixedsize=true, label="", margin=0];',
             '  edge [arrowsize=0.6];']
    children = {}
    for gid, g in groups.items():
        children.setdefault(g.get("parent"), []).append(gid)
    for n, node in nodes.items():
        if node.get("group") and node["group"] not in groups:
            raise DiagramError(f"node {n}: unknown group {node['group']!r}")

    def emit(parent, indent):
        for gid in children.get(parent, []):
            g = groups[gid]
            w, h = kit.spaced_size(g.get("label", " "), z["group"])
            lines.append(f"{indent}subgraph {q('cluster_' + gid)} {{")
            lines.append(f'{indent}  label={fixed_label(w, h + s["group_label_gap"])}; labeljust=l; labelloc=t; '
                         f'margin={s["group_pad"]};')
            emit(gid, indent + "  ")
            lines.append(f"{indent}}}")
        for n, node in nodes.items():
            if node.get("group") == parent:
                m = models[n]
                col = f', group={q(node["column"])}' if node.get("column") else ""
                lines.append(f'{indent}{q(n)} [width={px(m["w"])}, height={px(m["h"])}{col}];')

    emit(None, "  ")
    for rank in d.get("same_rank", []):
        lines.append("  { rank=same; " + "; ".join(q(x) for x in rank) + "; }")
    for k, l in enumerate(links):
        for ep in (l["from"], l["to"]):
            if ep not in nodes:
                raise DiagramError(f"link endpoint {ep!r} is not a node")
        lab = labs[k]
        lw, lh = lab["w"], lab["h"]
        if vias[k]:
            vw, vh = kit.spaced_size(vias[k], z["protocol"])
            lw, lh = max(lw, vw), lh + vh + 4
        attrs = [f"id={q('e' + str(k))}"]
        if lab["text"].raw or lab["step"] is not None or vias[k]:
            attrs.append(f"label={fixed_label(lw + 8, lh + 4)}")
        if l.get("constraint") is False:
            attrs.append("constraint=false")
        lines.append(f"  {q(l['from'])} -> {q(l['to'])} [{', '.join(attrs)}];")
    lines.append("}")
    dot_src = "\n".join(lines)
    try:
        res = subprocess.run(["dot", "-Tjson"], input=dot_src, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise DiagramError("graph layout needs Graphviz `dot` on PATH")
    if res.returncode != 0:
        raise DiagramError("dot failed: " + res.stderr.strip())
    g = json.loads(res.stdout)
    bb = [float(v) for v in g["bb"].split(",")]
    H = bb[3]

    def pt(sx, sy):
        return float(sx) - bb[0], H - float(sy)

    body = []
    group_labels = []
    objects = g.get("objects", [])
    # Clusters, outermost first (dot lists them before nested ones).
    for o in objects:
        name = o.get("name", "")
        if name.startswith("cluster_") and "bb" in o:
            x0, y0, x1, y1 = (float(v) for v in o["bb"].split(","))
            gid = name[len("cluster_"):]
            body.append(kit.group_svg(groups[gid], x0 - bb[0], H - y1, x1 - x0, y1 - y0, gid, group_labels))
    for o in objects:
        name = o.get("name", "")
        if name in nodes and "pos" in o:
            x, y = pt(*o["pos"].split(","))
            m = models[name]
            if nodes[name].get("shape") == "start":
                body.append(kit.start_svg(x - m["w"] / 2, y - m["h"] / 2, m["w"], name))
            else:
                body.append(kit.box_svg(m, x - m["w"] / 2, y - m["h"] / 2, name))
    for e in g.get("edges", []):
        k = int(e["id"][1:])
        l = links[k]
        pos = e["pos"].split()
        end = None
        start = None
        pts = []
        for p in pos:
            if p.startswith("e,"):
                end = pt(*p[2:].split(","))
            elif p.startswith("s,"):
                start = pt(*p[2:].split(","))
            else:
                pts.append(pt(*p.split(",")))
        dpath = f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"
        for i in range(1, len(pts) - 2, 3):
            dpath += " C " + " ".join(f"{fmt(a)} {fmt(b)}" for a, b in pts[i:i + 3])
        color = kit.role(l["color"])["stroke"] if l.get("color") else kit.c["line"]
        body.append(f"<!-- link {l['from']} -> {l['to']} -->")
        if end:
            dpath += f" L {fmt(end[0])} {fmt(end[1])}"
            body.append(kit.path_arrow(dpath, pts[-1], end, color, l.get("style") == "dashed"))
        else:
            body.append(kit.path_arrow(dpath, pts[-2], pts[-1], color, l.get("style") == "dashed"))
        if "lp" in e:
            lx, ly = pt(*e["lp"].split(","))
            lab = labs[k]
            vh = 0
            if vias[k]:
                vw, vh = kit.spaced_size(vias[k], z["protocol"])
            total_h = lab["h"] + (vh + 4 if vias[k] else 0)
            top = ly - total_h / 2
            if lab["text"].raw or lab["step"] is not None:
                body.append(kit.step_label_svg(lab, lx - lab["w"] / 2, top))
            if vias[k]:
                body.append(kit.spaced_label(vias[k], lx, top + lab["h"] + 4, z["protocol"], kit.c["muted"], "middle"))
    return "\n".join(body + group_labels), bb[2] - bb[0], bb[3] - bb[1]


LAYOUTS = {"stack": layout_stack, "sequence": layout_sequence, "graph": layout_graph}


def merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def print_report(svg, theme):
    """Description text size, in points, once the figure is fitted into the
    book's figure box (96 px per inch, as WeasyPrint reads SVG)."""
    m = re.search(r'width="([0-9.]+)" height="([0-9.]+)"', svg)
    w_mm, h_mm = (float(v) * 25.4 / 96 for v in m.groups())
    pr = theme["print"]
    pt = theme["size"]["text"] * 0.75
    out = {"width_px": float(m.group(1)), "height_px": float(m.group(2))}
    for name, box_h in (("normal", pr["box_height_mm"]), ("tall", pr["tall_height_mm"])):
        scale = min(1.0, pr["box_width_mm"] / w_mm, box_h / h_mm)
        out[name] = round(pt * scale, 1)
    out["fits"] = "normal" if out["normal"] >= pr["min_print_pt"] else \
        "tall" if out["tall"] >= pr["min_print_pt"] else "no"
    return out


def load_theme(theme_path=None):
    return tomllib.loads((theme_path or HERE / "theme.toml").read_text(encoding="utf-8"))


def render(src, theme_path=None):
    theme = load_theme(theme_path)
    d = tomllib.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    if "theme" in d:  # per-diagram overrides are allowed only for spacing
        unknown = set(d["theme"]) - {"space"}
        if unknown:
            raise DiagramError("a diagram may override only [theme.space]; colours and fonts live in the theme")
        theme = merge(theme, d["theme"])
    kit = Kit(theme)
    layout = d.get("layout")
    if layout not in LAYOUTS:
        raise DiagramError(f"layout must be one of {', '.join(LAYOUTS)}")
    body, w, h = LAYOUTS[layout](kit, d)
    return kit.document(d, body, w, h)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--theme", type=pathlib.Path)
    ap.add_argument("--png", help="also write a PNG through rsvg-convert")
    ap.add_argument("--zoom", default="2", help="PNG zoom factor (default 2)")
    ap.add_argument("--report", action="store_true",
                    help="print the description text size the figure gets in the book (pt)")
    a = ap.parse_args(argv)
    try:
        svg = render(a.src, a.theme)
    except (DiagramError, KeyError, tomllib.TOMLDecodeError) as e:
        print(f"render.py: {a.src}: {e}", file=sys.stderr)
        return 1
    pathlib.Path(a.out).write_text(svg, encoding="utf-8")
    if a.report:
        r = print_report(svg, load_theme(a.theme))
        print(f"{a.out}: {fmt(r['width_px'])} x {fmt(r['height_px'])} px; text {r['normal']} pt in the "
              f"normal box, {r['tall']} pt in the tall box; fits: {r['fits']}")
    if a.png:
        r = subprocess.run(["rsvg-convert", "-z", a.zoom, a.out, "-o", a.png])
        if r.returncode:
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
