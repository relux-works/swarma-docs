#!/usr/bin/env bash
# Build the Swarma Link book: Markdown chapters -> HTML (pandoc) -> PDF (WeasyPrint).
#
#   link-book/build.sh             builds link-book/swarma-link.ru.pdf from link-book/ru/
#   link-book/build.sh ru OUT      writes the PDF to OUT instead
#   link-book/build.sh --identify  prints how this build would be identified and builds nothing
#
# Reuses the Swarma book's template, stylesheet and Lua filter (book/), so the
# two books look the same. Needs pandoc 3.x and WeasyPrint 69+, and the PT
# Serif, PT Sans and PT Mono fonts.
#
# Figures live in link-book/src/<name>.toml and render to
# link-book/diagrams/<name>.svg with scripts/diagram-kit/render.py; they are
# rendered after review. Before the build:
#  - structural pass (always): every figure a chapter links has a TOML source,
#    every TOML source has its SVG, and diagrams/ holds no SVG without a source;
#  - render pass: every SVG equals a fresh render of its source and passes
#    --require-fit for its box ({.tall} links: tall, others: normal). It needs
#    the Graphviz the diagram kit pins. link_BOOK_SKIP_FIGURE_RENDER=1 skips
#    only this pass, with a warning.
# An image WeasyPrint cannot load also fails the build.
#
# The cover and the PDF metadata identify the build, so that two PDFs of one
# version can be told apart: the commit the PDF was built from, the date of
# that commit (UTC) and the release candidate. The release candidate is read
# from a tag books-<version>-rc<N> that points at the built commit, where
# <version> is the version in the date line of the title metadata; a tag
# books-<version> gives the final edition and no label. A commit without such
# a tag, and a tree whose sources differ from the commit, give a working
# build, and the cover says so. The PDF gets the date as its creation and
# modification date and the whole identification as its subject.
# Outside a git checkout set all three of LINK_BOOK_BUILD_ID (the commit),
# LINK_BOOK_BUILD_DATE (YYYY-MM-DDThh:mm:ssZ) and LINK_BOOK_RELEASE (rcN,
# final or work); a value that is set replaces what git says.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
book="$here/../book"
kit="$here/../scripts/diagram-kit/render.py"
identify=0
if [ "${1:-}" = "--identify" ]; then
  identify=1
  shift
fi
lang="${1:-ru}"
src="$here/$lang"
out="${2:-$here/swarma-link.$lang.pdf}"

