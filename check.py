#!/usr/bin/env python3
"""Checks every calibre file before it is merged:

    python3 check.py

Lists each problem with its file and line (unknown or misspelt keys, values that are not allowed,
missing sources, broken TOML, names in order.toml or lookalikes/ that have no file, ...) and
exits with 1 when there is one. In GitHub Actions the problems also show on the pull request's files.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def problems(root=ROOT):
    """[(path, line or None, message)]: [] when every file under `root` is fine."""
    sys.path.insert(0, ROOT)
    try:
        import cartridges
    except Exception as e:  # importing cartridges reads this repository's own files first
        if getattr(e, "problems", None) is None or os.path.abspath(root) != ROOT:
            raise
        return e.problems
    try:
        cartridges.load(root)
    except cartridges.DataError as e:
        return e.problems
    return []


def main(root=ROOT):
    found = problems(root)
    github = os.environ.get("GITHUB_ACTIONS") == "true"
    for path, line, message in found:
        print(f"{path}{f':{line}' if line else ''}: {message}")
        if github:
            where = f"file={path}" + (f",line={line}" if line else "")
            print(f"::error {where},title=Calibre data::{message}")
    if found:
        print(f"\n{len(found)} problem{'s' if len(found) != 1 else ''} in the calibre files.")
        return 1
    import cartridges
    t = cartridges.load(root)
    names = [s["name"] for _, items in t["CATALOGUE"] for s in items]
    values = [(n, urls) for n in names for urls in t["MEASUREMENT_SOURCES"][n].values()]
    unsourced = [n for n, urls in values if not urls]
    print(f"All {len(names)} calibre files are fine; {len(unsourced)} of {len(values)} measurements "
          f"(in {len(set(unsourced))} calibres) still have no source.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT))
