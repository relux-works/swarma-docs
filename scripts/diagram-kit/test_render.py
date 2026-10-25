#!/usr/bin/env python3
"""Positive and negative checks for render.py on disposable fixtures.

    python3 scripts/diagram-kit/test_render.py

The graph cases need Graphviz `dot`; they are skipped, and say so, without it.
Cases that compare graph output with committed SVG also need the pinned
Graphviz version (render.GRAPHVIZ_PIN).
"""
import contextlib
import io
import pathlib
import re
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402

HAVE_DOT = shutil.which("dot") is not None
PINNED = HAVE_DOT and render.graphviz_version() == render.GRAPHVIZ_PIN
needs_dot = unittest.skipUnless(HAVE_DOT, "Graphviz dot not installed; graph layout not checked")

STACK = '''
layout = "stack"
[groups.g]
label = "Граница"
role = "key"
[nodes.a]
role = "human"
name = "Оператор"
[nodes.b]
group = "g"
role = "key"
name = "Signer"
text = "подписывает `nonce` → ответ"
[nodes.c]
role = "service"
name = "Ворота"
[[links]]
from = "a"
to = "b"
step = 1
label = "действие"
[[links]]
from = "b"
to = "c"
step = 2
label = "конверт"
via = "Matrix"
[[links]]
from = "c"
to = "b"
step = 3
label = "ответ"
[[links]]
from = "c"
to = "a"
step = 4
label = "результат"
'''

SEQUENCE = '''
layout = "sequence"
[nodes.a]
role = "agent"
name = "Агент"
[nodes.b]
role = "store"
name = "Реестр"
[[seq]]
from = "a"
to = "b"
step = 1
label = "запрос"
[[seq]]
alt = "право есть"
[[seq]]
from = "b"
to = "b"
step = 2
label = "проверка"
[[seq]]
else = "права нет"
[[seq]]
from = "b"
to = "a"
step = 2
label = "отказ"
color = "alert"
[[seq]]
end = true
[[seq]]
note = "Примечание."
over = ["a", "b"]
'''

GRAPH = '''
layout = "graph"
[groups.g]
label = "Мост"
role = "service"
[nodes.a]
role = "external"
name = "Matrix"
[nodes.b]
group = "g"
role = "service"
name = "Ядро"
[[links]]
from = "a"
to = "b"
step = 1
label = "событие"
'''

# Participant containers, a divider, a note on one participant inside an alt
# branch, an opt frame, a self-message in a middle column and nested alt.
SEQ_FULL = '''
layout = "sequence"
[groups.left]
label = "Машина донора"
role = "external"
[groups.right]
label = "Наша сторона"
role = "service"
[nodes.a]
group = "left"
role = "agent"
name = "Агент"
[nodes.b]
group = "left"
role = "service"
name = "Мост"
[nodes.c]
group = "right"
role = "service"
name = "Вход"
[nodes.d]
role = "store"
name = "Ящик"
[[seq]]
divider = "Первая часть"
[[seq]]
from = "a"
to = "b"
step = 1
label = "запрос"
[[seq]]
from = "b"
to = "b"
step = 2
label = "проверка"
[[seq]]
alt = "ключ есть"
[[seq]]
note = "ошибка не включает запасной путь"
on = "b"
[[seq]]
alt = "внутреннее условие"
[[seq]]
from = "b"
to = "c"
step = 3
label = "команда"
[[seq]]
end = true
[[seq]]
else = "ключа нет"
[[seq]]
from = "b"
to = "a"
step = 3
label = "отказ"
color = "alert"
[[seq]]
end = true
[[seq]]
divider = "Вторая часть"
[[seq]]
opt = "почта есть"
[[seq]]
from = "c"
to = "d"
step = 4
label = "почта"
[[seq]]
end = true
'''

# A state machine with start, end, a note beside one node and ranks.
GRAPH_STATES = '''
layout = "graph"
same_rank = [["done", "fail"]]
[nodes.s]
shape = "start"
[nodes.sent]
role = "service"
name = "Отправлена"
note = "Поздняя квитанция отклоняется."
[nodes.done]
role = "service"
name = "Завершена"
[nodes.fail]
role = "alert"
name = "Не удалась"
[nodes.e1]
shape = "end"
[[links]]
from = "s"
to = "sent"
[[links]]
from = "sent"
to = "done"
label = "принятие"
[[links]]
from = "sent"
to = "fail"
label = "срок прошёл"
[[links]]
from = "done"
to = "e1"
label = "держатель: новый"
[[links]]
from = "fail"
to = "e1"
constraint = false
'''

# Columns and uniform width in a graph.
GRAPH_COLUMNS = '''
layout = "graph"
uniform_width = true
[nodes.a]
column = "main"
role = "service"
name = "Провайдер носителя"
[nodes.b]
column = "main"
role = "service"
name = "Ядро"
[nodes.c]
column = "main"
role = "store"
name = "Почтовый ящик с длинным именем"
[nodes.x]
role = "agent"
name = "Агент"
[[links]]
from = "a"
to = "b"
[[links]]
from = "b"
to = "c"
[[links]]
from = "x"
to = "c"
'''

