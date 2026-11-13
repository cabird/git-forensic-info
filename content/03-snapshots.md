# Snapshots, not diffs

A commit does not store what changed. It points to one root tree, and that tree is a complete snapshot of every file in the project at that moment.

That sounds wasteful, but nothing is copied. A commit that changes one file gets a new blob for that file and new trees for the directories above it. Everything else is referred to by the same hashes as before. In the demo, the second commit edits only `src/util.py`:

{{output:sharing}}

`docs` has the same tree hash in both commits, so it is the same stored object. `src` has a new one.

{{diagram:snapshot_sharing}}

The diffs you see in `git log -p` or in a pull request are computed on demand by comparing two snapshots. They are a view of the record, not the record. (Packfiles do use deltas for compression, but every object still reads back whole.)

::: why
Any commit can be examined on its own as a complete copy of the code at that point. When someone describes "the changes in a commit", they are describing a comparison that Git computed. The snapshots on either side are the evidence.
:::
