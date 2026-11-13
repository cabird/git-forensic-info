# Comparing two repositories

The usual task: one repository produced in a case, and a second copy from somewhere else, such as an earlier production, an open-source upstream or a copy obtained through another channel. Work from the cheapest check to the most detailed.

1. **Look for shared commit hashes.** Run `git rev-list --all` in each and compare the lists. One shared commit means that commit and all of its ancestors are identical in both.
2. **Compare tree hashes for the directories you care about.** `git rev-parse <commit>:<path>` prints the hash of the directory at that path in that commit.
3. **Descend only where hashes differ.** `git ls-tree <commit>:<path>` lists one level, and adding `-r` lists every file below it with its blob hash. With both histories fetched into one scratch repository, `git diff --stat <a> <b>` does the descent for you.

{{output:compare}}

The two `src` directories are identical. The complete snapshots differ only by the files the filter removed.

Keep one limit in mind. A matching tree hash verifies **that snapshot**. It says nothing about how the directory got there, and the two histories behind it may differ. To verify history, pair the commits and compare at each pair, as in section 6.

::: why
This is how you establish that material from an uncontrolled source is the same as what was produced, or show exactly where it is not, without reading either one line by line.
:::