# Side lanes on both sides at the root and a lane inside a group.
STACK_LANES = '''
layout = "stack"
[groups.g]
label = "Хост"
role = "service"
[nodes.a]
role = "human"
name = "Оператор"
[nodes.b]
group = "g"
role = "service"
name = "Мост"
[nodes.c]
group = "g"
role = "service"
name = "Ворота"
[nodes.d]
group = "g"
role = "store"
name = "Ящик"
[[links]]
from = "a"
to = "b"
step = 1
label = "команда"
[[links]]
from = "b"
to = "c"
step = 2
[[links]]
from = "c"
to = "d"
step = 3
[[links]]
from = "b"
to = "d"
label = "аудит"
side = "right"
[[links]]
from = "d"
to = "a"
step = 4
label = "результат"
side = "left"
[[links]]
from = "c"
to = "a"
step = 4
label = "отказ"
color = "alert"
side = "left"
[[links]]
from = "d"
to = "a"
label = "копия журнала"
side = "right"
'''

# A note beside a group (left) and beside a node (right), next to a lane
# inside the group.
STACK_NOTES = '''
layout = "stack"
[groups.g]
label = "Хост"
role = "service"
note = "Граница процесса."
note_side = "left"
[nodes.a]
role = "human"
name = "Оператор"
[nodes.b]
group = "g"
role = "service"
name = "Мост"
[nodes.c]
group = "g"
role = "service"
name = "Ворота"
[nodes.d]
group = "g"
role = "store"
name = "Ящик"
note = "Тело хранится до чтения."
[[links]]
from = "a"
to = "b"
step = 1
label = "команда"
[[links]]
from = "b"
to = "c"
step = 2
[[links]]
from = "c"
to = "d"
step = 3
[[links]]
from = "b"
to = "d"
label = "аудит"
side = "right"
'''

SVG = "{http://www.w3.org/2000/svg}"
KIT = render.Kit(render.load_theme())


def geo(svg):
    return render.read_geometry(svg, KIT)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="diagram-kit-")
        self.addCleanup(self.tmp.cleanup)
        self.dir = pathlib.Path(self.tmp.name)

    def src(self, text, name="d.toml"):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def render_ok(self, text, **kw):
        svg = render.render(self.src(text), **kw)
        root = ET.fromstring(svg)  # well-formed XML
        self.assertEqual(root.tag, SVG + "svg")
        return svg, root

    def refused(self, text, reason, **kw):
        with self.assertRaises(render.DiagramError) as cm:
            render.render(self.src(text), **kw)
        self.assertIn(reason, str(cm.exception))
        return str(cm.exception)


class RenderTests(Base):
    # Claim: each layout renders well-formed SVG that uses only theme colours,
    # draws circled step numbers as shapes, sets code in PT Mono, and never
    # needs foreignObject (WeasyPrint cannot draw it).
    def test_layouts_render(self):
        theme = render.load_theme()
        palette = {v.lower() for v in theme["color"].values()}
        for role in theme["role"].values():
            palette |= {v.lower() for v in role.values()}
        cases = [STACK, SEQUENCE, SEQ_FULL, STACK_LANES, STACK_NOTES] + ([GRAPH, GRAPH_STATES, GRAPH_COLUMNS] if HAVE_DOT else [])
        for text in cases:
            svg, root = self.render_ok(text)
            self.assertNotIn("foreignObject", svg)
            self.assertNotIn("`", svg)
            for el in root.iter():
                for attr in ("fill", "stroke"):
                    v = el.get(attr)
                    if v and v != "none":
                        self.assertIn(v.lower(), palette, f"{attr}={v} is not a theme colour")
            if "step =" in text or "shape =" in text:
                self.assertTrue(any(el.tag == SVG + "circle" for el in root.iter()))
        svg, _ = self.render_ok(STACK)
        self.assertIn('font-family="PT Mono, monospace">nonce<', svg)

    # Claim: the output is byte-identical across runs for the same source and theme.
    def test_deterministic(self):
        for text in [STACK, SEQUENCE, SEQ_FULL, STACK_LANES, STACK_NOTES] + ([GRAPH, GRAPH_STATES] if HAVE_DOT else []):
            self.assertEqual(render.render(self.src(text)), render.render(self.src(text)))

    # Claim: a run that starts with a space after a font change keeps its gap,
    # because every run after the first carries its own x (renderers drop
    # spaces at tspan edges).
    def test_runs_have_positions(self):
        svg, root = self.render_ok(STACK)
        for text in root.iter(SVG + "text"):
            spans = list(text.iter(SVG + "tspan"))
            for sp in spans[1:]:
                self.assertIsNotNone(sp.get("x"))
            for sp in spans:
                self.assertEqual(sp.text, sp.text.strip(" "))

    # Claim: sources that break the contract are refused with a named reason
    # and no SVG; each case differs from a valid source in one place.
    def test_refusals(self):
        cases = {
            "unknown role": STACK.replace('role = "service"', 'role = "blue"'),
            "override only [theme.space]": STACK + '\n[theme.color]\nline = "#ff0000"\n',
            "group g is split": STACK.replace('[nodes.b]\ngroup = "g"\n', '[nodes.b]\n')
                                       .replace('[nodes.a]\nrole', '[nodes.a]\ngroup = "g"\nrole')
                                       .replace('[nodes.c]\nrole', '[nodes.c]\ngroup = "g"\nrole'),
            "alt without end": SEQUENCE.replace("[[seq]]\nend = true\n", ""),
            "else outside alt": SEQUENCE.replace('[[seq]]\nalt = "право есть"\n', ""),
            "neither a node nor a group": STACK.replace('to = "c"\nstep = 2', 'to = "zz"\nstep = 2'),
            "unknown node": SEQUENCE.replace('to = "b"\nstep = 1', 'to = "zz"\nstep = 1'),
            "layout must be one of": STACK.replace('layout = "stack"', 'layout = "mindmap"'),
            "unknown group": STACK.replace('group = "g"', 'group = "nope"'),
        }
        for reason, text in cases.items():
            with self.subTest(reason=reason):
                self.refused(text, reason)

    # Claim: the "split group" check accepts a group whose nodes are adjacent
    # (positive control for the refusal above).
    def test_contiguous_group_accepted(self):
        self.render_ok(STACK.replace('[nodes.c]\nrole', '[nodes.c]\ngroup = "g"\nrole'))

    # Claim: the CLI exits non-zero on a refused source, prints the reason
    # without a traceback and writes no file.
    def test_cli_refusal_writes_nothing(self):
        out = self.dir / "out.svg"
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = render.main([str(self.src(STACK.replace('role = "service"', 'role = "blue"'))), str(out)])
        self.assertEqual(rc, 1)
        self.assertFalse(out.exists())
        self.assertIn("unknown role", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())


