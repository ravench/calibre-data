# Calibre data

The shared calibre catalogue for
[Schiesstagebuch](https://github.com/ravench/schiesstagebuch),
[Kaliberfinder](https://github.com/ravench/kaliberfinder) and the
[calibre wall poster](https://github.com/ravench/calibre-poster).

The values are for drawings and for matching photos, **not reloading data**.

## The files

Every calibre is one [TOML](https://toml.io) file in `calibres/<category>/`, named after the calibre
(`.22 LR` is `calibres/rimfire/22-lr.toml`). The folder is the calibre's category, and the only place
it is stored: `rimfire`, `handgun`, `rifle`, `black-powder`, `shotgun` and `air-gun`. The apps know
these six as `Randfeuer`, `Kurzwaffe`, `Langwaffe`, `Schwarzpulver`, `Flinte` and `Luftdruck`, the
names they show (`CATEGORIES` in `cartridges.py`), so a new category needs a change in the apps too.

`cannon` (`Kanone`, the 20 to 40 mm rounds of automatic cannon; tank, naval and artillery guns
stay out) is in the catalogue only, not yet in the apps (`NOT_IN_APPS`):
its calibres are in `ALL_CATALOGUE` and the per-calibre tables but not in `CATALOGUE`, so the apps'
JSON does not change. No C.I.P. or SAAMI sheet covers them, so a cannon file keeps only the
measurements a source gives (`bullet` and `case_length` are required, the others optional; the name
gives both, 35x228 being a 35 mm round with a 228 mm case). It has no
`[primer]` (cannon primers are not reloading sizes), no `display_aliases` and no lookalike group:
the apps read those whole.

- `order.toml`: the order the apps and the poster list the calibres in. A calibre that is not listed
  comes after the listed ones of its category, by name, so a new calibre needs no entry here.
- `countries.toml`: the country codes a calibre's `origin` can name, with English name and flag emoji.
- `books.toml`: the printed books a source can name (see [Sources](#sources)), with title, edition,
  year and ISBN.
- `docs/template.toml`: a calibre file with every field explained, to start a new calibre from.
- `lookalikes.toml`: the groups of calibres that are cartridges of their own but look alike.
- `cartridges.py` reads and checks all of them and gives the apps' generators, `outline.py` and the
  poster the same tables as before (`CATALOGUE`, `INTRODUCED`, `PRIMERS`, `ORIGIN`, ...).
- `outline.py`: the side view of each calibre as SVG path data (`outline(spec)`), and
  `identical_groups()`, the calibres that look exactly the same from the side (today .308 Win / 7.62
  NATO and .223 Rem / 5.56 NATO / GP 90). A crimped blank (e.g. the .22 blank 6.8/11) has no bullet:
  its case narrows to the star crimp. A wadcutter seated flush (.32 S&W Long Wadcutter) shows no
  bullet either. `bulletMaterial` is `steel` (GP 1890 cap) or `lead`, a hollow point's `bullet` has
  its cavity cut into the nose, `tip` is a soft point's lead tip (or a plastic tip, `tipMaterial`
  `polymer`) drawn over the bullet, `head` the brass head of a shot shell or paper case
  (`headMaterial` `steel`: the steel head of a hybrid case), `patch` the paper band, `caseMaterial`
  set when the case is not brass, `currentCaseMaterials` the other materials made today (not drawn).
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
# No source yet for overall_length.
sources = [
  "book:cotw-18 p. 176",
  "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf",
]

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

[case]
material = "brass"
sources = []
```

Text goes in quotes, numbers and `true` don't. Lines starting with `#` are notes for people; the
apps ignore them.

### Sources

Every table has a `sources` list of web addresses (`https://…`) and book pages, one or several:

```toml
sources = [
  "https://en.wikipedia.org/wiki/.22_Long_Rifle",
  "https://municion.org/producto/22-long-rifle/",
  "book:cotw-18 p. 670",
]
```

A book page is `book:`, the book's id in `books.toml`, and the page the value is printed on: the
book's own page number, not the page of a PDF scan. `book:cotw-18 p. 670` is page 670 of the 18th
edition of *Cartridges of the World*. A manual that numbers its pages by chapter has pages like
`book:tm-43-0001-27 p. 14-13` (chapter 14, page 13). Cite a value with its page; never copy a book's
text or tables into this repository. A book that is not in `books.toml` yet needs an entry there
first (title and year; edition, authors, editors, publisher, place and ISBN where it has them).

An empty list `sources = []` means the values have not been checked against a source yet. That is
allowed for the measurements, the primer (then it counts as unverified), the bullet and a brass
case; a year, a shoulder angle, a case head, a steel or plastic bullet, a case material other than
brass and the case materials made today always need one.
`sources(name, table)` in `cartridges.py` gives the whole list; the old tables (`INTRODUCED`,
`SHOULDER_ANGLES`, ...) keep the first one.

### Top of the file

| Key | | Meaning |
|---|---|---|
| `name` | required | The calibre's name as the apps show it, written as in [Names](#names). The file name follows from it (`.22 LR` is `22-lr.toml`); `check.py` gives the right one. |
| `kind` | required | `rimless`, `rimmed`, `belted`, `rimfire`, `shot` (shot shell), `ball` (round ball or BB), `minie` (Minié bullet) or `pellet` (air gun pellet). |
| `profile` | required | Bullet nose of the round as first sold (the apps draw it): `spitzer`, `round`, `flat`, `patched` (paper-patched lead body under a steel cap, GP 1890) or `crimped` (no bullet, the mouth folded shut in a star: blanks and power-tool loads). |
| `profile_today` | optional | The nose of today's usual load, where it is not the first one: the .303 British is drawn `round` but loaded `spitzer` since the Mk VII. Same values as `profile`; for the catalogue only. A `# Today:` comment above it names the source, as `# Nose:` does for `profile`. |
| `aliases` | required | Search aliases, lower case as people type them (`[]` for none). Never the name of another calibre. |
| `display_aliases` | | One or two printable other names, shown in the apps' lists and search and on the poster. Calibres that are separate cartridges are never aliases of each other: .223 Rem / 5.56 NATO / GP 90 and .308 Win / 7.62 NATO differ in loading and are not necessarily interchangeable, so each has its own file. |
| `origin` | | Code from `countries.toml` of the state that introduced the calibre (see [Origin](#origin)). |
| `origin_candidates` | | Instead of `origin` while two or more states can claim it: their codes, likelier first. |
| `worldwide` | | `true` for a calibre in common use worldwide (independent of `origin`: 9x19 mm is German and worldwide). Includes the generic gauges and pellet sizes. |
| `obsolete` | | `true` when no longer in regular factory production (only surplus, boutique loads or reloading). The apps can hide these by default; the poster can mark them. |
| `rare` | | `true` when you are unlikely to find it (see [Rare](#rare)). |

### Names

New names follow the way most names here are written, so the lists read alike. Where a rule leaves
a choice, follow the calibre's family (`.25 WSSM` like `.223 WSSM`, `.38-56 WCF` like `.45-90 WCF`).

- Numbers and units as the SI writes them (SI Brochure, ISO 80000-1): a space before the unit
  (`9 mm`, `3 inch`), units in lower case, a decimal point (`7.62`), and a plain lower-case `x`
  without spaces between bore and case length (`7.62x51 mm`). `check.py` reports `9mm`, `9 MM`,
  `7,62`, `7.62×51`, `9X19` and `7.62 x 51`.
- Metric calibres: bore x case length, `mm`, the rim or bore letters, then the name:
  `7.62x51 mm NATO`, `9x19 mm`, `7x65 mm R`, `8x57 mm IS`, `6.5x50 mm SR Arisaka`. The bore alone
  where the case length is not part of the usual name: `9 mm Glisenti`, `6.5 mm Creedmoor`.
- Inch calibres keep the leading dot: `.308 Winchester`, `.45 ACP`. Maker names are written out
  (`Winchester`, `Remington`) unless the short form is the cartridge's usual name (`ACP`, `S&W`,
  `H&H`, `WMR`, `BMG`).
- A hyphen or slash in the designation stays as the cartridge is known: `.45-70 Government`,
  `.30-06 Springfield`, `6.5-284 Norma`, `7 mm-08 Remington`, `.577/450 Martini-Henry`.
- Trade names as the maker sells them: `6.5 PRC`, `8.6 Blackout`, `7.5 FK`.
- Where two cartridges would get the same name, the case length, the year or the ignition tells
  them apart: `.450/400 Nitro Express 3 inch`, `10.4 mm Swiss Ordnance 1872 Rimfire`,
  `.44 Henry Centrefire`.
- A cartridge with two common names gets the other one in brackets, mostly the metric one first:
  `9 mm Browning kurz (.380 ACP)`, `9.3x66 mm Sako (.370 Sako Magnum)`, `.22 Blank (6.8/11)`. Swiss
  service rounds carry their service name: `7.5x55 mm Swiss (GP 11)`, `5.6 mm GP 90`.
- Round balls, BBs and pellets: the size they are sold as, and in brackets the real diameter or the
  other size people know them by: `.44 Rundkugel (.454)`, `4.5 mm Diabolo (.177)`,
  `4.4 mm Stahl-BB (.177 BB)`, `6 mm Airsoft-BB`. Minié bullets by bore: `.58 Minié`.
- Shot shells: gauge/case length in mm, `12/70`, `.410/76`.
- English, except for rounds known in Switzerland by another name, for example `Knall`,
  `Rundkugel`, `Diabolo`, `Stahl-BB`, `Kadettenpatrone`, `Browning kurz`, `7.65 mm Longue`.
- Short forms and other spellings (`.308 Win`, `9 mm Para`, `12,7x99 mm NATO`) go in
  `display_aliases` or `aliases`, which keep a name as it is printed elsewhere.

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
| `kind = "shot"` | `diameter`, `rim`, `length` (the loaded shell as crimped), optional `case_length` (the hull opened by firing: the length in the name, 70 for a 12/70) |
| `profile = "crimped"` | `rim`, `base`, `mouth` (at the star crimp), `length` |

`sources` lists every page the measurements come from, the page of most of them first. When only
some of them have a source, a note above the list names the others, as in the example above (the
shoulder position is from the C.I.P. sheet there, the other diameters and the case length from the
book):

```toml
# No source yet for case_length.
sources = [
  "https://en.wikipedia.org/wiki/7×64mm",
  "https://bobp.cip-bobp.org/uploads/tdcc/tab-ii/tabiical-en-page24.pdf",
]
```

These lists were filled in from the history of this repository in November 2026: each measurement
counts the page it was taken from when the calibre was added or the value last changed, as the
commits and notes say. Values the notes call estimated (most shoulder positions before the C.I.P.
sheets), values worked out from a drawing or an angle, values measured on a cartridge and the
first catalogue (which named no sources) have none yet. The pages were not compared value by value:
a sample of about 280 values was, and the ones not found on their page count as without a source.
When you check a measurement against a source, add the page and update the note.

In November 2026 the measurements still without a source were compared with the dimension tables of
*Cartridges of the World* (18th edition, 2026) and the physical data of Donnelly's *Handloader's
Manual of Cartridge Conversions* (1987), and then with the cartridge drawings of the *Hornady Handbook
of Cartridge Reloading* (10th edition, 2016) and the Maximum COL and Max. Case Length lines under
them. Where a book prints the same value, to the precision it prints (a value in thousandths of an
inch to about 0.07 mm, in hundredths to about 0.19 mm), its page was added, even when another book
prints another value. Values no book prints the same kept no source. A book page that prints more of
the values than the earlier sources gave together was listed first. Some of Hornady's length bars
start at the .200 line where the base diameter is measured, not at the head; such a bar's value plus
0.200 is the length from the head. The same was then done with the cartridge dimension table of
*Jane's Ammunition Handbook* (2002-2003, pp. 681-682) and the round lengths of the US Army data
sheets TM 43-0001-27 (1994). Their figures also gave the cannon rounds the diameters and lengths
their names and web sources left out; Jane's table measures some cannon cases 0.5 to 1 mm shorter
than their names (25x137 at 136.5 mm), and the names' lengths were kept. The cartridge table of
Williams's *Rapid Fire* (2000, pp. 225-230) then gave the other cannon rounds their rim and base:
20x139 (whose rim Jane's table and Jane's own entry give differently), 30x165, 35x228 and the two
Bofors 40 mm rounds. Jane's and Koll's *Soviet Cannon* (2009) gave 30x165 and 35x228 their round
lengths.

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
Federal's ammunition and the COTW table use small pistol.
Cartridges of the World's dimension tables give the primer as a letter (S small rifle, SP small
pistol, L large rifle, LP large pistol) or, in the European and British tables, as the Berdan
primer's diameter: .177 in. (4.5 mm) is small, .216-.217 in. (5.5 mm) large and .250-.254 in.
Berdan Nitro.

### `[shoulder_angle]`

Bottleneck cases: `degrees` between the shoulder and the case axis (the American convention,
alpha/2). C.I.P. sheets print the full cone angle alpha, so their value is halved; for those
calibres `shoulder_at` is the sheet's L1. A bottleneck case without one is drawn at 32° until a
source is found (`SHOULDER_UNSOURCED` in `tests/test_outline.py` lists them).

### `[case_head]`

`rim_thickness` (R on the C.I.P. sheets, maximum cartridge) for every kind of case. Rimless and
belted cases add their extractor groove where a C.I.P. sheet gives it, all three or none: `ramp_top`
(E: head to the top of the extractor-groove ramp; belted: head to the front of the belt),
`groove_diameter` (E1) and `ramp_angle` (delta: the groove's front ramp to the case axis, degrees).
A case made from a parent case without its own sheet keeps the parent's head (the note says which).
Without a C.I.P. sheet, the rim thickness can come from a book (Cartridges of the World prints it in
its dimension tables, Donnelly as E); the note gives the inches as printed. Book values are nominal
rather than the C.I.P. maximum, so a calibre from a book can have a rim up to about 0.3 mm thinner
than a relative with a C.I.P. sheet (.38 Special 1.37 mm from the book, its wadcutter 1.5 mm from
the sheet). A rim without a thickness is
drawn 1.5 mm thick (rimmed), 1.1 mm (rimfire) or 1.3 mm (rimless and belted); rimless and belted
cases without a groove get a generic one (`HEAD_UNSOURCED` in `tests/test_outline.py` lists them).

### `[bullet]`, `[case]`, `[current_cases]`

- `[bullet]` `type`, in every calibre with a bullet (not shot shells, cannon rounds or blanks: star-
  crimped ones and closed plain cylinders, overall length = case length and rim = base = neck =
  bullet, such as the 9 mm P.A.K.); no type is taken for granted. For a cartridge, the bullet it was
  first sold with: `jacketed` (a full metal jacket or another all-copper bullet), `lead` (bare lead,
  also lubricated or wax coated), `paper` (lead wrapped in paper below the nose), `softpoint`
  (copper jacket with the lead core showing at the tip), `polymer` (copper jacket with a plastic
  tip: V-Max, ELD, FTX, SST, AccuBond), `hollowpoint` (copper jacket with a cavity in the nose, only
  where the first load and nearly every one since are hollow points: the 5 mm Remington Rimfire
  Magnum, .22 TCM, .25 NAA, .357 Remington Maximum and .400 Cor-Bon; open-tip match bullets count as
  `jacketed`) or `steel` (a solid steel projectile: the MPS underwater dart). The GP 1890 steel cap
  is its own profile (`patched`). For a ball, Minié bullet or pellet, what it is made of: `lead`,
  `steel` or `plastic` (steel BBs and airsoft BBs). `sources = []` means not checked. Steel and
  plastic need a source; an unchecked type other than `jacketed` (or `lead` for loose projectiles),
  such as a hunting round's soft point inferred from its use, is listed in `BULLET_INFERRED`.
- `[case]` `material`, in every calibre with a case (not shot shells, balls, Minié bullets or
  pellets): the original case, `brass`, `copper`, lacquered `steel`, `nickel`-plated steel,
  `aluminium`, `paper` (brass foil covered in paper on a brass head, Boxer's Snider case) or `hybrid`
  (brass body on a steel head). Every material but brass needs a source; brass may have
  `sources = []` while it is not checked. The outlines name only the materials that are not brass
  (`caseMaterial`).
- `[current_cases]` `materials`: other case materials made today (brass .45-70, steel 9x19, CCI
  Blazer's aluminium), never the original's own (brass only where the original is not brass); the
  original stays the drawn one.

### `[fired_by]`: the firearms that fire it

Optional, mostly for old and obsolete rounds: the firearms that define the round, that is the arm it
was made for and its main service rifles; not every rifle chambered for it today, machine guns or
later conversions. For the catalogue only; the apps do not show it yet.

```toml
[fired_by]
firearms = ["Vetterli M1869", "Vetterli M1869/81"]
sources = ["https://en.wikipedia.org/wiki/.41_Swiss"]
```

`firearms` names each one as maker or designer and model, the model year written `M1869` whatever
the source writes (`Vetterli M69/81` is `Vetterli M1869/81`), the same way in every file; the family
name alone where the whole series fires it and the source names no model (`Berthier`,
`Snider-Enfield`). Needs a source.

### `[[tip_colours]]`: what coloured bullet tips mean

Optional, for military rounds whose bullet tip is painted to show what it does: one `[[tip_colours]]`
table for each code, at the end of the file. Kaliberfinder lists them on the calibre's page (its generator reads
`TIP_COLOURS`; the sources stay here).

```toml
[[tip_colours]]
colours = ["red", "silver"]
meaning = ["armour-piercing", "incendiary", "tracer"]
description = "US M20, Swiss M.65"
countries = ["US", "CH"]
sources = [
  "https://en.wikipedia.org/wiki/.50_BMG",
  "book:labbett p. 80",
  "book:labbett p. 76",
  "book:labbett p. 77",
]
```

- `colours`: from the tip down, one or more of `black`, `white`, `grey`, `silver`, `red`, `orange`,
  `yellow`, `green`, `blue`, `purple` or `brown` (`["red", "silver"]`: a red tip above a silver band).
- `meaning`: one or more of `ball`, `armour-piercing`, `incendiary`, `explosive`, `tracer`,
  `spotting` (a flash or smoke where it hits, also ranging rounds), `subsonic` or `frangible`; an API
  round is `["armour-piercing", "incendiary"]`.
- `description` (optional): the round's name, in English.
- `countries` (optional): codes from `countries.toml` of the armies that mark it so. The same colours
  can mean something else in another army; the same colours with the same meaning are one table
  that lists all their countries.
- `sources`: at least one.

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

Calibres that are cartridges of their own but look alike, so an app can show the others from any
one of them (`lookalikes(name)`). All groups are in `lookalikes.toml`, each a `[[group]]` with a
name and its calibres, the parent first:

```toml
[[group]]
name = ".308 Winchester"
differ_by = ["load"]
calibres = [".308 Winchester", "7.62x51 mm NATO"]
```

A group's `name` is the parent's name or the family's, such as `8x57 mm` for the four 8x57 mm
rounds. It is unique and never the name of a calibre outside the group. `LOOKALIKE_NAMES` lists the
names in the order of `LOOKALIKES`.

A group's cases share one design; `differ_by` says what tells them apart: `rim` (rimmed or rimless
twin), `bore` (bullet diameter), `length` (case length), `seating` (a wadcutter seated flush or
nearly so), `load` (C.I.P., SAAMI or the service gives the same case a hotter load or another
chamber that the older or weaker guns must not fire) or `ignition` (rimfire and centrefire versions
of one cartridge: a rimfire gun cannot fire the centrefire one, nor the other way round). Each
calibre is in at most one group. Other names of the same cartridge are search aliases, not groups.
The groups were judged against Cartridges of the World (14th ed., 2014) and the C.I.P. and SAAMI
lists.

## In Python

`import cartridges` reads the files once. `CATALOGUE` names each category as the apps know it
(`Randfeuer` for the folder `rimfire`, see `CATEGORIES`); `ALL_CATALOGUE` adds the categories not yet
in the apps (`Kanone`), whose dicts have `None` for a measurement no source gives. Besides the tables, `tags(name)` gives `[]`,
`["obsolete"]`, `["rare"]` or both; `origin(name)` gives `(code, name, flag)` or `None` and
`origin_candidates(name)` the open candidates the same way; `is_worldwide(name)`, `bullet(name)`,
`case_material(name)`, `current_case_materials(name)`, `loose_material(name)`, `shoulder_angle(name)`,
`case_head(name)`, `rim_thickness(name)` and `lookalikes(name)` look up one value; `sources(name, table)` lists every source
of a table (`"mm"`, `"introduced"`, `"primer"`, ...). `TIP_COLOURS` holds the tip colour codes, each
with its own sources, and `FIRED_BY` the firearms of a round. A problem in the files stops the import with a
`DataError` that lists them all.

## Adding or changing a calibre

1. Copy [`docs/template.toml`](docs/template.toml) (every field explained) or the file of a similar
   calibre into the right `calibres/<category>/` folder, give it the new name (see [Names](#names))
   and change the values. Add a source for each value you know and keep a note of anything
   measured or estimated.
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
measurement or table, a source that is not a web address or a page of a book in `books.toml`, a
name that writes a number or unit another way than [Names](#names), a file whose name does not
follow the calibre's name, an alias two calibres use or that is another calibre's name, a category
the apps do not know or that is missing from `order.toml`, names in `order.toml` or
`lookalikes.toml` without a file. The *Check calibre files* job runs it on every pull request. It
needs Python 3.11 or newer.

The tests (`python3 -m unittest discover -s tests`) also check the catalogue as a whole: a bottleneck
case without a shoulder angle or a rimless or belted case without an extractor groove in its
`[case_head]` must be listed in
`tests/test_outline.py`, and calibres that look exactly the same need a group in `lookalikes.toml`.

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
