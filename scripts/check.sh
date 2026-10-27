#!/bin/sh
# Hygiene check for the paper, the book and the a2a book (Russian sources).
#
#   sh scripts/check.sh
#
# Fails on: status markers outside the state chapter; internal identifiers
# (board elements, runs, review findings, decision numbers, arbiter rulings);
# local paths; names that never appear in the published text; delivery
# hedges in book chapters outside the state chapter and in the chain paper
# (paper/chain/*.tex); the prose blacklist of editorial/style.ru.md in book
# chapters, in the chain paper and in the signing note
# (editorial/notes/signing-auth/ru/*.md); the same blacklist, hedges and
# readiness wording in TeX form for the platform paper (paper/platform/*.tex),
# where \measured{...} exempts a measurement or availability fact from the
# readiness rule only.
# Prints every hit with its file and
# line. The a2a book (a2a-book/ru) follows the book's rules, with its own
# state chapter a2a-book/ru/09-gde-my.md as the only place for markers and
# delivery hedges. sources/ and editorial/ are working material and are not checked,
# except editorial/notes/*/ru/*.md: the signing note's blacklist is blocking,
# the other notes get an advisory blacklist pass.
#
#   STRICT_PROSE=0 sh scripts/check.sh   # report book blacklist hits, do not fail
#
# The checks are lexical. A dash is any em dash, and any en dash except in a
# numeric range whose left side is a digit (0–2, L0–L2, 09–21). A hedge is
# "пока", "ещё не" (also written "еще не"), "в v0" or "не реализован...";
# other wordings of the same meaning pass. The checker pins a UTF-8 locale
# whatever the caller's environment, and refuses to run without one.
set -u

# Bracket expressions and the case fold below work on characters only under a
# UTF-8 locale. Take the first one that matches a Cyrillic letter class and
# folds Cyrillic case; refuse when none does.
utf8=
for loc in C.UTF-8 en_US.UTF-8 C.utf8 en_US.utf8; do
  if printf 'Пока ё\n' | LC_ALL=$loc grep -qiE '^пока [ё]$' 2>/dev/null; then
    utf8=$loc
    break
  fi
done
[ -n "$utf8" ] || { echo "check.sh: no UTF-8 locale available (tried C.UTF-8, en_US.UTF-8); refusing" >&2; exit 2; }
LC_ALL=$utf8
export LC_ALL

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2

files=$(find book/ru a2a-book/ru paper -type f \( -name '*.md' -o -name '*.tex' \) 2>/dev/null | sort)
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
hit "arbiter ruling identifier" '\b(ac|tb)-R[0-9]+\b'
hit "review finding number" '(^|[^A-Za-z0-9-])F-[0-9]{2,3}([^0-9]|$)'
hit "decision number" '(^|[^A-Za-z0-9-])D-0[0-9]{2}([^0-9]|$)'
hit "local path" '/(Users|home)/[A-Za-z0-9._-]+'
hit "machine or seat name" '\b(ivmbp|rise1|macbook-iv|rose-air|astra-0[0-9]|orch-[a-z-]+)\b'
hit "retired name" '([Ss]lopcore|пасек|\bульев?\b|диких? пчёл|Seraph|\bKeymaker\b|\bSwarm (Runtime|Protocol|Chain|Keeper|Curator|Signer)\b)'

# Only the state chapter may carry markers, including split or unmatched ones.
marker_files=$(find book/ru a2a-book/ru paper -type f \( -name '*.md' -o -name '*.tex' \) ! -path 'book/ru/29-gde-my.md' ! -path 'a2a-book/ru/09-gde-my.md' 2>/dev/null | sort)
[ -z "$marker_files" ] || hit "status marker" '[⟦⟧]' "$marker_files"
hit "TeX status label" '\\status\{'