class ThemeTests(Base):
    # Claim: the reviewer's injection probes through [theme.space] are refused
    # with the key named, and nothing reaches the SVG.
    def test_space_override_probes_refused(self):
        probes = {
            "theme.space.group_dash: must match": '[theme.space]\ngroup_dash = \'8 6" style="fill:#ff00ff;stroke:#00ff00\'\n',
            "theme.space.group_dash": '[theme.space]\ngroup_dash = \'8 6" onload="alert(1)\'\n',
            "theme.space.pad: must be a non-negative number": "[theme.space]\npad = 'abc'\n",
            "theme.space.pad: must be a non-negative": "[theme.space]\npad = true\n",
            "theme.space.box_stroke: must be a non-negative": "[theme.space]\nbox_stroke = -2\n",
            "theme.space.lane: must be a non-negative": "[theme.space]\nlane = nan\n",
            "theme.space.colour: unknown key": "[theme.space]\ncolour = 1\n",
            "theme.space.line_height: must be greater than zero": "[theme.space]\nline_height = 0\n",
            "override only [theme.space]": '[theme.font]\nsans = "Comic Sans"\n',
            "theme.space.frame_dash": '[theme.space]\nframe_dash = "x"\n',
        }
        for reason, tail in probes.items():
            with self.subTest(reason=reason):
                self.refused(STACK + "\n" + tail, reason)

    # Claim: valid spacing overrides are accepted and take effect (positive
    # control: the override mechanism is not simply disabled).
    def test_space_override_accepted(self):
        svg, _ = self.render_ok(STACK + '\n[theme.space]\ngroup_dash = "4 4"\npad = 20\n')
        self.assertIn('stroke-dasharray="4 4"', svg)
        self.assertNotIn('stroke-dasharray="8 6"', svg)

    # Claim: a theme file is checked as strictly as a source: every section
    # and key is whitelisted and typed, the roles are fixed; the shipped theme
    # passes.
    def test_theme_file_checked(self):
        base = (HERE / "theme.toml").read_text(encoding="utf-8")
        cases = {
            "theme.color.line: must be a colour": base.replace('line = "#3a3f47"', 'line = "#3a3f47; x"'),
            "theme.font.sans: must be a font family name": base.replace('sans = "PT Sans"', 'sans = \'PT Sans" onload="x\''),
            "theme.extra: unknown key": base + '\n[extra]\nx = 1\n',
            "theme.role.alarm: unknown role": base.replace("[role.alert]", "[role.alarm]"),
            "theme.space.group_dash: must match": base.replace('group_dash = "8 6"', 'group_dash = "8 6\\""'),
            "theme.size.text: must be greater than zero": base.replace("text = 15", "text = 0"),
        }
        for reason, text in cases.items():
            with self.subTest(reason=reason):
                p = self.dir / "theme.toml"
                p.write_text(text, encoding="utf-8")
                with self.assertRaises(render.DiagramError) as cm:
                    render.load_theme(p)
                self.assertIn(reason, str(cm.exception))
        p = self.dir / "theme.toml"
        p.write_text(base, encoding="utf-8")
        render.load_theme(p)

    # Claim: attribute values go through quoteattr, so a quote or angle
    # bracket in a value stays inside the attribute; label text is escaped.
    def test_attribute_and_text_escaping(self):
        frag = render.el("rect", fill='a"b<c>&\'d', data_id="x")
        node = ET.fromstring(frag)
        self.assertEqual(node.get("fill"), 'a"b<c>&\'d')
        self.assertEqual(set(node.attrib), {"fill", "data-id"})
        svg, root = self.render_ok(STACK.replace('name = "Ворота"', 'name = "<script>&\\"x"'))
        self.assertNotIn("<script>", svg)
        texts = ["".join(t.itertext()) for t in root.iter(SVG + "text")]
        self.assertTrue(any("<script>&\"x" in t for t in texts))