# Build identification (see the header).
repo="$here/.."
build_id="${LINK_BOOK_BUILD_ID:-}"
build_date="${LINK_BOOK_BUILD_DATE:-}"
release="${LINK_BOOK_RELEASE:-}"
dirty=0
if [ -z "$build_id" ] || [ -z "$build_date" ] || [ -z "$release" ]; then
  if ! command -v git >/dev/null || ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "build.sh: not a git checkout: set LINK_BOOK_BUILD_ID, LINK_BOOK_BUILD_DATE and LINK_BOOK_RELEASE" >&2
    exit 1
  fi
  # The sources of the PDF: chapters, figures, both stylesheets, this script,
  # the shared template and filter, the diagram kit.
  if [ -n "$(git -C "$repo" status --porcelain -- link-book/ru link-book/src link-book/diagrams \
      link-book/style.css link-book/build.sh book/template.html book/style.css book/filters scripts/diagram-kit)" ]; then
    dirty=1
  fi
  [ -n "$build_id" ] || build_id="$(git -C "$repo" rev-parse HEAD)"
  if [ -z "$build_date" ]; then
    if (( dirty )); then
      build_date="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    else
      build_date="$(TZ=UTC git -C "$repo" log -1 --date=format-local:%Y-%m-%dT%H:%M:%SZ --format=%cd HEAD)"
    fi
  fi
  if [ -z "$release" ]; then
    release=work
    if (( ! dirty )); then
      # Only tags of the version on the cover count. A tag of the final
      # edition wins over a release candidate on the same commit; of several
      # release candidates the highest number is taken.
      version="$(sed -n 's/^date: .*версия \([0-9][0-9.]*\).*$/\1/p' "$src"/00-*.md | head -n 1)"
      if [ -z "$version" ]; then
        echo "build.sh: the date line of the title metadata names no version" >&2
        exit 1
      fi
      tags="$(git -C "$repo" tag --points-at HEAD --list "books-$version" "books-$version-rc*")"
      if grep -qxF -- "books-$version" <<<"$tags"; then
        release=final
      else
        rc="$(sed -n -E "s/^books-${version//./\\.}-rc([1-9][0-9]?)\$/\\1/p" <<<"$tags" | sort -n | tail -n 1)"
        [ -z "$rc" ] || release="rc$rc"
      fi
    fi
  fi
fi
if ! [[ "$build_id" =~ ^[0-9a-f]{12,64}$ ]]; then
  echo "build.sh: the build id must be 12 to 64 lowercase hexadecimal characters" >&2
  exit 1
fi
if ! [[ "$build_date" =~ ^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$ ]]; then
  echo "build.sh: the build date must be YYYY-MM-DDThh:mm:ssZ" >&2
  exit 1
fi
months=(января февраля марта апреля мая июня июля августа сентября октября ноября декабря)
human_date="$((10#${BASH_REMATCH[3]})) ${months[$((10#${BASH_REMATCH[2]} - 1))]} ${BASH_REMATCH[1]} года"
case "$release" in
  rc[1-9]|rc[1-9][0-9]) release_text="релиз-кандидат ${release#rc}" ;;
  final) release_text="" ;;
  work) release_text="рабочая сборка" ;;
  *) echo "build.sh: the release must be rcN, final or work" >&2; exit 1 ;;
esac
if (( dirty )); then
  build_text="Собрано $human_date из коммита ${build_id:0:12} с изменениями поверх него"
  build_meta="сборка $build_date из коммита $build_id с изменениями поверх него"
else
  build_text="Собрано из коммита ${build_id:0:12} от $human_date"
  build_meta="сборка из коммита $build_id от $build_date"
fi
build_meta_args=(--metadata build="$build_text" --metadata build-date="$build_date" --metadata build-meta="$build_meta")
[ -z "$release_text" ] || build_meta_args+=(--metadata release="$release_text")
if (( identify )); then
  printf 'release: %s\ncover: %s\nmetadata: %s\ndate: %s\n' "${release_text:-(final edition, no label)}" "$build_text" "$build_meta" "$build_date"
  exit 0
fi

for tool in pandoc weasyprint python3; do
  command -v "$tool" >/dev/null || { echo "build.sh: $tool not found" >&2; exit 1; }
done

shopt -s nullglob
chapters=("$src"/[0-9][0-9]-*.md)
if (( ${#chapters[@]} == 0 )); then
  echo "build.sh: no chapters in $src" >&2
  exit 1
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/swarma-link.XXXXXX")"
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

if [ "${link_BOOK_SKIP_FIGURE_RENDER:-}" = 1 ]; then
  echo "build.sh: WARNING: link_BOOK_SKIP_FIGURE_RENDER=1, figure freshness and fit are not checked" >&2
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
  "${build_meta_args[@]}" \
  --output "$tmp/note.html"

# Relative image paths in the chapters (../diagrams/…) resolve against the
# chapter directory. WeasyPrint only logs an image it cannot load; that fails
# the build here, and the PDF is moved to OUT only after a clean run.
weasyprint \
  --base-url "$src/" \
  --stylesheet "$book/style.css" \
  --stylesheet "$here/style.css" \
  "$tmp/note.html" "$tmp/book.pdf" 2> "$tmp/weasyprint.log" || { cat "$tmp/weasyprint.log" >&2; exit 1; }
cat "$tmp/weasyprint.log" >&2
if grep -q 'Failed to load image' "$tmp/weasyprint.log"; then
  echo "build.sh: an image failed to load; $out is left unchanged" >&2
  exit 1
fi
mv "$tmp/book.pdf" "$out"

echo "$out"
