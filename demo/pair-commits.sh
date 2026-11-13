#!/usr/bin/env bash
# pair-commits.sh REPO_A REPO_B PATH
# Pairs the commits of two repositories by subject, author and author date,
# then prints each pair's commit hashes and the tree hash of PATH on each side.
# Read-only: it runs only rev-parse and log.
set -euo pipefail
A=$1 B=$2 P=$3
short() { git -C "$1" rev-parse --short=7 "$2" 2>/dev/null || echo "-"; }

a=$(basename "$A") b=$(basename "$B")
printf '%-25s %-9s %-9s  %-13s %-13s\n' "subject" "$a" "$b" "$a:$P" "$b:$P"
git -C "$A" log --reverse --topo-order --format='%H%x09%s%x09%ae%x09%aI' |
while IFS=$'\t' read -r hash subject email date; do
  other=$(git -C "$B" log --all --format='%H%x09%s%x09%ae%x09%aI' |
    awk -F'\t' -v s="$subject" -v e="$email" -v d="$date" '$2==s && $3==e && $4==d {print $1; exit}')
  ta=$(short "$A" "$hash:$P")
  if [ -n "$other" ]; then
    tb=$(short "$B" "$other:$P")
    mark=$([ "$ta" = "$tb" ] && echo "same" || echo "DIFFERENT")
    printf '%-25s %-9s %-9s  %-13s %-13s %s\n' "$subject" "${hash:0:7}" "${other:0:7}" "$ta" "$tb" "$mark"
  else
    printf '%-25s %-9s %-9s  %-13s %-13s\n' "$subject" "${hash:0:7}" "-" "$ta" "-"
  fi
done
