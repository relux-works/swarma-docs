#!/usr/bin/env python3
"""Regenerate metrics.json: advance widths of PT Sans and PT Mono.

    python3 make-metrics.py PTSans.ttc PTMono.ttc metrics.json

Run it only when the fonts change. Needs fontTools (`pip install fonttools`,
in a virtual environment); render.py itself needs only the standard library.
Accepts .ttc collections or the four .ttf files in the order regular, bold:
    python3 make-metrics.py --ttf Sans.ttf Sans-Bold.ttf Mono.ttf Mono-Bold.ttf metrics.json
"""
import json
import sys

from fontTools.ttLib import TTCollection, TTFont

RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x400, 0x45F), (0x2010, 0x2027), (0x2030, 0x203A),
          (0x2190, 0x21FF), (0x2200, 0x22FF), (0x2460, 0x2473)]


def from_ttc(path, family):
    fonts = {}
    for f in TTCollection(path).fonts:
        fonts[f["name"].getDebugName(4)] = f
    return fonts[family], fonts[family + " Bold"]


def table(font):
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    widths = {}
    for a, b in RANGES:
        for cp in range(a, b + 1):
            glyph = cmap.get(cp)
            if glyph is not None:
                widths[chr(cp)] = round(hmtx[glyph][0] * 1000 / upm)
    return {"default": widths["n"], "widths": "".join(widths), "advances": list(widths.values())}


def main(argv):
    if argv[:1] == ["--ttf"] and len(argv) == 6:
        sans, sans_b, mono, mono_b = (TTFont(p) for p in argv[1:5])
        out = argv[5]
    elif len(argv) == 3:
        sans, sans_b = from_ttc(argv[0], "PT Sans")
        mono, mono_b = from_ttc(argv[1], "PT Mono")
        out = argv[2]
    else:
        print(__doc__, file=sys.stderr)
        return 2
    data = {"sans": table(sans), "sans-bold": table(sans_b), "mono": table(mono), "mono-bold": table(mono_b)}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
