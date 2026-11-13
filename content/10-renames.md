# Renames, moves and copies

Git does not record renames, moves or copies. A commit holds a snapshot, and when you ask for a diff, Git guesses: if a file disappears from one path and the same or similar content appears at another, Git reports a rename.

{{output:renames}}

The same two snapshots read as "renamed" or as "deleted and added", depending on a flag. `R100` and `C100` mean Git scored the files as 100% similar. That score does not guarantee equal blobs (it ignores line order, for one), so confirm with `git rev-parse`. Below 100%, Git compares content against a similarity threshold (50% by default; `-M90%` raises it to 90%). Copies are found only if you ask, and only `--find-copies-harder` considers every file as a possible source. `git log --follow` uses the same guesswork to trace one file back through renames.

::: why
"This file was moved from there", "copied from there" and "rewritten from scratch" are inferences, not facts stored in the repository. Exact-hash matches are solid. For anything less, report the options and thresholds you used, because different settings can tell a different story.
:::
