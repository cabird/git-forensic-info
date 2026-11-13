"""The primer's figures. Each function takes the demo's named hashes and
returns (svg_markup, caption). Add a figure by writing a function here and
registering it in FIGURES; reference it from content with {{diagram:name}}.
"""
from .svg import Canvas, GREY, INK, MUTED, RED

GREEN = "#2c6e2f"

# The demo history, oldest first, and each commit's parents.
ORDER = ["init", "fix", "rename", "tools", "chmod", "feature", "currency", "merge", "release"]
PARENTS = {"fix": ["init"], "rename": ["fix"], "tools": ["rename"], "chmod": ["tools"],
           "feature": ["chmod"], "currency": ["chmod"], "merge": ["currency", "feature"],
           "release": ["merge"]}


def history(c, H, y0, prefix="", present=ORDER, up=True, state=None, colw=80, x0=44, lift=46):
    """Draw the demo's commit graph left to right, one column per commit.
    Commits missing from `present` leave a gap; arrows skip to the nearest kept ancestor."""
    boxes = {}
    for i, n in enumerate(ORDER):
        if n in present:
            cy = y0 + (-lift if up else lift) * (n == "feature")
            boxes[n] = c.node("commit", x0 + colw * i, cy, [(H[prefix + n][:7], "hash")], state=state, pad=7)
    for child in ORDER:
        if child not in boxes:
            continue
        for p in PARENTS.get(child, []):
            while p not in boxes:
                p = PARENTS[p][0]
            a, b = boxes[child], boxes[p]
            if a.cy == b.cy:
                c.arrow(a.left(), b.right())
            elif child == "feature":      # branch leaves its parent: run back, then drop onto it
                edge = b.top(20) if up else b.bottom(20)
                c.arrow(a.left(), (edge[0], a.cy), edge)
            else:                          # merge reaches back to the branch tip
                edge = a.top(-12) if up else a.bottom(-12)
                c.arrow(edge, (edge[0], b.cy), b.right())
    return boxes


def object_types(H):
    s = lambda k: H[k][:7]
    c = Canvas("object_types", "The four Git object types and how they point to one another: "
               "tag to commit, commit to tree, tree to blob.")
    cw, lx, rx = 340, 8, 388
    tag = c.card("tag", lx, 14, cw, "annotated tag", s("tag"), [
        f"object  {s('release')}…", "type    commit", "tag     v1.0",
        "tagger  Ada Example … 1710497100 +0000", "", "Version 1.0"],
        "A named pointer to one object, with a message.")
    commit = c.card("commit", rx, 14, cw, "commit", s("release"), [
        f"tree       {s('release.tree')}…", f"parent     {s('merge')}…",
        "author     Ada Example … 1710496800 +0000",
        "committer  Ada Example … 1710496800 +0000",
        "gpgsig     -----BEGIN PGP SIGNATURE …", "", "Release 1.0"],
        "A snapshot, its parents, and stated who and when.")
    y2 = commit.y + commit.h + 52
    tree = c.card("tree", rx, y2, cw, "tree", s("release.tree"), [
        f"100644 blob {s('blob.readme.release')}…  README.md",
        f"040000 tree {H['release.docs'][:7]}…  docs",
        f"040000 tree {s('release.src')}…  src",
        f"040000 tree {H['release.tools'][:7]}…  tools"],
        "One directory: a mode, hash and name per entry.")
    blob = c.card("blob", lx, y2, cw, "blob", s("blob.readme.release"), [
        "# Ledgerlite", "", "A tiny demo project used in the …", "", "Current version: 1.0"],
        "Only the bytes: no name, no mode, no date.")
    c.arrow((tag.x + tag.w, tag.line_y[0]), (commit.x, tag.line_y[0]), label="object")
    c.arrow(commit.bottom(), (tree.cx, tree.y), label="tree", ldx=8, ldy=4, lanchor="start")
    c.arrow((tree.x, tree.line_y[0]), (blob.x + blob.w, tree.line_y[0]), label="entry")
    return c.render(), ("One of each object type from the demo repository. Each object refers to the "
                        "next by its hash: the tag names a commit, the commit names its root tree, "
                        "and the tree names a blob for each file and a tree for each subdirectory.")


