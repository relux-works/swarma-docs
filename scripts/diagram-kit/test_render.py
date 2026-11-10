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
import subprocess
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


def acting_instance_problem(src):
    """Why the composed figure at src mislabels the acting agent instance, or
    None. The acting participant is the one that sends a message to the node
    named "Прокси модели"; its header name and subtitle are read from the
    rendered SVG, not from the source text."""
    d = render.load_source(src)
    proxies = {k for k, n in d["nodes"].items() if n.get("name") == "Прокси модели"}
    senders = {m["from"] for m in d.get("seq", []) if m.get("to") in proxies and m.get("from") not in proxies}
    if len(senders) != 1:
        return f"expected one participant that calls the model proxy, found {sorted(senders)}"
    sender = senders.pop()
    header = drawn_header(src, sender)
    if header is None:
        return f"participant {sender} is not drawn once"
    name, subtitle = header
    if re.search(r"(?i)\bслот", name):
        return f"the participant that calls the model proxy is headed '{name}': the slot stands for the instance"
    if not re.search(r"(?i)экземпляр", name):
        return f"the participant that calls the model proxy is headed '{name}', not as the agent instance"
    if not re.search(r"(?i)слот", subtitle):
        return f"the subtitle '{subtitle}' does not place the instance in its slot"
    return None


def drawn_header(src, node):
    """The header of one participant as the rendered SVG shows it: (name,
    subtitle), or None when the participant is not drawn exactly once."""
    svg = render.render(src)
    marker = f"<!-- node {node} -->"
    if svg.count(marker) != 1:
        return None
    header = svg.split(marker)[1].split("<!-- ")[0]
    name, subtitle = [], []
    for run in re.findall(r"<tspan([^>]*)>([^<]*)</tspan>", header):
        (name if 'font-weight="bold"' in run[0] else subtitle).append(run[1])
    return " ".join(name).strip(), " ".join(subtitle).strip()


def branch_messages(d):
    """Every message of a sequence source with the labels of the frames it
    sits in, outermost first: for an alt frame the label of the current
    branch, for an opt frame its label."""
    stack, out = [], []
    for m in d.get("seq", []):
        if "alt" in m:
            stack.append(m["alt"])
        elif "opt" in m:
            stack.append(m["opt"])
        elif "else" in m:
            stack[-1] = m["else"]
        elif m.get("end"):
            stack.pop()
        elif "from" in m:
            out.append((m, tuple(stack)))
    return out


def unsigned_mail_guard_problem(part1, part2):
    """Why the mail-delivery pair lets a body reach the session host without
    the decision guard, or None. Relations are read from the parsed sources
    that the renderer accepts; both parts must also render."""
    def flat(label):
        return " ".join(label.split())

    def by_name(d, name):
        ids = [k for k, n in d["nodes"].items() if n.get("name") == name]
        return ids[0] if len(ids) == 1 else None

    d1, d2 = render.load_source(part1), render.load_source(part2)
    for part, src, d in (("part 1", part1, d1), ("part 2", part2, d2)):
        guard = by_name(d, "Decision guard")
        if guard is None or drawn_header(src, guard) is None:
            return f"{part}: the decision guard is not drawn once"
    guard1, host1 = by_name(d1, "Decision guard"), by_name(d1, "Хост сессий")
    for m, frames in branch_messages(d1):
        if host1 is not None and m["to"] == host1 and m["from"] != host1:
            return f"part 1: '{flat(m['label'])}' rings the session host before the decision guard"
        if frames and re.search(r"(?i)нет подписи", frames[-1]) and m["to"] != guard1:
            target = d1["nodes"][m["to"]].get("name")
            return f"part 1: the unsigned branch sends '{flat(m['label'])}' to '{target}', past the decision guard"
    unsigned1 = [m for m, frames in branch_messages(d1) if frames and re.search(r"(?i)нет подписи", frames[-1])]
    if not unsigned1:
        return "part 1: no branch for an unsigned body"
    guard2, host2 = by_name(d2, "Decision guard"), by_name(d2, "Хост сессий")
    if host2 is None:
        return "part 2: the session host is not a participant"
    msgs = branch_messages(d2)
    if not any(m["to"] == guard2 and m["from"] != guard2 and not frames for m, frames in msgs):
        return "part 2: the body does not enter the decision guard before the branches"
    refusal = [(m, f) for m, f in msgs if f and re.search(r"(?i)недоступен", f[-1]) and re.search(r"(?i)отказал", f[-1])]
    if not refusal:
        return "part 2: no branch for a refusing or unavailable guard"
    bells = [(m, f) for m, f in msgs if m["to"] == host2 and m["from"] != host2]
    for m, frames in bells:
        if not any(re.search(r"(?i)guard разрешил", f) for f in frames):
            return f"part 2: '{flat(m['label'])}' reaches the session host outside the 'guard разрешил' branch"
    if not any(re.search(r"(?i)метаданн", m["label"]) for m, _ in bells):
        return "part 2: no metadata-only bell for an unsigned body after the guard allows it"
    return None


