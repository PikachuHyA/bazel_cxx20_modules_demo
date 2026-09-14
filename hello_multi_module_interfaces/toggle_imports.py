#!/usr/bin/env python3
"""Switch foo/bar imports; run bazel build //:foobar separately to reproduce."""

import argparse
from pathlib import Path
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "direction", nargs="?", default="toggle",
        choices=("toggle", "foo-to-bar", "bar-to-foo", "status"),
        help="foo-to-bar means foo imports bar (default: toggle)",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    paths = {name: root / (name + ".cppm") for name in ("foo", "bar")}
    texts = {name: path.read_bytes().decode("utf-8") for name, path in paths.items()}
    patterns = {
        "foo": re.compile(r"^[ \t]*(?:export[ \t]+)?import[ \t]+bar[ \t]*;[ \t]*(?://[^\r\n]*)?(?:\r?\n|$)", re.M),
        "bar": re.compile(r"^[ \t]*(?:export[ \t]+)?import[ \t]+foo[ \t]*;[ \t]*(?://[^\r\n]*)?(?:\r?\n|$)", re.M),
    }
    present = {name: bool(patterns[name].search(texts[name])) for name in paths}
    if args.direction == "status":
        if present["foo"] and present["bar"]:
            print("foo <-> bar (both import each other)")
        elif present["foo"]:
            print("foo -> bar (foo imports bar)")
        elif present["bar"]:
            print("bar -> foo (bar imports foo)")
        else:
            print("No foo/bar import relationship")
        return
    if args.direction == "toggle":
        if present["foo"] == present["bar"]:
            parser.error("Expected exactly one import direction; specify foo-to-bar or bar-to-foo explicitly")
        importer = "bar" if present["foo"] else "foo"
    else:
        importer = "foo" if args.direction == "foo-to-bar" else "bar"
    imported = "bar" if importer == "foo" else "foo"
    updated = dict(texts)
    updated[imported] = patterns[imported].sub("", texts[imported])
    if not present[importer]:
        declaration = re.compile(r"^[ \t]*export[ \t]+module[ \t]+" + importer + r"[ \t]*;[ \t]*(?://[^\r\n]*)?(?:\r?\n|$)", re.M)
        match = declaration.search(texts[importer])
        if match is None:
            parser.error("Cannot find export module " + importer + "; in " + str(paths[importer]))
        newline = "\r\n" if "\r\n" in texts[importer] else "\n"
        prefix = "" if match.group().endswith("\n") else newline
        updated[importer] = (texts[importer][:match.end()] + prefix + "import " + imported + ";" + newline + texts[importer][match.end():])
    # Remove the old edge first to avoid temporarily creating a cycle.
    for name in (imported, importer):
        if updated[name] != texts[name]:
            paths[name].write_bytes(updated[name].encode("utf-8"))
    print(importer + " -> " + imported + " (" + importer + " imports " + imported + ")")
    print("Next: bazel build //:foobar")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError) as exc:
        sys.exit(str(exc))