class SchemaTests(Base):
    # Claim: each malformed source is refused with a DiagramError naming the
    # key; none is accepted silently or ends in a Python traceback. Each case
    # differs from a valid fixture in one place.
    def test_schema_refusals(self):
        cases = [
            ("links[0].lable: unknown key", STACK.replace('label = "действие"', 'lable = "действие"')),
            ("nodes.a.styel: unknown key", STACK.replace('name = "Оператор"', 'name = "Оператор"\nstyel = "dashed"')),
            ("must be one of solid, dashed", STACK.replace('label = "действие"', 'label = "действие"\nstyle = "dotted"')),
            ("links[0].step: must be an integer from 1 to 99", STACK.replace("step = 1\n", 'step = "1"\n')),
            ("links[0].step: must be an integer from 1 to 99", STACK.replace("step = 1\n", "step = 0\n")),
            ("links[0].step: must be an integer from 1 to 99", STACK.replace("step = 1\n", "step = 1.5\n")),
            ("nodes: must be a table", 'layout = "stack"\nnodes = 5\n'),
            ("links[0]: missing key 'from'", STACK.replace('from = "a"\nto = "b"', 'to = "b"')),
            ("seq[0]: missing key 'to'", SEQUENCE.replace('to = "b"\nstep = 1', 'step = 1')),
            ("seq[1]: needs exactly one of", SEQUENCE.replace('alt = "право есть"', 'alt = "право есть"\nfrom = "a"')),
            ("seq[5].end: must be true", SEQUENCE.replace("end = true", "end = false")),
            ("control character", STACK.replace('label = "действие"', 'label = "дей\\u0007ствие"')),
            ("links[0].color: unknown role", STACK.replace('label = "действие"', 'label = "действие"\ncolor = "red"')),
            ("must be an identifier", STACK.replace("[nodes.c]", '[nodes."c\\\\"]').replace('"c"', '"c\\\\"')),
            ("not valid TOML", STACK + "\n[[links]\n"),
            ("missing key 'name'", STACK.replace('name = "Ворота"', 'text = "без имени"')),
            ("links[1].via: a protocol label", STACK.replace('to = "c"\nstep = 2', 'to = "c"\nside = "right"\nstep = 2')),
            ("same element", STACK.replace('from = "a"\nto = "b"', 'from = "b"\nto = "b"')),
            ("seq[4]: a note is either over", SEQ_FULL.replace('on = "b"', 'on = "b"\nover = ["a", "b"]')),
            ("side places a note", SEQUENCE.replace('over = ["a", "b"]', 'over = ["a", "b"]\nside = "left"')),
        ]
        if HAVE_DOT:
            cases += [
                ("direction: must be one of TB, LR, BT, RL", 'direction = "TB]; x [shape=circle"\n' + GRAPH),
                ("splines: must be one of spline, polyline", 'splines = "ortho; x"\n' + GRAPH),
                ("same_rank[0]: unknown node 'zz'", 'same_rank = [["a", "zz"]]\n' + GRAPH),
                ("groups.g.parent: unknown group", GRAPH.replace('label = "Мост"', 'label = "Мост"\nparent = "nope"')),
                ("uniform_width: must be true or false", 'uniform_width = "yes"\n' + GRAPH),
                ("constraint: must be true or false", GRAPH.replace('label = "событие"', 'label = "событие"\nconstraint = 1')),
                ("drawn as a dot", GRAPH_STATES.replace('shape = "end"', 'shape = "end"\ntext = "конец"')),
                ("shape: must be one of box, start, end", GRAPH.replace('name = "Matrix"', 'name = "Matrix"\nshape = "diamond"')),
            ]
        for reason, text in cases:
            with self.subTest(reason=reason):
                self.refused(text, reason)

    # Claim: group structure errors are refused: a parent cycle, a third
    # nesting level and a group without nodes (a graph used to drop its nodes
    # silently).
    def test_group_structure_refusals(self):
        three = STACK.replace('[groups.g]', '[groups.h]\nlabel = "Внешняя"\n[groups.k]\nlabel = "Средняя"\nparent = "h"\n[groups.g]\nparent = "k"')
        self.refused(three, "nesting is limited to two levels")
        cycle = STACK.replace('[groups.g]', '[groups.h]\nparent = "g"\n[groups.g]\nparent = "h"')
        self.refused(cycle, "cycle")
        empty = STACK.replace('[groups.g]', '[groups.empty]\nlabel = "Пусто"\n[groups.g]')
        self.refused(empty, "groups.empty: has no nodes")
        two = STACK.replace('[groups.g]', '[groups.h]\nlabel = "Хост"\n[groups.g]\nparent = "h"')
        self.render_ok(two)  # positive control: two levels are fine

    # Claim: the CLI reports schema errors as one line, exit 1, no traceback
    # (the reviewer's raw-traceback probes `pad = 'abc'` and `nodes = 5`).
    def test_cli_schema_errors_are_clean(self):
        for text in (STACK + "\n[theme.space]\npad = 'abc'\n", 'layout = "stack"\nnodes = 5\n'):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = render.main([str(self.src(text)), str(self.dir / "o.svg")])
            self.assertEqual(rc, 1)
            self.assertNotIn("Traceback", err.getvalue())
            self.assertRegex(err.getvalue(), r"render\.py: .*: (theme\.space\.pad|nodes): ")