def snapshot_sharing(H):
    s = lambda k: H[k][:7]
    c = Canvas("snapshot_sharing", "Two commits whose snapshots share every object except the "
               "edited file and the trees above it.")
    L, M, R = 124, 368, 612
    c.region(M - 92, 158, 184, 312, fill="#f7f7f4")
    c.text(M, 177, "stored once, used by both", size=12, fill=MUTED)
    c1 = c.node("commit", L, 40, [("Initial project", "name"), (s("init"), "hash")])
    c2 = c.node("commit", R, 40, [("Fix rounding in util.py", "name"), (s("fix"), "hash")])
    r1 = c.node("tree", L, 128, [("root tree", "name"), (s("init.tree"), "hash")])
    r2 = c.node("tree", R, 128, [("root tree", "name"), (s("fix.tree"), "hash")], state="changed")
    readme = c.node("blob", M, 216, [("README.md", "name"), (s("blob.readme"), "hash")])
    docs = c.node("tree", M, 288, [("docs", "name"), (s("init.docs"), "hash")])
    guide = c.node("blob", M, 360, [("guide.md", "name"), (s("blob.guide"), "hash")])
    main = c.node("blob", M, 432, [("main.py", "name"), (s("blob.main"), "hash")])
    s1 = c.node("tree", L, 288, [("src", "name"), (s("init.src"), "hash")])
    s2 = c.node("tree", R, 288, [("src", "name"), (s("fix.src"), "hash")], state="changed")
    u1 = c.node("blob", L, 432, [("util.py", "name"), (s("blob.util.old"), "hash")])
    u2 = c.node("blob", R, 432, [("util.py", "name"), (s("blob.util"), "hash")], state="changed")
    c.arrow(c2.left(), c1.right(), label="parent")
    c.arrow(c1.bottom(), (r1.cx, r1.y), label="tree", ldx=8, ldy=4, lanchor="start")
    c.arrow(c2.bottom(), (r2.cx, r2.y), label="tree", ldx=8, ldy=4, lanchor="start")
    for root, src, util, side in ((r1, s1, u1, 1), (r2, s2, u2, -1)):
        near = (lambda b: b.left()) if side == 1 else (lambda b: b.right())
        c.arrow(root.bottom(), (src.cx, src.y))
        c.arrow(root.bottom(side * 22), near(readme))
        c.arrow(root.bottom(side * 11), near(docs))
        c.arrow(src.bottom(), util.top())
        c.arrow(src.bottom(side * 14), near(main))
    c.arrow(docs.bottom(), guide.top())
    c.legend(kinds=("commit", "tree", "blob"), states=("changed",))
    return c.render(), ("The first two commits of the demo. The second edits only <code>util.py</code>, "
                        "so it needs one new blob and new trees for <code>src</code> and the root. "
                        "Everything else is the same object in both snapshots.")


def merkle_ripple(H):
    s = lambda k: H[k][:7]
    c = Canvas("merkle_ripple", "Editing one file changes the hash of that blob and of every "
               "object above it, and nothing else.")
    then = lambda a, b: f"{s(a)} → {s(b)}"
    commit = c.node("commit", 368, 36, [("commit", "name"), (then("init", "fix"), "hash")], state="changed")
    root = c.node("tree", 368, 124, [("root tree", "name"), (then("init.tree", "fix.tree"), "hash")], state="changed")
    readme = c.node("blob", 130, 216, [("README.md", "name"), (s("blob.readme"), "hash")], state="same")
    docs = c.node("tree", 340, 216, [("docs", "name"), (s("init.docs"), "hash")], state="same")
    src = c.node("tree", 524, 216, [("src", "name"), (then("init.src", "fix.src"), "hash")], state="changed")
    guide = c.node("blob", 340, 308, [("guide.md", "name"), (s("blob.guide"), "hash")], state="same")
    main = c.node("blob", 440, 308, [("main.py", "name"), (s("blob.main"), "hash")], state="same")
    util = c.node("blob", 580, 308, [("util.py", "name"), (then("blob.util.old", "blob.util"), "hash")], state="changed")
    c.arrow(root.bottom(-30), readme.top(), color=GREY)
    c.arrow(root.bottom(), (docs.cx, docs.y), color=GREY)
    c.arrow(docs.bottom(), guide.top(), color=GREY)
    c.arrow(src.bottom(-30), main.top(), color=GREY)
    c.arrow(commit.bottom(), (root.cx, root.y), color=RED, width=2.2,
            label="lists the new root hash", ldx=10, ldy=4, lanchor="start")
    c.arrow(root.bottom(30), (src.cx, src.y), color=RED, width=2.2,
            label="lists the new src hash", ldx=12, ldy=0, lanchor="start")
    c.arrow(src.bottom(30), util.top(), color=RED, width=2.2,
            label="lists the new blob hash", ldx=12, ldy=0, lanchor="start")
    c.text(util.cx, util.y + util.h + 20, "the one edited file", size=12, fill=RED)
    c.legend(kinds=("commit", "tree", "blob"), states=("changed", "same"))
    return c.render(), ("The same edit, seen as hashes. Each object contains the hashes of the objects "
                        "below it, so a new blob hash forces a new <code>src</code> tree, a new root tree "
                        "and a new commit. Siblings off that path keep their hashes.")


