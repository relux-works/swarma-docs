#!/bin/sh
# Reproduce the tool comparison in editorial/notes/diagram-style-notes.ru.md.
#
#   sh scripts/diagram-kit/probe/run.sh [OUT_DIR]      # default: .temp/diagram-probe
#
# Two probes: a stack figure (a command from the phone: phone.toml, phone.d2
# with theme.d2, phone.mmd with mermaid.json, phone.puml) and a sequence
# (grants: book/src/grant-issue-and-check.toml and seq.puml, PlantUML with
# the house style). Every tool found on PATH renders its sources to SVG; each
# SVG is then put through WeasyPrint the way the book is built, and the PDF
# page is rasterised with pdftoppm, so a tool whose SVG breaks in the book
# shows it. A missing optional tool is reported and skipped; nothing is
# installed. The kit is not optional: if either kit render fails, the probe
# exits 1.
#
# Tools: python3 (the kit), d2, plantuml, mmdc (Mermaid CLI; set MMDC_CHROME
# to a Chrome binary when puppeteer has no browser of its own), weasyprint,
# pdftoppm, rsvg-convert. Versions go to OUT_DIR/versions.txt. Reference
# images are not part of the probe and are not stored in the repository.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
out=${1:-"$root/.temp/diagram-probe"}
mkdir -p "$out"
out=$(cd "$out" && pwd)
cd "$here" || exit 2

have() { command -v "$1" >/dev/null 2>&1; }
note() { printf '%s\n' "$*" | tee -a "$out/versions.txt"; }
: > "$out/versions.txt"

kit_failed=0
kit() {
  python3 "$root/scripts/diagram-kit/render.py" "$1" "$2" --report > "$out/kit.log" 2>&1
  status=$?
  tee -a "$out/versions.txt" < "$out/kit.log"
  [ "$status" = 0 ] || { note "kit: render of $1 failed"; kit_failed=1; }
}
note "kit: $(python3 --version 2>&1); graphviz: $(dot -V 2>&1)"
kit phone.toml "$out/phone-kit.svg"
kit "$root/book/src/grant-issue-and-check.toml" "$out/seq-kit.svg"

if have d2; then
  note "d2: $(d2 --version 2>&1)"
  d2 phone.d2 "$out/phone-d2.svg" >/dev/null 2>&1 || note "d2: render failed"
else
  note "d2: not found, skipped"
fi

if have plantuml; then
  note "plantuml: $(plantuml -version 2>&1 | head -1)"
  plantuml -tsvg -o "$out" phone.puml seq.puml >/dev/null 2>&1 || note "plantuml: render failed"
  [ -f "$out/phone.svg" ] && mv "$out/phone.svg" "$out/phone-puml.svg"
  [ -f "$out/seq.svg" ] && mv "$out/seq.svg" "$out/seq-puml.svg"
else
  note "plantuml: not found, skipped"
fi

if have mmdc; then
  note "mermaid: $(mmdc --version 2>&1)"
  set -- -c mermaid.json
  if [ -n "${MMDC_CHROME:-}" ]; then
    printf '{"executablePath": "%s", "args": ["--no-sandbox"]}\n' "$MMDC_CHROME" > "$out/puppeteer.json"
    set -- "$@" -p "$out/puppeteer.json"
  fi
  mmdc -i phone.mmd -o "$out/phone-mmd.svg" "$@" >/dev/null 2>&1 || note "mermaid: render failed"
else
  note "mermaid: not found, skipped"
fi

svgs=$(cd "$out" && ls -- *.svg 2>/dev/null)
for s in $svgs; do
  have rsvg-convert && rsvg-convert -z 1.5 "$out/$s" -o "$out/${s%.svg}.png"
done

if have weasyprint && have pdftoppm; then
  note "weasyprint: $(weasyprint --version 2>&1)"
  {
    echo '<html><head><meta charset="utf-8"><style>@page{size:A4;margin:12mm}'
    echo 'figure{margin:0 0 8mm;page-break-inside:avoid} img{display:block;max-width:167mm;max-height:168mm}'
    echo 'figcaption{font:9pt "PT Sans"}</style></head><body>'
    for s in $svgs; do
      echo "<figure><img src=\"$s\"><figcaption>$s</figcaption></figure>"
    done
    echo '</body></html>'
  } > "$out/book.html"
  (cd "$out" && weasyprint book.html book.pdf >/dev/null 2>&1) || note "weasyprint: failed"
  [ -f "$out/book.pdf" ] && pdftoppm -r 110 -png "$out/book.pdf" "$out/book-page"
else
  note "weasyprint or pdftoppm: not found, book check skipped"
fi
echo "probe: outputs in $out"
exit "$kit_failed"
