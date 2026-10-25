#!/usr/bin/env bash
# Check the book's figures against src/MANIFEST.md before rendering:
#  - every diagram a chapter references has a source in src/ and a manifest row
#    (a PNG needs src/<name>.puml, an SVG needs src/<name>.toml);
#  - every source in src/ has a manifest row;
#  - every upstream copy still has the SHA-256 recorded in the manifest;
#  - diagrams/ holds no render without a source;
#  - every SVG equals a fresh diagram-kit render of its source, and its
#    smallest text stays legible in its book box: `{.tall}` links need
#    --require-fit tall, all other links --require-fit normal.
# The freshness check of `graph` figures needs the Graphviz version the
# diagram kit pins; the kit refuses any other version and so does this check.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kit="$here/../scripts/diagram-kit/render.py"
manifest="$here/src/MANIFEST.md"
fail=0
row() { grep -E "^\| $1 \|" "$manifest" || true; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/check-figures.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

for ref in $(grep -ohE '\.\./diagrams/[a-z0-9-]+\.(png|svg)' "$here"/ru/*.md | sed -E 's#.*/##' | sort -u); do
  stem="${ref%.*}"
  case "$ref" in
    *.png) src="$stem.puml" ;;
    *.svg) src="$stem.toml" ;;
  esac
  [ -f "$here/src/$src" ] || { echo "missing source: src/$src (used by a chapter)"; fail=1; }
  [ -n "$(row "$stem")" ] || { echo "missing manifest row: $stem"; fail=1; }
done
for src in "$here"/src/*.puml "$here"/src/*.toml; do
  [ -e "$src" ] || continue
  file="$(basename "$src")"
  stem="${file%.*}"
  r="$(row "$stem")"
  [ -n "$r" ] || { echo "source without manifest row: $stem"; fail=1; continue; }
  want="$(printf '%s\n' "$r" | awk -F'|' '{gsub(/ /,"",$5); print $5}')"
  if [ "$want" != "—" ]; then
    got="$(shasum -a 256 "$src" | cut -d' ' -f1)"
    [ "$got" = "$want" ] || { echo "upstream copy changed: $stem ($got != $want)"; fail=1; }
  fi
done
for render in "$here"/diagrams/*.png "$here"/diagrams/*.svg; do
  [ -e "$render" ] || continue
  file="$(basename "$render")"
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
  svg="$here/diagrams/$stem.svg"
  [ -f "$svg" ] || { echo "source without render: src/$stem.toml"; fail=1; continue; }
  fit=normal
  if grep -qE "\.\./diagrams/$stem\.svg\)\{[^}]*\.tall" "$here"/ru/*.md; then fit=tall; fi
  if ! python3 "$kit" "$src" "$tmp/$stem.svg" --require-fit "$fit" >"$tmp/$stem.log" 2>&1; then
    echo "render refused or does not fit the $fit box: src/$stem.toml"
    sed 's/^/  /' "$tmp/$stem.log"
    fail=1
    continue
  fi
  cmp -s "$tmp/$stem.svg" "$svg" || { echo "stale render: diagrams/$stem.svg (render src/$stem.toml again)"; fail=1; }
done
[ "$fail" = 0 ] && echo "figures: ok"
exit "$fail"
