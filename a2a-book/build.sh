#!/usr/bin/env bash
# Build the a2a book with the platform book's kit (book/build.sh):
# Markdown chapters -> HTML (pandoc) -> PDF (WeasyPrint).
#
#   a2a-book/build.sh          builds a2a-book/a2a-book.ru.pdf from a2a-book/ru/
#   a2a-book/build.sh ru OUT   writes the PDF to OUT instead
#
# The kit checks the figures against a2a-book/src/MANIFEST.md and
# a2a-book/diagrams/ first, with the same rules and switches as the platform
# book (BOOK_SKIP_FIGURE_RENDER=1 skips only the render pass). a2a-book/style.css
# is applied after book/style.css and changes only the running header.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOK_ROOT="$here" BOOK_PDF_NAME=a2a-book exec bash "$here/../book/build.sh" "$@"
