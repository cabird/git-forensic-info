# The Merkle structure

Put the last two sections together. A tree's hash is computed from its entries, and each entry contains the hash of a child. So a tree's hash depends on everything underneath it. This arrangement is called a Merkle tree.

Change one byte in one file and its blob hash changes. That changes the entry in its directory's tree, so that tree's hash changes, and so on up to the root tree and the commit. Nothing else moves. Sibling files and directories keep their hashes.

{{diagram:merkle_ripple}}

The same thing happens along history. Each commit contains its parents' hashes, so a commit's hash depends on its entire ancestry. Merges have two parents, which makes history a graph and not a line (a Merkle DAG).

{{output:graph}}

{{diagram:commit_dag}}

Three consequences do most of the work in forensic analysis:

1. **Equal tree hashes mean identical directories**: every name, every mode and every byte, all the way down. There is nothing further to inspect.
2. **Equal commit hashes mean identical content and identical history**, back to the first commit.
3. **Any change changes every hash above it**: the trees up to the root, that commit, and every commit descended from it.

::: why
One 40-character comparison can stand in for comparing thousands of files. If two repositories agree on a tree hash, you can state that those directories are byte-for-byte identical without opening a file, and anyone can check the claim independently.
:::
