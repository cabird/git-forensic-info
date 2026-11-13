# Case study: a production and an unofficial copy

This is an anonymized account of a real pattern.

A party produced a source repository for inspection in a secure review room. Separately, the attorneys received an unofficial copy of the source code through a channel other than the producing party. It was said to be authentic, and more complete than the production made on the record. If it matched the production, the analysis could be done on the unofficial copy with ordinary tools, outside the review room.

They did not obviously match. The production held only some of the top-level directories, and the unofficial copy held many more. No commit hash appeared in both. That is what section 6 predicts: the production had been rebuilt to contain only those directories, so every one of its commits was new.

So the analyst compared tree hashes instead: `git rev-parse HEAD:<directory>` for each produced directory in the review room, and the same command on the unofficial copy. Every one matched.

{{diagram:case_study}}

That established that the produced directories were byte-for-byte identical in both copies at that snapshot, so findings about those directories in the unofficial copy applied equally to the produced code. Some commits in the unofficial copy also carried valid GitHub web-flow signatures, which authenticated its history, up to those commits, as it had existed on GitHub.

The limits were stated just as carefully. The match covered one snapshot, not the history of those directories. And the signatures authenticated the unofficial copy, not the production.