class ConstructTests(Base):
    # Claim: participant containers frame exactly their participants' headers;
    # the other participant stays outside.
    def test_sequence_containers(self):
        svg, _ = self.render_ok(SEQ_FULL)
        g = geo(svg)
        frames = {x["id"]: x["r"] for x in g["groups"]}
        boxes = {x["id"]: x["r"] for x in g["boxes"]}
        self.assertTrue(render.within(boxes["a"], frames["left"]) and render.within(boxes["b"], frames["left"]))
        self.assertTrue(render.within(boxes["c"], frames["right"]))
        self.assertFalse(render.overlap(boxes["d"], frames["right"]) or render.overlap(boxes["d"], frames["left"]))
        self.assertFalse(render.overlap(frames["left"], frames["right"]))

    # Claim: participants of one container must be neighbours, and a sequence
    # container cannot nest.
    def test_sequence_container_refusals(self):
        split = SEQ_FULL.replace('[nodes.d]\nrole', '[nodes.d]\ngroup = "left"\nrole')
        self.refused(split, "groups.left: list its participants next to each other")
        self.refused(SEQ_FULL.replace('role = "service"\n[nodes.a]', 'role = "service"\nparent = "left"\n[nodes.a]'),
                     "groups.right.parent: unknown key")

    # Claim: a divider draws a rule across the whole figure with its label on
    # a plate; a divider inside a frame is refused.
    def test_dividers(self):
        svg, root = self.render_ok(SEQ_FULL)
        self.assertEqual(svg.count("<!-- divider -->"), 2)
        width = float(root.get("width")) - 2 * render.load_theme()["space"]["pad"]
        rules = [l for l in root.iter(SVG + "line") if l.get("y1") == l.get("y2") and l.get("stroke") == KIT.c["muted"]
                 and l.get("stroke-dasharray") is None]
        self.assertTrue(rules)
        for l in rules:
            self.assertAlmostEqual(float(l.get("x2")) - float(l.get("x1")), width, delta=1)
        bad = SEQ_FULL.replace('[[seq]]\nalt = "внутреннее условие"', '[[seq]]\ndivider = "внутри"\n[[seq]]\nalt = "внутреннее условие"')
        self.refused(bad, "a divider cannot sit inside alt")

    # Claim: a note on one participant sits beside its lifeline (right by
    # default, left on request) and inside the alt branch that holds it.
    def test_note_on_participant_in_alt(self):
        svg, root = self.render_ok(SEQ_FULL)
        g = geo(svg)
        note = g["notes"][0]["r"]
        frames = [f["r"] for f in g["frames"]]
        self.assertTrue(any(render.within(note, f) for f in frames))
        bline = [l for l in root.iter(SVG + "line") if l.get("stroke-dasharray") == "4 5"]
        xs = sorted(float(l.get("x1")) for l in bline)
        # lifeline of b is the second one; the note starts 10 px right of it
        self.assertAlmostEqual(note[0] - (xs[1] + self.pad_shift(root)), 10, delta=1)
        svg2, _ = self.render_ok(SEQ_FULL.replace('on = "b"', 'on = "b"\nside = "left"'))
        note2 = geo(svg2)["notes"][0]["r"]
        self.assertLess(note2[2], note[0])
        self.refused(SEQ_FULL.replace('on = "b"', 'on = "zz"'), "unknown node 'zz'")

    def pad_shift(self, root):
        """x offset of the body group (padding plus the layout's own shift)."""
        shift = 0.0
        for g in root.iter(SVG + "g"):
            m = re.match(r"translate\(([-0-9.]+) ", g.get("transform") or "")
            if m:
                shift += float(m.group(1))
        return shift

    # Claim: an opt frame is drawn dotted with round caps and an alt frame
    # dashed, so the kinds differ; else inside opt and opt without end are
    # refused.
    def test_opt_frame(self):
        svg, root = self.render_ok(SEQ_FULL)
        frames = {r.get("data-kind"): r for r in root.iter(SVG + "rect") if r.get("class") == "frame"}
        theme = render.load_theme()
        self.assertEqual(frames["opt"].get("stroke-dasharray"), theme["space"]["opt_dash"])
        self.assertEqual(frames["opt"].get("stroke-linecap"), "round")
        self.assertEqual(frames["alt"].get("stroke-dasharray"), theme["space"]["frame_dash"])
        self.assertNotEqual(theme["space"]["opt_dash"], theme["space"]["frame_dash"])
        self.refused(SEQ_FULL.replace('label = "почта"\n', 'label = "почта"\n[[seq]]\nelse = "нет"\n'),
                     "else belongs to alt")
        self.refused(SEQ_FULL.rstrip()[: -len("[[seq]]\nend = true")], "opt without end")

    # Claim: nested alt frames are inset inside their parent frame.
    def test_nested_alt(self):
        svg, _ = self.render_ok(SEQ_FULL)
        alts = [f["r"] for f in geo(svg)["frames"]]
        inner = [a for a in alts if any(a != b and render.within(a, b) for b in alts)]
        self.assertEqual(len(inner), 1)

    # Claim: a self-message in a middle column loops to the right; in the last
    # column it loops to the left, so the figure does not grow sideways.
    def test_self_message_direction(self):
        svg, root = self.render_ok(SEQ_FULL)
        g = geo(svg)
        loop = next(e for e in g["edges"] if e["from"] == e["to"] == "b")
        self.assertGreater(max(p[0] for p in loop["pts"]), loop["pts"][0][0] + 20)
        svg2, _ = self.render_ok(SEQUENCE)
        loop2 = next(e for e in geo(svg2)["edges"] if e["from"] == e["to"] == "b")
        self.assertLess(min(p[0] for p in loop2["pts"]), loop2["pts"][0][0] - 20)

    # Claim: a stack note sits beside its node (right) or its group (left) on
    # a connector, outside the column; a note on a side that carries a return
    # lane is refused.
    def test_stack_notes(self):
        svg, _ = self.render_ok(STACK_NOTES)
        g = geo(svg)
        notes = {n["id"]: n["r"] for n in g["notes"]}
        boxes = {b["id"]: b["r"] for b in g["boxes"]}
        groups = {x["id"]: x["r"] for x in g["groups"]}
        self.assertGreater(notes["note_d"][0], boxes["d"][2])
        self.assertLess(notes["note_g"][2], groups["g"][0])
        conns = [e for e in g["edges"] if e["cls"] == "connector"]
        self.assertEqual({(c["from"], c["to"]) for c in conns}, {("d", "note_d"), ("g", "note_g")})
        bad = STACK_NOTES + '[[links]]\nfrom = "d"\nto = "a"\nside = "left"\n'
        self.refused(bad, "groups.g.note: the left side carries a return lane")

    # Claim: root lanes on both sides and a lane inside a group render without
    # geometry problems; two lanes on one side nest: the outer lane attaches
    # higher on the upper box.
    def test_side_lanes(self):
        svg, _ = self.render_ok(STACK_LANES)
        g = geo(svg)
        left = [e for e in g["edges"] if e["edge"] in ("e4", "e5")]
        self.assertEqual(len(left), 2)
        outer = min(left, key=lambda e: min(p[0] for p in e["pts"]))
        inner = max(left, key=lambda e: min(p[0] for p in e["pts"]))
        self.assertLess(outer["pts"][-1][1], inner["pts"][-1][1])
        inside = next(e for e in g["edges"] if e["from"] == "b" and e["to"] == "d")
        group = next(x["r"] for x in g["groups"] if x["id"] == "g")
        self.assertTrue(all(render.hit(render.grow(group, 1), p) for p in inside["pts"]))

    # Claim (regression, review P2-8): a long return label on a root lane is
    # wholly inside the viewBox. The reviewer's probe: three boxes, c -> a.
    def test_root_lane_long_label_inside(self):
        text = '''
layout = "stack"
[nodes.a]
role = "service"
name = "Первый"
[nodes.b]
role = "service"
name = "Второй"
[nodes.c]
role = "service"
name = "Третий"
[[links]]
from = "c"
to = "a"
label = "очень длинная подпись возврата, которая не помещается вдоль полосы между близкими блоками"
'''
        svg, root = self.render_ok(text)
        g = geo(svg)
        view = (0, 0, g["W"], g["H"])
        for t in g["texts"]:
            self.assertTrue(render.within(t["r"], view), t["s"])
        self.assertTrue(any("близкими" in t["s"] for t in g["texts"]))

    @needs_dot
    # Claim: graph start and end states are drawn (dot; ring around a dot),
    # the end state has an incoming arrow, a note sits beside its node on the
    # same rank with a connector, and same_rank puts nodes on one line.
    def test_graph_states_and_note(self):
        svg, root = self.render_ok(GRAPH_STATES)
        g = geo(svg)
        boxes = {b["id"]: b["r"] for b in g["boxes"]}
        circles = list(root.iter(SVG + "circle"))
        self.assertIn("<!-- node e1 -->", svg)
        ring = next(c for c in circles if c.get("data-id") == "e1")
        self.assertEqual(ring.get("fill"), KIT.c["background"])
        self.assertTrue(any(c.get("cx") == ring.get("cx") and c.get("fill") == KIT.c["line"] for c in circles))
        self.assertTrue(any(e["to"] == "e1" for e in g["edges"]))
        note = g["notes"][0]["r"]
        sent = boxes["sent"]
        self.assertAlmostEqual((note[1] + note[3]) / 2, (sent[1] + sent[3]) / 2, delta=1)
        self.assertGreater(note[0], sent[2])
        self.assertTrue(any(e["cls"] == "connector" and e["from"] == "sent" for e in g["edges"]))
        self.assertAlmostEqual(boxes["done"][1] + boxes["done"][3], boxes["fail"][1] + boxes["fail"][3], delta=1)

    @needs_dot
    # Claim: column keeps nodes on one vertical line and uniform_width gives
    # every node of a column one width while a node outside keeps its own.
    def test_graph_columns_uniform(self):
        svg, _ = self.render_ok(GRAPH_COLUMNS)
        boxes = {b["id"]: b["r"] for b in geo(svg)["boxes"]}
        widths = {k: round(r[2] - r[0], 1) for k, r in boxes.items()}
        self.assertEqual(widths["a"], widths["b"])
        self.assertEqual(widths["b"], widths["c"])
        self.assertLess(widths["x"], widths["a"])
        centres = {round((boxes[k][0] + boxes[k][2]) / 2) for k in "abc"}
        self.assertEqual(len(centres), 1)
        svg2, _ = self.render_ok(GRAPH_COLUMNS.replace("uniform_width = true\n", ""))
        boxes2 = {b["id"]: b["r"] for b in geo(svg2)["boxes"]}
        self.assertNotEqual(round(boxes2["a"][2] - boxes2["a"][0]), round(boxes2["c"][2] - boxes2["c"][0]))

    @needs_dot
    # Claim: the graph layout is pinned to one Graphviz version: another
    # version is refused unless the draft switch is set; the SVG names the
    # version it was laid out with.
    def test_graphviz_pin(self):
        svg, _ = self.render_ok(GRAPH)
        self.assertIn(f"<!-- graphviz {render.graphviz_version()} -->", svg)
        pin = render.GRAPHVIZ_PIN
        try:
            render.GRAPHVIZ_PIN = "0.0.0"
            self.refused(GRAPH, "pinned to Graphviz 0.0.0")
            self.render_ok(GRAPH, graphviz_any=True)
            self.render_ok(STACK)  # stack does not touch Graphviz
        finally:
            render.GRAPHVIZ_PIN = pin


