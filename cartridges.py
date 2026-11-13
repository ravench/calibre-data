"""Calibre catalogue with approximate cartridge dimensions (mm, CIP/SAAMI-ish).

Shared by Schiesstagebuch, Kaliberfinder and the calibre wall poster (each pins this
repository as a git submodule); outline.py draws the side view of every calibre.
Dimensions are approximations for drawings and matching, not reloading data.

The data lives in TOML files: one per calibre in calibres/, plus order.toml,
countries.toml, books.toml and lookalikes.toml (README.md lists every field). This module reads and
checks them and builds the tables the apps' generators, outline.py and the poster use.
`python3 check.py` lists every problem in the files.
"""
import difflib, os, re, unicodedata

try:
    import tomllib
except ModuleNotFoundError as e:  # Python 3.10 and older
    raise ImportError("calibre-data needs Python 3.11 or newer (it reads TOML with tomllib)") from e

ROOT = os.path.dirname(os.path.abspath(__file__))

# Kinds
RIMLESS, SEMI_RIMMED, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET = (
    "rimless", "semi-rimmed", "rimmed", "belted", "rimfire", "shot", "ball", "minie", "pellet")
KINDS = (RIMLESS, SEMI_RIMMED, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET)
LOOSE = (BALL, MINIE, PELLET)  # loose projectiles, not cartridges
# Bullet profiles. PATCHED: paper-patched lead body with a steel-capped ogive nose (GP 1890).
# CRIMPED: no bullet; the case mouth is folded shut in a star (blanks and power-tool loads).
SPITZER, ROUND, FLAT, PATCHED, CRIMPED = "spitzer", "round", "flat", "patched", "crimped"
PROFILES = (SPITZER, ROUND, FLAT, PATCHED, CRIMPED)
# How names write numbers and units (README.md, Names); other spellings belong in the aliases.
NAME_RULES = (
    (re.compile(r"[\d¼½¾](mm|inch)\b", re.I), "a space between the number and the unit: '9 mm', '3 inch'"),
    (re.compile(r"\b(?!(?-i:mm|inch)\b)(mm|inch)\b", re.I), "the unit in lower case: 'mm', 'inch'"),
    (re.compile(r"\d,\d"), "a decimal point, not a comma: '7.62'"),
    (re.compile(r"×|\dX\d"), "a plain lower-case x between the sizes: '7.62x51 mm'"),
    (re.compile(r"\d\s+x\s*\d|\d\s*x\s+\d"), "no spaces around the x: '7.62x51 mm'"),
)
# Categories: a calibre file's `categories` (and key in order.toml) -> the name the apps and the poster
# know the category by. A calibre can be in several; the first is its primary category, the one it is
# listed under in order.toml and CATALOGUE. Those names are German because the apps show them (translated); the apps
# know only the first six, so a new category needs a change in the apps too.
CATEGORIES = {"rimfire": "Randfeuer", "handgun": "Kurzwaffe", "rifle": "Langwaffe",
              "black-powder": "Schwarzpulver", "shotgun": "Flinte", "air-gun": "Luftdruck",
              "cannon": "Kanone"}
# Categories for the catalogue only, not yet in the apps: their calibres are in ALL_CATALOGUE and
# the per-calibre tables but not in CATALOGUE, may leave out measurements no source gives (only bullet
# and case_length are required) and have no [primer] (cannon primers are not reloading sizes),
# display_aliases or lookalike group, the parts the apps' generators read whole.
NOT_IN_APPS = ("cannon",)


def c(name, kind, rim, base, shoulder, neck, case, sh_at, oal, bullet, profile, aliases=()):
    return dict(name=name, kind=kind, rim=rim, base=base, shoulder=shoulder, neck=neck,
                case=case, sh_at=sh_at, oal=oal, bullet=bullet, profile=profile, aliases=list(aliases))


def straight(name, kind, rim, base, neck, case, oal, bullet, profile, aliases=()):
    return c(name, kind, rim, base, None, neck, case, None, oal, bullet, profile, aliases)


def blank(name, rim, base, mouth, length, aliases=(), kind=RIMFIRE):
    """A crimped blank: no bullet, the case (`length` long) narrows to `mouth` at the star crimp.
    `bullet` holds the nominal bore so drawings and tables keep a width."""
    return c(name, kind, rim, base, None, mouth, length, None, length, base, CRIMPED, aliases)


def shot(name, dia, rim, length, aliases=(), case_length=None):
    """`length` is the loaded shell as crimped; `case_length` the hull opened by firing (the length in
    the name: a 12/70 opens to 70 mm), the same when not given."""
    return c(name, SHOT, rim, dia, None, dia, case_length or length, None, length, dia, FLAT, aliases)


def ball(name, dia, aliases=()):
    return c(name, BALL, dia, dia, None, dia, 0, None, dia, dia, ROUND, aliases)


