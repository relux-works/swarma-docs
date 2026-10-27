#!/usr/bin/env bash
# Check the book's figures against src/MANIFEST.md before rendering.
#
#   bash book/check-figures.sh               both passes
#   bash book/check-figures.sh --structural  structural pass only (no Graphviz)
#   bash book/check-figures.sh --render      render pass only
#
# BOOK_ROOT=DIR checks another book that uses this kit (chapters in DIR/ru/,
# sources and manifest in DIR/src/, renders in DIR/diagrams/); by default the
# platform book in book/ is checked.
#
# Structural pass:
#  - every diagram a chapter references has a source in src/ and a manifest row
#    (a PNG needs src/<name>.puml, an SVG needs src/<name>.toml);
#  - every source in src/ has a manifest row;
#  - every upstream copy still has the SHA-256 recorded in the manifest;
#  - diagrams/ holds no render without a source, and every TOML source has
#    its SVG;
#  - every link to a figure carries the same box class (`{.tall}` or none),
#    and the manifest "Поле" column names that box.
# Render pass:
#  - every SVG equals a fresh diagram-kit render of its source, and its
#    smallest text stays legible in its book box: `{.tall}` links need
#    --require-fit tall, all other links --require-fit normal.
# The render pass needs the Graphviz version the diagram kit pins
# (GRAPHVIZ_PIN in render.py) and refuses up front on any other version.
set -euo pipefail
kit="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/diagram-kit/render.py"
here="$(cd "${BOOK_ROOT:-$(dirname "${BASH_SOURCE[0]}")}" && pwd)"
manifest="$here/src/MANIFEST.md"
structural=1
render=1
case "${1:-}" in
  "") ;;
  --structural) render=0 ;;
  --render) structural=0 ;;
  *) echo "usage: check-figures.sh [--structural | --render]" >&2; exit 2 ;;
esac
fail=0
row() { grep -E "^\| $1 \|" "$manifest" || true; }
col() { printf '%s\n' "$1" | awk -F'|' -v n="$2" '{gsub(/^ +| +$/,"",$n); print $n}'; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/check-figures.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# One line per chapter link: "<file> <box>", box is tall or normal.
grep -ohE '\.\./diagrams/[a-z0-9-]+\.(png|svg)\)(\{[^}]*\})?' "$here"/ru/*.md \
  | sed -E 's#^\.\./diagrams/##; s#\)\{[^}]*\.tall[^}]*\}$# tall#; s#\)(\{[^}]*\})?$# normal#' \
  | sort -u > "$tmp/links"

# The box a figure is held to: the class of its links, or the manifest column
# when no chapter links it.
box_of() {
  local stem="$1" boxes
  boxes="$(awk -v f="$stem.svg" '$1 == f {print $2}' "$tmp/links" | sort -u)"
  if [ -n "$boxes" ]; then
    printf '%s\n' "$boxes" | head -1
  elif [ "$(col "$(row "$stem")" 6)" = tall ]; then
    echo tall
  else
    echo normal
  fi
}

if [ "$structural" = 1 ]; then
  for ref in $(cut -d' ' -f1 "$tmp/links" | sort -u); do
    stem="${ref%.*}"
    case "$ref" in
      *.png) src="$stem.puml" ;;
      *.svg) src="$stem.toml" ;;
    esac
    [ -f "$here/src/$src" ] || { echo "missing source: src/$src (used by a chapter)"; fail=1; }
    r="$(row "$stem")"
    [ -n "$r" ] || { echo "missing manifest row: $stem"; fail=1; continue; }
    boxes="$(awk -v f="$ref" '$1 == f {print $2}' "$tmp/links")"
    if [ "$(printf '%s\n' "$boxes" | wc -l | tr -d ' ')" != 1 ]; then
      echo "linked both with and without {.tall}: $ref"; fail=1; continue
    fi
    case "$(col "$r" 6)" in
      tall) want=tall ;;
      обычное) want=normal ;;
      *) want="?" ;;
    esac
    [ "$want" = "$boxes" ] || { echo "manifest box differs from the link class: $stem (manifest $(col "$r" 6), link $boxes)"; fail=1; }
  done
  for src in "$here"/src/*.puml "$here"/src/*.toml; do
    [ -e "$src" ] || continue
    file="$(basename "$src")"
    stem="${file%.*}"
    r="$(row "$stem")"
    [ -n "$r" ] || { echo "source without manifest row: $stem"; fail=1; continue; }
    want="$(col "$r" 5)"
    if [ "$want" != "—" ]; then
      got="$(shasum -a 256 "$src" | cut -d' ' -f1)"
      [ "$got" = "$want" ] || { echo "upstream copy changed: $stem ($got != $want)"; fail=1; }
    fi
  done
  for out in "$here"/diagrams/*.png "$here"/diagrams/*.svg; do
    [ -e "$out" ] || continue
    file="$(basename "$out")"
    stem="${file%.*}"
    case "$file" in
      *.png) src="$stem.puml" ;;
      *.svg) src="$stem.toml" ;;
    esac
    [ -f "$here/src/$src" ] || { echo "render without source: diagrams/$file"; fail=1; }
  done
  for src in "$here"/src/*.toml; do
    [ -e "$src" ] || continue
    stem="$(basename "$src" .toml)"
    [ -f "$here/diagrams/$stem.svg" ] || { echo "source without render: src/$stem.toml"; fail=1; }
  done
fi

if [ "$render" = 1 ]; then
  pin="$(sed -nE 's/^GRAPHVIZ_PIN = "([^"]+)"$/\1/p' "$kit")"
  found="$(dot -V 2>&1 | sed -nE 's/.*version ([0-9.]+).*/\1/p' || true)"
  if [ -z "$pin" ] || [ "$found" != "$pin" ]; then
    echo "render pass needs Graphviz ${pin:-?} (the diagram kit pin), found ${found:-none}"
    exit 1
  fi
  for src in "$here"/src/*.toml; do
    [ -e "$src" ] || continue
    stem="$(basename "$src" .toml)"
    svg="$here/diagrams/$stem.svg"
    [ -f "$svg" ] || { echo "source without render: src/$stem.toml"; fail=1; continue; }
    fit="$(box_of "$stem")"
    if ! python3 "$kit" "$src" "$tmp/$stem.svg" --require-fit "$fit" >"$tmp/$stem.log" 2>&1; then
      echo "render refused or does not fit the $fit box: src/$stem.toml"
      sed 's/^/  /' "$tmp/$stem.log"
      fail=1
      continue
    fi
    cmp -s "$tmp/$stem.svg" "$svg" || { echo "stale render: diagrams/$stem.svg (render src/$stem.toml again)"; fail=1; }
  done
fi

if [ "$fail" = 0 ]; then
  if [ "$structural" = 1 ] && [ "$render" = 1 ]; then echo "figures: ok"
  elif [ "$structural" = 1 ]; then echo "figures: structural ok"
  else echo "figures: render ok"
  fi
fi
exit "$fail"
