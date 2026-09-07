"""
Rebuild Builder's Delight chisel groups as Chipped workbench groups.

Reads the mod jars in <instance>/mods, converts every Builder's Delight
"chisel" group into a Chipped interchange group, and writes one KubeJS
server script. Re-run it after a mod update; it overwrites its own output
file and nothing else.

Usage:
    py tools/gen_bd_chipped_groups.py                 # merge mode (default)
    py tools/gen_bd_chipped_groups.py separate        # keep vanilla with Chipped
    py tools/gen_bd_chipped_groups.py merge --out X   # write somewhere else
    py tools/gen_bd_chipped_groups.py --disable-iron-chisel   # also mute the old chisel
"""

import json
import sys
import zipfile
from pathlib import Path

INSTANCE = Path(__file__).resolve().parent.parent
MODS = INSTANCE / "mods"
DEFAULT_OUT = INSTANCE / "kubejs" / "server_scripts" / "bd_chipped_groups.js"

BD_JAR_GLOB = "BuildersDelight-*.jar"
CHIPPED_JAR_GLOB = "chipped-*.jar"

# Blocks to keep out of the Chipped groups. Each of these has its own crafting
# recipe in kubejs/server_scripts/builders_delight.js, and letting the chisel
# hand them out for free would make those recipes pointless.
#
# An excluded block is simply dropped: no Chipped group offers it, and the
# Iron Chisel is muted separately, so crafting becomes the only way to get one.
# Edit this list and re-run to change your mind.
EXCLUDE = {
    "buildersdelight:lantern_1",  # paper lantern
    "buildersdelight:lantern_3",  # copper lantern
    "buildersdelight:lantern_4",  # wooden lantern
    "buildersdelight:lantern_7",  # golden lantern
    "buildersdelight:chain_1",    # golden chain
    "buildersdelight:chain_2",    # rope chain
    "buildersdelight:chain_3",    # copper chain
}


def newest(glob):
    jars = sorted(MODS.glob(glob))
    if not jars:
        sys.exit("No jar matching %s in %s" % (glob, MODS))
    return jars[-1]


def norm(item_id):
    """A bare tag entry means the minecraft namespace."""
    return item_id if ":" in item_id else "minecraft:" + item_id


def read_bd_groups(jar_path):
    """Read data/<ns>/chisel/<name>.json out of the jar.

    Anything in EXCLUDE is dropped here, so it reaches no later step.

    Returns three values:
      groups   -> {group name: [item id, ...]}, excluded blocks already gone
      sources  -> {group name: namespace}, needed to override the file later.
                  Every group found is listed, even one left too small to use,
                  so muting the Iron Chisel still covers it.
      excluded -> the excluded ids that were actually found in the jar
    """
    groups, sources, excluded = {}, {}, set()
    with zipfile.ZipFile(jar_path) as jar:
        for name in jar.namelist():
            parts = name.split("/")
            if (len(parts) == 4 and parts[0] == "data"
                    and parts[2] == "chisel" and name.endswith(".json")):
                group = parts[3][:-len(".json")]
                sources[group] = parts[1]
                variants = json.loads(jar.read(name)).get("variants", [])
                variants = [norm(v) for v in variants]
                excluded.update(v for v in variants if v in EXCLUDE)
                variants = [v for v in variants if v not in EXCLUDE]
                if len(variants) > 1:
                    groups[group] = variants
    return groups, sources, excluded


def read_chipped_owners(jar_path):
    """{item id: chipped tag that already contains it}"""
    owner = {}
    prefix = "data/chipped/tags/item/"
    with zipfile.ZipFile(jar_path) as jar:
        for name in jar.namelist():
            if name.startswith(prefix) and name.endswith(".json"):
                tag = "chipped:" + name[len(prefix):-len(".json")]
                for value in json.loads(jar.read(name)).get("values", []):
                    if not value.startswith("#"):
                        owner.setdefault(norm(value), tag)
    return owner


def build_plan(groups, owner, mode):
    """Split the groups into additions to Chipped tags and brand new groups."""
    additions, new_groups = {}, {}
    for name in sorted(groups):
        variants = groups[name]
        free = [v for v in variants if v not in owner]
        host = next((owner[v] for v in variants if v in owner), None)
        if mode == "merge" and host and free:
            additions.setdefault(host, []).extend(free)
        elif len(free) > 1:
            new_groups["kubejs:bd_" + name] = free
    return additions, new_groups


def find_overlaps(groups):
    """Items listed in more than one group would make the bench pick one at random."""
    seen = {}
    for name, variants in groups.items():
        for v in variants:
            seen.setdefault(v, []).append(name)
    return {k: v for k, v in seen.items() if len(v) > 1}


