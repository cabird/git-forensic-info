# Rewritten history

A commit's hash covers its content, its parents and its metadata, so history can never be edited in place. The tools that appear to edit it (`commit --amend`, `rebase`, `cherry-pick`, squash merges, `filter-repo`, `filter-branch`) build new commits and move the branch to them. The result is a new, valid history with different hashes.

To show the effect, the demo repository was cloned and run through `git filter-repo --path src/`, which rebuilds history as if only the `src` directory had ever existed. A producing party might do the same to limit a production to the directories in scope.

{{diagram:filtered_history}}

The table below pairs the commits of the two repositories by subject line, author and author date, then prints the commit hashes and the `src` tree hash on each side:

{{output:pairing}}

Every surviving commit has a new hash. (Here even the first commit lost files. Any commits before the first change would have kept their hashes.) Three commits have no counterpart because they touched only `docs` or `tools`. The signature on the release commit is gone, because the commit it signed no longer exists in this history. But the `src` tree hash at each surviving commit is unchanged, because a tree hash depends only on what is under it.

Fingerprints of rewriting:

- the same messages, authors and dates under different commit hashes;
- identical trees under different commit hashes (only metadata, parents or a signature changed);
- commits in one copy with no counterpart in the other;
- signatures that are missing or fail where the other copy's verify;
- more than one root commit (`git rev-list --max-parents=0 --all`), though merged-in projects and shallow clones produce these too;
- committer dates bunched at one moment, which rebase, amend and cherry-pick cause (`filter-repo` keeps the original dates).

The pairing technique generalizes. Compare each pair at three levels: commit hash, then root tree hash, then subtree hashes. That tells you exactly what differs and where. When two copies share the start of a long history, you can binary-search `git rev-list --first-parent --reverse` for the first commit hash that differs, because once commit hashes diverge they never agree again.

::: why
Different commit hashes do not mean different code, and a rewritten history is not necessarily a sign of bad faith, though it may be. Determining bad faith requires being able to determine precisely what was kept, what was changed and what was dropped.
:::
