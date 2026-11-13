# What a hash proves, and what it doesn't

A hash proves **identity of content**. For a commit, that content includes the exact ancestry. That is all it proves.

It does not prove **when** something happened or **who** did it. The author and committer names, emails and dates in a commit are plain text supplied by whoever created it, and Git records whatever it is given. Every name and date in this primer's demo repository was set by a script, and every hash in it is perfectly valid. A rewritten history is just as internally consistent as an original one. (`git log` may also display names rewritten by a `.mailmap` file; `git cat-file -p` shows what the commit itself says.)

Two things can anchor a commit to the outside world:

- **A signature.** Commits and tags can be signed with a GPG or SSH key. Commits created through GitHub's web interface, such as merge commits made with the merge button (but not "rebase and merge"), are typically signed by GitHub's own "web-flow" key, which shows that GitHub created that commit object.
- **An independent record of the hash.** If a full commit hash appears in an email, a produced document, a CI log or a public copy with a known date, then that commit and everything it depends on existed by then. A shortened hash is much weaker evidence (section 1).

A signature is computed over the commit's content, and that content includes the tree hash and the parent hashes. So a valid signature on one commit vouches for its whole snapshot and for **every commit reachable from it**. It vouches for their content, not for who wrote them or when.

{{diagram:signature_coverage}}

{{output:verify}}

Read that output carefully. "Good signature" means this key signed exactly this commit. The warning underneath is GPG saying it has no basis for connecting the key to a person. That link has to come from somewhere else, such as a key published on the person's account. The signature's own date also comes from the signer's clock.

One caution: verifying a signature runs external programs named in Git's configuration, and a repository's own `.git/config` can point `gpg.program` at anything, or name its own list of trusted SSH keys (`gpg.ssh.allowedSignersFile`). Inspect the configuration of an untrusted repository before running commands inside it (section 14).

::: why
Be precise about which claim you are making. "These files are identical to those" is a hash claim and is as strong as the hash function. "This was written on 4 March by Ada" is a metadata claim and needs corroboration from signatures or outside records.
:::
