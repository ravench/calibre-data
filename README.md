# Calibre data

Dimensions of cartridges, one [TOML](https://toml.io) file per calibre, each value with its
sources. Made for drawing cartridges and matching photos, **not for reloading**.

It feeds the Schiesstagebuch and Kaliberfinder apps and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

## Files

- `calibres/`: one file per calibre, e.g. [`calibres/308-winchester.toml`](calibres/308-winchester.toml)
- [`docs/template.toml`](docs/template.toml): a calibre file with every field explained
- [`docs/format.md`](docs/format.md): the full reference: fields, sources, names, rules
- `order.toml`, `countries.toml`, `books.toml`, `lookalikes.toml`: list order, country codes,
  cited books, calibres that look alike
- `cartridges.py`: reads and checks everything (`import cartridges`; Python 3.11+)
- `outline.py`: side views as SVG paths
- `check.py`: checks every file

## Use

```python
import cartridges
cartridges.CATALOGUE              # calibres by category
cartridges.sources(".308 Winchester", "mm")
```

As a git submodule: `git submodule add https://github.com/ravench/calibre-data`.

## Contribute

Copy `docs/template.toml` or a similar calibre, cite a source for each value, then run

```sh
python3 check.py
python3 -m unittest discover -s tests
```

and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Data: [ODbL 1.0](LICENSE.md). Code and docs: MIT. © 2026 Simon Giotta and the contributors.
