# Checking a loose file against a repository

Someone hands you a single file and says it came from the codebase. Hash its exact bytes, then ask the repository where that blob appears:

{{output:loose}}

`--find-object` lists the commits that added or removed that blob at some path. Here those are the commit that introduced the fixed `util.py` and the commit that copied it into `tools`. It skips merge commits unless you add `-m`. Without `--no-filters`, `hash-object` may convert line endings first and hash the converted content (section 1).

The second file is the same code saved with Windows line endings. Each line has one extra byte, so it is a different blob and the search finds nothing. A miss therefore does not prove the content was never in the repository. Line endings (`core.autocrlf`), a trailing newline, the text encoding or an editor's reformatting are each enough to cause one. After a miss, normalize the file and try again, or fall back to comparing text.

::: why
An exact match on the raw bytes is conclusive and takes seconds. A non-match tells you only that the bytes differ. The reason still has to be found.
:::
