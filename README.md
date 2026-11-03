# Calibre data

The shared calibre catalogue for
[Schiesstagebuch](https://github.com/ravench/schiesstagebuch),
[Kaliberfinder](https://github.com/ravench/kaliberfinder) and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

- `cartridges.py`: every calibre with its approximate dimensions in mm (CIP/SAAMI, rounded),
  search aliases, printable alternative names and primer sizes, and the year each calibre was
  first introduced (`INTRODUCED`, with the page it was checked against; `INTRODUCED_UNKNOWN`
  lists the entries that aren't one cartridge and why; where sources disagree, the earliest
  probable year).
- `outline.py`: the side view of each calibre as SVG path data (`outline(spec)`), and
  `identical_groups()`, the calibres that look exactly the same from the side
  (today .308 Win / 7.62 NATO and .223 Rem / 5.56 NATO / GP 90).

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