def minie(name, dia, length, aliases=()):
    return c(name, MINIE, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


def pellet(name, dia, length, aliases=()):
    return c(name, PELLET, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


# Primer per calibre: the primer of the original factory ammunition, which is today's Boxer size for
# calibres still loaded. Primers sit in the centre of the case head. Old British Nitro Expresses and
# many old European and American black-powder rounds came with the large .254" Berdan "Nitro" primer
# (Kynoch #40, today RWS 6507), measured on headstamp photos (see PRIMER_SOURCES). Other Berdan
# primers (4.5 and 5.5 mm, e.g. 7.62x39, 7.62x54R surplus) keep the nearest size, with their
# diameter in the file where a source gives it; rimfire and caseless entries have none. The tiny
# Kolibri and Liliput pistol rounds have primers smaller than any reloading size: "miniature", with
# the diameter measured on headstamp photos in the file. Any size may give its measured diameter
# (Berdan primers differ a little from the Boxer size); PRIMER_MM gives every calibre's primer
# diameter, measured or nominal.
SMALL_PISTOL, LARGE_PISTOL, SMALL_RIFLE, LARGE_RIFLE, SHOTSHELL_209, BMG_35, BERDAN_NITRO, MINIATURE = (
    "small-pistol", "large-pistol", "small-rifle", "large-rifle", "shotshell-209", "bmg-35",
    "berdan-nitro", "miniature")
PRIMER_DIAMETERS = {  # mm, nominal primer cup diameter
    SMALL_PISTOL: 4.45, SMALL_RIFLE: 4.45,     # .175"
    LARGE_PISTOL: 5.33, LARGE_RIFLE: 5.33,     # .210"
    SHOTSHELL_209: 6.15,                       # .242"
    BMG_35: 8.03,                              # .316", CCI #35
    BERDAN_NITRO: 6.45,                        # .254", Kynoch #40 / RWS 6507
}

# Bottleneck cases without a sourced shoulder angle are drawn at this one.
DEFAULT_SHOULDER_ANGLE = 32

# Original bullets: JACKETED is a full metal jacket or another all-copper bullet.
JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP = "jacketed", "lead", "paper", "softpoint", "polymer"
HOLLOW_POINT = "hollowpoint"
# Case materials, and what balls, Minié bullets and pellets are made of (LEAD, STEEL or PLASTIC).
BRASS, COPPER, STEEL, NICKEL, PAPER, HYBRID = "brass", "copper", "steel", "nickel", "paper", "hybrid"
ALUMINIUM = "aluminium"
PLASTIC = "plastic"
# What a jacket looks like on the outside, where it is not copper-coloured (gilding metal, tombac, copper,
# copper-plated or -washed steel): CUPRONICKEL (silver: cupronickel, or steel clad or plated with it or
# with nickel) or STEEL (bare or lacquered steel). Only bullets with a jacket have one.
CUPRONICKEL = "cupronickel"
JACKET_METALS = (CUPRONICKEL, STEEL)
# What tells lookalikes apart (differ_by in lookalikes.toml).
RIM, BORE, LENGTH, SEATING, LOAD, IGNITION = "rim", "bore", "length", "seating", "load", "ignition"


# ---- Reading and checking the files --------------------------------------------------------------

class DataError(Exception):
    """Problems in the TOML files: `problems` is a list of (path relative to the repository, line or
    None, message)."""

    def __init__(self, problems):
        self.problems = problems
        super().__init__("\n".join(_format(p) for p in problems))


def _format(problem):
    path, line, message = problem
    return f"{path}{f':{line}' if line else ''}: {message}"


def slug(name):
    """The file name (without .toml) a calibre's file must have: its name in lower case ASCII, every
    run of other characters a hyphen (".22 LR" is 22-lr.toml, "3¼ inch" 3-1-4-inch, "2⅜ inch" 2-3-8-inch)."""
    name = "".join(" " + unicodedata.normalize("NFKD", ch).replace("\u2044", "/")
                   if unicodedata.name(ch, "").startswith("VULGAR FRACTION") else ch for ch in name)
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# Measurements by shape: the short forms of balls, Minié bullets, pellets, shot shells and crimped
# blanks, and the full form of every other cartridge (shoulder and shoulder_at only for bottlenecks).
MM_FULL = ("rim", "base", "shoulder", "shoulder_at", "neck", "case_length", "overall_length", "bullet")
MM_SHAPES = {  # shape: (required keys, optional keys)
    "ball": (("diameter",), ()),
    "loose": (("diameter", "length"), ()),
    "shot": (("diameter", "rim", "length"), ("case_length",)),
    "blank": (("rim", "base", "mouth", "length"), ()),
    "cartridge": (("rim", "base", "neck", "case_length", "overall_length", "bullet"), ("shoulder", "shoulder_at")),
    "partial": (("case_length", "bullet"), ("rim", "base", "shoulder", "shoulder_at", "neck", "overall_length")),
}
TOP_KEYS = {"name", "categories", "kind", "profile", "profile_today", "aliases", "display_aliases", "origin",
            "origin_candidates", "origin_sources", "worldwide", "obsolete", "rare"}
# [case_head] keys beside rim_thickness: the extractor groove of a rimless, semi-rimmed or belted case, all three
# or none.
HEAD_GROOVE = ("ramp_top", "groove_diameter", "ramp_angle")
FACTS = {  # table: (required keys, optional keys, sources: "required", "optional" or "may be empty")
    "mm": ((), (), "may be empty"),  # keys by shape, above
    "introduced": ((), ("year", "unknown"), "optional"),
    "primer": (("size",), ("diameter",), "may be empty"),  # diameter: measured mm, required for miniature
    "shoulder_angle": (("degrees",), (), "required"),
    "case_head": (("rim_thickness",), HEAD_GROOVE, "required"),
    "bullet": (("type",), ("jacket",), "may be empty"),
    "case": (("material",), (), "may be empty"),  # every case but brass needs a source
    "current_cases": (("materials",), (), "required"),
    "fired_by": (("firearms",), (), "required"),
}
# steel: the MPS dart
CARTRIDGE_BULLETS = (JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT, STEEL)
JACKETED_BULLETS = (JACKETED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT)  # the types that may name a jacket
LOOSE_BULLETS = (LEAD, STEEL, PLASTIC)
BULLET_TYPES = CARTRIDGE_BULLETS + (PLASTIC,)
CASE_MATERIALS = (BRASS, COPPER, STEEL, NICKEL, ALUMINIUM, PAPER, HYBRID)
CURRENT_CASE_MATERIALS = (BRASS, COPPER, STEEL, NICKEL, ALUMINIUM)
DIFFER_BY = (RIM, BORE, LENGTH, SEATING, LOAD, IGNITION)
GROUP_KEYS = ("name", "differ_by", "calibres")
# A printed book as a source: "book:<id> p. <page>", the id of a book in books.toml. A manual that
# numbers its pages by chapter has pages such as "14-13" (chapter 14, page 13).
BOOK_SOURCE = re.compile(r"book:(?P<id>[^\s]+) p\. (?P<page>[1-9][0-9]*(?:-[1-9][0-9]*)?)")
BOOK_KEYS = ("title", "year", "edition", "authors", "editors", "publisher", "place", "isbn")
# [[colour_codes]]: what a painted bullet tip, cartridge base or primer annulus means, a table for each
# code. `part` says where the paint is (PARTS). A tip's colours are listed from the tip down (["red",
# "silver"]: a red tip above a silver band); a base (the head of the case) and an annulus (the lacquer
# ring around the primer) have one colour. The meanings combine (["armour-piercing", "incendiary"] is
# an API round).
COLOUR_CODE_KEYS = (("part", "colours", "meaning", "sources"), ("description", "countries"))  # (required, optional)
PARTS = ("tip", "base", "annulus")
COLOURS = ("black", "white", "grey", "silver", "red", "orange", "yellow", "green", "blue", "purple", "brown")
MEANINGS = ("ball", "armour-piercing", "incendiary", "explosive", "tracer", "spotting", "subsonic", "frangible",
            "proof", "reduced-charge")


def is_blank(profile, rim, base, neck, bullet, case_length, overall_length):
    """A blank without a bullet: star-crimped (CRIMPED), or closed inside the case, a plain cylinder with
    nothing above the mouth (the 9 mm P.A.K., the 8 mm and .315 Knall)."""
    return profile == CRIMPED or (case_length is not None and overall_length == case_length
                                  and rim == base == neck == bullet)


def _shape(kind, profile, category=None):
    if kind == BALL:
        return "ball"
    if kind in (MINIE, PELLET):
        return "loose"
    if kind == SHOT:
        return "shot"
    if profile == CRIMPED:
        return "blank"
    return "partial" if category in NOT_IN_APPS else "cartridge"


def _entry(name, kind, profile, aliases, m, category=None):
    """The catalogue dict of a calibre, built by the helper of its shape (None for a measurement a
    partial one leaves out)."""
    shape = _shape(kind, profile, category)
    if shape == "ball":
        return ball(name, m["diameter"], aliases)
    if shape == "loose":
        return (minie if kind == MINIE else pellet)(name, m["diameter"], m["length"], aliases)
    if shape == "shot":
        return shot(name, m["diameter"], m["rim"], m["length"], aliases, m.get("case_length"))
    if shape == "blank":
        return blank(name, m["rim"], m["base"], m["mouth"], m["length"], aliases, kind=kind)
    return c(name, kind, m.get("rim"), m.get("base"), m.get("shoulder"), m.get("neck"), m["case_length"],
             m.get("shoulder_at"), m.get("overall_length"), m["bullet"], profile, aliases)


class _File:
    """One parsed TOML file and the problems found in it."""

    def __init__(self, root, rel, problems):
        self.rel, self.problems = rel, problems
        with open(os.path.join(root, rel), "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):  # the byte order mark some Windows editors write
            raw = raw[3:]
        self.text = raw.decode("utf-8", errors="replace")
        try:
            self.data = tomllib.loads(raw.decode("utf-8"))
        except UnicodeDecodeError as e:
            self.data = None
            self.problem(None, f"not UTF-8 text: {e}")
        except tomllib.TOMLDecodeError as e:
            self.data = None
            m = re.search(r"\(at line (\d+)", str(e))
            self.problem(int(m.group(1)) if m else None, f"not valid TOML: {e}")

    def line(self, table=None, key=None, nth=0):
        """The line of `key` (in `[table]`, or the `nth` `[[table]]`), of the table header, or None."""
        lines = self.text.split("\n")
        start = 0
        if table:
            hdr = [i for i, l in enumerate(lines) if re.match(rf"\s*\[\[?\s*{re.escape(table)}\s*\]\]?", l)]
            if len(hdr) <= nth:
                return None
            start = hdr[nth]
            if key is None:
                return start + 1
        for i in range(start + (1 if table else 0), len(lines)):
            if table is None and re.match(r"\s*\[", lines[i]):
                break
            if table and i > start and re.match(r"\s*\[", lines[i]):
                break
            if key and re.match(rf"\s*\"?{re.escape(key)}\"?\s*=", lines[i]):
                return i + 1
        return None

    def problem(self, line, message):
        self.problems.append((self.rel, line, message))


def _close(word, choices):
    match = difflib.get_close_matches(str(word), [str(c) for c in choices], n=1, cutoff=0.6)
    return f' (did you mean "{match[0]}"?)' if match else ""


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_text_list(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _check_keys(f, table, data, allowed, required):
    for k in data:
        if k not in allowed:
            line = f.line(table, k) or (f.line(k) if table is None else None)
            f.problem(line, f"unknown key {k!r}{' in [' + table + ']' if table else ''}"
                                        f"{_close(k, allowed)}; allowed: {', '.join(sorted(allowed))}")
    for k in required:
        if k not in data:
            f.problem(f.line(table), f"[{table}] needs {k!r}" if table else f"needs {k!r}")


def _check_sources(f, table, data, rule, books=None, nth=0, key="sources"):
    """The sources of one table (the `nth` of a [[table]]): web addresses and book pages (`books`: the
    ids in books.toml, or None when books.toml could not be read). Without a table, the list is the
    top-level `key` (origin_sources)."""
    label = key if table is None else f"[[{table}]]" if table == "colour_codes" else f"[{table}]"
    if key not in data:
        if rule != "optional":
            f.problem(f.line(table, nth=nth), f"{label} needs a sources list (an empty list [] when nothing is checked yet)"
                      if rule == "may be empty" else f"{label} needs sources = [\"https://…\"]")
        return []
    urls = data[key]
    if not _is_text_list(urls):
        f.problem(f.line(table, key, nth), f"{label} must be a list of web addresses in quotes" if table is None
                  else f"{label} sources must be a list of web addresses in quotes")
        return []
    if rule == "required" and not urls:
        f.problem(f.line(table, key, nth), f"{label} needs at least one source")
    for u in urls:
        book = BOOK_SOURCE.fullmatch(u)
        if book:
            if books is not None and book["id"] not in books:
                f.problem(f.line(table, key, nth), f"{label} source {u!r} names no book in books.toml"
                                                    f"{_close(book['id'], books)}")
        elif u.startswith("book:"):
            f.problem(f.line(table, key, nth), f"{label} source {u!r} must be written book:<id> p. <page>, "
                                                f"e.g. \"book:cotw-18 p. 176\"")
        elif not re.fullmatch(r"https://[^\s\"<>]+\.[^\s\"<>]+", u):
            f.problem(f.line(table, key, nth), f"{label} source {u!r} is not a https:// web address "
                                                f"or a book page (book:<id> p. <page>)")
    if len(set(urls)) != len(urls):
        f.problem(f.line(table, key, nth), f"{label} lists a source twice")
    return urls


def _isbn_ok(isbn):
    """An ISBN-10 or ISBN-13 with hyphens or without, whose check digit is right."""
    if not isinstance(isbn, str) or not re.fullmatch(r"[0-9X]+(-[0-9X]+)*", isbn):
        return False
    d = isbn.replace("-", "")
    if re.fullmatch(r"[0-9]{9}[0-9X]", d):
        return sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(d)) % 11 == 0
    if re.fullmatch(r"97[89][0-9]{10}", d):
        return sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(d)) % 10 == 0
    return False


def _read_books(bf):
    """Check books.toml; returns {id: book table}."""
    books = {}
    if not bf.data:
        bf.problem(None, "lists no books")
    for bid, v in bf.data.items():
        if not isinstance(v, dict):
            bf.problem(bf.line(None, bid), f"{bid} must be a table: [{bid}] with title = \"…\" and year = …")
            continue
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", bid):
            bf.problem(bf.line(bid), f"the book id [{bid}] must be lower case letters, digits and hyphens")
        _check_keys(bf, bid, v, set(BOOK_KEYS), ("title", "year"))
        for k in BOOK_KEYS:
            if k in v and k != "year" and (not isinstance(v[k], str) or not v[k].strip()):
                bf.problem(bf.line(bid, k), f"[{bid}] {k} must be text in quotes")
        year = v.get("year")
        if "year" in v and (not isinstance(year, int) or isinstance(year, bool) or not 1500 <= year <= 2100):
            bf.problem(bf.line(bid, "year"), f"[{bid}] year must be the year printed, such as 1965, without quotes")
        if isinstance(v.get("isbn"), str) and not _isbn_ok(v["isbn"]):
            bf.problem(bf.line(bid, "isbn"), f"[{bid}] isbn {v['isbn']!r} is not a valid ISBN (check digit?)")
        books[bid] = v
    return books


def _check_colour_codes(f, codes, shape, countries, books):
    """Check a calibre's [[colour_codes]] tables (`shape`: its shape in MM_SHAPES)."""
    if not isinstance(codes, list) or not codes or not all(isinstance(t, dict) for t in codes):
        f.problem(f.line(None, "colour_codes") or f.line("colour_codes"),
                  "each colour code is a [[colour_codes]] table with part, colours, meaning and sources")
        return
    if shape not in ("cartridge", "partial"):
        f.problem(f.line("colour_codes"), "[[colour_codes]] is only for cartridges with a bullet")
    req, opt = COLOUR_CODE_KEYS
    seen = {}
    for i, t in enumerate(codes):
        def at(key=None, i=i):
            return f.line("colour_codes", key, nth=i) or f.line("colour_codes", nth=i)
        for k in t:
            if k not in req + opt:
                f.problem(at(k), f"unknown key {k!r} in [[colour_codes]]{_close(k, req + opt)}; "
                                 f"allowed: {', '.join(sorted(req + opt))}")
        for k in req:
            if k not in t and k != "sources":  # _check_sources reports that
                f.problem(at(), f"[[colour_codes]] needs {k!r}")
        _check_sources(f, "colour_codes", t, "required", books, nth=i)
        if "part" in t and t["part"] not in PARTS:
            f.problem(at("part"), f"[[colour_codes]] part is \"tip\", \"base\" or \"annulus\"{_close(str(t['part']), PARTS)}")
        elif t.get("part") != "tip" and _is_text_list(t.get("colours")) and len(t["colours"]) > 1:
            f.problem(at("colours"), f"[[colour_codes]] {'a' if t['part'] == 'base' else 'an'} {t['part']} has one colour, "
                                     f"not {len(t['colours'])}")
        for k, choices in (("colours", COLOURS), ("meaning", MEANINGS)):
            if k not in t:
                continue
            bad = [x for x in t[k] if x not in choices] if _is_text_list(t[k]) else [t[k]]
            if bad or not t[k]:
                f.problem(at(k), f"[[colour_codes]] {k} lists one or more of {', '.join(choices)}"
                                 f"{_close(bad[0], choices) if bad else ''}")
            elif len(set(t[k])) != len(t[k]):
                f.problem(at(k), f"[[colour_codes]] {k} lists {next(x for x in t[k] if t[k].count(x) > 1)!r} twice")
        if "description" in t and (not isinstance(t["description"], str) or not t["description"].strip()):
            f.problem(at("description"), "[[colour_codes]] description must be text in quotes")
        if "countries" in t:
            codes = t["countries"]
            if not _is_text_list(codes) or not codes:
                f.problem(at("countries"), "[[colour_codes]] countries lists one or more country codes")
            elif len(set(codes)) != len(codes):
                f.problem(at("countries"), "[[colour_codes]] countries lists a country twice")
            elif countries is not None:
                for code in codes:
                    if code not in countries:
                        f.problem(at("countries"), f"[[colour_codes]] country {code!r} is not a code in "
                                                   f"countries.toml{_close(code, countries)}")
        if t.get("part") in PARTS and _is_text_list(t.get("colours")) and _is_text_list(t.get("meaning")):
            key = (t["part"], tuple(t["colours"]), frozenset(t["meaning"]))
            if key in seen:
                f.problem(at("colours"), f"[[colour_codes]] {' over '.join(t['colours'])} {t.get('part')} with this meaning is "
                                         f"already on line {seen[key]}: list all its countries there")
            seen.setdefault(key, at())


def _read_calibre(f, countries, books=None):
    """Check one calibre file; returns (entry dict, raw data, facts) or None when it cannot be used."""
    d = f.data
    tables = {k for k, v in d.items() if isinstance(v, dict) and k != "colour_codes"}
    top = {k for k in d if k not in tables and k != "colour_codes"}
    _check_keys(f, None, {k: d[k] for k in top}, TOP_KEYS, ("name", "categories", "kind", "profile", "aliases"))
    for t in tables:
        if t not in FACTS:
            f.problem(f.line(t), f"unknown table [{t}]{_close(t, FACTS)}; allowed: {', '.join(FACTS)}")
    if "mm" not in tables:
        f.problem(None, "needs a [mm] table with the measurements")
    if "introduced" not in tables:
        f.problem(None, "needs an [introduced] table (year and sources, or unknown with the reason)")
    name, kind, profile = d.get("name"), d.get("kind"), d.get("profile")
    if not isinstance(name, str) or not name.strip():
        f.problem(f.line(None, "name"), "name must be text in quotes")
        return None
    for rule, how in NAME_RULES:
        if rule.search(name):
            f.problem(f.line(None, "name"), f"the name {name!r} needs {how}")
    expected = slug(name) + ".toml"
    if os.path.basename(f.rel) != expected:
        f.problem(f.line(None, "name"), f"the file of {name!r} must be called {expected}")
    cats = d.get("categories")
    category = cats[0] if _is_text_list(cats) and cats and cats[0] in CATEGORIES else None
    if "categories" not in d:
        pass  # reported by _check_keys
    elif not _is_text_list(cats) or not cats:
        f.problem(f.line(None, "categories"), "categories must be a list of one or more categories in quotes, "
                                              "the primary one first")
    else:
        for c in cats:
            if c not in CATEGORIES:
                key = {app: key for key, app in CATEGORIES.items()}.get(c)
                hint = f" (write {key} for {c})" if key else _close(c, CATEGORIES)
                f.problem(f.line(None, "categories"), f"category {c!r} is not one of {', '.join(CATEGORIES)}{hint}")
        if len(set(cats)) != len(cats):
            f.problem(f.line(None, "categories"), "categories lists a category twice")
        hidden = [c for c in cats if c in NOT_IN_APPS]
        if hidden and len({c for c in cats if c in CATEGORIES}) > len(set(hidden)):
            f.problem(f.line(None, "categories"), f"{', '.join(hidden)} is not in the apps yet: a calibre in it "
                                                  "is in no other category")
    if kind not in KINDS:
        f.problem(f.line(None, "kind"), f"kind {kind!r} is not one of {', '.join(KINDS)}{_close(kind, KINDS)}")
    if profile not in PROFILES:
        f.problem(f.line(None, "profile"),
                  f"profile {profile!r} is not one of {', '.join(PROFILES)}{_close(profile, PROFILES)}")
    if "profile_today" in d:
        today = d["profile_today"]
        if today not in PROFILES:
            f.problem(f.line(None, "profile_today"),
                      f"profile_today {today!r} is not one of {', '.join(PROFILES)}{_close(today, PROFILES)}")
        elif today == profile:
            f.problem(f.line(None, "profile_today"), "profile_today is the same as profile: leave it out")
    for k in ("aliases", "display_aliases"):
        if k in d and not _is_text_list(d[k]):
            f.problem(f.line(None, k), f"{k} must be a list of texts in quotes")
    if _is_text_list(d.get("aliases")) and len(set(d["aliases"])) != len(d["aliases"]):
        f.problem(f.line(None, "aliases"), "aliases lists a name twice")
    if _is_text_list(d.get("display_aliases")) and not 1 <= len(d["display_aliases"]) <= 2:
        f.problem(f.line(None, "display_aliases"), "display_aliases holds one or two names")
    if "display_aliases" in d and category in NOT_IN_APPS:
        f.problem(f.line(None, "display_aliases"),
                  f"display_aliases are for the apps, which do not show {category} calibres yet: remove them")
    for k in ("worldwide", "obsolete", "rare"):
        if k in d and not isinstance(d[k], bool):
            f.problem(f.line(None, k), f"{k} must be true or false (without quotes)")
    if "origin" in d and countries is not None and d["origin"] not in countries:
        f.problem(f.line(None, "origin"),
                  f"origin {d['origin']!r} is not a code in countries.toml{_close(d['origin'], countries)}")
    if "origin_candidates" in d:
        cands = d["origin_candidates"]
        if not _is_text_list(cands) or len(cands) < 2:
            f.problem(f.line(None, "origin_candidates"), "origin_candidates lists two or more country codes")
        elif countries is not None:
            for code in cands:
                if code not in countries:
                    f.problem(f.line(None, "origin_candidates"),
                              f"origin candidate {code!r} is not a code in countries.toml{_close(code, countries)}")
        if "origin" in d:
            f.problem(f.line(None, "origin_candidates"), "a calibre has origin or origin_candidates, not both")
    if "origin" in d or "origin_candidates" in d:
        if "origin_sources" not in d:
            f.problem(f.line(None, "origin") or f.line(None, "origin_candidates"),
                      "origin needs origin_sources, the pages that name that state (an empty list [] when "
                      "nothing is checked yet)")
        else:
            _check_sources(f, None, d, "may be empty", books, key="origin_sources")
    elif "origin_sources" in d:
        f.problem(f.line(None, "origin_sources"), "origin_sources without origin or origin_candidates")
    if kind not in KINDS or profile not in PROFILES or "mm" not in tables:
        return None

    facts = {}
    ok = True
    for t in tables & set(FACTS):
        data = d[t]
        req, opt, rule = FACTS[t]
        if t == "mm":
            req, opt = MM_SHAPES[_shape(kind, profile, category)]
            if _shape(kind, profile, category) == "cartridge" and ("shoulder" in data) != ("shoulder_at" in data):
                f.problem(f.line("mm"), "[mm] needs both shoulder and shoulder_at (bottleneck) or neither (straight case)")
                ok = False
        allowed = set(req) | set(opt) | {"sources"}
        before = len(f.problems)
        _check_keys(f, t, data, allowed, req)
        urls = _check_sources(f, t, data, rule, books)
        for k, v in data.items():
            if k == "sources" or k not in allowed:
                continue
            if t == "mm" or t == "case_head" or k == "degrees":
                if not _is_number(v) or v <= 0:
                    f.problem(f.line(t, k), f"[{t}] {k} must be a number above 0, without quotes")
        if t == "introduced":
            if ("year" in data) == ("unknown" in data):
                f.problem(f.line(t), "[introduced] has either year (with sources) or unknown (the reason)")
            elif "year" in data:
                if not isinstance(data["year"], int) or isinstance(data["year"], bool) or not 1500 <= data["year"] <= 2100:
                    f.problem(f.line(t, "year"), "[introduced] year must be a year such as 1887, without quotes")
                if not urls and _is_text_list(data.get("sources", [])):
                    f.problem(f.line(t), "[introduced] year needs at least one source")
            elif not isinstance(data["unknown"], str) or not data["unknown"].strip():
                f.problem(f.line(t, "unknown"), "[introduced] unknown must say why there is no year, in quotes")
        if t == "primer" and data.get("size") == MINIATURE and "diameter" not in data:
            f.problem(f.line(t), f"[primer] a {MINIATURE!r} size needs its diameter (mm)")
        elif t == "primer" and "diameter" in data:
            dia, nominal = data["diameter"], PRIMER_DIAMETERS.get(data.get("size"))
            if not _is_number(dia) or not (1 <= dia < 4.45 if nominal is None else abs(dia - nominal) <= 0.5):
                f.problem(f.line(t, "diameter"), "[primer] diameter is the measured primer in mm: 1 to under 4.45 "
                                                 "for a miniature primer, else within 0.5 of its size's nominal one")
            elif not data.get("sources"):
                f.problem(f.line(t), "[primer] a measured diameter needs a source")
        enums = {("primer", "size"): tuple(PRIMER_DIAMETERS) + (MINIATURE,), ("bullet", "type"): BULLET_TYPES,
                 ("bullet", "jacket"): JACKET_METALS, ("case", "material"): CASE_MATERIALS}
        for (tt, k), allowed_values in enums.items():
            if t == tt and k in data and data[k] not in allowed_values:
                f.problem(f.line(t, k), f"[{t}] {k} {data[k]!r} is not one of {', '.join(allowed_values)}"
                                        f"{_close(data[k], allowed_values)}")
        if t == "current_cases" and "materials" in data:
            mats = data["materials"]
            if not _is_text_list(mats) or not mats or any(m not in CURRENT_CASE_MATERIALS for m in mats):
                f.problem(f.line(t, "materials"), f"[current_cases] materials lists one or more of "
                                                  f"{', '.join(CURRENT_CASE_MATERIALS)}")
        if t == "fired_by" and "firearms" in data:
            arms = data["firearms"]
            if not _is_text_list(arms) or not arms or not all(a.strip() and a == a.strip() for a in arms):
                f.problem(f.line(t, "firearms"), "[fired_by] firearms lists one or more firearm names in quotes, "
                                                 "without spaces around them")
            elif len({a.casefold() for a in arms}) != len(arms):
                f.problem(f.line(t, "firearms"), "[fired_by] firearms lists a firearm twice")
        if t == "shoulder_angle" and _is_number(data.get("degrees")) and not 0 < data["degrees"] < 90:
            f.problem(f.line(t, "degrees"), "[shoulder_angle] degrees is the angle to the case axis, above 0 and below 90")
        ok = ok and len(f.problems) == before
        facts[t] = dict(data, sources=urls)
    if "colour_codes" in d:
        _check_colour_codes(f, d["colour_codes"], _shape(kind, profile, category), countries, books)
    if not ok or category is None or not all(c in CATEGORIES for c in cats):
        return None
    if kind in (RIMFIRE,) + LOOSE:
        if "primer" in facts:
            f.problem(f.line("primer"), f"a {kind} calibre has no primer: remove [primer]")
    elif category in NOT_IN_APPS:
        if "primer" in facts:
            f.problem(f.line("primer"), f"a {category} round has no [primer] (not a reloading size): remove it")
    elif "primer" not in facts:
        f.problem(None, "a centrefire calibre needs a [primer] table (size and sources, or sources = [] if not checked)")
    if kind == SEMI_RIMMED and not facts["mm"].get("rim", 0) > facts["mm"].get("base", 0):
        f.problem(f.line("mm", "rim"), "a semi-rimmed case has a rim wider than its base")
    if category == "cannon" and not 20 <= facts["mm"]["bullet"] <= 57:
        f.problem(f.line("mm", "bullet"), "cannon holds the 20 to 57 mm cannon rounds: bullet is 20 to 57")
    if kind in LOOSE + (SHOT,):
        if "case" in facts:
            f.problem(f.line("case"), f"a {kind} calibre has no metal case: remove [case]")
    elif "case" not in facts:
        f.problem(None, 'needs a [case] table: material = "brass" (sources = [] if not checked) or another '
                        "material with its sources")
    elif facts["case"]["material"] != BRASS and not facts["case"]["sources"]:
        f.problem(f.line("case"), f"[case] material {facts['case']['material']!r} needs a source")
    m = facts["mm"]
    if kind == SHOT or category in NOT_IN_APPS or kind not in LOOSE and is_blank(profile, m.get("rim"), m.get("base"), m.get("neck"),
                                                           m.get("bullet"), m.get("case_length"), m.get("overall_length")):
        if "bullet" in facts:
            f.problem(f.line("bullet"), "shot shells, blanks and cannon rounds have no [bullet]: remove it")
    elif "bullet" not in facts:
        usual = LEAD if kind in LOOSE else JACKETED
        f.problem(None, f'needs a [bullet] table: type = "{usual}" (sources = [] if not checked) or another type')
    else:
        allowed = LOOSE_BULLETS if kind in LOOSE else CARTRIDGE_BULLETS
        if facts["bullet"]["type"] not in allowed:
            f.problem(f.line("bullet", "type"), f"a {kind} calibre's [bullet] type is one of {', '.join(allowed)}")
        elif facts["bullet"]["type"] in (STEEL, PLASTIC) and not facts["bullet"]["sources"]:
            f.problem(f.line("bullet"), f"[bullet] type {facts['bullet']['type']!r} needs a source")
        elif "jacket" in facts["bullet"] and facts["bullet"]["type"] not in JACKETED_BULLETS:
            f.problem(f.line("bullet", "jacket"), f"only a bullet with a jacket ({', '.join(JACKETED_BULLETS)}) "
                                                  f"has a [bullet] jacket")
    if "case_head" in facts:
        groove = [k for k in HEAD_GROOVE if k in facts["case_head"]]
        if kind in (RIMMED, RIMFIRE) and groove:
            f.problem(f.line("case_head"), f"a {kind} case has no extractor groove: [case_head] has only rim_thickness")
        elif kind not in (RIMMED, RIMFIRE, RIMLESS, SEMI_RIMMED, BELTED):
            f.problem(f.line("case_head"), f"a {kind} calibre has no [case_head]")
        elif groove and len(groove) < len(HEAD_GROOVE):
            f.problem(f.line("case_head"), "[case_head] has ramp_top, groove_diameter and ramp_angle together, "
                                           "or only rim_thickness")
    aliases = d.get("aliases", []) if _is_text_list(d.get("aliases")) else []
    entry = _entry(name, kind, profile, aliases, facts["mm"], category)
    return entry, d, facts


def load(root=ROOT):
    """Read and check every file under `root`; returns the tables, or raises DataError listing every
    problem found."""
    problems = []

    def read(rel):
        if not os.path.exists(os.path.join(root, rel)):
            problems.append((rel, None, "missing"))
            return None
        f = _File(root, rel, problems)
        return f if f.data is not None else None

    countries, country_names = {}, {}
    before = len(problems)
    cf = read("countries.toml")
    if cf:
        if not cf.data:
            cf.problem(None, "lists no countries")
        for code, v in cf.data.items():
            if not isinstance(v, dict) or not isinstance(v.get("name"), str):
                cf.problem(cf.line(code), f"[{code}] needs name = \"…\"")
                continue
            _check_keys(cf, code, v, {"name", "de", "fr", "it", "flag"}, ("name", "de", "fr", "it"))
            for lang in ("de", "fr", "it"):
                if lang in v and not (isinstance(v[lang], str) and v[lang].strip()):
                    cf.problem(cf.line(code, lang), f"[{code}] {lang} must be the name in that language, in quotes")
            if "flag" in v and not isinstance(v["flag"], str):
                cf.problem(cf.line(code, "flag"), f"[{code}] flag must be the flag emoji in quotes")
            countries[code] = (v["name"], v.get("flag"))
            country_names[code] = {"en": v["name"], **{lang: v[lang] for lang in ("de", "fr", "it") if isinstance(v.get(lang), str)}}
    if len(problems) > before:  # check the calibres' origins only against a good list
        countries = None

    books = {}
    before = len(problems)
    bf = read("books.toml")
    if bf:
        books = _read_books(bf)
    if len(problems) > before:  # check the book sources only against a good list
        books = None

    order = {}
    of = read("order.toml")
    if of:
        for cat, names in of.data.items():
            if cat not in CATEGORIES:
                key = {app: key for key, app in CATEGORIES.items()}.get(cat)
                hint = f" (write {key} for {cat})" if key else _close(cat, CATEGORIES)
                of.problem(of.line(None, cat), f"category {cat!r} is not one of {', '.join(CATEGORIES)}{hint}")
                continue
            if not _is_text_list(names):
                of.problem(of.line(None, cat), f"{cat} must be a list of calibre names in quotes")
                continue
            order[cat] = names

        for cat in CATEGORIES:
            if cat not in of.data:
                of.problem(None, f"misses the category {cat!r}")

    found = {}  # primary category -> [(entry, raw, facts, file)]
    cal_dir = os.path.join(root, "calibres")
    if not os.path.isdir(cal_dir):
        problems.append(("calibres", None, "missing: the folder with one file per calibre"))
    for fn in sorted(os.listdir(cal_dir)) if os.path.isdir(cal_dir) else []:
        rel = f"calibres/{fn}"
        if fn.startswith("."):  # .DS_Store and other hidden files
            continue
        if os.path.isdir(os.path.join(cal_dir, fn)):
            problems.append((rel, None, "calibre files go straight into calibres/, with their categories in the "
                                        "file (categories = [...]): move them out of this folder"))
            continue
        if not fn.endswith(".toml"):
            problems.append((rel, None, "only .toml files belong here"))
            continue
        f = read(rel)
        if f is None:
            continue
        got = _read_calibre(f, countries, books)
        if got:
            found.setdefault(got[1]["categories"][0], []).append((*got, f))

    # Across files: unique names and aliases, the order list, lookalike groups.
    by_name = {}
    for cat, items in found.items():
        for entry, raw, facts, f in items:
            if entry["name"] in by_name:
                f.problem(f.line(None, "name"), f"{entry['name']!r} also has the file {by_name[entry['name']][3].rel}")
            else:
                by_name[entry["name"]] = (cat, raw, facts, f)
    seen_alias = {}
    by_lower = {n.lower(): n for n in by_name}
    for name, (cat, raw, facts, f) in by_name.items():
        aliases = raw.get("aliases", [])
        for a in aliases if _is_text_list(aliases) else []:
            if a in seen_alias and seen_alias[a] != name:
                f.problem(f.line(None, "aliases"), f"alias {a!r} is also an alias of {seen_alias[a]!r}")
            if by_lower.get(a.lower(), name) != name:
                f.problem(f.line(None, "aliases"), f"alias {a!r} is the name of the calibre {by_lower[a.lower()]!r}")
            seen_alias.setdefault(a, name)
    def has_file(n):  # also a file with a problem of its own, so it is not reported twice
        return os.path.exists(os.path.join(cal_dir, slug(n) + ".toml"))

    catalogue = []
    for cat, names in order.items():
        if cat not in found and not any(has_file(n) for n in names):
            of.problem(of.line(None, cat), f"no calibre has {cat!r} as its first category")
            continue
        files = {e["name"]: e for e, *_ in found.get(cat, [])}
        listed = []
        for n in names:
            if n in listed:
                of.problem(of.line(None, cat), f"{n!r} is listed twice")
            elif n not in files and n not in by_name and has_file(n):
                pass
            elif n not in files:
                where = by_name.get(n)
                of.problem(of.line(None, cat), f"{n!r} is not a calibre whose first category is {cat}" +
                           (f" (its first category is {where[0]})" if where else _close(n, files)))
            else:
                listed.append(n)
        rest = sorted(n for n in files if n not in listed)
        catalogue.append((CATEGORIES[cat], [files[n] for n in listed + rest]))

    lookalikes, group_names = [], []
    lf = read("lookalikes.toml")
    if lf:
        _check_keys(lf, None, lf.data, {"group"}, ())
        groups = lf.data.get("group", [])
        if groups == []:
            lf.problem(None, "lists no groups")
        if not isinstance(groups, list) or not all(isinstance(g, dict) for g in groups):
            lf.problem(lf.line(None, "group") or lf.line("group"),
                       "each group is a [[group]] table with differ_by and calibres")
            groups = []
        grouped, titles = {}, {}
        owners = {}  # a calibre's name, aliases and display aliases, lower case: the calibre
        for n, (_, raw, *_rest) in by_name.items():
            for other in [n] + [a for k in ("aliases", "display_aliases") if _is_text_list(raw.get(k))
                                for a in raw[k]]:
                owners.setdefault(other.lower(), n)
        for i, g in enumerate(groups):
            def at(key=None, i=i):
                return lf.line("group", key, nth=i) or lf.line("group", nth=i) or lf.line(None, "group")
            for k in g:
                if k not in GROUP_KEYS:
                    lf.problem(at(k), f"unknown key {k!r} in [[group]]{_close(k, GROUP_KEYS)}; "
                                      "allowed: calibres, differ_by, name")
            for k in GROUP_KEYS:
                if k not in g:
                    lf.problem(at(), f"[[group]] needs {k!r}")
            title, diff, names = g.get("name"), g.get("differ_by"), g.get("calibres")
            named = isinstance(title, str) and title.strip() == title != ""
            if "name" in g and not named:
                lf.problem(at("name"), "name is the group's name, as text without spaces around it")
            elif "name" in g:
                owner = owners.get(title.lower())
                if title.lower() in titles:
                    lf.problem(at("name"), f"name {title!r} is already the name of the group on line "
                                           f"{titles[title.lower()]}")
                elif owner and not (_is_text_list(names) and owner in names):
                    lf.problem(at("name"), f"name {title!r} names the calibre {owner!r}, which is not in this group")
                titles[title.lower()] = at()
            if "differ_by" in g:
                bad = [x for x in diff if x not in DIFFER_BY] if _is_text_list(diff) else [diff]
                if bad or not diff:
                    lf.problem(at("differ_by"), f"differ_by lists one or more of {', '.join(DIFFER_BY)}"
                                                f"{_close(bad[0], DIFFER_BY) if bad else ''}")
                    continue
            if "calibres" in g and (not _is_text_list(names) or len(names) < 2):
                lf.problem(at("calibres"), "calibres lists two or more calibre names, the parent first")
                continue
            if "differ_by" not in g or "calibres" not in g:
                continue
            for n in names:
                if n not in by_name and has_file(n):
                    pass
                elif n not in by_name:
                    lf.problem(at("calibres"), f"{n!r} is not a calibre{_close(n, by_name)}")
                elif n in grouped:
                    lf.problem(at("calibres"), f"{n!r} is already in the group on line {grouped[n]}")
                elif by_name[n][0] in NOT_IN_APPS:
                    lf.problem(at("calibres"), f"{n!r} is a {by_name[n][0]} calibre, which the apps do not show yet")
                else:
                    grouped[n] = at()
            if named:  # otherwise reported above
                lookalikes.append((tuple(diff), list(names)))
                group_names.append(title)

    if problems:
        raise DataError(sorted(problems, key=lambda p: (p[0], p[1] or 0)))

    t = {k: {} for k in ("DISPLAY_ALIASES", "PRIMERS", "PRIMER_MM", "PRIMER_SOURCES", "INTRODUCED", "INTRODUCED_UNKNOWN",
                         "SHOULDER_ANGLES", "CASE_HEADS", "RIM_THICKNESS", "ORIGIN", "ORIGIN_UNDECIDED", "ORIGIN_SOURCES", "BULLETS", "JACKETS", "CASES",
                         "CURRENT_CASES", "SOURCES", "COLOUR_CODES", "FIRED_BY", "CALIBRE_CATEGORIES",
                         "PROFILE_TODAY")}
    sets = {k: set() for k in ("PRIMER_UNVERIFIED", "OBSOLETE", "RARE", "WORLDWIDE", "BULLET_INFERRED",
                               "ORIGIN_UNVERIFIED")}
    for _, items in catalogue:
        for e in items:
            n = e["name"]
            _, raw, facts, _ = by_name[n]
            t["CALIBRE_CATEGORIES"][n] = tuple(CATEGORIES[c] for c in raw["categories"])
            if "display_aliases" in raw:
                t["DISPLAY_ALIASES"][n] = list(raw["display_aliases"])
            for flag in ("obsolete", "rare", "worldwide"):
                if raw.get(flag):
                    sets[flag.upper()].add(n)
            if "origin" in raw:
                t["ORIGIN"][n] = raw["origin"]
            if "profile_today" in raw:
                t["PROFILE_TODAY"][n] = raw["profile_today"]
            if "origin_candidates" in raw:
                t["ORIGIN_UNDECIDED"][n] = tuple(raw["origin_candidates"])
            if "origin_sources" in raw:
                t["SOURCES"][(n, "origin")] = list(raw["origin_sources"])
                if raw["origin_sources"]:
                    t["ORIGIN_SOURCES"][n] = raw["origin_sources"][0]
                else:
                    sets["ORIGIN_UNVERIFIED"].add(n)
            for fact, data in facts.items():
                t["SOURCES"][(n, fact)] = list(data["sources"])
            first = lambda fact: facts[fact]["sources"][0] if facts[fact]["sources"] else None  # noqa: E731
            i = facts["introduced"]
            if "year" in i:
                t["INTRODUCED"][n] = (i["year"], first("introduced"))
            else:
                t["INTRODUCED_UNKNOWN"][n] = i["unknown"]
            if "primer" in facts:
                t["PRIMERS"][n] = facts["primer"]["size"]
                t["PRIMER_MM"][n] = facts["primer"].get("diameter") or PRIMER_DIAMETERS[facts["primer"]["size"]]
                if facts["primer"]["sources"]:
                    t["PRIMER_SOURCES"][n] = first("primer")
                else:
                    sets["PRIMER_UNVERIFIED"].add(n)
            if "shoulder_angle" in facts:
                t["SHOULDER_ANGLES"][n] = (facts["shoulder_angle"]["degrees"], first("shoulder_angle"))
            if "case_head" in facts:
                h = facts["case_head"]
                t["RIM_THICKNESS"][n] = (h["rim_thickness"], first("case_head"))
                if "ramp_top" in h:
                    t["CASE_HEADS"][n] = (h["rim_thickness"], h["ramp_top"], h["groove_diameter"], h["ramp_angle"],
                                          first("case_head"))
            if "bullet" in facts:
                t["BULLETS"][n] = (facts["bullet"]["type"], first("bullet"))
                if "jacket" in facts["bullet"]:
                    t["JACKETS"][n] = facts["bullet"]["jacket"]
                if not facts["bullet"]["sources"] and facts["bullet"]["type"] != (LEAD if e["kind"] in LOOSE else JACKETED):
                    sets["BULLET_INFERRED"].add(n)
            if "case" in facts:
                t["CASES"][n] = (facts["case"]["material"], first("case"))
            if "current_cases" in facts:
                t["CURRENT_CASES"][n] = (tuple(facts["current_cases"]["materials"]), first("current_cases"))
            if "fired_by" in facts:
                t["FIRED_BY"][n] = (tuple(facts["fired_by"]["firearms"]), first("fired_by"))
            if "colour_codes" in raw:
                t["COLOUR_CODES"][n] = [{"part": c["part"], "colours": tuple(c["colours"]), "meaning": tuple(c["meaning"]),
                                         "description": c.get("description"),
                                         "countries": tuple(c.get("countries", ())),
                                         "sources": list(c["sources"])} for c in raw["colour_codes"]]
    t.update(sets)
    t["WORLDWIDE"] = frozenset(t["WORLDWIDE"])
    hidden = {CATEGORIES[cat] for cat in NOT_IN_APPS}
    t.update(CATALOGUE=[(cat, items) for cat, items in catalogue if cat not in hidden], ALL_CATALOGUE=catalogue,
             COUNTRIES=countries, COUNTRY_NAMES=country_names, BOOKS=books or {}, LOOKALIKES=lookalikes,
             LOOKALIKE_NAMES=group_names)
    return t


_t = load()

# The catalogue: [(category, [calibre dicts])] in the order of order.toml, each calibre under its
# primary category (the first of its categories), each category by the name the apps know it by
# (CATEGORIES: "Randfeuer" for rimfire). Each dict has name, kind,
# rim, base, shoulder (None for straight cases), neck, case (length), sh_at (where the shoulder
# starts, None for straight cases), oal, bullet (diameters and lengths in mm), profile and aliases.
CATALOGUE = _t["CATALOGUE"]
# CATALOGUE and the categories not yet in the apps (NOT_IN_APPS), whose dicts can have None for a
# measurement no source gives.
ALL_CATALOGUE = _t["ALL_CATALOGUE"]
# {name: (categories by the apps' names, the primary one first)}: every calibre of ALL_CATALOGUE, also
# in the categories it is not listed under.
CALIBRE_CATEGORIES = _t["CALIBRE_CATEGORIES"]
# Printable alternative names (max 2), shown in the app's calibre lists and search, and on the poster.
DISPLAY_ALIASES = _t["DISPLAY_ALIASES"]
# Primer size per centrefire calibre; PRIMER_SOURCES has the first source of the checked ones,
# PRIMER_UNVERIFIED the ones not checked yet.
PRIMERS, PRIMER_SOURCES, PRIMER_UNVERIFIED = _t["PRIMERS"], _t["PRIMER_SOURCES"], _t["PRIMER_UNVERIFIED"]
# Primer diameter in mm per centrefire calibre: the file's measured diameter, else PRIMER_DIAMETERS of its size.
PRIMER_MM = _t["PRIMER_MM"]
# {name: (year, first source)}; calibres without a year are in INTRODUCED_UNKNOWN with the reason.
INTRODUCED, INTRODUCED_UNKNOWN = _t["INTRODUCED"], _t["INTRODUCED_UNKNOWN"]
# {name: (degrees from the case axis, first source)} for bottleneck cases.
SHOULDER_ANGLES = _t["SHOULDER_ANGLES"]
# {name: (rim thickness R, ramp top E, groove diameter E1, ramp angle delta, first source)}: rimless and
# belted cases with their whole head.
CASE_HEADS = _t["CASE_HEADS"]
# {name: (rim thickness, first source)}: every case with a [case_head], CASE_HEADS' ones too.
RIM_THICKNESS = _t["RIM_THICKNESS"]
OBSOLETE, RARE, WORLDWIDE = _t["OBSOLETE"], _t["RARE"], _t["WORLDWIDE"]
COUNTRIES = _t["COUNTRIES"]  # code: (English name, flag emoji or None)
# code: {"en", "de", "fr", "it"}: the country's name in the apps' languages (Kaliberfinder's
# generator reads it, 2026-11-12; the German name is the app's localization key).
COUNTRY_NAMES = _t["COUNTRY_NAMES"]
ORIGIN, ORIGIN_UNDECIDED = _t["ORIGIN"], _t["ORIGIN_UNDECIDED"]  # {name: code}, {name: (codes, likelier first)}
# The first page naming each calibre's origin (ORIGIN or ORIGIN_UNDECIDED); ORIGIN_UNVERIFIED the
# calibres whose origin_sources are still empty.
ORIGIN_SOURCES, ORIGIN_UNVERIFIED = _t["ORIGIN_SOURCES"], _t["ORIGIN_UNVERIFIED"]
# {name: (bullet, first source or None)}: every calibre with a bullet (not shot shells, blanks or cannon
# rounds); no source means not checked.
BULLETS = _t["BULLETS"]
# Unchecked bullets other than the usual one (a jacket; lead for balls, Minié bullets and pellets), such
# as hunting rounds whose sources give no bullet: soft point from their use.
BULLET_INFERRED = _t["BULLET_INFERRED"]
JACKETS = _t["JACKETS"]  # {name: CUPRONICKEL or STEEL}: jackets that are not copper-coloured
CASES = _t["CASES"]  # {name: (material, first source)}
CURRENT_CASES = _t["CURRENT_CASES"]  # {name: (other case materials made today, first source)}
LOOKALIKES = _t["LOOKALIKES"]  # [(what tells them apart, calibres)], in the file's order
LOOKALIKE_NAMES = _t["LOOKALIKE_NAMES"]  # each group's name, in the same order
SOURCES = _t["SOURCES"]  # {(name, table): [every source]}
BOOKS = _t["BOOKS"]  # {book id: its table in books.toml}: the books a source "book:<id> p. <page>" names
# {name: [{part, colours, meaning, description or None, countries, sources}]}: what a painted bullet tip,
# cartridge base or primer annulus means, from the [[colour_codes]] tables (part "tip", "base" or "annulus"; a tip's colours from
# the tip down). Kaliberfinder's generator reads it for the
# calibre page (2026-11-11); the sources stay here.
COLOUR_CODES = _t["COLOUR_CODES"]
# {name: (firearms that fire it, first source)}: the firearms that define a round, mostly old and
# obsolete ones. For the catalogue only; the apps do not read it.
FIRED_BY = _t["FIRED_BY"]
# {name: profile}: the nose of today's usual load where it is not the one first sold (profile). For the
# catalogue only; the apps draw profile.
PROFILE_TODAY = _t["PROFILE_TODAY"]


def sources(name, fact):
    """Every source of one of a calibre's values, as listed in its file: fact is the table name
    ("mm", "introduced", "primer", "shoulder_angle", "case_head", "bullet", "case", "current_cases"
    or "fired_by"), or "origin" for origin_sources; [] when nothing is checked yet or the calibre has no
    such table."""
    return list(SOURCES.get((name, fact), []))


def shoulder_angle(name):
    """Half cone angle of the shoulder in degrees (sourced, or the default)."""
    entry = SHOULDER_ANGLES.get(name)
    return entry[0] if entry else DEFAULT_SHOULDER_ANGLE


def case_head(name):
    """(rim thickness, ramp top or belt front, groove diameter, ramp angle) or None."""
    entry = CASE_HEADS.get(name)
    return entry[:4] if entry else None


def rim_thickness(name):
    """The rim's thickness in mm, or None where no source gives it."""
    entry = RIM_THICKNESS.get(name)
    return entry[0] if entry else None


def categories(name):
    """A calibre's categories by the apps' names, the primary one first: ("Langwaffe",) for .308 Winchester;
    () for a name that is not a calibre."""
    return CALIBRE_CATEGORIES.get(name, ())


def is_obsolete(name):
    return name in OBSOLETE


def is_rare(name):
    return name in RARE


def tags(name):
    """The status tags of a calibre: [], ["obsolete"], ["rare"] or ["obsolete", "rare"]."""
    return [t for t, s in (("obsolete", OBSOLETE), ("rare", RARE)) if name in s]


def origin(name):
    """(code, English name, flag emoji or None) of the state that introduced a calibre, or None (not a
    single cartridge, or still open in ORIGIN_UNDECIDED, see origin_candidates). Worldwide use is
    separate: is_worldwide."""
    code = ORIGIN.get(name)
    return (code, *COUNTRIES[code]) if code else None


def origin_candidates(name):
    """The states that can claim a calibre whose origin is still open, likelier first, as
    (code, English name, flag emoji or None) tuples; () when origin() answers or nothing is known."""
    return tuple((code, *COUNTRIES[code]) for code in ORIGIN_UNDECIDED.get(name, ()))


def is_worldwide(name):
    """True for a calibre in common use worldwide (WORLDWIDE); independent of origin()."""
    return name in WORLDWIDE


def bullet(name):
    """The original bullet of a calibre: JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP, HOLLOW_POINT or
    STEEL (LEAD, STEEL or PLASTIC for balls, Minié bullets and pellets); None for shot shells, blanks and
    cannon rounds."""
    return BULLETS.get(name, (None, None))[0]


def jacket(name):
    """What the original bullet's jacket looks like: COPPER, CUPRONICKEL or STEEL; None for a bullet with
    no jacket (lead, paper-patched, steel, or none at all)."""
    if bullet(name) not in JACKETED_BULLETS:
        return None
    return JACKETS.get(name, COPPER)


def case_material(name):
    """What the case is made of: BRASS, COPPER, STEEL, NICKEL, ALUMINIUM, PAPER or HYBRID."""
    return CASES.get(name, (BRASS, None))[0]


def current_case_materials(name):
    """Case materials made today besides the original one, e.g. (BRASS,) for the .45-70."""
    return CURRENT_CASES.get(name, ((), None))[0]


def loose_material(name):
    """What a ball, Minié bullet or pellet is made of: LEAD, STEEL or PLASTIC (its [bullet] type)."""
    return bullet(name)


def lookalikes(name):
    """The other calibres of `name`'s lookalike group, parent first; [] when it has none."""
    for _, names in LOOKALIKES:
        if name in names:
            return [n for n in names if n != name]
    return []
