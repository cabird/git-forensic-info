# Recovering deleted or unreachable material

Deleting a file in a commit removes it from later snapshots. Earlier commits still contain it. Even discarding a commit removes only the *reference* to it: the objects stay in the repository until garbage collection prunes them. That is normally weeks or months later, but on an old copy the first `git gc`, which some everyday commands start automatically, can remove them at once.

In the demo, a commit containing a notes file was made and then immediately thrown away with `git reset --hard`:

{{output:recover}}

No branch contains that file, yet the blob is still there and readable. The reflog, a local diary of where each branch has pointed, also remembers the discarded commit. Other places to look are `git stash list`, `git notes`, and refs outside `refs/heads`, which `git for-each-ref` lists (a mirror of a GitHub repository can include `refs/pull/*`).

The last command shows the catch: a fresh clone of the same repository does not have the object. What survives depends on how the copy was made.

| How it was copied | What you get |
|---|---|
| Raw copy of the `.git` directory | Everything in the repository: unreachable objects, reflogs, stashes, config, hooks (but not uncommitted files, which sit outside `.git`) |
| `git clone` | Objects reachable from branches and tags; no reflogs, stashes or other refs. (A clone from a local path can carry unreachable objects too) |
| Shallow clone (`--depth`) | Recent commits only; earlier history is cut off |
| `git bundle` | Only the refs and range its creator chose |
| Export and re-import, or filtering | Rewritten commits get new hashes, and signatures are dropped (section 6) |

::: why
Ask how a repository was collected before drawing conclusions from what is absent. When you are the one requesting it, a forensic copy of the whole working directory, `.git` included, preserves far more than a clone does.
:::