def command_performer_problem(src):
    """Why the composed figure at src mislabels the participant that runs the
    command, or None. That participant is the target of the message labelled
    "команда" and the sender of "вывод"; headers are read from the rendered
    SVG, not from the source text."""
    d = render.load_source(src)
    runs = {m["to"] for m in d.get("seq", []) if m.get("label") == "команда"}
    outs = {m["from"] for m in d.get("seq", []) if m.get("label") == "вывод"}
    if len(runs) != 1 or runs != outs:
        return f"expected one participant that takes the command and returns the output, found {sorted(runs | outs)}"
    performer = runs.pop()
    header = drawn_header(src, performer)
    if header is None:
        return f"participant {performer} is not drawn once"
    name, subtitle = header
    if re.search(r"(?i)уч[её]тн\w+ запис", name):
        return f"the participant that runs the command is headed '{name}': an OS account stands for the process"
    if not re.search(r"(?i)процесс", name):
        return f"the participant that runs the command is headed '{name}', not as a process"
    if not re.search(r"(?i)уч[её]тн\w+ запис\w+ слота", subtitle):
        return f"the subtitle '{subtitle}' does not place the process under the slot account"
    for sender in {m["from"] for m in d.get("seq", []) if m.get("label") == "команда"}:
        checker = drawn_header(src, sender)
        if checker is None or re.search(r"(?i)слот", " ".join(checker)):
            return f"the checking service that sends the command is drawn inside the slot account: {checker}"
    return None


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
            "theme.space.pad: must be at most 2000": "[theme.space]\npad = 1e308\n",
            "theme.space.seq_label_width: must be at most 2000": "[theme.space]\nseq_label_width = 2001\n",
            "theme.space.line_height: must be at most 4": "[theme.space]\nline_height = 4.5\n",
            "theme.space.letter_spacing: must be at most 4": "[theme.space]\nletter_spacing = 10\n",
            "theme.space.graph_ranksep: must be at most 20": "[theme.space]\ngraph_ranksep = 1e9\n",
        }
        for reason, tail in probes.items():
            with self.subTest(reason=reason):
                self.refused(STACK + "\n" + tail, reason)

    # Claim: valid spacing overrides are accepted and take effect (positive
    # control: the override mechanism is not simply disabled).
    def test_space_override_accepted(self):
        svg, _ = self.render_ok(STACK + '\n[theme.space]\ngroup_dash = "4 4"\npad = 20\n')
        self.assertIn('width="', svg)
        self.assertNotIn("inf", svg)
        # The bounds themselves are allowed (boundary positive control).
        self.render_ok(STACK + '\n[theme.space]\nline_height = 4\ngap_min = 2000\n')
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

    # Claim: a note on one participant sits beside its lifeline inside the
    # enclosing alt frame and inside the participant's container. b is the
    # last participant of its container, so a note asked on the right moves
    # to the left, ending 10 px before b's lifeline; on a (first of the same
    # container) the right side is kept (positive control). A note on the
    # only participant of a container is refused: either side covers a border.
    def test_note_on_participant_in_alt(self):
        svg, root = self.render_ok(SEQ_FULL)
        g = geo(svg)
        note = g["notes"][0]["r"]
        frames = [f["r"] for f in g["frames"]]
        self.assertTrue(any(render.within(note, f) for f in frames))
        left = next(x["r"] for x in g["groups"] if x["id"] == "left")
        self.assertTrue(render.within(note, left))
        bline = [l for l in root.iter(SVG + "line") if l.get("stroke-dasharray") == "4 5"]
        xs = sorted(float(l.get("x1")) for l in bline)
        shift = self.pad_shift(root)
        # lifeline of b is the second one; the note ends 10 px left of it
        self.assertAlmostEqual((xs[1] + shift) - note[2], 10, delta=1)
        svg2, _ = self.render_ok(SEQ_FULL.replace('on = "b"', 'on = "b"\nside = "left"'))
        self.assertAlmostEqual(geo(svg2)["notes"][0]["r"][2], note[2], delta=1)
        svg3, root3 = self.render_ok(SEQ_FULL.replace('on = "b"', 'on = "a"'))
        note3 = geo(svg3)["notes"][0]["r"]
        xs3 = sorted(float(l.get("x1")) for l in root3.iter(SVG + "line") if l.get("stroke-dasharray") == "4 5")
        self.assertAlmostEqual(note3[0] - (xs3[0] + self.pad_shift(root3)), 10, delta=1)
        self.refused(SEQ_FULL.replace('on = "b"', 'on = "c"'), "the note on c would cover the border of right")
        self.refused(SEQ_FULL.replace('on = "b"', 'on = "zz"'), "unknown node 'zz'")

    def pad_shift(self, root):
        """x offset of the body group (padding plus the layout's own shift)."""
        shift = 0.0
        for g in root.iter(SVG + "g"):
            m = re.match(r"translate\(([-0-9.]+) ", g.get("transform") or "")
            if m:
                shift += float(m.group(1))
        return shift

    # Claim (review r2, P2-2): where a message crosses container borders its
    # label plate lies between two borders, never on one; this holds for the
    # four cross-machine messages of the remote-worker-turn pilot, whose
    # labels sit in the gap between the donor's and our container. Divider
    # pills and frame condition labels keep clear of the borders too.
    def test_cross_boundary_labels_clear(self):
        src = (ROOT / "scripts/diagram-kit/fixtures/remote-worker-turn-full.toml").read_text(encoding="utf-8")
        for text in (SEQ_FULL, src):
            with self.subTest(source=text[:30]):
                svg, _ = self.render_ok(text)
                g = geo(svg)
                for grp in g["groups"]:
                    for p in g["plates"]:
                        r = render.grow(p["r"], 2)
                        self.assertFalse(render.overlap(r, grp["r"]) and not render.within(r, grp["r"]),
                                         (grp["id"], p["r"]))
        g = geo(self.render_ok(src)[0])
        donor = next(x["r"] for x in g["groups"] if x["id"] == "donor")
        ours = next(x["r"] for x in g["groups"] if x["id"] == "ours")
        crossing = [p["r"] for p in g["plates"] if p["r"][0] > donor[2] and p["r"][2] < ours[0]]
        self.assertEqual(len(crossing), 4)

    # Claim (book wave review, P3-8): a participant alone in its container
    # loops its self-message to the right, and the container widens so the
    # label plate lies inside it, in a middle column and in the last column;
    # the next participant's header stays outside the widened container.
    # Limit: checks plate and header geometry, not the loop path itself.
    def test_self_message_in_one_participant_container(self):
        base = """
layout = "sequence"
[groups.kg]
label = "Граница"
role = "key"
[nodes.x]
role = "service"
name = "Диспетчер"
[nodes.k]
group = "kg"
role = "key"
name = "Ключник"
%s
[[seq]]
from = "x"
to = "k"
step = 1
label = "зарегистрировать"
[[seq]]
from = "k"
to = "k"
step = 2
label = "сохранить привязку личности и пути деривации"
"""
        tail = '[nodes.y]\nrole = "store"\nname = "Реестр"\n'
        for name, text in (("middle", base % tail), ("last", base % "")):
            with self.subTest(column=name):
                g = geo(self.render_ok(text)[0])
                grp = next(x["r"] for x in g["groups"] if x["id"] == "kg")
                plates = [p["r"] for p in g["plates"]]
                self.assertTrue(plates)
                for r in plates:
                    r = render.grow(r, 2)
                    self.assertFalse(render.overlap(r, grp) and not render.within(r, grp), (grp, r))
                label = max(plates, key=lambda r: r[0])
                self.assertTrue(render.within(label, grp))
                boxes = {x["id"]: x["r"] for x in g["boxes"]}
                if "y" in boxes:
                    self.assertFalse(render.overlap(boxes["y"], grp))

    # Claim: a note over participants on both sides of a container border is
    # drawn under the containers, clear of every border; such a note followed
    # by a message is refused, and a note over one container stays in its row
    # (positive control).
    def test_note_across_containers(self):
        src = SEQ_FULL + '[[seq]]\nnote = "Общее примечание."\nover = ["a", "d"]\n'
        svg, _ = self.render_ok(src)
        g = geo(svg)
        note = next(n["r"] for n in g["notes"] if n["r"][3] - n["r"][1] < 60 and n["r"][2] - n["r"][0] > 300)
        self.assertGreater(note[1], max(x["r"][3] for x in g["groups"]))
        self.refused(src + '[[seq]]\nfrom = "a"\nto = "b"\nlabel = "ещё"\n', "spans a container border")
        svg2, _ = self.render_ok(SEQ_FULL + '[[seq]]\nnote = "Слева."\nover = ["a", "b"]\n')
        g2 = geo(svg2)
        left = next(x["r"] for x in g2["groups"] if x["id"] == "left")
        self.assertTrue(any(render.within(n["r"], left) for n in g2["notes"] if n["r"][2] - n["r"][0] > 100))

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
    # column it loops to the left; at the right edge of a container with a
    # neighbour inside it loops to the left, so its label stays inside.
    def test_self_message_direction(self):
        svg, root = self.render_ok(SEQ_FULL.replace('from = "b"\nto = "b"', 'from = "a"\nto = "a"'))
        g = geo(svg)
        loop = next(e for e in g["edges"] if e["from"] == e["to"] == "a")
        self.assertGreater(max(p[0] for p in loop["pts"]), loop["pts"][0][0] + 20)
        svg2, _ = self.render_ok(SEQUENCE)
        loop2 = next(e for e in geo(svg2)["edges"] if e["from"] == e["to"] == "b")
        self.assertLess(min(p[0] for p in loop2["pts"]), loop2["pts"][0][0] - 20)
        # b is the last participant of its container: the loop and its label
        # turn left and stay inside the container.
        svg3, _ = self.render_ok(SEQ_FULL)
        g3 = geo(svg3)
        loop3 = next(e for e in g3["edges"] if e["from"] == e["to"] == "b")
        self.assertLess(min(p[0] for p in loop3["pts"]), loop3["pts"][0][0] - 20)
        left = next(x["r"] for x in g3["groups"] if x["id"] == "left")
        plate = next(p["r"] for p in g3["plates"] if render.hit(p["r"], (p["r"][0] + 1, p["r"][1] + 1))
                     and any(t["s"].endswith("проверка") and render.within(t["r"], p["r"], 1.5) for t in g3["texts"]))
        self.assertTrue(render.within(plate, left))

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

    # Claim (review r2, P2-2): a label plate, a note or a divider pill on a
    # container border, and an alt frame edge along one, are reported; the
    # clean sequence with containers passes (positive control), and a plate
    # or note fully inside a container is not reported (near-miss control).
    def test_lint_plate_and_note_on_boundary(self):
        svg, _ = self.render_ok(SEQ_FULL)
        self.assertEqual(render.lint(svg, KIT), [])
        g = geo(svg)
        left = next(x["r"] for x in g["groups"] if x["id"] == "left")
        bx, ymid = left[2], (left[1] + left[3]) / 2
        cases = {
            "a label plate covers a boundary":
                f'<rect x="{bx - 30}" y="{ymid}" width="60" height="18" fill="#ffffff" class="plate"/>',
            "a note covers a boundary":
                f'<rect x="{bx - 40}" y="{ymid + 40}" width="80" height="30" rx="10" class="note"/>',
            "a frame edge runs along a boundary":
                f'<rect x="{left[0] + 20}" y="{ymid}" width="{bx - left[0] - 19}" height="40" fill="none" class="frame"/>',
        }
        for reason, extra in cases.items():
            with self.subTest(reason=reason):
                probs = render.lint(self.planted(svg, extra), KIT)
                self.assertTrue(any(reason in p for p in probs), probs)
        inside = (f'<rect x="{bx - 90}" y="{left[3] - 30}" width="40" height="10" fill="#ffffff" class="plate"/>')
        self.assertFalse(any("boundary" in p for p in render.lint(self.planted(svg, inside), KIT)))

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


