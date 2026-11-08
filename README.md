# Calibre data

The shared calibre catalogue for
[Schiesstagebuch](https://github.com/ravench/schiesstagebuch),
[Kaliberfinder](https://github.com/ravench/kaliberfinder) and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

- `cartridges.py`: every calibre with its approximate dimensions in mm (CIP/SAAMI, rounded),
  search aliases, printable alternative names and primer sizes (`PRIMER_SOURCES` names where each
  was checked; `PRIMER_UNVERIFIED` lists the ones not yet checked), and the year each calibre was
  first introduced (`INTRODUCED`, with the page it was checked against; `INTRODUCED_UNKNOWN`
  lists the entries that aren't one cartridge and why; where sources disagree, the earliest
  probable year), `OBSOLETE`, the calibres no longer in regular factory production, and `RARE`, the calibres you
  are unlikely to find, so a match is more likely a false positive (independent of `OBSOLETE`;
  `tags(name)` gives `[]`, `["obsolete"]`, `["rare"]` or both).
- `ORIGIN` maps each calibre to the state that introduced it, tilted to the main adopter, user or
  producer where only the developer sits elsewhere (the 7.65 mm Parabellum is Swiss), as a code in
  `COUNTRIES` (English name and flag emoji; historical states such as the Soviet Union and unions
  such as NATO have no emoji). No entry means
  the entry is not a single cartridge (balls, gauges, pellets, blanks) or the origin is still open:
  `ORIGIN_UNDECIDED` lists those with the candidate states. `origin(name)` gives
  `(code, name, flag)` or `None`; `origin_candidates(name)` gives the open candidates the same
  way, likelier first. `WORLDWIDE` is the separate set of calibres in common use worldwide, and
  `is_worldwide(name)` tests it (9x19 mm is both German and worldwide). Since 2026-11-07 there is
  no `WW` country code: a worldwide round carries its country, and the globe is a second marker.
- `BULLETS` gives the bullet each calibre was first sold with where it was not a full metal
  jacket: `LEAD`, `PAPER_PATCHED` (lead wrapped in paper below the nose), `SOFT_POINT`
  (jacket with a lead tip) or `POLYMER_TIP` (jacket with a plastic tip), with the page that says so (`BULLET_INFERRED`: hunting rounds
  without a source, soft point from their use). `CASES` lists cases that were not brass
  (`COPPER`, lacquered `STEEL`, `NICKEL`-plated steel, `PAPER`-covered foil on a brass head, `HYBRID` brass body on a steel head). `CURRENT_CASES` lists other case materials
  made today (brass .45-70, steel 9x19); the original stays the drawn one. `bullet(name)`,
  `case_material(name)` and `current_case_materials(name)` look them up.
- `SHOULDER_ANGLES` gives each bottleneck case its shoulder angle (degrees from the case axis,
  the American alpha/2) with the page it was read from: mostly the C.I.P. sheets, whose `L1`
  is then the calibre's `sh_at`. Cases without a source yet are drawn at
  `DEFAULT_SHOULDER_ANGLE` (32°); the tests list them, so a new calibre needs an angle or a
  conscious entry there.
- `CASE_HEADS` / `case_head(name)`: rim thickness, extractor-groove diameter and ramp (or belt front) of the rimless and belted cases from the C.I.P. sheets; the outline draws each head from them, other cases keep a generic head.
- `LOOKALIKES` lists the groups of calibres that are cartridges of their own but look alike
  (.223 Rem / 5.56 NATO / GP 90, rimmed and rimless twins such as 7x64 / 7x65 R, the .32 S&W Long
  and its Wadcutter), each with what tells them apart: `RIM`, `BORE`, `LENGTH` (the case
  length), `SEATING` (a wadcutter seated flush or nearly so) or `LOAD` (a hotter load or another chamber that a
  board or the service specifies). `lookalikes(name)` gives the others of a calibre's group, so an
  app can show the whole group from any one of them. Other names of the same cartridge are search
  aliases, not groups.
- `outline.py`: the side view of each calibre as SVG path data (`outline(spec)`), and
  `identical_groups()`, the calibres that look exactly the same from the side
  (today .308 Win / 7.62 NATO and .223 Rem / 5.56 NATO / GP 90). A crimped blank (`CRIMPED`,
  e.g. the .22 blank 6.8/11) has no bullet: its case narrows to the star crimp. A wadcutter seated
  flush (.32 S&W Long Wadcutter) shows no bullet either.
  `bulletMaterial` is `steel` (GP 1890 cap) or `lead`, `tip` is a soft point's lead tip (or a plastic tip, `tipMaterial` `polymer`) drawn over
  the bullet, `head` the brass head of a shot shell or paper case (`headMaterial` `steel`: the steel head of a hybrid case), `patch` the paper band, `caseMaterial` set when the case is not brass, `currentCaseMaterials` the other materials made today (not drawn).

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
