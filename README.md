# Calibre data

The shared calibre catalogue for
[Schiesstagebuch](https://github.com/ravench/schiesstagebuch),
[Kaliberfinder](https://github.com/ravench/kaliberfinder) and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

- `cartridges.py`: every calibre with its approximate dimensions in mm (CIP/SAAMI, rounded),
  search aliases, printable alternative names and primer sizes, and the year each calibre was
  first introduced (`INTRODUCED`, with the page it was checked against; `INTRODUCED_UNKNOWN`
  lists the entries that aren't one cartridge and why; where sources disagree, the earliest
  probable year), `OBSOLETE`, the calibres no longer in regular factory production, and `RARE`, the calibres you
  are unlikely to find, so a match is more likely a false positive (independent of `OBSOLETE`;
  `tags(name)` gives `[]`, `["obsolete"]`, `["rare"]` or both).
- `ORIGIN` maps the calibres clearly linked to one country (national service rounds, regional
  hunting rounds) to a code in `COUNTRIES` (English name and flag emoji; historical states such
  as the Soviet Union have no emoji). Calibres in common use worldwide get `WORLDWIDE` ("WW",
  🌐) instead; no entry means neither a clear country nor universal use. `origin(name)` looks it up.
- `BULLETS` gives the bullet each calibre was first sold with where it was not a full metal
  jacket: `LEAD`, `PAPER_PATCHED` (lead wrapped in paper below the nose), `SOFT_POINT`
  (jacket with a lead tip) or `POLYMER_TIP` (jacket with a plastic tip), with the page that says so (`BULLET_INFERRED`: hunting rounds
  without a source, soft point from their use). `CASES` lists cases that were not brass
  (`COPPER`, lacquered `STEEL`, `NICKEL`-plated steel, `PAPER`-covered foil, `HYBRID` brass body on a steel head). `CURRENT_CASES` lists other case materials
  made today (brass .45-70, steel 9x19); the original stays the drawn one. `bullet(name)`,
  `case_material(name)` and `current_case_materials(name)` look them up.
- `outline.py`: the side view of each calibre as SVG path data (`outline(spec)`), and
  `identical_groups()`, the calibres that look exactly the same from the side
  (today .308 Win / 7.62 NATO and .223 Rem / 5.56 NATO / GP 90). A crimped blank (`CRIMPED`,
  e.g. the .22 blank 6.8/11) has no bullet: its case narrows to the star crimp.
  `bulletMaterial` is `steel` (GP 1890 cap) or `lead`, `tip` is a soft point's lead tip (or a plastic tip, `tipMaterial` `polymer`) drawn over
  the bullet, `head` with `headMaterial` `steel` the steel head of a hybrid case, `patch` the paper band, `caseMaterial` set when the case is not brass, `currentCaseMaterials` the other materials made today (not drawn).

The values are for drawings and for matching photos, **not reloading data**.

## Using it

Each repository includes this one as a git submodule at `calibre-data/` and pins a commit:

```sh
git submodule update --init                 # after cloning
git -C calibre-data pull origin main        # move to the newest data
git add calibre-data && git commit -m "Update calibre data"
```

Then regenerate the app's JSON (or the poster) so it uses the new data. In GitHub Actions,
check out with `submodules: true`.

## Changing the data

Edit `cartridges.py` here, run the tests, open a pull request, then bump the submodule in the
apps and the poster.

```sh
python3 -m unittest discover -s tests
```

## Licence

[PolyForm Noncommercial 1.0.0](LICENSE.md), © 2026 Simon Giotta. Contributions need the
[Contributor License Agreement](CLA.md).
