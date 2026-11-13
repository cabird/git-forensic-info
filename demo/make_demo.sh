#!/usr/bin/env bash
# Builds the demo repositories from scratch and captures the command output
# that the primer embeds. Everything that feeds a hash is pinned (names,
# emails, dates, signing key, signing time), so every hash is the same on
# every run. Results: demo/work/{original,filtered,fresh,compare,loose}
# (throwaway) and demo/output/*.txt + hashes.json (committed, read by build.py).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
OUT="$HERE/output"
rm -rf "$WORK" "$OUT"
mkdir -p "$WORK/home" "$OUT"

# --- isolate from the user's Git and GPG configuration -----------------------
export HOME="$WORK/home"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL="$WORK/gitconfig"
export TZ=UTC LC_ALL=C GIT_PAGER=cat PAGER=cat
git config --global init.defaultBranch main
git config --global core.abbrev 7
git config --global core.autocrlf false
git config --global advice.detachedHead false

ADA="Ada Example <ada@example.com>"
RAJ="Raj Sample <raj@example.com>"

# as WHO AUTHOR_DATE [COMMITTER_DATE] -- command...
as() {
  local who=$1 adate=$2 cdate=$2
  shift 2
  if [ "$1" != "--" ]; then cdate=$1; shift; fi
  shift
  local name=${who%% <*} email=${who##*<}
  email=${email%>}
  GIT_AUTHOR_NAME="$name" GIT_AUTHOR_EMAIL="$email" GIT_AUTHOR_DATE="$adate" \
  GIT_COMMITTER_NAME="$name" GIT_COMMITTER_EMAIL="$email" GIT_COMMITTER_DATE="$cdate" \
    "$@"
}

# --- signing: a throwaway key and a frozen clock keep the signature stable ---
SIGN=0
if command -v gpg >/dev/null 2>&1; then
  export GNUPGHOME="$(mktemp -d "${TMPDIR:-/tmp}/gfp-gnupg.XXXXXX")"   # short path: agent socket limit
  trap 'gpgconf --kill gpg-agent >/dev/null 2>&1 || true; rm -rf "$GNUPGHOME"' EXIT
  chmod 700 "$GNUPGHOME"
  if gpg --batch --quiet --import "$HERE/keys/ada-demo-signing-key.asc" 2>/dev/null; then
    SIGN=1
    export DEMO_SIGN_TIME=20240315T100000
    git config --global gpg.program "$HERE/gpg-fixed-clock.sh"
    git config --global user.signingkey D35B7073DE677DC3BA4DC7867E5FDA60395E9A41
  fi
fi
[ "$SIGN" = 1 ] || echo "warning: gpg unavailable; the release commit will be unsigned and its hash will differ" >&2

# --- the original repository ------------------------------------------------
ORIG="$WORK/original"
git init -q "$ORIG"
cd "$ORIG"
mkdir src docs

cat > README.md <<'EOF'
# Ledgerlite

A tiny demo project used in the Git forensics primer.
EOF
cat > src/main.py <<'EOF'
from util import total


def main():
    print(total([1.10, 2.20, 3.30]))


if __name__ == "__main__":
    main()
EOF
cat > src/util.py <<'EOF'
def total(amounts):
    return sum(amounts)
EOF
cat > docs/guide.md <<'EOF'
# Guide

Run `python3 src/main.py` to print the total.
EOF
git add -A
as "$ADA" 2024-03-04T09:00:00+00:00 -- git commit -q -m "Initial project"

cat > src/util.py <<'EOF'
def total(amounts):
    return round(sum(amounts), 2)
EOF
git add -A
as "$ADA" 2024-03-04T14:30:00+00:00 -- git commit -q -m "Fix rounding in util.py"

git mv docs/guide.md docs/handbook.md
as "$RAJ" 2024-03-05T11:15:00+05:30 -- git commit -q -m "Rename guide to handbook"

mkdir tools
printf '#!/bin/sh\npython3 src/main.py "$@"\n' > tools/run.sh
cp src/util.py tools/util.py
git add -A
as "$RAJ" 2024-03-06T16:05:00+05:30 -- git commit -q -m "Add tools directory"

chmod +x tools/run.sh
git add -A
as "$RAJ" 2024-03-06T16:20:00+05:30 -- git commit -q -m "Make run.sh executable"

# feature branch: authored on the 7th, committed on the 8th (as after a rebase)
git checkout -q -b feature
cat > src/main.py <<'EOF'
import sys

from util import total


def main():
    amounts = [1.10, 2.20, 3.30]
    if "--verbose" in sys.argv:
        print("adding", amounts)
    print(total(amounts))


if __name__ == "__main__":
    main()
EOF
git add -A
as "$ADA" 2024-03-07T10:20:00+00:00 2024-03-08T09:05:00+00:00 -- git commit -q -m "Add --verbose flag"

git checkout -q main
printf 'CURRENCY = "USD"\n' > src/config.py
printf '\nThe currency is set in `src/config.py`.\n' >> docs/handbook.md
git add -A
as "$RAJ" 2024-03-07T15:45:00+05:30 -- git commit -q -m "Add currency setting"

as "$ADA" 2024-03-08T09:30:00+00:00 -- git merge -q --no-ff -m "Merge branch 'feature'" feature

sed -i 's/^import sys$/import sys\n\nVERSION = "1.0"/' src/main.py
printf '\nCurrent version: 1.0\n' >> README.md
git add -A
if [ "$SIGN" = 1 ]; then
  as "$ADA" 2024-03-15T10:00:00+00:00 -- git commit -q -S -m "Release 1.0"
else
  as "$ADA" 2024-03-15T10:00:00+00:00 -- git commit -q -m "Release 1.0"
fi
as "$ADA" 2024-03-15T10:05:00+00:00 -- git tag -a -m "Version 1.0" v1.0

# a commit that is made and then thrown away: gone from the branch, not from the repo
printf 'db password: hunter2  (remove before committing!)\n' > src/debug_notes.txt
git add -A
as "$RAJ" 2024-03-15T17:30:00+05:30 -- git commit -q -m "WIP debug notes"
as "$RAJ" 2024-03-15T17:42:00+05:30 -- git reset -q --hard HEAD~1

# --- derived copies ----------------------------------------------------------
cd "$WORK"
# a real clone (not a file copy) carries only what the refs reach
git clone -q --no-local original fresh 2>/dev/null

# the "produced" repository: history rebuilt to contain only src/
git clone -q --no-local original filtered 2>/dev/null
if [ -z "${DEMO_NO_FILTER_REPO:-}" ] && git filter-repo --version >/dev/null 2>&1; then
  FILTER_TOOL="git filter-repo --path src/"
  (cd filtered && git filter-repo --quiet --path src/ >/dev/null 2>&1)
else
  FILTER_TOOL="git filter-branch (fallback)"
  (cd filtered && git branch -q feature origin/feature && git remote remove origin &&
    FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty --tag-name-filter cat \
      --index-filter 'git rm -r -q --cached --ignore-unmatch -- README.md docs tools' -- --all >/dev/null 2>&1 &&
    git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin)
fi

# a scratch repository holding both histories, for cross-repository diffs
git clone -q --no-local original compare 2>/dev/null
git -C compare fetch -q ../filtered 'refs/heads/*:refs/remotes/filtered/*'

# a loose file "handed over" outside any repository, plus a CRLF copy of it
mkdir loose
cp original/src/util.py loose/util.py
sed 's/$/\r/' loose/util.py > loose/util-crlf.py

# --- named hashes ------------------------------------------------------------
o() { git -C "$ORIG" rev-parse "$@"; }
f() { git -C "$WORK/filtered" rev-parse "$@"; }
bysubject() { git -C "$1" log --all --format='%H %s' | awk -v s="$2" '{h=$1; sub(/^[^ ]+ /,""); if ($0==s) print h}'; }

declare -A H
NAMES=(init fix rename tools chmod feature currency merge release)
SUBJECTS=("Initial project" "Fix rounding in util.py" "Rename guide to handbook" "Add tools directory"
          "Make run.sh executable" "Add --verbose flag" "Add currency setting" "Merge branch 'feature'" "Release 1.0")
for i in "${!NAMES[@]}"; do
  n=${NAMES[$i]}
  c=$(bysubject "$ORIG" "${SUBJECTS[$i]}")
  H[$n]=$c
  H[$n.tree]=$(o "$c^{tree}")
  for d in src docs tools; do
    if t=$(o -q --verify "$c:$d" 2>/dev/null); then H[$n.$d]=$t; fi
  done
  fc=$(bysubject "$WORK/filtered" "${SUBJECTS[$i]}")
  if [ -n "$fc" ]; then
    H[f.$n]=$fc
    H[f.$n.tree]=$(f "$fc^{tree}")
    H[f.$n.src]=$(f "$fc:src")
  fi
done
H[tag]=$(o v1.0)
H[f.tag]=$(f v1.0)
H[wip]=$(o 'HEAD@{1}')
H[wip.blob]=$(o 'HEAD@{1}:src/debug_notes.txt')
H[blob.readme]=$(o "${H[init]}:README.md")
H[blob.readme.release]=$(o "${H[release]}:README.md")
H[blob.guide]=$(o "${H[init]}:docs/guide.md")
H[blob.main]=$(o "${H[init]}:src/main.py")
H[blob.util.old]=$(o "${H[init]}:src/util.py")
H[blob.util]=$(o "${H[fix]}:src/util.py")
H[blob.run]=$(o "${H[tools]}:tools/run.sh")
H[blob.util.crlf]=$(git hash-object "$WORK/loose/util-crlf.py")

{
  echo "{"
  for k in $(printf '%s\n' "${!H[@]}" | sort); do printf '  "%s": "%s",\n' "$k" "${H[$k]}"; done | sed '$ s/,$//'
  echo "}"
} > "$OUT/hashes.json"

s() { echo "${H[$1]:0:7}"; }   # abbreviated hash, as shown in commands

# --- captured command output -------------------------------------------------
# cap NAME DIR  (commands on stdin, one per line): writes "$ command" + output
cap() {
  local name=$1 dir=$2 line
  : > "$OUT/$name.txt"
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    printf '$ %s\n' "$line" >> "$OUT/$name.txt"
    (cd "$dir" && eval "$line") >> "$OUT/$name.txt" 2>&1 < /dev/null || true
  done
}

cap blob "$ORIG" <<EOF
git cat-file -t $(s blob.util)
git cat-file -s $(s blob.util)
git cat-file -p $(s blob.util)
EOF

cap hash_object "$ORIG" <<EOF
git hash-object src/util.py
(printf 'blob %d\\0' "\$(wc -c < src/util.py)"; cat src/util.py) | sha1sum
EOF

cap tree "$ORIG" <<EOF
git cat-file -p $(s fix.tree)
EOF

cap commit "$ORIG" <<EOF
git cat-file -p $(s fix)
EOF

cap tag "$ORIG" <<EOF
git cat-file -p v1.0
EOF

cap names_modes "$ORIG" <<EOF
git ls-tree -r $(s tools)
git ls-tree $(s chmod) tools/
EOF

cap sharing "$ORIG" <<EOF
git rev-parse $(s init):docs $(s fix):docs
git rev-parse $(s init):src $(s fix):src
EOF

cap graph "$ORIG" <<EOF
git log --graph --oneline
EOF

cap verify "$ORIG" <<EOF
git verify-commit $(s release)
EOF

cap pairing "$WORK" <<EOF
../pair-commits.sh original filtered src
EOF

cap compare "$WORK" <<EOF
git -C original rev-parse v1.0:src
git -C filtered rev-parse v1.0:src
git -C compare diff --stat v1.0 filtered/main
EOF

cap loose "$ORIG" <<EOF
git hash-object ../loose/util.py
git log --all --oneline --find-object=$(s blob.util)
git hash-object ../loose/util-crlf.py
git log --all --oneline --find-object=${H[blob.util.crlf]}
EOF

cap renames "$ORIG" <<EOF
git diff --name-status $(s fix) $(s rename)
git diff --name-status --no-renames $(s fix) $(s rename)
git show --name-status --format= --find-copies-harder $(s tools)
EOF

cap dates "$ORIG" <<EOF
git log --date=iso-strict --format='%h  %ad  %cd  %an'
EOF

cap recover "$ORIG" <<EOF
git fsck --unreachable --no-reflogs
git reflog -2
git cat-file -p $(s wip.blob)
git -C ../fresh cat-file -t $(s wip.blob)
EOF

echo "demo rebuilt: $(ls "$OUT" | wc -l) files in demo/output (filtered with: $FILTER_TOOL)"
