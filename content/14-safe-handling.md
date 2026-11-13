# Safe handling of evidence repositories

A repository is not inert data. Its configuration can make ordinary Git commands run programs, and some everyday commands rewrite or delete what is stored.

::: box Before you run anything
- **Work on a copy.** Hash the original first, for example a checksum of an archive of the whole directory, for chain of custody.
- **Read `.git/config` and `.git/hooks/` in a text viewer.** Settings such as `core.fsmonitor`, `core.pager`, `core.hooksPath`, `core.sshCommand`, `gpg.program`, `diff.external`, `diff.*.textconv` and `filter.*` can make routine commands, even `log` and `diff`, execute arbitrary programs. Follow any `include.path` to the file it pulls in. A `promisor` remote marks a partial clone, where ordinary commands fetch missing objects from the network.
- **Check that nothing is substituted.** Run `git fsck`, and look for replace refs (`git replace -l`), `.git/info/grafts` and `.git/shallow`. Each can make Git show content or history that differs from what a hash names. Setting `GIT_NO_REPLACE_OBJECTS=1` turns replacement off.
- **Prefer read-only commands**: `cat-file`, `ls-tree`, `rev-parse`, `rev-list`, `log`, `diff`, `fsck`. Avoid `checkout`, `pull`, `gc`, `repack` and `prune` on evidence. `gc` can destroy unreachable objects, and commands that write (`commit`, `merge`, `fetch`, `rebase`) can start it automatically.
- **Set `GIT_OPTIONAL_LOCKS=0`** so that commands like `status` do not write to the repository.
- **Record what you did**: the Git version (`git --version`), the exact commands, and their output. Use a current Git release: older ones have had flaws that let a crafted repository run code.
:::