class TextTests(Base):
    # Claim: the last line of a wrapped label is not a lone word when the line
    # above can give one. Control: the plain balanced wrap of the same text at
    # the same measure does end with a lone word, so the case is meaningful.
    def test_no_widow(self):
        found = 0
        for raw in ("сто два три подпись", "сто два ключ соединение", "подписи условия сроки актуальный отзыв"):
            t = KIT.text(raw, 15, bold=True)
            for w in range(60, 400, 2):
                plain = t.balanced(t.paragraphs[0], w)
                t.wrap(w)
                fixable = len(plain) > 1 and len(plain[-1]) == 1 and len(plain[-2]) >= 3 and \
                    t.line_width([plain[-2][-1]] + plain[-1]) <= w
                if fixable:
                    found += 1
                    self.assertGreaterEqual(len(t.lines[-1]), 2, (raw, w))
                if max(t.word_width(x) for x in t.paragraphs[0]) <= w:
                    self.assertLessEqual(t.width, w + 0.5)
        self.assertGreater(found, 0, "no control case: the plain wrap never left a fixable widow")

    # Claim: a one- or two-letter word never ends a line (it stays with the
    # next word), and an explicit line break in the source is kept.
    def test_short_words_and_breaks(self):
        t = KIT.text("срок не длиннее; глубина в пределах", 15, bold=True)
        for w in range(60, 300, 3):
            t.wrap(w)
            for line in t.lines[:-1]:
                last = line[-1][-1][0]
                self.assertFalse(render.SHORT_WORD.match(last), (w, last))
        t = KIT.text("цепочка до корня; подмножество;\nсрок не длиннее", 15).wrap(1000)
        self.assertEqual(len(t.lines), 2)
        self.assertEqual(t.lines[0][-1][-1][0], "подмножество;")


