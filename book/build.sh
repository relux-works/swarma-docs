#!/usr/bin/env bash
# Build the Swarma book: Markdown chapters -> HTML (pandoc) -> PDF (WeasyPrint).
#
#   book/build.sh          builds book/swarma-book.ru.pdf from book/ru/
#   book/build.sh ru OUT   writes the PDF to OUT instead
#
# Needs pandoc 3.x and WeasyPrint 69+, and the PT Serif, PT Sans and PT Mono fonts.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lang="${1:-ru}"
src="$here/$lang"
out="${2:-$here/swarma-book.$lang.pdf}"

for tool in pandoc weasyprint; do
  command -v "$tool" >/dev/null || { echo "build.sh: $tool not found" >&2; exit 1; }
done

shopt -s nullglob
chapters=("$src"/[0-9][0-9]-*.md)
if (( ${#chapters[@]} == 0 )); then
  echo "build.sh: no chapters in $src" >&2
  exit 1
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/swarma-book.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# Chapter 0 is numbered 0, so the offset is -1.
pandoc "${chapters[@]}" \
  --from markdown \
  --to html5 \
  --standalone \
  --template "$here/template.html" \
  --lua-filter "$here/filters/book.lua" \
  --toc --toc-depth=2 \
  --syntax-highlighting=none \
  --number-sections --number-offset=-1 \
  --metadata lang="$lang" \
  --output "$tmp/note.html"

# Relative image paths in the chapters (../diagrams/…) resolve against the
# chapter directory.
weasyprint \
  --base-url "$src/" \
  --stylesheet "$here/style.css" \
  "$tmp/note.html" "$out"

echo "$out"
