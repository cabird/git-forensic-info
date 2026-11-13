# The four object types

Everything Git stores is one of four kinds of object. {{fig:object_types}} shows one of each from the demo repository.

{{diagram:object_types}}

A **blob** is the contents of a file and nothing else. It has no filename, no path, no permissions and no timestamp. `git cat-file` shows any object's type (`-t`), size (`-s`) and content (`-p`):

{{output:blob}}

A **tree** is a directory: a sorted list of entries, each holding a mode, a name, and the hash of a blob (a file) or of another tree (a subdirectory). Names and file modes live here. Git records whether a file is executable, not its full permissions or owner. The modes you will meet are `100644` (file), `100755` (executable file), `120000` (symlink), `040000` (subdirectory) and `160000` (submodule).

{{output:tree}}

Because a blob is only bytes, two files with the same content are one blob, however many places they appear. Renaming a file or making it executable creates no new blob either. Only the tree changes:

{{output:names_modes}}

`src/util.py` and `tools/util.py` are one blob listed twice. After `chmod +x`, `run.sh` keeps its blob hash and only its mode differs. (Details for anyone recomputing tree hashes by hand: ordinary Git commands do not record empty directories, entries are sorted as if directory names ended in `/`, and a directory's mode is stored as `40000`, without the leading zero.)

A **commit** is a short piece of text. It holds the hash of one root tree, the hashes of its parent commits (none for the first commit, usually two for a merge), an author line and a committer line, each with a Unix time and a timezone offset, an optional signature, and the message.

{{output:commit}}

An **annotated tag** is a named pointer to another object, usually a commit, with its own tagger, date, message and optional signature. Branches and lightweight tags are not objects at all. Each is just a name for one hash.

::: why
Know which object answers which question. "Is this the same file?" is a blob question. "Is this the same directory, with the same names and modes?" is a tree question. "Is this the same project state with the same history?" is a commit question.
:::
