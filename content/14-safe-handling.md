# Safe handling of evidence repositories

A repository is not inert data. Its configuration can make ordinary Git commands run programs, and some everyday commands rewrite or delete what is stored.

::: box Before you run anything
- **Work on a copy.** Hash the original first, for example a checksum of an archive of the whole directory, for chain of custody.
- **Read `.git/config` and `.git/hooks/` in a text viewer.** Settings such as `core.fsmonitor`, `core.pager`, `core.sshCommand`, `gpg.program`, `diff.external` and aliases can make routine commands execute arbitrary programs.
- **Prefer read-only commands**: `cat-file`, `ls-tree`, `rev-parse`, `rev-list`, `log`, `diff`, `fsck`. Avoid `checkout`, `pull`, `gc`, `repack` and `prune` on evidence. `gc` can destroy unreachable objects.
- **Set `GIT_OPTIONAL_LOCKS=0`** so that commands like `status` do not write to the repository.
- **Record what you did**: the Git version (`git --version`), the exact commands, and their output.
:::