def write_disable_overrides(sources):
    """Empty every Builder's Delight chisel group, so the Iron Chisel does nothing.

    The KubeJS data folder sits above mod data packs, and the mod reads one
    resource per path, so a file written here replaces the mod's own copy.
    An empty variants list gives the chisel nothing to convert.

    Delete the folders this writes to put the Iron Chisel back.
    """
    written = []
    for group in sorted(sources):
        target = (INSTANCE / "kubejs" / "data" / sources[group]
                  / "chisel" / (group + ".json"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{ "variants": [] }\n', encoding="utf-8")
        written.append(target)
    return written


def js_entries(mapping, indent="  "):
    lines = []
    for key in sorted(mapping):
        lines.append('%s"%s": [' % (indent, key))
        for item in mapping[key]:
            lines.append('%s  "%s",' % (indent, item))
        lines.append("%s]," % indent)
    return "\n".join(lines)


TEMPLATE = '''// GENERATED by tools/gen_bd_chipped_groups.py - do not hand-edit.
// Sources: %(bd_jar)s + %(chipped_jar)s
// Mode: %(mode)s. %(n_add)d groups merged into Chipped tags, %(n_new)d new groups.
// %(n_excluded)d block(s) excluded by hand in the generator, so no group offers them.

const CHIPPED_TAG_ADDITIONS = {
%(additions)s
};

const NEW_GROUPS = {
%(new_groups)s
};

ServerEvents.tags("item", (event) => {
  Object.keys(CHIPPED_TAG_ADDITIONS).forEach((tag) => {
    event.add(tag, CHIPPED_TAG_ADDITIONS[tag]);
  });
  Object.keys(NEW_GROUPS).forEach((tag) => {
    event.add(tag, NEW_GROUPS[tag]);
  });
});

ServerEvents.recipes((event) => {
  const ingredients = Object.keys(NEW_GROUPS).map((tag) => ({ tag: tag }));
  if (ingredients.length > 0) {
    event.custom({ type: "chipped:workbench", ingredients: ingredients });
  }
});
'''


def main():
    args = [a for a in sys.argv[1:]]
    mode = "merge"
    out = DEFAULT_OUT
    disable_chisel = False
    if "--disable-iron-chisel" in args:
        args.remove("--disable-iron-chisel")
        disable_chisel = True
    if args and args[0] in ("merge", "separate"):
        mode = args.pop(0)
    if args and args[0] == "--out":
        out = Path(args[1])

    bd_jar = newest(BD_JAR_GLOB)
    chipped_jar = newest(CHIPPED_JAR_GLOB)

    groups, sources, excluded = read_bd_groups(bd_jar)
    owner = read_chipped_owners(chipped_jar)
    additions, new_groups = build_plan(groups, owner, mode)

    print("Builder's Delight jar: %s" % bd_jar.name)
    print("Chipped jar:           %s" % chipped_jar.name)
    print("Chisel groups found:   %d (%d variant entries)"
          % (len(groups), sum(len(v) for v in groups.values())))
    print("Merged into Chipped:   %d tags, %d items added"
          % (len(additions), sum(len(v) for v in additions.values())))
    print("New Chipped groups:    %d tags, %d items"
          % (len(new_groups), sum(len(v) for v in new_groups.values())))
    print("Excluded, so dropped:  %d of %d listed" % (len(excluded), len(EXCLUDE)))

    missing = EXCLUDE - excluded
    if missing:
        print("\nWARNING: %d excluded id(s) are in no chisel group, so excluding"
              " them changes nothing. Check for a typo:" % len(missing))
        for item in sorted(missing):
            print("  %s" % item)

    overlaps = find_overlaps(groups)
    if overlaps:
        print("\nWARNING: %d item(s) appear in more than one group:" % len(overlaps))
        for item in sorted(overlaps):
            print("  %s -> %s" % (item, ", ".join(overlaps[item])))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE % {
        "bd_jar": bd_jar.name,
        "chipped_jar": chipped_jar.name,
        "mode": mode,
        "n_add": len(additions),
        "n_new": len(new_groups),
        "n_excluded": len(excluded),
        "additions": js_entries(additions),
        "new_groups": js_entries(new_groups),
    }, encoding="utf-8")
    print("\nWrote %s" % out)

    if disable_chisel:
        written = write_disable_overrides(sources)
        print("Emptied %d Iron Chisel group(s) under kubejs/data" % len(written))


if __name__ == "__main__":
    main()