def commit_dag(H):
    c = Canvas("commit_dag", "The demo history as a graph: every commit points back to its parents "
               "and down to its own root tree.")
    y0 = 150
    b = history(c, H, y0)
    for n, box in b.items():
        up = n == "feature"
        ty = box.cy + (-56 if up else 56)
        t = c.node("tree", box.cx, ty, [(H[n + ".tree"][:7], "hash")], pad=7)
        c.arrow(box.top() if up else box.bottom(), t.bottom() if up else (t.cx, t.y), color=GREEN)
    c.text(84, y0 - 22, "parent", size=12, fill=MUTED)
    c.text(52, y0 + 31, "tree", size=12, fill=GREEN, anchor="start")
    c.text(b["feature"].cx - 44, b["feature"].cy - 22, "branch", size=12, fill=MUTED, anchor="end")
    c.text(b["merge"].cx + 4, y0 - 30, "merge: two parents", size=12, fill=MUTED, anchor="start")
    c.legend(kinds=("commit", "tree"))
    return c.render(), ("The nine demo commits, oldest on the left. Arrows run from each commit to its "
                        "parent, so every hash depends on everything to its left. Each commit also "
                        "names one root tree: its full snapshot.")


def signature_coverage(H):
    c = Canvas("signature_coverage", "A signature on one commit covers that commit and every "
               "commit reachable from it, but nothing made later.")
    y0 = 118
    c.region(6, y0 - 104, 724, 132, fill="#eef6ea", stroke=GREEN)
    c.text(20, y0 - 82, f"vouched for by the signature on {H['release'][:7]}", size=13, fill=GREEN,
           anchor="start", bold=True)
    b = history(c, H, y0)
    rel = b["release"]
    c.label(rel.cx, rel.y - 20, "signed", fill=GREEN, bold=True)
    wip = c.node("commit", rel.cx, y0 + 66, [(H["wip"][:7], "hash")], state="ghost", pad=7)
    c.arrow(wip.top(), rel.bottom())
    c.text(wip.x - 10, wip.cy + 4, "a later, unsigned commit: not covered", size=12, fill=MUTED, anchor="end")
    c.legend(kinds=("commit",), extra=("arrows point from a commit to its parent",))
    return c.render(), ("The release commit is signed. What was signed includes the hash of its parent, "
                        "which fixes that commit, which names its own parent, and so on back to the "
                        "first commit. Altering anything in the shaded area would change the hash of "
                        "the signed commit and break the signature.")