# Delivery hedges belong to the state chapter only (style.ru.md, "Голос"),
# in the book and in the a2a book alike.
# The chain paper (paper/chain/*.tex) is held to the same voice.
voice_files=$(find book/ru a2a-book/ru paper/chain -type f \( -name '*.md' -o -name '*.tex' \) ! -path 'book/ru/29-gde-my.md' ! -path 'a2a-book/ru/09-gde-my.md' 2>/dev/null | sort)
if [ -n "$voice_files" ]; then
  out=$(grep -niE -- '(^|[^[:alpha:]])(пока|[её]щ[её][[:space:]]+не|в[[:space:]]+v0|не[[:space:]]+реализован[[:alpha:]]*)($|[^[:alpha:]])' $voice_files 2>/dev/null)
  if [ -n "$out" ]; then
    echo '== delivery hedge'
    echo "$out"
    fail=1
  fi
fi

# Prose blacklist (editorial/style.ru.md, "Чёрный список"). Blocking for book
# chapters, the chain paper (paper/chain/*.tex) and the signing note in
# editorial/notes/signing-auth/ru/;
# STRICT_PROSE=0 turns those hits into reports. Other editorial notes in
# editorial/notes/*/ru/ stay advisory until their own pass lands.
prose_files=$( { find book/ru a2a-book/ru editorial/notes/signing-auth/ru -type f -name '*.md'; find paper/chain -type f -name '*.tex'; } 2>/dev/null | sort)
note_files=$(find editorial/notes -mindepth 3 -maxdepth 3 -type f -path 'editorial/notes/*/ru/*.md' ! -path 'editorial/notes/signing-auth/ru/*' 2>/dev/null | sort)
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
prose "dash in prose" '—|(^|[^0-9])–|–($|[^[:alnum:]])'
prose "guillemets" '[«»]'
prose "antithesis" '(не[[:space:]]+просто[[:space:]].*,[[:space:]]+а[[:space:]])|(это[[:space:]]+не[[:space:]].*,[[:space:]]+а[[:space:]])|(речь[[:space:]]+не[[:space:]]+о[[:space:]])'
prose "filler opener" '(стоит[[:space:]]+отметить|важно[[:space:]]+понимать|давайте[[:space:]]+разбер|в[[:space:]]+современном[[:space:]]+мире)'
prose "marketing adjective" '(^|[^[:alpha:]])(мощн[[:alpha:]]*|бесшовн[[:alpha:]]*)($|[^[:alpha:]])'