class LintTests(Base):
    def planted(self, svg, extra):
        return svg.replace("</svg>", extra + "\n</svg>")

    # Claim: the lint passes every fixture (positive control) and catches each
    # planted violation with its own message (instrument control): a plate on
    # an arrow, text outside the viewBox, overlapping boxes, a label away from
    # its arrow, text spilling out of a box, text across a boundary and two
    # lines drawn on top of each other.
    def test_lint_detects_planted_violations(self):
        svg, root = self.render_ok(STACK)
        self.assertEqual(render.lint(svg, KIT), [])
        g = geo(svg)
        edge = next(e for e in g["edges"] if e["from"] == "a")
        mx, my = edge["pts"][len(edge["pts"]) // 2]
        box = next(b for b in g["boxes"] if b["id"] == "c")["r"]
        spill = "текст"
        while KIT.m.width(spill, "sans", 15) < box[2] - box[0] + 20:
            spill += " текст"
        cases = {
            "runs through a label plate":
                f'<rect x="{mx - 20}" y="{my - 8}" width="40" height="16" fill="#ffffff" class="plate"/>',
            "lies outside the viewBox":
                f'<text x="{g["W"] + 40}" y="20" font-size="15" fill="#1f2328"><tspan font-family="PT Sans">край</tspan></text>',
            "overlaps box zz":
                f'<rect x="{box[0] + 10}" y="{box[1] + 5}" width="80" height="30" class="box" data-id="zz"/>',
            "spills out of box c":
                f'<text x="{box[0] + 4}" y="{(box[1] + box[3]) / 2}" font-size="15" fill="#1f2328">'
                f'<tspan font-family="PT Sans">{spill}</tspan></text>',
            "crosses a boundary":
                f'<rect x="{box[0] - 30}" y="{box[1] - 30}" width="40" height="300" class="group"/>',
        }
        for reason, extra in cases.items():
            with self.subTest(reason=reason):
                probs = render.lint(self.planted(svg, extra), KIT)
                self.assertTrue(any(reason in p for p in probs), probs)
        x0, y0 = edge["pts"][0]
        x1, y1 = edge["pts"][-1]
        twin = (f'<path d="M {x0} {y0} L {x1} {y1}" class="connector" data-from="x" data-to="y"/>')
        probs = render.lint(self.planted(svg, twin), KIT)
        self.assertTrue(any("run on top of each other" in p for p in probs), probs)
        probs = render.lint(self.fix_label_shift(svg), KIT)
        self.assertTrue(any("from its arrow" in p for p in probs), probs)

    def fix_label_shift(self, svg):
        """Move the first tagged label 120 px down, away from its arrow."""
        m = re.search(r'<g class="label" data-edge="e0">.*?\n</g>', svg, flags=re.S)
        return svg[:m.start()] + '<g transform="translate(0 120)">' + m.group(0) + "</g>" + svg[m.end():]

    # Claim: a planted overlap makes render() itself fail, so the lint gates
    # the render and is not only a separate tool.
    def test_render_fails_on_planted_overlap(self):
        orig = render.LAYOUTS["stack"]

        def bad(kit, d, opts):
            body, w, h = orig(kit, d, opts)
            return body + '\n<rect x="0" y="0" width="5000" height="60" class="plate"/>', w, h
        try:
            render.LAYOUTS["stack"] = bad
            self.refused(STACK, "geometry lint:")
        finally:
            render.LAYOUTS["stack"] = orig
        self.render_ok(STACK)


class PrintTests(Base):
    # Claim: the print report judges the figure on its smallest text, not only
    # on descriptions (limit: 96 px per inch, as WeasyPrint reads SVG).
    def test_print_report(self):
        theme = render.load_theme()
        small = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><text font-size="15"/></svg>'
        huge = '<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="3000"><text font-size="15"/></svg>'
        self.assertEqual(render.print_report(small, theme)["fits"], "normal")
        self.assertEqual(render.print_report(huge, theme)["fits"], "no")
        # The same canvas with one 9 px label no longer fits the normal box.
        tiny = small.replace("</svg>", '<text font-size="9"/></svg>')
        r = render.print_report(tiny, theme)
        self.assertEqual(r["smallest_px"], 9)
        self.assertNotEqual(r["fits"], "normal")
        self.assertGreaterEqual(r["normal_text"], theme["print"]["min_print_pt"])

    # Claim: --require-fit exits 3 when the smallest text would print below
    # the limit in the requested box, and 0 when it fits.
    def test_require_fit(self):
        out = self.dir / "o.svg"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(render.main([str(self.src(STACK)), str(out), "--require-fit", "tall"]), 0)
            many = SEQUENCE.replace('[nodes.b]', "\n".join(
                f'[nodes.p{i}]\nrole = "service"\nname = "Участник с длинным именем {i}"' for i in range(9)) + "\n[nodes.b]")
            self.assertEqual(render.main([str(self.src(many)), str(out), "--require-fit", "tall"]), 3)


class PilotTests(Base):
    # Claim: every committed -v2 source renders through schema and lint, and
    # its committed SVG is byte-identical to a fresh render (graph pilots need
    # the pinned Graphviz and are skipped without it).
    def test_pilots_fresh(self):
        sources = sorted(ROOT.glob("book/src/*-v2.toml")) + sorted(ROOT.glob("editorial/notes/*/src/*-v2.toml"))
        self.assertGreaterEqual(len(sources), 7)
        for src in sources:
            with self.subTest(src=src.name):
                if render.load_source(src).get("layout") == "graph" and not PINNED:
                    self.skipTest("graph pilot needs the pinned Graphviz")
                svg = render.render(src)
                committed = src.parent.parent / "diagrams" / (src.stem + ".svg")
                self.assertEqual(svg, committed.read_text(encoding="utf-8"), f"{committed} is stale")


if __name__ == "__main__":
    unittest.main()
