#!/usr/bin/env python3
"""Positive and negative checks for render.py on disposable fixtures.

    python3 scripts/diagram-kit/test_render.py

The graph cases need Graphviz `dot`; they are skipped, and say so, without it.
"""
import pathlib
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402

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

SVG = "{http://www.w3.org/2000/svg}"


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="diagram-kit-")
        self.addCleanup(self.tmp.cleanup)
        self.dir = pathlib.Path(self.tmp.name)

    def src(self, text, name="d.toml"):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def render_ok(self, text):
        svg = render.render(self.src(text))
        root = ET.fromstring(svg)  # well-formed XML
        self.assertEqual(root.tag, SVG + "svg")
        return svg, root

    # Claim: each layout renders well-formed SVG that uses only theme colours,
    # draws circled step numbers as shapes, sets code in PT Mono, and never
    # needs foreignObject (WeasyPrint cannot draw it).
    def test_layouts_render(self):
        theme = render.load_theme()
        palette = {v.lower() for v in theme["color"].values()} | {"#ffffff"}
        for role in theme["role"].values():
            palette |= {v.lower() for v in role.values()}
        cases = [STACK, SEQUENCE] + ([GRAPH] if shutil.which("dot") else [])
        for text in cases:
            svg, root = self.render_ok(text)
            self.assertNotIn("foreignObject", svg)
            self.assertNotIn("`", svg)
            for el in root.iter():
                for attr in ("fill", "stroke"):
                    v = el.get(attr)
                    if v and v not in ("none",):
                        self.assertIn(v.lower(), palette, f"{attr}={v} is not a theme colour")
            self.assertTrue(any(el.tag == SVG + "circle" for el in root.iter()))
        svg, _ = self.render_ok(STACK)
        self.assertIn('font-family="PT Mono, monospace">nonce<', svg)

    # Claim: the output is byte-identical across runs for the same source and theme.
    def test_deterministic(self):
        for text in [STACK, SEQUENCE] + ([GRAPH] if shutil.which("dot") else []):
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

    @unittest.skipUnless(shutil.which("dot"), "Graphviz dot not installed; graph layout not checked")
    def test_graph_renders_group_and_edge(self):
        svg, root = self.render_ok(GRAPH)
        self.assertIn("<!-- group g -->", svg)
        self.assertIn("<!-- link a -> b -->", svg)

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
                with self.assertRaises(render.DiagramError) as cm:
                    render.render(self.src(text))
                self.assertIn(reason, str(cm.exception))

    # Claim: the "split group" check accepts a group whose nodes are adjacent
    # (positive control for the refusal above).
    def test_contiguous_group_accepted(self):
        text = STACK.replace('[nodes.c]\nrole', '[nodes.c]\ngroup = "g"\nrole')
        self.render_ok(text)

    # Claim: the CLI exits non-zero on a refused source and writes no file.
    def test_cli_refusal_writes_nothing(self):
        out = self.dir / "out.svg"
        rc = render.main([str(self.src(STACK.replace('role = "service"', 'role = "blue"'))), str(out)])
        self.assertEqual(rc, 1)
        self.assertFalse(out.exists())

    # Claim: the print report marks a compact figure as fitting the normal box
    # and an oversized one as not fitting at all (limit: 96 px per inch).
    def test_print_report(self):
        theme = render.load_theme()
        small = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"/>'
        huge = '<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="3000"/>'
        self.assertEqual(render.print_report(small, theme)["fits"], "normal")
        self.assertEqual(render.print_report(huge, theme)["fits"], "no")


if __name__ == "__main__":
    unittest.main()