def filtered_history(H):
    c = Canvas("filtered_history", "Filtering history to one directory gives every commit a new hash "
               "and drops some commits, but the kept directory's tree hashes are unchanged.")
    ytop, ymid, ybot = 104, 196, 288
    c.text(12, 20, "Original history: 9 commits", anchor="start", bold=True)
    top = history(c, H, ytop, up=True)
    touched = {"init": "all files", "fix": "src", "rename": "docs", "tools": "tools", "chmod": "tools",
               "feature": "src", "currency": "src, docs", "release": "src, README"}
    kept = [n for n in ORDER if "f." + n in H]
    bot = history(c, H, ybot, prefix="f.", present=kept, up=False, state="changed")
    for n in ORDER:
        if n in kept:
            t = c.node("tree", top[n].cx, ymid, [("src", "name"), (H[n + ".src"][:7], "hash")], pad=7)
            c.arrow(top[n].bottom(), (t.cx, t.y), color=GREEN)
            c.arrow(bot[n].top(), t.bottom(), color=GREEN)
            if n in touched:
                c.text(top[n].cx, top[n].y - 8, touched[n], size=12, fill=MUTED)
        else:
            x = top[n].cx
            c.arrow(top[n].bottom(), (x, ymid - 50), color=RED, dashed=True, head=False)
            c.text(x, ymid - 33, "✕", size=15, fill=RED, bold=True)
            c.text(x, ymid - 14, touched[n], size=12, fill=RED)
    mid = top["tools"].cx
    c.text(mid, ymid + 12, "dropped: these touched", size=12, fill=RED)
    c.text(mid, ymid + 28, "nothing under src", size=12, fill=RED)
    c.text(12, ybot + 82, "Filtered to src/: 6 commits, every commit hash new, same src trees",
           anchor="start", bold=True)
    c.legend(kinds=("commit", "tree"), states=("changed",), extra=("grey and red labels: paths each commit touched",))
    return c.render(), ("The demo history before and after <code>git filter-repo --path src/</code>. "
                        "Each surviving commit has a new hash, yet it and its original both contain the "
                        "very same <code>src</code> tree. Commits that touched nothing under "
                        "<code>src</code> have no counterpart.")


def case_study(H):
    c = Canvas("case_study", "A produced repository with some directories and an unofficial copy "
               "with many more: the commits differ, but the shared directories have equal tree hashes.")
    c.text(16, 22, "Produced in the review room", anchor="start", bold=True)
    c.text(720, 22, "Unofficial copy", anchor="end", bold=True)
    lc = c.node("commit", 110, 62, [("commit", "name"), ("1111111", "hash")])
    lr = c.node("tree", 110, 146, [("root tree", "name"), ("2222222", "hash")])
    rc = c.node("commit", 610, 62, [("commit", "name"), ("9999999", "hash")])
    rr = c.node("tree", 610, 146, [("root tree", "name"), ("8888888", "hash")])
    c.arrow(lc.bottom(), (lr.cx, lr.y))
    c.arrow(rc.bottom(), (rr.cx, rr.y))
    c.arrow(lc.right(), rc.left(), dashed=True, head=False, color=GREY, label="≠  commit hashes differ", ldy=-7)
    c.arrow(lr.right(), rr.left(), dashed=True, head=False, color=GREY, label="≠  root tree hashes differ", ldy=-7)
    c.region(532, 196, 194, 196, fill="#f7f7f4")
    c.text(629, 215, "dozens of other directories", size=12, fill=MUTED)
    others = ["billing", "web", "mobile", "infra", "tests"]
    for i, name in enumerate(others):
        c.node("tree", 584 + 92 * (i % 2), 250 + 50 * (i // 2), [(name, "name")], state="same", minw=76)
    c.text(676, 354, "… and more", size=12, fill=MUTED)
    c.arrow(rr.bottom(), (rr.cx, 196), color=GREY)
    dirs = [("engine", "aaaa111"), ("parser", "bbbb222"), ("runtime", "cccc333")]
    for i, (name, fake) in enumerate(dirs):
        y = 240 + 62 * i
        a = c.node("tree", 232, y, [(name, "name"), (fake, "hash")], minw=84)
        b = c.node("tree", 428, y, [(name, "name"), (fake, "hash")], minw=84)
        c.arrow((lr.cx, lr.y + lr.h), (lr.cx, y), a.left())
        c.arrow(rr.left(8), (500, rr.cy + 8), (500, y), b.right())
        c.equals(a.right(), b.left(), "same hash")
    c.legend(kinds=("commit", "tree"), extra=("grey: not in the production", "names and hashes are placeholders"))
    return c.render(), ("The case in one picture. Nothing matches at the commit or root level, because "
                        "the production was rebuilt to contain only some directories. The tree hashes of "
                        "those directories match exactly, so their contents are identical.")


FIGURES = {f.__name__: f for f in (object_types, snapshot_sharing, merkle_ripple, commit_dag,
                                   signature_coverage, filtered_history, case_study)}
