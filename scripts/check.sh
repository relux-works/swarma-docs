#!/bin/sh
# Hygiene check for the paper and the book (Russian sources).
#
#   sh scripts/check.sh
#
# Fails on: status markers outside the state chapter; internal identifiers
# (board elements, runs, review findings, decision numbers);
# local paths; names that never appear in the published text; delivery
# hedges in book chapters outside the state chapter; the prose blacklist of
# editorial/style.ru.md in book chapters. Prints every hit with its file and
# line. sources/ and editorial/ are working material and are not checked,
# except editorial/notes/*/ru/*.md, which gets an advisory blacklist pass.
#
#   STRICT_PROSE=0 sh scripts/check.sh   # report book blacklist hits, do not fail
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

# Delivery hedges belong to the state chapter only (style.ru.md, "Голос").
voice_files=$(find book/ru -type f -name '*.md' ! -path 'book/ru/29-gde-my.md' 2>/dev/null | sort)
if [ -n "$voice_files" ]; then
  out=$(grep -niE -- '(^|[^[:alpha:]])(пока|ещё[[:space:]]+не|в[[:space:]]+v0|не[[:space:]]+реализован[[:alpha:]]*)($|[^[:alpha:]])' $voice_files 2>/dev/null)
  if [ -n "$out" ]; then
    echo '== delivery hedge'
    echo "$out"
    fail=1
  fi
fi

# Prose blacklist (editorial/style.ru.md, "Чёрный список"). Blocking for book
# chapters; STRICT_PROSE=0 turns those hits into reports. Editorial notes in
# editorial/notes/*/ru/ are always advisory until their own pass lands.
prose_files=$(find book/ru -type f -name '*.md' 2>/dev/null | sort)
note_files=$(find editorial/notes -mindepth 3 -maxdepth 3 -type f -path 'editorial/notes/*/ru/*.md' 2>/dev/null | sort)
prose() {
  # $1 label, $2 extended regex (case-insensitive)
  if [ -n "$prose_files" ]; then
    out=$(grep -niE -- "$2" $prose_files 2>/dev/null)
    if [ -n "$out" ]; then
      if [ "${STRICT_PROSE:-1}" = 0 ]; then echo "== $1 (advisory)"; else echo "== $1"; fail=1; fi
      echo "$out"
    fi
  fi
  if [ -n "$note_files" ]; then
    out=$(grep -niE -- "$2" $note_files 2>/dev/null)
    if [ -n "$out" ]; then
      echo "== $1 in editorial notes (advisory)"
      echo "$out"
    fi
  fi
}
prose "dash in prose" '[[:space:]](—|–)[[:space:]]|[[:alpha:]](—|–)[[:alpha:]]'
prose "guillemets" '[«»]'
prose "antithesis" '(не[[:space:]]+просто[[:space:]].*,[[:space:]]+а[[:space:]])|(это[[:space:]]+не[[:space:]].*,[[:space:]]+а[[:space:]])|(речь[[:space:]]+не[[:space:]]+о[[:space:]])'
prose "filler opener" '(стоит[[:space:]]+отметить|важно[[:space:]]+понимать|давайте[[:space:]]+разбер|в[[:space:]]+современном[[:space:]]+мире)'
prose "marketing adjective" '(^|[^[:alpha:]])(мощн[[:alpha:]]*|бесшовн[[:alpha:]]*)($|[^[:alpha:]])'

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
