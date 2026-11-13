# Brief notes

**Submodules.** A tree entry with mode `160000` holds the hash of a commit in a *different* repository. The parent repository pins exactly which version was used, but the code itself is not there. You need the other repository too.

**Git LFS.** Large files handled by LFS are replaced in the repository by small text pointers. Each pointer holds a SHA-256 of the real content, which is stored outside Git's object database: on an LFS server, with a local cache under `.git/lfs`. The blob hash covers the pointer, so matching tree hashes prove matching pointers. Verify the real files against the SHA-256 inside each pointer.

**SHA-256 repositories.** Git can create repositories that use SHA-256 throughout. Hashes are 64 characters, and the same content has unrelated hashes in the two formats, so compare like with like. The ideas in this primer apply unchanged.
