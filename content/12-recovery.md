# Recovering deleted or unreachable material

Deleting a file in a commit removes it from later snapshots. Earlier commits still contain it. Even discarding a commit removes only the *reference* to it: the objects stay in the repository until garbage collection prunes them, usually weeks or months later.

In the demo, a commit containing a notes file was made and then immediately thrown away with `git reset --hard`:

{{output:recover}}

No branch contains that file, yet the blob is still there and readable. The reflog, a local diary of where each branch has pointed, also remembers the discarded commit. Other places to look are `git stash list`, `git notes`, and refs outside `refs/heads`, which `git for-each-ref` lists (a mirror of a GitHub repository can include `refs/pull/*`).

The last command shows the catch: a fresh clone of the same repository does not have the object. What survives depends on how the copy was made.

| How it was copied | What you get |
|---|---|
| Raw copy of the `.git` directory | Everything: unreachable objects, reflogs, stashes, config, hooks |
| `git clone` | Objects reachable from branches and tags; no reflogs or stashes. (A clone from a local path can carry unreachable objects too) |
| Shallow clone (`--depth`) | Recent commits only; earlier history is cut off |
| `git bundle` | Only the refs and range its creator chose |
| Export and re-import, or filtering | New hashes throughout (section 6) |

::: why
Ask how a repository was collected before drawing conclusions from what is absent. When you are the one requesting it, a forensic copy of the whole `.git` directory preserves far more than a clone does.
:::