class FigureTests(Base):
    # Claim: every committed book figure source (book/src/*.toml) and every
    # -v2 pilot of a note renders through schema and lint, and its committed
    # SVG is byte-identical to a fresh render (graph figures need the pinned
    # Graphviz and are skipped without it). The whole-flow fixtures in
    # fixtures/ render through schema and lint too; the book uses their halves.
    def test_figures_fresh(self):
        sources = sorted(ROOT.glob("book/src/*.toml")) + sorted(ROOT.glob("editorial/notes/*/src/*-v2.toml"))
        self.assertGreaterEqual(len(sources), 7)
        for src in sources:
            with self.subTest(src=src.name):
                if render.load_source(src).get("layout") == "graph" and not PINNED:
                    self.skipTest("graph figure needs the pinned Graphviz")
                svg = render.render(src)
                committed = src.parent.parent / "diagrams" / (src.stem + ".svg")
                self.assertEqual(svg, committed.read_text(encoding="utf-8"), f"{committed} is stale")

    # Claim: in the composed rental-work figure of the Link book the lifeline
    # that sends the request to the model proxy is headed as the agent
    # instance, and the slot is named only as the place of that instance
    # (its subtitle). The glossary forbids calling the instance a slot.
    # Negative control: the same source with only the header name changed
    # back to "Слот", the words "экземпляр агента" kept in the subtitle, is
    # reported as the slot standing for the instance; both words are present
    # there, so a token search over the source would pass it.
    # Limit: reads the header of one participant in one figure; it does not
    # check the prose or other figures, and it renders in memory only.
    def test_rental_work_keeps_instance_distinct_from_slot(self):
        src = ROOT / "link-book/src/rental-work.toml"
        text = src.read_text(encoding="utf-8")
        self.assertIsNone(acting_instance_problem(src))
        mutant = text.replace('name = "Экземпляр агента"', 'name = "Слот"').replace(
            'text = "в слоте"', 'text = "экземпляр агента"')
        self.assertEqual(mutant.count('name = "Слот"'), 1)
        self.assertEqual(mutant.count('text = "экземпляр агента"'), 1)
        self.assertEqual(acting_instance_problem(self.src(mutant, "rental-work-mutant.toml")),
                         "the participant that calls the model proxy is headed 'Слот': the slot stands for the instance")

    # Claim: in the mail-delivery pair of the platform book no body reaches
    # the session host without the decision guard. In part 1 the unsigned
    # branch hands the body to the guard and nothing rings the host. In
    # part 2 the body enters the guard before any branch, a refusing or
    # unavailable guard has its own branch without a bell, every bell sits in
    # the "guard разрешил" branch, and the allowed unsigned body still gets
    # its metadata-only bell (the valid neighbour).
    # Negative controls keep the guard on the admitted path, so a search for
    # the word "guard" passes them: (a) part 1 with the unsigned body held in
    # the mailbox and a bell sent from the gates; (b) part 2 with a bell sent
    # from the gates before the guard frame; (c) part 2 with a bell inside
    # the refusal branch. Each must be reported with its own message.
    # Limit: reads the relations of these two sources as the renderer parses
    # them; it does not read the chapter prose and proves nothing about a
    # running bridge.
    def test_unsigned_mail_requires_incoming_guard(self):
        p1, p2 = ROOT / "book/src/mailbox-delivery-1.toml", ROOT / "book/src/mailbox-delivery-2.toml"
        t1, t2 = p1.read_text(encoding="utf-8"), p2.read_text(encoding="utf-8")
        self.assertIsNone(unsigned_mail_guard_problem(p1, p2))

        to_guard = 'from = "gate"\nto = "guard"\nstep = 4\nlabel = "тело как недоверенные данные"\n'
        bypass = ('from = "gate"\nto = "mailbox"\nstep = 4\nlabel = "удержать тело в карантине"\n\n[[seq]]\n'
                  'from = "gate"\nto = "host"\nstep = 5\nlabel = "звонок только с метаданными"\n')
        self.assertEqual(t1.count(to_guard), 1)
        host = '[nodes.host]\nrole = "service"\nname = "Хост сессий"\n\n[[seq]]\nfrom = "provider"\nto = "provider"'
        m1 = t1.replace(to_guard, bypass).replace('[[seq]]\nfrom = "provider"\nto = "provider"', host, 1)
        self.assertIn('to = "guard"', m1)  # the admitted path still goes to the guard
        self.assertEqual(unsigned_mail_guard_problem(self.src(m1, "mail-1-mutant.toml"), p2),
                         "part 1: the unsigned branch sends 'удержать тело в карантине' to 'Почтовый ящик', past the decision guard")

        entry = '[[seq]]\nfrom = "gate"\nto = "guard"\nstep = 4\n'
        self.assertEqual(t2.count(entry), 1)
        early = '[[seq]]\nfrom = "gate"\nto = "host"\nstep = 5\nlabel = "звонок только с метаданными"\n\n' + entry
        self.assertEqual(unsigned_mail_guard_problem(p1, self.src(t2.replace(entry, early), "mail-2-early.toml")),
                         "part 2: 'звонок только с метаданными' reaches the session host outside the 'guard разрешил' branch")

        allow = '[[seq]]\nelse = "guard разрешил"\n'
        self.assertEqual(t2.count(allow), 1)
        leak = '[[seq]]\nfrom = "mailbox"\nto = "host"\nstep = 6\nlabel = "звонок только с метаданными"\n\n' + allow
        self.assertEqual(unsigned_mail_guard_problem(p1, self.src(t2.replace(allow, leak), "mail-2-refusal.toml")),
                         "part 2: 'звонок только с метаданными' reaches the session host outside the 'guard разрешил' branch")

    # Claim: in the project-side figure of the remote turn the lifeline that
    # takes "команда" and returns "вывод" is headed as a process, the slot
    # account is named only as the context that process runs under (its
    # subtitle), and the service that sends the command is not drawn inside
    # the slot account.
    # Negative control: the same source with only the header changed back to
    # "Учётная запись слота" and the words "процесс команды" moved to the
    # subtitle is reported as an account standing for the process; both
    # phrases are present there, so a token search would pass it.
    # Limit: reads the headers of two participants in one figure as the SVG
    # draws them; it does not check the prose or the donor-side figure.
    def test_remote_command_lifeline_names_process(self):
        src = ROOT / "book/src/remote-worker-turn-ours.toml"
        text = src.read_text(encoding="utf-8")
        self.assertIsNone(command_performer_problem(src))
        mutant = text.replace('name = "Процесс команды"', 'name = "Учётная запись слота"').replace(
            'text = "под учётной записью слота"', 'text = "процесс команды"')
        self.assertEqual(mutant.count('name = "Учётная запись слота"'), 1)
        self.assertEqual(mutant.count('text = "процесс команды"'), 1)
        self.assertEqual(command_performer_problem(self.src(mutant, "remote-turn-mutant.toml")),
                         "the participant that runs the command is headed 'Учётная запись слота': an OS account stands for the process")

    # Claim (book wave review, P2-5 and P3-14): the structural pass of
    # book/check-figures.sh, which book/build.sh runs before every build,
    # passes on a copy of the book and fails with the intended message for a
    # chapter link without a source, a figure linked with and without
    # {.tall}, and a manifest "Поле" that differs from the link class.
    # Limit: runs on a copy of the committed book; the render pass (freshness
    # and fit) is covered by test_figures_fresh and the planted controls in
    # the wave notes.
    def test_check_figures_structural(self):
        def copy():
            tmp = pathlib.Path(tempfile.mkdtemp(dir=self.dir))
            for sub in ("ru", "src", "diagrams"):
                shutil.copytree(ROOT / "book" / sub, tmp / "book" / sub)
            shutil.copy(ROOT / "book/check-figures.sh", tmp / "book")
            return tmp

        def run(tmp):
            return subprocess.run(["bash", str(tmp / "book/check-figures.sh"), "--structural"],
                                  capture_output=True, text=True)

        clean = run(copy())
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertIn("figures: structural ok", clean.stdout)
        def append(t, text):
            with (t / "book/ru/02-swarma-celikom.md").open("a", encoding="utf-8") as f:
                f.write(text)

        plants = {
            "missing source: src/nope.toml": lambda t: append(t, "\n![Нет](../diagrams/nope.svg)\n"),
            "linked both with and without {.tall}: one-shot-agent-1.svg":
                lambda t: append(t, "\n![Ещё раз](../diagrams/one-shot-agent-1.svg){.tall}\n"),
            "manifest box differs from the link class: one-shot-agent-1": lambda t: (t / "book/src/MANIFEST.md").write_text(
                (t / "book/src/MANIFEST.md").read_text(encoding="utf-8").replace(
                    "| one-shot-agent-1 | `one-shot-agent-1.toml` | книга | — | обычное |",
                    "| one-shot-agent-1 | `one-shot-agent-1.toml` | книга | — | tall |"),
                encoding="utf-8"),
        }
        for want, plant in plants.items():
            with self.subTest(plant=want):
                tmp = copy()
                plant(tmp)
                r = run(tmp)
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(want, r.stdout)

    def test_fixtures_render(self):
        fixtures = sorted((ROOT / "scripts/diagram-kit/fixtures").glob("*.toml"))
        self.assertEqual(len(fixtures), 2)
        for src in fixtures:
            with self.subTest(src=src.name):
                self.assertIn("<svg", render.render(src))


if __name__ == "__main__":
    unittest.main()
