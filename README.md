# Calibre data

The shared calibre catalogue for
[Schiesstagebuch](https://github.com/ravench/schiesstagebuch),
[Kaliberfinder](https://github.com/ravench/kaliberfinder) and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

The values are for drawings and for matching photos, **not reloading data**.

## The files

Every calibre is one [TOML](https://toml.io) file in `calibres/<category>/`, named after the calibre
(`.22 LR` is `calibres/Randfeuer/22-lr.toml`). The categories are the folders: `Randfeuer`,
`Kurzwaffe`, `Langwaffe`, `Schwarzpulver`, `Flinte` and `Luftdruck`.

- `order.toml`: the order the apps and the poster list the calibres in. A calibre that is not listed
  comes after the listed ones of its category, by name, so a new calibre needs no entry here.
- `countries.toml`: the country codes a calibre's `origin` can name, with English name and flag emoji.
- `lookalikes.toml`: groups of calibres that are cartridges of their own but look alike.
- `cartridges.py` reads and checks all of them and gives the apps' generators, `outline.py` and the
  poster the same tables as before (`CATALOGUE`, `INTRODUCED`, `PRIMERS`, `ORIGIN`, ...).
- `outline.py`: the side view of each calibre as SVG path data (`outline(spec)`), and
  `identical_groups()`, the calibres that look exactly the same from the side
  (today .308 Win / 7.62 NATO and .223 Rem / 5.56 NATO / GP 90). A crimped blank (e.g. the .22 blank
  6.8/11) has no bullet: its case narrows to the star crimp. A wadcutter seated flush (.32 S&W Long
  Wadcutter) shows no bullet either. `bulletMaterial` is `steel` (GP 1890 cap) or `lead`, `tip` is a
  soft point's lead tip (or a plastic tip, `tipMaterial` `polymer`) drawn over the bullet, `head` the
  brass head of a shot shell or paper case (`headMaterial` `steel`: the steel head of a hybrid case),
  `patch` the paper band, `caseMaterial` set when the case is not brass, `currentCaseMaterials` the
  other materials made today (not drawn).
- `check.py`: checks every file (see [Checking](#checking)).

## A calibre file

```toml
# Notes about the calibre: where values come from, what was measured, what to watch out for.
name = ".308 Winchester"
kind = "rimless"
profile = "spitzer"
aliases = ["308", "308win"]

origin = "US"
worldwide = true

[mm]
rim = 11.9
base = 11.9
shoulder = 11.5
shoulder_at = 39.62
neck = 8.7
case_length = 51.2
overall_length = 71.1
bullet = 7.82
sources = ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"]

[introduced]
year = 1952
sources = ["https://en.wikipedia.org/wiki/.308_Winchester"]

[primer]
size = "large-rifle"
sources = ["https://en.wikipedia.org/wiki/.308_Winchester"]

[shoulder_angle]
# C.I.P. 308 Win.
degrees = 20
sources = ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"]
```

Text goes in quotes, numbers and `true` don't. Lines starting with `#` are notes for people; the
apps ignore them.

### Sources

Every table has a `sources` list of web addresses (`https://…`), one or several:

```toml
sources = [
  "https://en.wikipedia.org/wiki/.22_Long_Rifle",
  "https://municion.org/producto/22-long-rifle/",
]
```

An empty list `sources = []` means the values have not been checked against a source yet. That is
allowed for the measurements, the primer (then it counts as unverified) and the bullet (then it is
inferred); a year, a shoulder angle, a case head, a case material, the case materials made today
and a projectile material always need one.
`sources(name, table)` in `cartridges.py` gives the whole list; the old tables (`INTRODUCED`,
`SHOULDER_ANGLES`, ...) keep the first one.

### Top of the file

| Key | | Meaning |
|---|---|---|
| `name` | required | The calibre's name as the apps show it. The file name follows from it. |
| `kind` | required | `rimless`, `rimmed`, `belted`, `rimfire`, `shot` (shot shell), `ball` (round ball or BB), `minie` (Minié bullet) or `pellet` (air gun pellet). |
| `profile` | required | Bullet nose: `spitzer`, `round`, `flat`, `patched` (paper-patched lead body under a steel cap, GP 1890) or `crimped` (no bullet, the mouth folded shut in a star: blanks and power-tool loads). |
| `aliases` | required | Search aliases, lower case as people type them (`[]` for none). Never the name of another calibre. |
| `display_aliases` | | One or two printable other names, shown in the apps' lists and search and on the poster. Calibres that are separate cartridges are never aliases of each other: .223 Rem / 5.56 NATO / GP 90 and .308 Win / 7.62 NATO differ in loading and are not necessarily interchangeable, so each has its own file. |
| `origin` | | Code from `countries.toml` of the state that introduced the calibre (see [Origin](#origin)). |
| `origin_candidates` | | Instead of `origin` while two or more states can claim it: their codes, likelier first. |
| `worldwide` | | `true` for a calibre in common use worldwide (independent of `origin`: 9x19 mm is German and worldwide). Includes the generic gauges and pellet sizes. |
| `obsolete` | | `true` when no longer in regular factory production (only surplus, boutique loads or reloading). The apps can hide these by default; the poster can mark them. |
| `rare` | | `true` when you are unlikely to find it (see [Rare](#rare)). |

### `[mm]`: measurements in millimetres

Most cartridges (C.I.P. letters of the maximum cartridge in brackets):

| Key | Meaning |
|---|---|
| `rim` | Rim diameter (R1); the belt for belted cases where it is wider. |
| `base` | Body diameter just above the head (P1). |
| `shoulder` | Bottleneck cases only: diameter where the shoulder starts (P2). |
| `shoulder_at` | Bottleneck cases only: distance from the head to where the shoulder starts (L1). |
| `neck` | Neck diameter at the mouth (H2). |
| `case_length` | Case length (L3). |
| `overall_length` | Cartridge length (L6). |
| `bullet` | Bullet diameter (G1). |

The neck length is not stored: the drawing runs the shoulder in from `shoulder_at` at the shoulder
angle until it reaches the neck diameter, and the rest up to `case_length` is the neck (at least
1.2 mm). The body taper follows from `base`, `shoulder` and `shoulder_at`.

Short forms:

| Calibre | Keys |
|---|---|
| `kind = "ball"` | `diameter` |
| `kind = "minie"` or `"pellet"` | `diameter`, `length` |
| `kind = "shot"` | `diameter`, `rim`, `length` (the case) |
| `profile = "crimped"` | `rim`, `base`, `mouth` (at the star crimp), `length` |

### `[introduced]`

`year` with `sources`: the year the calibre was first introduced, released as factory ammunition or
adopted for service (for a wildcat, the year it became a factory round; for a military round, the
year of adoption). Where sources disagree or give only a period, the earliest probable year is used.
Without a year, `unknown` says why (shot shells, loose balls and pellets are not one cartridge with
one launch); `sources` can then list the pages that were checked.

### `[primer]`

Every centrefire calibre has one, rimfire calibres, balls, Minié bullets and pellets none. `size` is
the primer of the original factory ammunition, which is today's Boxer size for calibres still loaded:
`small-pistol`, `large-pistol`, `small-rifle`, `large-rifle`, `shotshell-209`, `bmg-35` or
`berdan-nitro` (the large .254" Berdan "Nitro" primer, Kynoch #40, today RWS 6507, of old British
Nitro Expresses and some old European rounds, measured on headstamp photos). Other Berdan primers
(4.5 and 5.5 mm, e.g. 7.62x39, 7.62x54R surplus) are within 0.2 mm of a Boxer size and keep that size.

Sources: Wikipedia pages are the cartridge infobox ("Primer type"); Hodgdon, Vihtavuori and Sierra
are the primers used in their published reloading data; Starline is the primer named on its brass
page. Shot shells: Hodgdon's shotshell data uses 209-size primers for every gauge and length listed.
municion.org: the primer diameter measured on its headstamp photos (median over the specimens,
scaled by the rim diameter; checked on 9 mm, .38 Special and .308 to within 2 %). It gives the
original primer: about 6.1-6.7 mm is the .254" Berdan Nitro primer, under 4.5 mm a small one.
Readings between two sizes (4.8-5.0 mm, about 6.0 mm) stay unverified (`sources = []`), like the
rounds with no reloading data, brass maker page or clear headstamp photo yet (old military rounds,
Nitro Expresses, European hunting rounds). Hodgdon loads .30 Super Carry with small rifle primers;
Federal's ammunition uses small pistol, so it stays small pistol until checked.

### `[shoulder_angle]`

Bottleneck cases: `degrees` between the shoulder and the case axis (the American convention,
alpha/2). C.I.P. sheets print the full cone angle alpha, so their value is halved; for those
calibres `shoulder_at` is the sheet's L1. A bottleneck case without one is drawn at 32° until a
source is found (`SHOULDER_UNSOURCED` in `tests/test_outline.py` lists them).

### `[case_head]`

Rimless and belted cases, from the C.I.P. sheets (maximum cartridge): `rim_thickness` (R),
`ramp_top` (E: head to the top of the extractor-groove ramp; belted: head to the front of the belt),
`groove_diameter` (E1) and `ramp_angle` (delta: the groove's front ramp to the case axis, degrees).
A case made from a parent case without its own sheet keeps the parent's head (the note says which).
Cases without one are drawn with a generic head.

### `[bullet]`, `[case]`, `[current_cases]`, `[projectile]`

- `[bullet]` `type`: the bullet the cartridge was first sold with where it was not a full metal
  jacket (or another all-copper bullet): `lead` (bare lead, also lubricated or wax coated), `paper`
  (lead wrapped in paper below the nose), `softpoint` (copper jacket with the lead core showing at
  the tip) or `polymer` (copper jacket with a plastic tip: V-Max, ELD, FTX, SST, AccuBond). The GP
  1890 steel cap is its own profile (`patched`). `sources = []`: hunting rounds whose sources give
  no bullet, soft point from their use, not checked.
- `[case]` `material`: the original case where it was not brass: `copper`, lacquered `steel`,
  `nickel`-plated steel, `paper` (brass foil covered in paper on a brass head, Boxer's Snider case)
  or `hybrid` (brass body on a steel head).
- `[current_cases]` `materials`: other case materials made today (brass .45-70, steel 9x19); the
  original stays the drawn one.
- `[projectile]` `material`: balls, Minié bullets and pellets not made of lead: `steel` or `plastic`
  (steel BBs and airsoft BBs).

### Origin

The state that introduced the calibre, for every calibre whose origin the sources agree on. A round
keeps its country when it spread worldwide (9x19 mm stays German, 7.62x39 mm Soviet); `worldwide`
marks the calibres in common use worldwide, so apps can show the flag, a globe or both. No origin
means the entry is not a single cartridge (balls, gauges, pellets) or the origin is still open
(`origin_candidates`). Blanks have no country: they are trade sizes made everywhere.

Historical states keep their own code (ISO 3166-3 SU/CS where one exists, else a made-up AH/RUE
that no ISO code uses, so RU stays today's Russia); they have no flag emoji, so apps draw their own.
The German Empire, Weimar Republic, Nazi Germany and West Germany are all DE, the Kingdom of Italy IT
and the Empire of Japan JP: the same state continues under today's flag. Unions of states get a code
too (NATO for the rounds NATO standardised; EU when needed).

Where only the developer sits in another state than the main adopters, users and producers, the
origin follows the latter: the 7.65 mm Parabellum is Swiss, the 9x23 mm Largo Spanish, the 9x21 mm
Italian. The two-state cases were decided in the thread "Verify country per cartridge"
(2026-11-07/08); in their notes the other claim stands after the colon. Military adoption is noted
for the service rounds; .25 ACP, .22 TCM, the Norma rounds, .500/416 and .500 Jeffery, 9.5x57,
9.3x57, .376 Steyr, 9x21 and .32 S&W Long WC were never issued by a military, and the .45 GAP (US
state police 2007-13) and .357 SIG (US federal and state police) only by police. `[introduced]`
keeps the round's own first year (the Largo's 1903 design), whichever state the origin names.

### Rare

Calibres you are unlikely to find, so a photo or measurement that matches one is far more likely a
false positive than the real thing. Independent of `obsolete`: most rare calibres are obsolete
collector rounds, but some are still made in small numbers (big Nitro and African rounds,
short-lived magnums, niche handgun rounds). Checked on 2026-11-04 against the share of each site's
listings a calibre has (waffenbörse.ch, swisswaffen.com, GunBroker, TownPost, Frankonia,
usedguns.com.au, zbrane.cz and others), so a big site counts for more than a small one: a calibre
with at least 0.5 per mille and at least 3 listings on any site is not rare, unless it is obsolete
(the guns outlive the ammunition). Under 0.05 per mille on GunBroker and at most 2 listings elsewhere
counts as rare.

### Lookalikes

`lookalikes.toml` groups calibres that are cartridges of their own but look alike, so an app can show
the others from any one of them (`lookalikes(name)`). Each group has `differ_by`, what tells them
apart: `rim`, `bore`, `length` (the case length), `seating` (a wadcutter seated flush or nearly so)
or `load` (a hotter load or another chamber that a board or the service specifies), and `calibres`,
the parent first. Other names of the same cartridge are search aliases, not groups.

## In Python

`import cartridges` reads the files once. Besides the tables, `tags(name)` gives `[]`,
`["obsolete"]`, `["rare"]` or both; `origin(name)` gives `(code, name, flag)` or `None` and
`origin_candidates(name)` the open candidates the same way; `is_worldwide(name)`, `bullet(name)`,
`case_material(name)`, `current_case_materials(name)`, `loose_material(name)`, `shoulder_angle(name)`,
`case_head(name)` and `lookalikes(name)` look up one value; `sources(name, table)` lists every source
of a table (`"mm"`, `"introduced"`, `"primer"`, ...). A problem in the files stops the import with a
`DataError` that lists them all.

## Adding or changing a calibre

1. Copy a file of a similar calibre in the right `calibres/<category>/` folder, give it the new name
   and change the values. Add a source for each value you know and keep a note of anything measured
   or estimated.
2. Run the checks and the tests:

   ```sh
   python3 check.py
   python3 -m unittest discover -s tests
   ```

3. Open a pull request. CI runs both; the check marks every problem on the pull request's files.
4. After it is merged, bump the submodule in the apps and the poster (below).

You can also edit a file in GitHub's web editor and open the pull request from there.

## Checking

`python3 check.py` reads every file and lists each problem with its file and line: broken TOML, an
unknown or misspelt key (with the key it probably means), a value that is not allowed, a missing
measurement or table, a source that is not a web address, a file whose name does not follow the
calibre's name, an alias two calibres use or that is another calibre's name, a category folder
missing from `order.toml`, names in `order.toml` or `lookalikes.toml` without a file. The *Check calibre files* job runs it on every pull request. It needs Python 3.11 or newer.

## Using it

Each repository includes this one as a git submodule at `calibre-data/` and pins a commit:

```sh
git submodule update --init                 # after cloning
git -C calibre-data pull origin main        # move to the newest data
git add calibre-data && git commit -m "Update calibre data"
```

Then regenerate the app's JSON (or the poster) so it uses the new data. In GitHub Actions,
check out with `submodules: true`.

## Licence

[PolyForm Noncommercial 1.0.0](LICENSE.md), © 2026 Simon Giotta. Contributions need the
[Contributor License Agreement](CLA.md).