# The platform paper (paper/platform/*.tex) is written in the finished-platform
# voice and follows the same prose rules in TeX form: a dash is a Unicode dash
# as above, "---" anywhere, or "--" outside a range whose left side is a digit
# (2--18, П1--П8 and L0--L2 pass); guillemets are Unicode or babel "<<"/">>"
# or \guillemot...; delivery hedges are the book's; readiness wording is
# "работает сегодня", "не построен...", "в разработке", "в планах",
# "не настро..."/"не настраива...", "не опубликован..."/"не публику...",
# "не развёрнут...", "не готов...", "планируется"/"планируются"/"планируем",
# "запланирован...", "будет"/"будут", "в будущем", "прототип...", "предстоит"
# and "появится"/"появятся". A phrase that states a measurement condition or
# the availability of an artifact is wrapped in \measured{...} in the TeX
# source; the readiness rule ignores that argument (one brace level) and every
# other rule still scans it. The rule is lexical: other wordings of a
# readiness claim pass, and the final judgement stays with the reviewer.
# Every hit is printed with its file name, even for a single file.
# Blocking unless STRICT_PROSE=0. Other TeX under paper/ is not scanned here.
platform_files=$(find paper/platform -type f -name '*.tex' 2>/dev/null | sort)
platform() {
  # $1 label, $2 extended regex (case-insensitive)
  [ -n "$platform_files" ] || return 0
  out=$(grep -HniE -- "$2" $platform_files 2>/dev/null)
  if [ -n "$out" ]; then
    if [ "${STRICT_PROSE:-1}" = 0 ]; then echo "== platform paper: $1 (advisory)"; else echo "== platform paper: $1"; fail=1; fi
    printf '%s\n' "$out"
  fi
}
platform "dash in prose" '—|(^|[^0-9])–|–($|[^[:alnum:]])|---|(^|[^0-9])--|--($|[^[:alnum:]])'
platform "guillemets" '[«»]|<<|>>|\\guillemot'
platform "antithesis" '(не[[:space:]]+просто[[:space:]].*,[[:space:]]+а[[:space:]])|(это[[:space:]]+не[[:space:]].*,[[:space:]]+а[[:space:]])|(речь[[:space:]]+не[[:space:]]+о[[:space:]])'
platform "filler opener" '(стоит[[:space:]]+отметить|важно[[:space:]]+понимать|давайте[[:space:]]+разбер|в[[:space:]]+современном[[:space:]]+мире)'
platform "marketing adjective" '(^|[^[:alpha:]])(мощн[[:alpha:]]*|бесшовн[[:alpha:]]*)($|[^[:alpha:]])'
platform "delivery hedge" '(^|[^[:alpha:]])(пока|[её]щ[её][[:space:]]+не|в[[:space:]]+v0|не[[:space:]]+реализован[[:alpha:]]*)($|[^[:alpha:]])'
platform_readiness() {
  # $1 label, $2 extended regex (case-insensitive); \measured{...} arguments removed first
  [ -n "$platform_files" ] || return 0
  out=$(for f in $platform_files; do
    sed -E 's/\\measured\{[^{}]*\}//g' "$f" | grep -niE -- "$2" | sed "s|^|$f:|"
  done)
  if [ -n "$out" ]; then
    if [ "${STRICT_PROSE:-1}" = 0 ]; then echo "== platform paper: $1 (advisory)"; else echo "== platform paper: $1"; fail=1; fi
    printf '%s\n' "$out"
  fi
}
platform_readiness "readiness wording" '(^|[^[:alpha:]])(работает[[:space:]]+сегодня|не[[:space:]]+построен[[:alpha:]]*|в[[:space:]]+разработке|в[[:space:]]+планах|не[[:space:]]+настро[[:alpha:]]*|не[[:space:]]+настраива[[:alpha:]]*|не[[:space:]]+опубликован[[:alpha:]]*|не[[:space:]]+публику[[:alpha:]]*|не[[:space:]]+развёрнут[[:alpha:]]*|не[[:space:]]+готов[[:alpha:]]*|планиру(ется|ются|ем)|запланирован[[:alpha:]]*|буд(ет|ут)|в[[:space:]]+будущем|прототип[[:alpha:]]*|предстоит|появ(ится|ятся))($|[^[:alpha:]])'

# TeX ligature dashes and babel quote shorthands in the chain paper: the
# Unicode checks above do not see `---`, a spaced `--`, `\guillemot...`,
# `<<`/`>>` or `"<`/`">`. Numeric ranges (`136--163`) pass; TikZ path lines
# (`\draw`) are skipped because `--` is their path operator.
chain_tex=$(find paper/chain -type f -name '*.tex' 2>/dev/null | sort)
if [ -n "$chain_tex" ]; then
  out=$(grep -HnE -- '(---|[[:space:]]--[[:space:]]|\\guillemot|<<|>>|"<|">)' $chain_tex 2>/dev/null | grep -v '\\draw')
  if [ -n "$out" ]; then
    echo '== TeX dash or quote'
    echo "$out"
    fail=1
  fi
fi

# Every book chapter starts with one level-1 heading (after front matter in 00).
for f in book/ru/[0-9][0-9]*.md a2a-book/ru/[0-9][0-9]*.md; do
  [ -e "$f" ] || continue
  n=$(grep -cE '^# ' "$f")
  if [ "$n" -lt 1 ]; then
    echo "== chapter without a level-1 heading: $f"
    fail=1
  fi
done

[ "$fail" -eq 0 ] && echo "check.sh: ok ($(echo "$files" | wc -l | tr -d ' ') files)"
exit "$fail"
