# Timestamps in depth

Each commit carries two dates. The **author date** is when the change was first committed, according to the author's machine. The **committer date** is when this particular commit object was created. They start out equal and drift apart when a commit is rebased, cherry-picked or amended, because the author date is carried over and the committer date is reset.

{{output:dates}}

Commit `{{h:feature}}` was authored on the 7th and committed on the 8th, which is what an amend, rebase or cherry-pick leaves behind. The timezone offsets (`+00:00`, `+05:30`) come from each machine's settings. They are a weak hint about where someone was working, and trivially changed.

Signals that deserve a closer look, none conclusive alone:

- a committer date earlier than a parent's;
- many commits with identical or tightly bunched committer dates, which suggests a rebase or similar rewrite;
- author and committer dates far apart;
- offsets that do not fit the supposed author.

What actually constrains time comes from outside the commit: signatures made with a key whose publication or revocation is dated independently (dates inside a key are set by its owner), server-side records such as GitHub push events and pull-request timelines, CI logs, and any dated document that quotes a hash.

::: why
Treat commit dates as statements by the author. They are useful for building a timeline and open to challenge. Tie the points that matter to something the author did not control.
:::
