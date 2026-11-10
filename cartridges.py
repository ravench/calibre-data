"""Calibre catalogue with approximate cartridge dimensions (mm, CIP/SAAMI-ish).

Shared by Schiesstagebuch, Kaliberfinder and the calibre wall poster (each pins this
repository as a git submodule); outline.py draws the side view of every calibre.
Dimensions are approximations for drawings and matching, not reloading data.

The data lives in TOML files: one per calibre in calibres/<category>/, plus order.toml,
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
RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET = (
    "rimless", "rimmed", "belted", "rimfire", "shot", "ball", "minie", "pellet")
KINDS = (RIMLESS, RIMMED, BELTED, RIMFIRE, SHOT, BALL, MINIE, PELLET)
LOOSE = (BALL, MINIE, PELLET)  # loose projectiles, not cartridges
# Bullet profiles. PATCHED: paper-patched lead body with a steel-capped round nose (GP 1890).
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
# Categories: the folder in calibres/ (and key in order.toml) -> the name the apps and the poster
# know the category by. Those names are German because the apps show them (translated); the apps
# know only these six, so a new category needs a change in the apps too.
CATEGORIES = {"rimfire": "Randfeuer", "handgun": "Kurzwaffe", "rifle": "Langwaffe",
              "black-powder": "Schwarzpulver", "shotgun": "Flinte", "air-gun": "Luftdruck"}


def c(name, kind, rim, base, shoulder, neck, case, sh_at, oal, bullet, profile, aliases=()):
    return dict(name=name, kind=kind, rim=rim, base=base, shoulder=shoulder, neck=neck,
                case=case, sh_at=sh_at, oal=oal, bullet=bullet, profile=profile, aliases=list(aliases))


def straight(name, kind, rim, base, neck, case, oal, bullet, profile, aliases=()):
    return c(name, kind, rim, base, None, neck, case, None, oal, bullet, profile, aliases)


def blank(name, rim, base, mouth, length, aliases=(), kind=RIMFIRE):
    """A crimped blank: no bullet, the case (`length` long) narrows to `mouth` at the star crimp.
    `bullet` holds the nominal bore so drawings and tables keep a width."""
    return c(name, kind, rim, base, None, mouth, length, None, length, base, CRIMPED, aliases)


def shot(name, dia, rim, length, aliases=()):
    return c(name, SHOT, rim, dia, None, dia, length, None, length, dia, FLAT, aliases)


def ball(name, dia, aliases=()):
    return c(name, BALL, dia, dia, None, dia, 0, None, dia, dia, ROUND, aliases)


def minie(name, dia, length, aliases=()):
    return c(name, MINIE, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


def pellet(name, dia, length, aliases=()):
    return c(name, PELLET, dia, dia, None, dia, 0, None, length, dia, ROUND, aliases)


# Primer per calibre: the primer of the original factory ammunition, which is today's Boxer size
# for calibres still loaded. Primers sit in the centre of the case head. Old British Nitro
# Expresses and some old European rounds came with the large .254" Berdan "Nitro" primer
# (Kynoch #40, today RWS 6507), measured on headstamp photos (see PRIMER_SOURCES). Other Berdan
# primers (4.5 and 5.5 mm, e.g. 7.62x39, 7.62x54R surplus) are within 0.2 mm of a Boxer size and
# keep that kind; rimfire and caseless entries have none.
SMALL_PISTOL, LARGE_PISTOL, SMALL_RIFLE, LARGE_RIFLE, SHOTSHELL_209, BMG_35, BERDAN_NITRO = (
    "small-pistol", "large-pistol", "small-rifle", "large-rifle", "shotshell-209", "bmg-35",
    "berdan-nitro")
PRIMER_DIAMETERS = {  # mm, nominal primer cup diameter
    SMALL_PISTOL: 4.45, SMALL_RIFLE: 4.45,     # .175"
    LARGE_PISTOL: 5.33, LARGE_RIFLE: 5.33,     # .210"
    SHOTSHELL_209: 6.15,                       # .242"
    BMG_35: 8.03,                              # .316", CCI #35
    BERDAN_NITRO: 6.45,                        # .254", Kynoch #40 / RWS 6507
}

# Bottleneck cases without a sourced shoulder angle are drawn at this one.
DEFAULT_SHOULDER_ANGLE = 32

# Original bullets (a calibre without [bullet] had a full metal jacket or another all-copper bullet).
JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP = "jacketed", "lead", "paper", "softpoint", "polymer"
# Case and projectile materials (a calibre without [case] has a brass case; a ball, Minié bullet or
# pellet without [projectile] is lead).
BRASS, COPPER, STEEL, NICKEL, PAPER, HYBRID = "brass", "copper", "steel", "nickel", "paper", "hybrid"
PLASTIC = "plastic"
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
    run of other characters a hyphen (".22 LR" is 22-lr.toml, "3¼ inch" 3-1-4-inch)."""
    s = unicodedata.normalize("NFKD", name.replace("¼", " 1/4")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# Measurements by shape: the short forms of balls, Minié bullets, pellets, shot shells and crimped
# blanks, and the full form of every other cartridge (shoulder and shoulder_at only for bottlenecks).
MM_FULL = ("rim", "base", "shoulder", "shoulder_at", "neck", "case_length", "overall_length", "bullet")
MM_SHAPES = {  # shape: (required keys, optional keys)
    "ball": (("diameter",), ()),
    "loose": (("diameter", "length"), ()),
    "shot": (("diameter", "rim", "length"), ()),
    "blank": (("rim", "base", "mouth", "length"), ()),
    "cartridge": (("rim", "base", "neck", "case_length", "overall_length", "bullet"), ("shoulder", "shoulder_at")),
}
TOP_KEYS = {"name", "kind", "profile", "aliases", "display_aliases", "origin", "origin_candidates",
            "worldwide", "obsolete", "rare"}
FACTS = {  # table: (required keys, optional keys, sources: "required", "optional" or "may be empty")
    "mm": ((), (), "may be empty"),  # keys by shape, above
    "introduced": ((), ("year", "unknown"), "optional"),
    "primer": (("size",), (), "may be empty"),
    "shoulder_angle": (("degrees",), (), "required"),
    "case_head": (("rim_thickness", "ramp_top", "groove_diameter", "ramp_angle"), (), "required"),
    "bullet": (("type",), (), "may be empty"),
    "case": (("material",), (), "required"),
    "current_cases": (("materials",), (), "required"),
    "projectile": (("material",), (), "required"),
    "fired_by": (("firearms",), (), "required"),
}
BULLET_TYPES = (LEAD, PAPER_PATCHED, SOFT_POINT, POLYMER_TIP)
CASE_MATERIALS = (COPPER, STEEL, NICKEL, PAPER, HYBRID)
CURRENT_CASE_MATERIALS = (BRASS, COPPER, STEEL, NICKEL)
PROJECTILE_MATERIALS = (STEEL, PLASTIC)
DIFFER_BY = (RIM, BORE, LENGTH, SEATING, LOAD, IGNITION)
# A printed book as a source: "book:<id> p. <page>", the id of a book in books.toml.
BOOK_SOURCE = re.compile(r"book:(?P<id>[^\s]+) p\. (?P<page>[1-9][0-9]*)")
BOOK_KEYS = ("title", "year", "edition", "authors", "editors", "publisher", "place", "isbn")
# [[tip_colours]]: what a coloured bullet tip means, a table for each code. Colours are listed from
# the tip down (["red", "silver"]: a red tip above a silver band); the meanings combine (["armour-piercing",
# "incendiary"] is an API round).
TIP_KEYS = (("colours", "meaning", "sources"), ("description", "countries"))  # (required, optional)
COLOURS = ("black", "white", "grey", "silver", "red", "orange", "yellow", "green", "blue", "purple", "brown")
MEANINGS = ("ball", "armour-piercing", "incendiary", "explosive", "tracer", "spotting", "subsonic", "frangible")


def _shape(kind, profile):
    if kind == BALL:
        return "ball"
    if kind in (MINIE, PELLET):
        return "loose"
    if kind == SHOT:
        return "shot"
    return "blank" if profile == CRIMPED else "cartridge"


def _entry(name, kind, profile, aliases, m):
    """The catalogue dict of a calibre, built by the helper of its shape."""
    shape = _shape(kind, profile)
    if shape == "ball":
        return ball(name, m["diameter"], aliases)
    if shape == "loose":
        return (minie if kind == MINIE else pellet)(name, m["diameter"], m["length"], aliases)
    if shape == "shot":
        return shot(name, m["diameter"], m["rim"], m["length"], aliases)
    if shape == "blank":
        return blank(name, m["rim"], m["base"], m["mouth"], m["length"], aliases, kind=kind)
    return c(name, kind, m["rim"], m["base"], m.get("shoulder"), m["neck"], m["case_length"], m.get("shoulder_at"),
             m["overall_length"], m["bullet"], profile, aliases)


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


def _check_sources(f, table, data, rule, books=None, nth=0):
    """The sources of one table (the `nth` of a [[table]]): web addresses and book pages (`books`: the
    ids in books.toml, or None when books.toml could not be read)."""
    label = f"[[{table}]]" if table == "tip_colours" else f"[{table}]"
    if "sources" not in data:
        if rule != "optional":
            f.problem(f.line(table, nth=nth), f"{label} needs a sources list (an empty list [] when nothing is checked yet)"
                      if rule == "may be empty" else f"{label} needs sources = [\"https://…\"]")
        return []
    urls = data["sources"]
    if not _is_text_list(urls):
        f.problem(f.line(table, "sources", nth), f"{label} sources must be a list of web addresses in quotes")
        return []
    if rule == "required" and not urls:
        f.problem(f.line(table, "sources", nth), f"{label} needs at least one source")
    for u in urls:
        book = BOOK_SOURCE.fullmatch(u)
        if book:
            if books is not None and book["id"] not in books:
                f.problem(f.line(table, "sources", nth), f"{label} source {u!r} names no book in books.toml"
                                                    f"{_close(book['id'], books)}")
        elif u.startswith("book:"):
            f.problem(f.line(table, "sources", nth), f"{label} source {u!r} must be written book:<id> p. <page>, "
                                                f"e.g. \"book:cotw-18 p. 176\"")
        elif not re.fullmatch(r"https://[^\s\"<>]+\.[^\s\"<>]+", u):
            f.problem(f.line(table, "sources", nth), f"{label} source {u!r} is not a https:// web address "
                                                f"or a book page (book:<id> p. <page>)")
    if len(set(urls)) != len(urls):
        f.problem(f.line(table, "sources", nth), f"{label} lists a source twice")
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


def _check_tip_colours(f, tips, shape, countries, books):
    """Check a calibre's [[tip_colours]] tables (`shape`: its shape in MM_SHAPES)."""
    if not isinstance(tips, list) or not tips or not all(isinstance(t, dict) for t in tips):
        f.problem(f.line(None, "tip_colours") or f.line("tip_colours"),
                  "each tip colour is a [[tip_colours]] table with colours, meaning and sources")
        return
    if shape != "cartridge":
        f.problem(f.line("tip_colours"), "[[tip_colours]] is only for cartridges with a bullet")
    req, opt = TIP_KEYS
    seen = {}
    for i, t in enumerate(tips):
        def at(key=None, i=i):
            return f.line("tip_colours", key, nth=i) or f.line("tip_colours", nth=i)
        for k in t:
            if k not in req + opt:
                f.problem(at(k), f"unknown key {k!r} in [[tip_colours]]{_close(k, req + opt)}; "
                                 f"allowed: {', '.join(sorted(req + opt))}")
        for k in req:
            if k not in t and k != "sources":  # _check_sources reports that
                f.problem(at(), f"[[tip_colours]] needs {k!r}")
        _check_sources(f, "tip_colours", t, "required", books, nth=i)
        for k, choices in (("colours", COLOURS), ("meaning", MEANINGS)):
            if k not in t:
                continue
            bad = [x for x in t[k] if x not in choices] if _is_text_list(t[k]) else [t[k]]
            if bad or not t[k]:
                f.problem(at(k), f"[[tip_colours]] {k} lists one or more of {', '.join(choices)}"
                                 f"{_close(bad[0], choices) if bad else ''}")
            elif len(set(t[k])) != len(t[k]):
                f.problem(at(k), f"[[tip_colours]] {k} lists {next(x for x in t[k] if t[k].count(x) > 1)!r} twice")
        if "description" in t and (not isinstance(t["description"], str) or not t["description"].strip()):
            f.problem(at("description"), "[[tip_colours]] description must be text in quotes")
        if "countries" in t:
            codes = t["countries"]
            if not _is_text_list(codes) or not codes:
                f.problem(at("countries"), "[[tip_colours]] countries lists one or more country codes")
            elif len(set(codes)) != len(codes):
                f.problem(at("countries"), "[[tip_colours]] countries lists a country twice")
            elif countries is not None:
                for code in codes:
                    if code not in countries:
                        f.problem(at("countries"), f"[[tip_colours]] country {code!r} is not a code in "
                                                   f"countries.toml{_close(code, countries)}")
        if _is_text_list(t.get("colours")) and _is_text_list(t.get("meaning")):
            key = (tuple(t["colours"]), frozenset(t["meaning"]))
            if key in seen:
                f.problem(at("colours"), f"[[tip_colours]] {' over '.join(t['colours'])} with this meaning is "
                                         f"already on line {seen[key]}: list all its countries there")
            seen.setdefault(key, at())


def _read_calibre(f, category, countries, books=None):
    """Check one calibre file; returns (entry dict, facts) or None when it cannot be used."""
    d = f.data
    tables = {k for k, v in d.items() if isinstance(v, dict) and k != "tip_colours"}
    top = {k for k in d if k not in tables and k != "tip_colours"}
    _check_keys(f, None, {k: d[k] for k in top}, TOP_KEYS, ("name", "kind", "profile", "aliases"))
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
    if kind not in KINDS:
        f.problem(f.line(None, "kind"), f"kind {kind!r} is not one of {', '.join(KINDS)}{_close(kind, KINDS)}")
    if profile not in PROFILES:
        f.problem(f.line(None, "profile"),
                  f"profile {profile!r} is not one of {', '.join(PROFILES)}{_close(profile, PROFILES)}")
    for k in ("aliases", "display_aliases"):
        if k in d and not _is_text_list(d[k]):
            f.problem(f.line(None, k), f"{k} must be a list of texts in quotes")
    if _is_text_list(d.get("aliases")) and len(set(d["aliases"])) != len(d["aliases"]):
        f.problem(f.line(None, "aliases"), "aliases lists a name twice")
    if _is_text_list(d.get("display_aliases")) and not 1 <= len(d["display_aliases"]) <= 2:
        f.problem(f.line(None, "display_aliases"), "display_aliases holds one or two names")
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
    if kind not in KINDS or profile not in PROFILES or "mm" not in tables:
        return None

    facts = {}
    ok = True
    for t in tables & set(FACTS):
        data = d[t]
        req, opt, rule = FACTS[t]
        if t == "mm":
            req, opt = MM_SHAPES[_shape(kind, profile)]
            if _shape(kind, profile) == "cartridge" and ("shoulder" in data) != ("shoulder_at" in data):
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
        enums = {("primer", "size"): tuple(PRIMER_DIAMETERS), ("bullet", "type"): BULLET_TYPES,
                 ("case", "material"): CASE_MATERIALS, ("projectile", "material"): PROJECTILE_MATERIALS}
        for (tt, k), allowed_values in enums.items():
            if t == tt and k in data and data[k] not in allowed_values:
                hint = {"bullet": " (leave [bullet] out for a full metal jacket)",
                        "case": " (leave [case] out for brass)", "projectile": " (leave [projectile] out for lead)"}
                f.problem(f.line(t, k), f"[{t}] {k} {data[k]!r} is not one of {', '.join(allowed_values)}"
                                        f"{_close(data[k], allowed_values)}{hint.get(t, '')}")
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
    if "tip_colours" in d:
        _check_tip_colours(f, d["tip_colours"], _shape(kind, profile), countries, books)
    if not ok:
        return None
    if kind in (RIMFIRE,) + LOOSE:
        if "primer" in facts:
            f.problem(f.line("primer"), f"a {kind} calibre has no primer: remove [primer]")
    elif "primer" not in facts:
        f.problem(None, "a centrefire calibre needs a [primer] table (size and sources, or sources = [] if not checked)")
    if "projectile" in facts and kind not in LOOSE:
        f.problem(f.line("projectile"), "[projectile] is only for balls, Minié bullets and pellets")
    aliases = d.get("aliases", []) if _is_text_list(d.get("aliases")) else []
    entry = _entry(name, kind, profile, aliases, facts["mm"])
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

    countries = {}
    before = len(problems)
    cf = read("countries.toml")
    if cf:
        if not cf.data:
            cf.problem(None, "lists no countries")
        for code, v in cf.data.items():
            if not isinstance(v, dict) or not isinstance(v.get("name"), str):
                cf.problem(cf.line(code), f"[{code}] needs name = \"…\"")
                continue
            _check_keys(cf, code, v, {"name", "flag"}, ("name",))
            if "flag" in v and not isinstance(v["flag"], str):
                cf.problem(cf.line(code, "flag"), f"[{code}] flag must be the flag emoji in quotes")
            countries[code] = (v["name"], v.get("flag"))
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
                folder = {app: folder for folder, app in CATEGORIES.items()}.get(cat)
                hint = f" (the folder of {cat} is {folder})" if folder else _close(cat, CATEGORIES)
                of.problem(of.line(None, cat), f"category {cat!r} is not one of {', '.join(CATEGORIES)}{hint}")
                continue
            if not _is_text_list(names):
                of.problem(of.line(None, cat), f"{cat} must be a list of calibre names in quotes")
                continue
            order[cat] = names

    found = {}  # category -> [(entry, raw, facts, file)]
    folders = []
    cal_dir = os.path.join(root, "calibres")
    if not os.path.isdir(cal_dir):
        problems.append(("calibres", None, "missing: the folder with one folder of calibre files per category"))
    for cat in sorted(os.listdir(cal_dir)) if os.path.isdir(cal_dir) else []:
        if cat.startswith("."):  # .DS_Store and other hidden files
            continue
        if not os.path.isdir(os.path.join(cal_dir, cat)):
            problems.append((f"calibres/{cat}", None, "only folders (one per category) belong in calibres/"))
            continue
        folders.append(cat)
        if of and cat not in of.data:
            problems.append((f"calibres/{cat}", None, f"category {cat!r} is not in order.toml"
                                                      f"{_close(cat, of.data)}"))
            continue
        if cat not in CATEGORIES:  # reported at its order.toml key (once order.toml reads); files stay out
            continue
        for fn in sorted(os.listdir(os.path.join(cal_dir, cat))):
            rel = f"calibres/{cat}/{fn}"
            if fn.startswith("."):
                continue
            if not fn.endswith(".toml"):
                problems.append((rel, None, "only .toml files belong here"))
                continue
            f = read(rel)
            if f is None:
                continue
            got = _read_calibre(f, cat, countries, books)
            if got:
                found.setdefault(cat, []).append((*got, f))

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
    def has_file(cat, n):  # also a file with a problem of its own, so it is not reported twice
        return os.path.exists(os.path.join(cal_dir, cat, slug(n) + ".toml"))

    catalogue = []
    for cat, names in order.items():
        if not os.path.isdir(os.path.join(cal_dir, cat)):
            of.problem(of.line(None, cat), f"category {cat!r} has no folder calibres/{cat}/{_close(cat, folders)}")
            continue
        files = {e["name"]: e for e, *_ in found.get(cat, [])}
        listed = []
        for n in names:
            if n in listed:
                of.problem(of.line(None, cat), f"{n!r} is listed twice")
            elif n not in files and has_file(cat, n):
                pass
            elif n not in files:
                where = by_name.get(n)
                of.problem(of.line(None, cat), f"{n!r} has no file in calibres/{cat}/" +
                           (f" (it is in calibres/{where[0]}/)" if where else _close(n, files)))
            else:
                listed.append(n)
        rest = sorted(n for n in files if n not in listed)
        catalogue.append((CATEGORIES[cat], [files[n] for n in listed + rest]))

    lookalikes = []
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
        grouped = {}
        for i, g in enumerate(groups):
            def at(key=None, i=i):
                return lf.line("group", key, nth=i) or lf.line("group", nth=i) or lf.line(None, "group")
            for k in g:
                if k not in ("differ_by", "calibres"):
                    lf.problem(at(k), f"unknown key {k!r} in [[group]]{_close(k, ('differ_by', 'calibres'))}; "
                                      "allowed: calibres, differ_by")
            for k in ("differ_by", "calibres"):
                if k not in g:
                    lf.problem(at(), f"[[group]] needs {k!r}")
            diff, names = g.get("differ_by"), g.get("calibres")
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
                if n not in by_name and any(has_file(cat, n) for cat in folders):
                    pass
                elif n not in by_name:
                    lf.problem(at("calibres"), f"{n!r} is not a calibre{_close(n, by_name)}")
                elif n in grouped:
                    lf.problem(at("calibres"), f"{n!r} is already in the group on line {grouped[n]}")
                else:
                    grouped[n] = at()
            lookalikes.append((tuple(diff), list(names)))

    if problems:
        raise DataError(sorted(problems, key=lambda p: (p[0], p[1] or 0)))

    t = {k: {} for k in ("DISPLAY_ALIASES", "PRIMERS", "PRIMER_SOURCES", "INTRODUCED", "INTRODUCED_UNKNOWN",
                         "SHOULDER_ANGLES", "CASE_HEADS", "ORIGIN", "ORIGIN_UNDECIDED", "BULLETS", "CASES",
                         "CURRENT_CASES", "LOOSE_MATERIALS", "SOURCES", "TIP_COLOURS", "FIRED_BY")}
    sets = {k: set() for k in ("PRIMER_UNVERIFIED", "OBSOLETE", "RARE", "WORLDWIDE")}
    for _, items in catalogue:
        for e in items:
            n = e["name"]
            _, raw, facts, _ = by_name[n]
            if "display_aliases" in raw:
                t["DISPLAY_ALIASES"][n] = list(raw["display_aliases"])
            for flag in ("obsolete", "rare", "worldwide"):
                if raw.get(flag):
                    sets[flag.upper()].add(n)
            if "origin" in raw:
                t["ORIGIN"][n] = raw["origin"]
            if "origin_candidates" in raw:
                t["ORIGIN_UNDECIDED"][n] = tuple(raw["origin_candidates"])
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
                if facts["primer"]["sources"]:
                    t["PRIMER_SOURCES"][n] = first("primer")
                else:
                    sets["PRIMER_UNVERIFIED"].add(n)
            if "shoulder_angle" in facts:
                t["SHOULDER_ANGLES"][n] = (facts["shoulder_angle"]["degrees"], first("shoulder_angle"))
            if "case_head" in facts:
                h = facts["case_head"]
                t["CASE_HEADS"][n] = (h["rim_thickness"], h["ramp_top"], h["groove_diameter"], h["ramp_angle"],
                                      first("case_head"))
            if "bullet" in facts:
                t["BULLETS"][n] = (facts["bullet"]["type"], first("bullet"))
            if "case" in facts:
                t["CASES"][n] = (facts["case"]["material"], first("case"))
            if "current_cases" in facts:
                t["CURRENT_CASES"][n] = (tuple(facts["current_cases"]["materials"]), first("current_cases"))
            if "projectile" in facts:
                t["LOOSE_MATERIALS"][n] = (facts["projectile"]["material"], first("projectile"))
            if "fired_by" in facts:
                t["FIRED_BY"][n] = (tuple(facts["fired_by"]["firearms"]), first("fired_by"))
            if "tip_colours" in raw:
                t["TIP_COLOURS"][n] = [{"colours": tuple(tip["colours"]), "meaning": tuple(tip["meaning"]),
                                        "description": tip.get("description"),
                                        "countries": tuple(tip.get("countries", ())),
                                        "sources": list(tip["sources"])} for tip in raw["tip_colours"]]
    t.update(sets)
    t["WORLDWIDE"] = frozenset(t["WORLDWIDE"])
    t.update(CATALOGUE=catalogue, COUNTRIES=countries, BOOKS=books or {}, LOOKALIKES=lookalikes)
    return t


_t = load()

# The catalogue: [(category, [calibre dicts])] in the order of order.toml, each category by the name
# the apps know it by (CATEGORIES: "Randfeuer" for the folder rimfire). Each dict has name, kind,
# rim, base, shoulder (None for straight cases), neck, case (length), sh_at (where the shoulder
# starts, None for straight cases), oal, bullet (diameters and lengths in mm), profile and aliases.
CATALOGUE = _t["CATALOGUE"]
# Printable alternative names (max 2), shown in the app's calibre lists and search, and on the poster.
DISPLAY_ALIASES = _t["DISPLAY_ALIASES"]
# Primer size per centrefire calibre; PRIMER_SOURCES has the first source of the checked ones,
# PRIMER_UNVERIFIED the ones not checked yet.
PRIMERS, PRIMER_SOURCES, PRIMER_UNVERIFIED = _t["PRIMERS"], _t["PRIMER_SOURCES"], _t["PRIMER_UNVERIFIED"]
# {name: (year, first source)}; calibres without a year are in INTRODUCED_UNKNOWN with the reason.
INTRODUCED, INTRODUCED_UNKNOWN = _t["INTRODUCED"], _t["INTRODUCED_UNKNOWN"]
# {name: (degrees from the case axis, first source)} for bottleneck cases.
SHOULDER_ANGLES = _t["SHOULDER_ANGLES"]
# {name: (rim thickness R, ramp top E, groove diameter E1, ramp angle delta, first source)}.
CASE_HEADS = _t["CASE_HEADS"]
OBSOLETE, RARE, WORLDWIDE = _t["OBSOLETE"], _t["RARE"], _t["WORLDWIDE"]
COUNTRIES = _t["COUNTRIES"]  # code: (English name, flag emoji or None)
ORIGIN, ORIGIN_UNDECIDED = _t["ORIGIN"], _t["ORIGIN_UNDECIDED"]  # {name: code}, {name: (codes, likelier first)}
BULLETS = _t["BULLETS"]  # {name: (bullet, first source or None)}
# Hunting rounds whose sources give no bullet: soft point from their use, not checked.
BULLET_INFERRED = {name for name, (_, url) in BULLETS.items() if url is None}
CASES = _t["CASES"]  # {name: (material, first source)}
CURRENT_CASES = _t["CURRENT_CASES"]  # {name: (other case materials made today, first source)}
LOOSE_MATERIALS = _t["LOOSE_MATERIALS"]  # {name: (material, first source)}
LOOKALIKES = _t["LOOKALIKES"]  # [(what tells them apart, calibres)], in the file's order
SOURCES = _t["SOURCES"]  # {(name, table): [every source]}
BOOKS = _t["BOOKS"]  # {book id: its table in books.toml}: the books a source "book:<id> p. <page>" names
# {name: [{colours, meaning, description or None, countries, sources}]}: what coloured bullet tips mean,
# from the [[tip_colours]] tables (colours from the tip down). For the catalogue only; the apps do not
# read it.
TIP_COLOURS = _t["TIP_COLOURS"]
# {name: (firearms that fire it, first source)}: the firearms that define a round, mostly old and
# obsolete ones. For the catalogue only; the apps do not read it.
FIRED_BY = _t["FIRED_BY"]


def sources(name, fact):
    """Every source of one of a calibre's values, as listed in its file: fact is the table name
    ("mm", "introduced", "primer", "shoulder_angle", "case_head", "bullet", "case", "current_cases",
    "projectile" or "fired_by"); [] when nothing is checked yet or the calibre has no such table."""
    return list(SOURCES.get((name, fact), []))


def shoulder_angle(name):
    """Half cone angle of the shoulder in degrees (sourced, or the default)."""
    entry = SHOULDER_ANGLES.get(name)
    return entry[0] if entry else DEFAULT_SHOULDER_ANGLE


def case_head(name):
    """(rim thickness, ramp top or belt front, groove diameter, ramp angle) or None."""
    entry = CASE_HEADS.get(name)
    return entry[:4] if entry else None


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
    """The original bullet of a calibre: JACKETED, LEAD, PAPER_PATCHED, SOFT_POINT or POLYMER_TIP."""
    return BULLETS.get(name, (JACKETED, None))[0]


def case_material(name):
    """What the case is made of: BRASS, COPPER, STEEL, NICKEL, PAPER or HYBRID."""
    return CASES.get(name, (BRASS, None))[0]


def current_case_materials(name):
    """Case materials made today besides the original one, e.g. (BRASS,) for the .45-70."""
    return CURRENT_CASES.get(name, ((), None))[0]


def loose_material(name):
    """What a ball, Minié bullet or pellet is made of: LEAD, STEEL or PLASTIC."""
    return LOOSE_MATERIALS.get(name, (LEAD, None))[0]


def lookalikes(name):
    """The other calibres of `name`'s lookalike group, parent first; [] when it has none."""
    for _, names in LOOKALIKES:
        if name in names:
            return [n for n in names if n != name]
    return []
