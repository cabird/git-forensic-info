# Git is a content-addressed database

Most of us picture Git as a chain of diffs. It isn't one. Underneath, Git is a key-value store: you give it some bytes, it stores them, and it hands back a key. The key is the hash of the bytes. Branches, history, diffs and renames are all built on top of that one idea.

Two things follow. The same content always gets the same key, on any machine, in any repository. And content cannot change without its key changing, so a key names exactly one piece of content.

The hash is SHA-1, written as 40 hex characters and usually shortened to the first seven or so. Git uses a hardened SHA-1 that detects the known collision attacks, and newer repositories can use SHA-256 instead (64 characters, same ideas).

{{output:hash_object}}

`git hash-object` works on any file, inside a repository or not. The second command shows there is no magic in it: a file's key is the SHA-1 of a short header (the word `blob`, the size in bytes, a zero byte) followed by the file's contents.

::: why
A Git hash is a fingerprint you can compute yourself from the material in front of you. You do not have to trust the repository, the tool, or whoever handed it over. If the bytes hash to the value, they are the bytes.
:::
