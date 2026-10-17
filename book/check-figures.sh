#!/usr/bin/env bash
# Check the book's figures against src/MANIFEST.md before rendering:
#  - every diagram a chapter references has a source in src/ and a manifest row;
#  - every source in src/ has a manifest row;
#  - every upstream copy still has the SHA-256 recorded in the manifest;
#  - diagrams/ holds no render without a source.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
manifest="$here/src/MANIFEST.md"
fail=0
row() { grep -E "^\| $1 \|" "$manifest" || true; }

for stem in $(grep -ohE '\.\./diagrams/[a-z0-9-]+\.png' "$here"/ru/*.md | sed -E 's#.*/##; s#\.png$##' | sort -u); do
  [ -f "$here/src/$stem.puml" ] || { echo "missing source: src/$stem.puml (used by a chapter)"; fail=1; }
  [ -n "$(row "$stem")" ] || { echo "missing manifest row: $stem"; fail=1; }
done
for src in "$here"/src/*.puml; do
  stem="$(basename "$src" .puml)"
  r="$(row "$stem")"
  [ -n "$r" ] || { echo "source without manifest row: $stem"; fail=1; continue; }
  want="$(printf '%s\n' "$r" | awk -F'|' '{gsub(/ /,"",$5); print $5}')"
  if [ "$want" != "—" ]; then
    got="$(shasum -a 256 "$src" | cut -d' ' -f1)"
    [ "$got" = "$want" ] || { echo "upstream copy changed: $stem ($got != $want)"; fail=1; }
  fi
done
for png in "$here"/diagrams/*.png; do
  [ -e "$png" ] || continue
  stem="$(basename "$png" .png)"
  [ -f "$here/src/$stem.puml" ] || { echo "render without source: diagrams/$stem.png"; fail=1; }
done
[ "$fail" = 0 ] && echo "figures: ok"
exit "$fail"
