#!/usr/bin/env bash
# Build the installation book: Markdown chapters -> HTML (pandoc) -> PDF (WeasyPrint).
#
#   install-book/build.sh          builds install-book/swarma-install.ru.pdf from install-book/ru/
#   install-book/build.sh ru OUT   writes the PDF to OUT instead
#
# Reuses the Swarma book's template, stylesheet and Lua filter (book/), so the
# two books look the same. Needs pandoc 3.x and WeasyPrint 69+, and the PT
# Serif, PT Sans and PT Mono fonts.
#
# Figures live in install-book/src/<name>.toml and render to
# install-book/diagrams/<name>.svg with scripts/diagram-kit/render.py; the
# orchestrator renders them after review. Before the build:
#  - structural pass (always): every figure a chapter links has a TOML source,
#    every TOML source has its SVG, and diagrams/ holds no SVG without a source;
#  - render pass: every SVG equals a fresh render of its source and passes
#    --require-fit for its box ({.tall} links: tall, others: normal). It needs
#    the Graphviz the diagram kit pins. INSTALL_BOOK_SKIP_FIGURE_RENDER=1 skips
#    only this pass, with a warning.
# An image WeasyPrint cannot load also fails the build.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
book="$here/../book"
kit="$here/../scripts/diagram-kit/render.py"
lang="${1:-ru}"
src="$here/$lang"
out="${2:-$here/swarma-install.$lang.pdf}"

for tool in pandoc weasyprint python3; do
  command -v "$tool" >/dev/null || { echo "build.sh: $tool not found" >&2; exit 1; }
done

shopt -s nullglob
chapters=("$src"/[0-9][0-9]-*.md)
if (( ${#chapters[@]} == 0 )); then
  echo "build.sh: no chapters in $src" >&2
  exit 1
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/swarma-install.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# One line per chapter link: "<stem> <box>", box is tall or normal.
grep -ohE '\.\./diagrams/[a-z0-9-]+\.svg\)(\{[^}]*\})?' "${chapters[@]}" \
  | sed -E 's#^\.\./diagrams/##; s#\.svg\)\{[^}]*\.tall[^}]*\}$# tall#; s#\.svg\)(\{[^}]*\})?$# normal#' \
  | sort -u > "$tmp/links" || true

fail=0
while read -r stem box; do
  [ -f "$here/src/$stem.toml" ] || { echo "build.sh: figure $stem has no source src/$stem.toml" >&2; fail=1; }
  if [ "$(awk -v s="$stem" '$1 == s' "$tmp/links" | wc -l)" -gt 1 ]; then
    echo "build.sh: figure $stem is linked with different boxes" >&2; fail=1
  fi
done < "$tmp/links"
for toml in "$here"/src/*.toml; do
  stem="$(basename "$toml" .toml)"
  [ -f "$here/diagrams/$stem.svg" ] || { echo "build.sh: source $stem.toml has no render diagrams/$stem.svg" >&2; fail=1; }
done
for svg in "$here"/diagrams/*.svg; do
  stem="$(basename "$svg" .svg)"
  [ -f "$here/src/$stem.toml" ] || { echo "build.sh: render $stem.svg has no source" >&2; fail=1; }
done
(( fail == 0 )) || { echo "build.sh: figure check failed" >&2; exit 1; }

if [ "${INSTALL_BOOK_SKIP_FIGURE_RENDER:-}" = 1 ]; then
  echo "build.sh: WARNING: INSTALL_BOOK_SKIP_FIGURE_RENDER=1, figure freshness and fit are not checked" >&2
else
  for toml in "$here"/src/*.toml; do
    stem="$(basename "$toml" .toml)"
    box="$(awk -v s="$stem" '$1 == s {print $2}' "$tmp/links")"
    python3 "$kit" "$toml" "$tmp/$stem.svg" --require-fit "${box:-normal}" >/dev/null || {
      echo "build.sh: figure $stem does not render or does not fit the ${box:-normal} box" >&2; exit 1; }
    cmp -s "$tmp/$stem.svg" "$here/diagrams/$stem.svg" || {
      echo "build.sh: diagrams/$stem.svg is stale; re-render it from src/$stem.toml" >&2; exit 1; }
  done
fi

# Chapter 0 is numbered 0, so the offset is -1.
pandoc "${chapters[@]}" \
  --from markdown \
  --to html5 \
  --standalone \
  --template "$book/template.html" \
  --lua-filter "$book/filters/book.lua" \
  --toc --toc-depth=2 \
  --section-divs \
  --syntax-highlighting=none \
  --number-sections --number-offset=-1 \
  --metadata lang="$lang" \
  --output "$tmp/note.html"

# Relative image paths in the chapters (../diagrams/…) resolve against the
# chapter directory. WeasyPrint only logs an image it cannot load; that fails
# the build here, and the PDF is moved to OUT only after a clean run.
weasyprint \
  --base-url "$src/" \
  --stylesheet "$book/style.css" \
  "$tmp/note.html" "$tmp/book.pdf" 2> "$tmp/weasyprint.log" || { cat "$tmp/weasyprint.log" >&2; exit 1; }
cat "$tmp/weasyprint.log" >&2
if grep -q 'Failed to load image' "$tmp/weasyprint.log"; then
  echo "build.sh: an image failed to load; $out is left unchanged" >&2
  exit 1
fi
mv "$tmp/book.pdf" "$out"

echo "$out"
