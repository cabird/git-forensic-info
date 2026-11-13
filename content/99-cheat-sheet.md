# Cheat sheet

### Core ideas

1. A blob is just bytes. Same bytes, same hash, anywhere.
2. Names and file modes live in trees, not in files.
3. Same tree hash: identical directory, all the way down.
4. Same commit hash: identical snapshot *and* identical history.
5. A valid signature fixes the content of its commit and every ancestor.
6. Hashes prove identity. They do not prove time or authorship.
7. Rewritten commits get new hashes. Untouched directories keep their tree hashes.
8. Git infers renames and copies. It does not record them.
9. Deleted rarely means gone, but it depends on how the copy was made.

### Reading the commands

Angle brackets mark a value you supply. Type the value, not the brackets.

| Notation | Meaning |
|---|---|
| `<commit>` | Any name for a commit: a full or shortened hash (`{{h:release}}`), a branch (`main`), a tag (`v1.0`), or `HEAD`, the commit checked out now |
| `<path>` | A file or directory, written from the top of the repository: `src` or `src/util.py`. `<commit>:<path>` names what was at that path in that commit |
| `^{tree}` | Typed exactly as shown, braces included. After a commit or tag it means "the root tree this points to", as in `v1.0^{tree}`. In Windows shells, put the whole name in double quotes |
| `<obj>`, `<blob>`, `<a>`, `<b>` | The hash of an object, or any other name for it. `<a>` and `<b>` can be two commits or two trees |

### Inspect objects

| Command | What it tells you |
|---|---|
| `git cat-file -t <obj>` (also `-s`, `-p`) | Type, size or content of any object |
| `git ls-tree <commit>:<path>` | A directory's entries: mode, type, hash, name. `-r` lists every file |
| `git rev-parse <commit>:<path>` | Hash of the file or directory at that path |
| `git rev-parse <commit>^{tree}` | Hash of the commit's root tree |
| `git hash-object --no-filters <file>` | Blob hash of a file's exact bytes |

### Walk history

| Command | What it tells you |
|---|---|
| `git rev-list --all` | Every reachable commit hash |
| `git rev-list --first-parent --reverse <branch>` | The main line, oldest first |
| `git rev-list --max-parents=0 --all` | Root commits (more than one is worth a look) |
| `git log --date=iso-strict --format='%H %ad %cd %an'` | Author date and committer date side by side |
| `git log --follow -- <file>` | One file's history through inferred renames |
| `git log --all -m --find-object=<blob>` | Commits that added or removed a blob (`-m` includes merges) |

### Compare

| Command | What it tells you |
|---|---|
| `git diff --stat <a> <b>` | Files that differ between two commits or trees |
| `git diff --name-status -M --find-copies-harder <a> <b>` | The same, with inferred renames and copies |
| `git diff --name-status --no-renames <a> <b>` | The same, with inference turned off |

### Signatures

| Command | What it tells you |
|---|---|
| `git log --show-signature` | Signature check for each commit in the log |
| `git verify-commit <commit>`, `git verify-tag <tag>` | Check one signature |

### Recovery

| Command | What it tells you |
|---|---|
| `git fsck --unreachable --no-reflogs` | Objects that no ref or the index reaches |
| `git reflog` | Where `HEAD` has pointed (local copies only) |
| `git for-each-ref` | Every ref, including ones outside branches and tags |
| `git count-objects -v` | Loose and packed object counts |
| `git bundle list-heads <file>` | The refs inside a bundle |

**First:** work on a copy, read `.git/config` and hooks, run `git fsck` and `git replace -l`, set `GIT_OPTIONAL_LOCKS=0`.
