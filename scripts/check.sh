#!/bin/sh
# Hygiene check for the paper and the book (Russian sources).
#
#   sh scripts/check.sh
#
# Fails on: status markers outside the state chapter; internal identifiers
# (board elements, runs, review findings, decision numbers);
# local paths; names that never appear in the published text. Prints every
# hit with its file and line. sources/ and editorial/ are not checked: they
# are working material, not publication. Delivery hedges in book chapters
# outside the state chapter are advisory during the voice pilot. Matches
# require editorial review: temporal design conditions use the same words.
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

files=$(find book/ru paper -type f \( -name '*.md' -o -name '*.tex' \) 2>/dev/null | sort)
[ -n "$files" ] || { echo "check.sh: nothing to check"; exit 0; }

fail=0
hit() {
  # $1 label, $2 extended regex
  out=$(grep -nE -- "$2" ${3:-$files} 2>/dev/null)
  if [ -n "$out" ]; then
    echo "== $1"
    echo "$out"
    fail=1
  fi
}

hit "board, run or review identifier" '\b(TASK|STORY|EPIC|BUG|RUN|SES)-[0-9]{6}-[0-9a-z]{6}\b'
hit "review finding number" '(^|[^A-Za-z0-9-])F-[0-9]{2,3}([^0-9]|$)'
hit "decision number" '(^|[^A-Za-z0-9-])D-0[0-9]{2}([^0-9]|$)'
hit "local path" '/(Users|home)/[A-Za-z0-9._-]+'
hit "machine or seat name" '\b(ivmbp|rise1|macbook-iv|rose-air|astra-0[0-9]|orch-[a-z-]+)\b'
hit "retired name" '([Ss]lopcore|пасек|\bульев?\b|диких? пчёл)'

# Only the state chapter may carry markers, including split or unmatched ones.
marker_files=$(find book/ru paper -type f \( -name '*.md' -o -name '*.tex' \) ! -path 'book/ru/29-gde-my.md' 2>/dev/null | sort)
[ -z "$marker_files" ] || hit "status marker" '[⟦⟧]' "$marker_files"
hit "TeX status label" '\\status\{'

# Flag wording for the remaining editorial pass without widening this pilot.
voice_files=$(find book/ru -type f -name '*.md' ! -path 'book/ru/29-gde-my.md' 2>/dev/null | sort)
if [ -n "$voice_files" ]; then
  out=$(grep -niE -- '(^|[^[:alpha:]])(пока|ещё[[:space:]]+не|в[[:space:]]+v0|не[[:space:]]+реализован[[:alpha:]]*)($|[^[:alpha:]])' $voice_files 2>/dev/null)
  if [ -n "$out" ]; then
    echo '== delivery hedge (advisory; review design conditions separately)'
    echo "$out"
  fi
fi

# Every book chapter starts with one level-1 heading (after front matter in 00).
for f in book/ru/[0-9][0-9]*.md; do
  [ -e "$f" ] || continue
  n=$(grep -cE '^# ' "$f")
  if [ "$n" -lt 1 ]; then
    echo "== chapter without a level-1 heading: $f"
    fail=1
  fi
done

[ "$fail" -eq 0 ] && echo "check.sh: ok ($(echo "$files" | wc -l | tr -d ' ') files)"
exit "$fail"
