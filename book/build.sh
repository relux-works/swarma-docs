#!/usr/bin/env bash
# Build the Swarma book: Markdown chapters -> HTML (pandoc) -> PDF (WeasyPrint).
#
#   book/build.sh          builds book/swarma-book.ru.pdf from book/ru/
#   book/build.sh ru OUT   writes the PDF to OUT instead
#
# BOOK_ROOT=DIR builds another book with the same kit: chapters from DIR/ru/,
# figures checked against DIR/src/ and DIR/diagrams/, and DIR/style.css, when
# present, applied after book/style.css. Without OUT the PDF goes to
# DIR/BOOK_PDF_NAME.ru.pdf (BOOK_PDF_NAME defaults to the directory name).
# a2a-book/build.sh is the wrapper for the a2a book. Without BOOK_ROOT the
# build is the platform book's, unchanged.
#
# Needs pandoc 3.x and WeasyPrint 69+, and the PT Serif, PT Sans and PT Mono fonts.
#
# The figures are checked first (book/check-figures.sh): the structural pass
# always runs, the render pass (fresh and fitting SVGs) needs the Graphviz the
# diagram kit pins and fails the build otherwise. BOOK_SKIP_FIGURE_RENDER=1
# skips only the render pass, with a warning. An image WeasyPrint cannot load
# also fails the build.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lang="${1:-ru}"
if [ -n "${BOOK_ROOT:-}" ]; then
  root="$(cd "$BOOK_ROOT" && pwd)"
  name="${BOOK_PDF_NAME:-$(basename "$root")}"
else
  root="$here"
  name="swarma-book"
fi
export BOOK_ROOT="$root"
src="$root/$lang"
out="${2:-$root/$name.$lang.pdf}"
stylesheets=(--stylesheet "$here/style.css")
if [ "$root" != "$here" ] && [ -f "$root/style.css" ]; then
  stylesheets+=(--stylesheet "$root/style.css")
fi

for tool in pandoc weasyprint; do
  command -v "$tool" >/dev/null || { echo "build.sh: $tool not found" >&2; exit 1; }
done

shopt -s nullglob
chapters=("$src"/[0-9][0-9]-*.md)
if (( ${#chapters[@]} == 0 )); then
  echo "build.sh: no chapters in $src" >&2
  exit 1
fi

bash "$here/check-figures.sh" --structural || { echo "build.sh: figure check failed" >&2; exit 1; }
if [ "${BOOK_SKIP_FIGURE_RENDER:-}" = 1 ]; then
  echo "build.sh: WARNING: BOOK_SKIP_FIGURE_RENDER=1, figure freshness and fit are not checked" >&2
else
  bash "$here/check-figures.sh" --render || {
    echo "build.sh: figure render check failed (BOOK_SKIP_FIGURE_RENDER=1 skips it for a draft)" >&2
    exit 1
  }
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
  --section-divs \
  --syntax-highlighting=none \
  --number-sections --number-offset=-1 \
  --metadata lang="$lang" \
  --output "$tmp/note.html"

# Relative image paths in the chapters (../diagrams/…) resolve against the
# chapter directory.
# WeasyPrint only logs an image it cannot load; that fails the build here,
# and the PDF is moved to OUT only after a clean run.
weasyprint \
  --base-url "$src/" \
  "${stylesheets[@]}" \
  "$tmp/note.html" "$tmp/book.pdf" 2> "$tmp/weasyprint.log" || { cat "$tmp/weasyprint.log" >&2; exit 1; }
cat "$tmp/weasyprint.log" >&2
if grep -q 'Failed to load image' "$tmp/weasyprint.log"; then
  echo "build.sh: an image failed to load; $out is left unchanged" >&2
  exit 1
fi
mv "$tmp/book.pdf" "$out"

echo "$out"
