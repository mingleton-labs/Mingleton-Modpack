# tools

Helper scripts for this modpack. Run them from the instance folder, the one
that holds `mods` and `kubejs`:

```bash
cd "C:\Users\Big Nuts\curseforge\minecraft\Instances\Modpack"
py tools\<script name>
```

These scripts need Python 3. The pack was set up against Python 3.11.4, reached
through the Windows `py` launcher.

Do not add a `#!/usr/bin/env python3` line to a script here. The `py` launcher
reads that line, tries to run `python3`, and hits the Microsoft Store alias
instead of your real interpreter. The script then fails with "Python was not
found".

---

## gen_bd_chipped_groups.py

Lets Chipped's chisel and workbenches craft every Builder's Delight block that
the Iron Chisel can craft.

### Why it exists

Both mods store their block groups as data, in the same shape.

Builder's Delight reads `data/<namespace>/chisel/<name>.json` and takes one
field, `variants`. Each file is one group of interchangeable blocks.

Chipped reads recipes of type `chipped:workbench`, which hold a list of
ingredients. Each ingredient is one group of interchangeable blocks.

So one Builder's Delight `variants` array converts directly into one Chipped
ingredient. This script does that conversion for all 116 groups at once, so
nobody has to write them by hand.

### What it does

1. Finds the newest `BuildersDelight-*.jar` and `chipped-*.jar` in `mods`. It
   matches on the filename pattern, so a version bump needs no edit here.
2. Reads every Builder's Delight chisel group out of its jar, dropping anything
   named in `EXCLUDE`.
3. Reads every `data/chipped/tags/item/*.json` out of the Chipped jar, to learn
   which blocks Chipped already claims.
4. Writes `kubejs/server_scripts/bd_chipped_groups.js`.

The generated script adds item tags and one `chipped:workbench` recipe. It
copies the shape of Chipped's own `data/chipped/recipe/mason_table.json`.

### How to run it

```bash
py tools\gen_bd_chipped_groups.py merge
```

Then run `/reload` in game.

These arguments are accepted:

| Argument                 | Meaning                                              |
| ------------------------ | ---------------------------------------------------- |
| `merge`                  | Default. See the modes below.                        |
| `separate`               | The safer, plainer alternative. See the modes below. |
| `--out PATH`             | Write somewhere other than `kubejs/server_scripts`.  |
| `--disable-iron-chisel`  | Also mute the Iron Chisel. See below.                |

### The two modes

70 of the Builder's Delight groups contain a vanilla block, and Chipped already
puts many of those same vanilla blocks in its own groups. Chipped picks the
**first** recipe that matches the block you insert, so a block listed in two
places lands in one group or the other and you do not control which. The two
modes are two ways to avoid that.

**`merge`** adds the Builder's Delight blocks to the Chipped tag that already
holds the vanilla block. You get one combined group per material, and you can
chisel from a vanilla block straight to a Builder's Delight variant. On the
current jars this merges 29 groups and creates 87 new ones.

**`separate`** never touches Chipped's tags. Every Builder's Delight group
becomes its own group. Simpler to reason about, but you cannot cross between a
vanilla block and a Builder's Delight variant in one step. On the current jars
this creates 116 groups.

In both modes, a vanilla block that Chipped already claims is left with Chipped
rather than copied.

### Dropping blocks from the migration

Some Builder's Delight blocks are better earned by crafting than handed out by a
chisel. The paper, wooden, copper and golden lanterns and chains all have their
own recipes in `kubejs/server_scripts/builders_delight.js`, and a chisel that
converts a plain lantern into a golden one would make those recipes pointless.

The `EXCLUDE` set at the top of the script names the blocks to leave out:

```python
EXCLUDE = {
    "buildersdelight:lantern_1",  # paper lantern
    ...
}
```

An excluded block is dropped at the point the jar is read, so no Chipped group
offers it and nothing downstream ever sees it. Combined with a muted Iron
Chisel, crafting becomes the only way to get one.

Edit the set and re-run to change your mind. The script reports how many of the
listed ids it actually found, and warns about any that appear in no chisel group
at all, which usually means a typo in an id.

Blocks stay in their group when only some members are excluded. The lantern
group keeps its four remaining variants; only the four named ones go.

### Muting the Iron Chisel

`--disable-iron-chisel` writes `{ "variants": [] }` over all 116 group files, at
`kubejs/data/buildersdelight/chisel/`. The KubeJS data folder sits above mod data
packs, and Builder's Delight reads one file per path, so these replace the mod's
own copies rather than adding to them.

An empty list leaves the Iron Chisel with nothing to convert, so it stops working
even for chisels already in a player's inventory. Removing its crafting recipe
cannot do that on its own.

To put the Iron Chisel back, delete `kubejs/data/buildersdelight/chisel/` and
run `/reload`. Leaving the flag off on a later run does **not** undo it, because
the script only ever writes.

The rest of the removal lives in KubeJS scripts, not here:

| File                                        | What it does                      |
| ------------------------------------------- | --------------------------------- |
| `kubejs/server_scripts/builders_delight.js`  | Removes the crafting recipe       |
| `kubejs/startup_scripts/builders_delight.js` | Takes it out of the creative tabs |
| `kubejs/client_scripts/builders_delight.js`  | Hides it and its category in JEI  |

### Reading the output

The script prints a summary. A run in `merge` mode looks like this:

```
Builder's Delight jar: BuildersDelight-1.21.1-v.1.4.jar
Chipped jar:           chipped-neoforge-1.21.1-4.0.2.jar
Chisel groups found:   116 (946 variant entries)
Merged into Chipped:   29 tags, 217 items added
New Chipped groups:    87 tags, 700 items
Excluded, so dropped:  7 of 7 listed
```

It also warns if any block appears in more than one group, because that brings
the first-match problem back. The current jars produce no such warning.

### When to run it again

After any update to Builder's Delight or Chipped. The generated file is a
snapshot of what was in the jars at the time, so it goes stale when they change.

### What it does not do

It never deletes anything, and it never changes the mod jars. It writes its own
output file, and, with `--disable-iron-chisel`, the override files listed above.
Nothing else is touched.

Without that flag it leaves the Iron Chisel alone, and both chisels work on
these blocks.

### Do not hand-edit the output

`kubejs/server_scripts/bd_chipped_groups.js` is generated. Any change you make
there is lost on the next run. Change this script instead.
