#!/usr/bin/env bash
# Build the Swarma two-pager: Markdown -> HTML (pandoc) -> PDF (WeasyPrint),
# the same way book/build.sh builds the book.
#
#   twopager/build.sh          builds swarma-twopager.ru.pdf and swarma-twopager.en.pdf
#   twopager/build.sh ru       builds one language
#
# Needs pandoc 3.x, WeasyPrint 69+, pdfinfo (poppler) and the PT Serif, PT Sans
# and PT Mono fonts. Fails when a PDF is not exactly two pages.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
langs=("$@")
(( ${#langs[@]} )) || langs=(ru en)

for tool in pandoc weasyprint pdfinfo; do
  command -v "$tool" >/dev/null || { echo "build.sh: $tool not found" >&2; exit 1; }
done

tmp="$(mktemp -d "${TMPDIR:-/tmp}/swarma-twopager.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

for lang in "${langs[@]}"; do
  src="$here/swarma-twopager.$lang.md"
  out="$here/swarma-twopager.$lang.pdf"
  [ -f "$src" ] || { echo "build.sh: $src not found" >&2; exit 1; }

  pandoc "$src" \
    --from markdown \
    --to html5 \
    --standalone \
    --template "$here/template.html" \
    --syntax-highlighting=none \
    --metadata lang="$lang" \
    --output "$tmp/$lang.html"

  weasyprint \
    --base-url "$here/" \
    --stylesheet "$here/twopager.css" \
    "$tmp/$lang.html" "$tmp/$lang.pdf" 2> "$tmp/$lang.log" || { cat "$tmp/$lang.log" >&2; exit 1; }
  cat "$tmp/$lang.log" >&2

  pages="$(pdfinfo "$tmp/$lang.pdf" | awk '/^Pages:/ {print $2}')"
  if [ "$pages" != 2 ]; then
    echo "build.sh: $lang has ${pages:-no} pages, expected 2; $out is left unchanged" >&2
    exit 1
  fi
  mv "$tmp/$lang.pdf" "$out"
  echo "$out"
done
