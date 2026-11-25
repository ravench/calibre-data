"""The TOML files and their checks: python3 -m unittest discover -s tests"""
import io, math, os, re, shutil, subprocess, sys, tempfile, tomllib, unittest
from contextlib import redirect_stdout

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import cartridges  # noqa: E402
import check  # noqa: E402
from cartridges import load, slug, DataError, sources  # noqa: E402

LR = "calibres/22-lr.toml"
LR_MM = ('sources = [\n  "https://saami.org/wp-content/uploads/2026/05/SAAMI-Z299.1-R2026-Rimfire-FINAL-Approved-2026-05-08.pdf#page=22",\n'
         '  "book:janes-ammo-2002 p. 681",\n  "book:cotw-18 p. 670",\n'
         '  "book:tm-43-0001-27 p. 3-5",\n]')  # the sources of .22 LR's [mm]
WIN = "calibres/308-winchester.toml"
KEY = {app: key for key, app in cartridges.CATEGORIES.items()}  # "Langwaffe": "rifle"
LOOK = "lookalikes.toml"
NATO_GROUP = 'name = "7.62x51 mm"\ndiffer_by = ["load"]\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]'
TIP = ('\n[[colour_codes]]\npart = "tip"\ncolours = ["black"]\nmeaning = ["armour-piercing"]\n'
       'sources = ["https://en.wikipedia.org/wiki/7.62×51mm_NATO"]\n')


class Copy:
    """A copy of the data files to break on purpose."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        shutil.copytree(os.path.join(ROOT, "calibres"), os.path.join(self.dir, "calibres"))
        for f in ("order.toml", "countries.toml", "books.toml", "lookalikes.toml"):
            shutil.copy(os.path.join(ROOT, f), self.dir)
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.dir)

    def path(self, rel):
        return os.path.join(self.dir, rel)

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return f.read()

    def write(self, rel, text):
        with open(self.path(rel), "w", encoding="utf-8") as f:
            f.write(text)

    def edit(self, rel, old, new):
        text = self.read(rel)
        assert old in text, (rel, old)
        self.write(rel, text.replace(old, new, 1))

    def line_of(self, rel, text):
        """The line number of the first line holding `text`."""
        return next(i for i, l in enumerate(self.read(rel).split("\n"), 1) if text in l)

    def problems(self):
        try:
            load(self.dir)
        except DataError as e:
            return e.problems
        return []


class LoadTests(unittest.TestCase):
    def test_the_files_have_no_problems(self):
        self.assertEqual(check.problems(), [])

    def test_every_calibre_file_is_named_after_its_calibre(self):
        for cat, items in cartridges.ALL_CATALOGUE:
            for s in items:
                with self.subTest(s["name"]):
                    self.assertTrue(os.path.exists(os.path.join(ROOT, "calibres", slug(s["name"]) + ".toml")))
                    self.assertEqual(cartridges.categories(s["name"])[0], cat)

    def test_slugs(self):
        self.assertEqual(slug(".22 LR"), "22-lr")
        self.assertEqual(slug(".450/400 Nitro Express 3¼ inch"), "450-400-nitro-express-3-1-4-inch")
        self.assertEqual(slug(".450/400 Nitro Express 2⅜ inch"), "450-400-nitro-express-2-3-8-inch")
        self.assertEqual(slug("9.5x57 mm Mannlicher-Schönauer"), "9-5x57-mm-mannlicher-schonauer")

    def test_catalogue_follows_order_toml(self):
        with open(os.path.join(ROOT, "order.toml"), "rb") as f:
            order = tomllib.load(f)
        self.assertEqual([KEY[cat] for cat, _ in cartridges.ALL_CATALOGUE], list(order))
        for cat, items in cartridges.ALL_CATALOGUE:
            names = [s["name"] for s in items]
            listed = order[KEY[cat]]
            self.assertEqual(names[:len(listed)], listed)
            self.assertEqual(names[len(listed):], sorted(names[len(listed):]))

    def test_categories_are_a_field_of_english_names_and_the_apps_names(self):
        self.assertEqual([n for n in os.listdir(os.path.join(ROOT, "calibres")) if not n.endswith(".toml")], [])
        self.assertEqual(cartridges.categories(".308 Winchester"), ("Langwaffe",))
        self.assertEqual(len(cartridges.CALIBRE_CATEGORIES), sum(len(items) for _, items in cartridges.ALL_CATALOGUE))
        self.assertEqual([cat for cat, _ in cartridges.CATALOGUE],
                         ["Randfeuer", "Kurzwaffe", "Langwaffe", "Schwarzpulver", "Flinte", "Luftdruck"])

    def test_a_cartridge_still_in_production_is_not_listed_under_black_powder(self):
        # Black powder is the shelf of black-powder cartridges nobody makes any more and of the
        # muzzle-loaders' balls and bullets. A cartridge that began with black powder and is still loaded
        # (with smokeless powder) stands with the guns that fire it.
        kinds = {s["name"]: s["kind"] for _, specs in cartridges.ALL_CATALOGUE for s in specs}
        made_today = cartridges.BLACK_POWDER - cartridges.OBSOLETE
        self.assertEqual(sorted(n for n in made_today if kinds[n] not in (cartridges.BALL, cartridges.MINIE)), [],
                         "a black-powder cartridge needs obsolete = true (docs/format.md)")
        self.assertEqual(cartridges.categories(".44-40 WCF"), ("Langwaffe", "Kurzwaffe"))
        for name in (".45-70 Government", ".38-55 Winchester", ".45 Colt", ".38-40 Winchester", ".32-20 Winchester"):
            self.assertIn(cartridges.categories(name)[0], ("Kurzwaffe", "Langwaffe"), name)
        for name in (".50-70 Government", ".577/450 Martini-Henry", ".44 Henry Centrefire"):
            self.assertEqual(cartridges.categories(name)[0], "Schwarzpulver", name)

    def test_guns_beyond_the_category_have_a_source(self):
        # A round's guns say what fires it; its category follows from them unless it is a black-powder or
        # rimfire round (2026-11-16). Guns a black-powder or rimfire round names, and a second gun of any
        # round, come from the source in its "# Guns:" note.
        guns = cartridges.CALIBRE_GUNS
        self.assertEqual(guns[".22 LR"], ("rifle", "handgun"))
        self.assertEqual(guns[".380 Short"], ("rifle", "handgun"))
        self.assertTrue(cartridges.is_black_powder(".380 Short"))
        # Handgun rounds factory carbines, lever actions or submachine guns are made for, the balls and
        # Minié bullets by their guns, the Flobert ball by its garden gun (2026-11-16).
        self.assertEqual(guns[".357 Magnum"], ("handgun", "rifle"))
        self.assertEqual(guns["9x19 mm"], ("handgun", "rifle"))
        self.assertEqual(guns[".36 Rundkugel (.375)"], ("handgun",))
        self.assertEqual(guns[".58 Minié"], ("rifle",))
        self.assertEqual(guns["9 mm Flobert Bosquette"], ("shotgun",))
        self.assertEqual(cartridges.categories(".357 Magnum"), ("Kurzwaffe", "Langwaffe"))
        # Only blanks name no gun: they are fired by blank and starter pistols and tools, not by a gun.
        self.assertEqual({n for n, g in guns.items() if not g},
                         {".22 SH (5.6/11)", "6.8/11", ".22 Long Blanc", "6 mm Flobert Blanc"})
        kinds = {s["name"]: s["kind"] for _, items in cartridges.ALL_CATALOGUE for s in items}
        for name, g in guns.items():
            with self.subTest(name):
                technology = cartridges.is_black_powder(name) or kinds[name] == "rimfire"
                if len(g) > 1 or g and technology:
                    with open(os.path.join(ROOT, "calibres", slug(name) + ".toml"), encoding="utf-8") as f:
                        self.assertRegex(f.read(), r"(?m)^# Guns: .+\nguns = ")
                if cartridges.is_black_powder(name) and kinds[name] not in cartridges.LOOSE:  # a case, not a ball
                    self.assertTrue({"rifle", "handgun"} & set(g))
                if "cannon" in g:
                    self.assertEqual(g, ("cannon",))

    def test_cannon_rounds_are_in_the_catalogue_but_not_in_the_apps(self):
        self.assertEqual([cat for cat, _ in cartridges.ALL_CATALOGUE][-1], "Kanone")
        self.assertEqual(cartridges.ALL_CATALOGUE[:-1], cartridges.CATALOGUE)
        cannon = dict(cartridges.ALL_CATALOGUE)["Kanone"]
        self.assertIn("20x138 mm B", [s["name"] for s in cannon])
        self.assertIsNone(next(s for s in cannon if s["name"] == "57x441 mm R")["sh_at"])  # no source gives it
        self.assertNotIn("20x138 mm B", cartridges.PRIMERS)
        self.assertTrue(all(20 <= s["bullet"] <= 57 for s in cannon))
        self.assertLessEqual({"20x102 mm", "35x228 mm", "40x365 mm R", "57x348 mm SR"}, {s["name"] for s in cannon})

    def test_cannon_rounds_of_the_swiss_army(self):
        # The cannon rounds up to 57 mm the Swiss Army adopted. These four were missing;
        # Rapid Fire (pp. 226-229) gives them, and the Swiss FMK case a thinner rim than the HS 820's.
        cannon = {s["name"] for s in dict(cartridges.ALL_CATALOGUE)["Kanone"]}
        self.assertLessEqual({"20x110 mm Hispano", "20x139 mm FMK", "24x138 mm", "34x239 mm"}, cannon)
        self.assertEqual(cartridges.rim_thickness("20x139 mm FMK"), 2.6)
        # Rapid Fire gives the HS 820 case a 3.5 mm rim; its AECC drawing, 3.04 mm (2026-11-15).
        self.assertEqual(cartridges.rim_thickness("20x139 mm"), 3.04)
        for name in ("20x139 mm FMK", "24x138 mm", "34x239 mm"):
            self.assertEqual(cartridges.origin(name)[0], "CH", name)

    def test_swiss_oerlikon_and_hispano_cannon_rounds(self):
        # The Oerlikon S round (20x110 mm RB) was missing, and with it the other Swiss
        # cannon rounds of Jane's table (p. 682): Oerlikon's three pre-war rounds with a rebated rim, the 20x128
        # of the KAA and KAB and the 30x170 of the HS 831 (Oerlikon KCB).
        cannon = {s["name"]: s for s in dict(cartridges.ALL_CATALOGUE)["Kanone"]}
        for name in ("20x72 mm RB", "20x101 mm RB", "20x110 mm RB", "20x128 mm", "30x170 mm"):
            with self.subTest(name):
                self.assertIn(name, cannon)
                self.assertEqual(cartridges.origin(name)[0], "CH")
        for name in ("20x72 mm RB", "20x101 mm RB", "20x110 mm RB"):  # rebated: the rim is narrower than the base
            self.assertLess(cannon[name]["rim"], cannon[name]["base"] - 2, name)
        # The Oerlikon S round is not the Hispano's 20x110: their rims are 2.6 mm apart.
        self.assertGreater(cannon["20x110 mm Hispano"]["rim"] - cannon["20x110 mm RB"]["rim"], 2.5)
        self.assertEqual(cartridges.rim_thickness("30x170 mm"), 3.48)  # AECC drawing 30-170-BGC-010
        self.assertEqual(cartridges.case_material("20x128 mm"), "steel")

    def test_every_cannon_round_of_rapid_fires_table(self):
        # All the rounds of Rapid Fire's Table 1 from 20 to 57 mm (pp. 225-231), by the
        # catalogue's names. Only the 40 mm of the Japanese Ho-301 is left out: it has no case.
        table = {
            "20x70 mm RB", "20x72 mm RB", "20x80 mm RB",
            "20x82 mm", "20x94 mm", "20x99 mm R", "20x101 mm RB", "20x102 mm", "20x105 mm B", "20x105 mm",
            "20x110 mm RB", "20x110 mm Hispano", "20x110 mm USN", "20x113 mm", "20x120 mm", "20x124 mm", "20x128 mm",
            "20x138 mm B", "20x139 mm FMK", "20x139 mm", "20x142 mm", "20x145 mm R", "23x115 mm", "23x152 mm B VYa",
            "23x152 mm B ZU-23", "23x260 mm", "24x138 mm", "25.4x87 mm R", "25.4x87 mm", "25x137 mm", "25x163 mm",
            "25x173 mm",
            "25x205 mm SR", "25x218 mm SR", "25x218 mm", "27x145 mm B", "28x199 mm SR", "30x29 mm B", "30x86 mm B",
            "30x90 mm RB", "30x92 mm RB", "30x97 mm B", "30x113 mm B", "30x114 mm", "30x122 mm", "30x155 mm B",
            "30x165 mm GSh-30", "30x165 mm 2A42", "30x170 mm", "30x173 mm KCA", "30x173 mm GAU-8",
            "30x184 mm B", "30x210 mm", "30x210 mm B", "34x239 mm", "35x228 mm", "37x69 mm R", "37x94 mm R",
            "37x101 mm SR", "37x112 mm R", "37x124 mm R", "37x136 mm R", "37x144 mm", "37x145 mm R",
            "37x155 mm", "37x190 mm", "37x198 mm", "37x223 mm SR", "37x232 mm SR", "37x240 mm", "37x250 mm R",
            "37x252 mm SR", "37x263 mm B", "40x53 mm SR", "40x158 mm R", "40x311 mm R", "40x365 mm R", "45x386 mm SR",
            "50x346 mm B", "50x420 mm R",
            "57x121 mm R", "57x230 mm R", "57x348 mm SR", "57x438 mm R", "57x441 mm R",
        }
        self.assertEqual(len(table), 85)
        cannon = {s["name"]: s for s in dict(cartridges.ALL_CATALOGUE)["Kanone"]}
        self.assertLessEqual(table, set(cannon))
        # Rapid Fire's 37x249R is the navy's case, which Autocannon (p. 158) measures at 250 mm with a 3.9 mm
        # rim; its 37x250R is the Soviet 61-K's semi-rimmed 37x252.
        self.assertIn("37x249r", cannon["37x250 mm R"]["aliases"])
        self.assertEqual(cartridges.rim_thickness("37x250 mm R"), 3.9)
        self.assertEqual(cartridges.rim_thickness("20x120 mm"), 5.0)  # Madsen's thick rim (AECC drawing)
        self.assertEqual(cartridges.rim_thickness("20x99 mm R"), 1.93)  # the ShVAK's (AECC drawing)
        # The Rikhter R-23's case is 15 mm across at the head and 30 mm further up (Rapid Fire p. 227).
        self.assertEqual((cannon["23x260 mm"]["rim"], cannon["23x260 mm"]["base"]), (15.0, 30.0))
        self.assertEqual(cartridges.origin("30x210 mm")[0], "CS")

    def test_every_cannon_round_has_its_rim_and_a_rimmed_one_a_rim_wider_than_its_base(self):
        # Rapid Fire's table gave the last cannon rounds without one their rim (2026-11-10).
        for s in dict(cartridges.ALL_CATALOGUE)["Kanone"]:
            self.assertIsNotNone(s["rim"], s["name"])
            if s["kind"] == cartridges.RIMMED:
                self.assertGreater(s["rim"], s["base"], s["name"])

    def test_a_calibre_missing_from_order_toml_comes_last_by_name(self):
        with Copy() as c:
            text = c.read("order.toml").replace('  ".22 LR",\n', "").replace('  ".22 Short",\n', "")
            c.write("order.toml", text)
            rimfire = dict(load(c.dir)["CATALOGUE"])["Randfeuer"]
            self.assertEqual([s["name"] for s in rimfire[-2:]], [".22 LR", ".22 Short"])

    def test_tables_keep_their_shapes(self):
        self.assertEqual(cartridges.INTRODUCED[".22 LR"], (1887, "https://en.wikipedia.org/wiki/.22_Long_Rifle"))
        self.assertEqual(cartridges.BULLETS[".22 LR"], ("lead", "https://en.wikipedia.org/wiki/.22_Long_Rifle"))
        self.assertEqual(cartridges.CURRENT_CASES[".308 Winchester"][0], ("steel",))
        self.assertIsInstance(cartridges.WORLDWIDE, frozenset)
        self.assertEqual(cartridges.COUNTRIES["CH"], ("Switzerland", "🇨🇭"))
        self.assertEqual(cartridges.COUNTRIES["SU"], ("Soviet Union", None))

    def test_sources_lists_every_source_and_tables_keep_the_first(self):
        with Copy() as c:
            c.edit(LR, 'year = 1887\nsources = ["https://en.wikipedia.org/wiki/.22_Long_Rifle"]',
                   'year = 1887\nsources = [\n  "https://en.wikipedia.org/wiki/.22_Long_Rifle",\n'
                   '  "https://municion.org/producto/22-long-rifle/",\n]')
            c.edit(LR, LR_MM, 'sources = ["https://saami.org/"]')
            t = load(c.dir)
            self.assertEqual(t["SOURCES"][(".22 LR", "introduced")],
                             ["https://en.wikipedia.org/wiki/.22_Long_Rifle", "https://municion.org/producto/22-long-rifle/"])
            self.assertEqual(t["INTRODUCED"][".22 LR"], (1887, "https://en.wikipedia.org/wiki/.22_Long_Rifle"))
            self.assertEqual(t["SOURCES"][(".22 LR", "mm")], ["https://saami.org/"])

    def test_sources_function(self):
        self.assertEqual(sources(".22 LR", "introduced"), ["https://en.wikipedia.org/wiki/.22_Long_Rifle"])
        self.assertEqual(sources(".22 LR", "shoulder_angle"), [])
        # the angle's own cite, else the [mm] sources
        self.assertEqual(sources(".308 Winchester", "shoulder_angle"),
                         ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"])
        self.assertEqual(cartridges.SHOULDER_ANGLES[".308 Winchester"],
                         (20, "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"))
        self.assertEqual(sources("7.62x25 mm Tokarev", "shoulder_angle"), sources("7.62x25 mm Tokarev", "mm"))  # no cite
        self.assertEqual(sources("No such calibre", "mm"), [])

    def test_most_calibres_name_the_source_of_their_measurements(self):
        names = [s["name"] for _, items in cartridges.CATALOGUE for s in items]
        self.assertGreater(sum(1 for n in names if sources(n, "mm")), len(names) / 2)
        self.assertEqual(sources(".350 Rigby Magnum", "mm"),  # the page of most values first
                         ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page138.pdf",
                          "book:cotw-18 p. 608", "book:donnelly p. 429"])

    def test_the_template_is_the_308_winchester_file_with_explanations(self):
        with open(os.path.join(ROOT, "docs", "template.toml"), "rb") as f:
            template = tomllib.load(f)
        with open(os.path.join(ROOT, WIN), "rb") as f:
            self.assertEqual(template, tomllib.load(f))
        with Copy() as c:  # and it passes the check as a calibre file
            shutil.copy(os.path.join(ROOT, "docs", "template.toml"), c.path(WIN))
            self.assertEqual(c.problems(), [])

    def test_the_template_explains_every_key_and_table(self):
        with open(os.path.join(ROOT, "docs", "template.toml"), encoding="utf-8") as f:
            text = f.read()
        keys = set(cartridges.TOP_KEYS) | set(cartridges.MM_FULL) | {"diameter", "mouth", "length"}
        for table, (req, opt, _) in cartridges.FACTS.items():
            keys |= set(req) | set(opt)
            self.assertRegex(text, rf"(?m)^# ?\[{table}\]$|^\[{table}\]$", table)
        keys |= set(cartridges.COLOUR_CODE_KEYS[0]) | set(cartridges.COLOUR_CODE_KEYS[1]) | set(cartridges.PARTS)
        self.assertRegex(text, r"(?m)^# \[\[colour_codes\]\]$")
        for k in keys | set(cartridges.COLOURS) | set(cartridges.MEANINGS):
            self.assertRegex(text, rf"\b{k}\b", k)

    def test_empty_primer_sources_mean_unverified(self):
        self.assertIn("9 mm PA Blanc", cartridges.PRIMER_UNVERIFIED)
        self.assertNotIn("9 mm PA Blanc", cartridges.PRIMER_SOURCES)

    def test_origin_sources(self):
        # Every calibre with a state has origin_sources; an empty list means not checked yet.
        named = set(cartridges.ORIGIN) | set(cartridges.ORIGIN_UNDECIDED)
        self.assertEqual(set(cartridges.ORIGIN_SOURCES) | cartridges.ORIGIN_UNVERIFIED, named)
        self.assertEqual(set(cartridges.ORIGIN_SOURCES) & cartridges.ORIGIN_UNVERIFIED, set())
        self.assertGreater(len(cartridges.ORIGIN_SOURCES), 600)
        # The kinds of source: Wikipedia's infobox, the Ammo Encyclopedia, a C.I.P. sheet, municion.org's PAÍS.
        self.assertEqual(cartridges.sources("7.5x55 mm Swiss (GP 11)", "origin"),
                         ["https://en.wikipedia.org/wiki/7.5×55mm_Swiss", "book:ammo-encyclopedia-2 p. 513",
                          "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page46.pdf"])
        self.assertEqual(cartridges.ORIGIN_SOURCES["9.3x72 mm R Sauer"],
                         "https://municion.org/producto/93-x-72-r-sauer-sohn/")
        # Two-state cases whose pages name the other state, and open ones, stay unverified.
        for name in ("7.65 mm Parabellum", "9x23 mm Largo", ".32 S&W Long Wadcutter"):
            self.assertIn(name, cartridges.ORIGIN_UNVERIFIED, name)
        self.assertEqual(cartridges.sources("12/70", "origin"), [])  # a gauge has no origin

    def test_empty_bullet_sources_mean_inferred(self):
        self.assertIn("8.5x55 mm Blaser", cartridges.BULLET_INFERRED)
        self.assertEqual(cartridges.BULLETS["8.5x55 mm Blaser"], ("softpoint", None))

    def test_short_forms_build_the_same_dicts_as_the_helpers(self):
        self.assertEqual(next(s for _, i in cartridges.CATALOGUE for s in i if s["name"] == "12/70"),
                         cartridges.shot("12/70", 20.6, 22.45, 61.09, ["12", "12/70", "12ga", "12gauge", "12 bore", "calibre 12", "calibro 12", "kaliber 12"], 70.0))
        blank = next(s for _, i in cartridges.CATALOGUE for s in i if s["name"] == ".22 SH (5.6/11)")
        self.assertEqual((blank["neck"], blank["oal"], blank["profile"]), (3.4, 11.1, "crimped"))


class CheckTests(unittest.TestCase):
    """Each mistake is found, with its file and line where there is one."""

    def assertProblem(self, copy, rel, pattern, line=True):
        """A problem in `rel` matching `pattern`, on line `line` (a number), on some line (True) or
        anywhere (False)."""
        found = copy.problems()
        hits = [p for p in found if p[0] == rel and re.search(pattern, p[2])]
        self.assertTrue(hits, f"no problem matching {pattern!r} in {rel}: {found}")
        if line is True:
            self.assertIsNotNone(hits[0][1], hits[0])
        elif line:
            self.assertEqual(hits[0][1], line, hits[0])

    def assertOnlyProblems(self, copy, rel, pattern):
        """Every problem is in `rel` and matches `pattern`: nothing else is reported because of it."""
        found = copy.problems()
        self.assertTrue(found)
        for p in found:
            self.assertEqual(p[0], rel, found)
            self.assertRegex(p[2], pattern)

    def test_misspelt_key_is_found_with_a_suggestion(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            self.assertProblem(c, WIN, r"unknown key 'shoulder_ad' in \[mm\] \(did you mean \"shoulder_at\"\?\)",
                               line=c.line_of(WIN, "shoulder_ad ="))

    def test_semi_rimmed_cases(self):
        # Semi-rimmed: a rim a little wider than the base with an extractor groove in front of it,
        # recorded as its own kind like belted. Case type G or H in the COTW 18 dimension
        # tables, plus the .25 ACP, 9 mm Browning Long (9x20 SR), .303 Magnum and .308 Marlin Express (the
        # .307 Winchester's case, which COTW lists as rimmed), which other sources call so, and the cannon
        # rounds that Rapid Fire, Jane's or Autocannon name SR.
        semi = {s["name"] for _, items in cartridges.ALL_CATALOGUE for s in items
                if s["kind"] == cartridges.SEMI_RIMMED}
        self.assertEqual(semi, {
            ".220 Swift", ".280 Ross", ".303 Magnum", ".32 Winchester Self-Loading", ".35 Winchester Self-Loading",
            ".351 Winchester Self-Loading", ".307 Winchester", ".308 Marlin Express", ".356 Winchester", "8 mm Nambu", ".38 ACP", ".38 AMU", ".38 Super", ".401 Winchester Self-Loading",
            ".455 Webley Automatic", ".50-115 Bullard", "6.35 mm Browning (.25 ACP)",
            "6.5x50 mm SR Arisaka", "6.5x53.5 mm SR Daudeteau", "7.65 mm Browning (.32 ACP)", "9 mm Browning Long",
            "25x205 mm SR", "25x218 mm SR", "28x199 mm SR", "37x101 mm SR", "37x223 mm SR", "37x232 mm SR",
            "37x252 mm SR", "40x53 mm SR", "45x386 mm SR", "57x348 mm SR"})
        with Copy() as c:
            c.edit(WIN, 'kind = "rimless"', 'kind = "semi-rimmed"')
            self.assertProblem(c, WIN, r"semi-rimmed case has a rim wider than its base", line=c.line_of(WIN, "rim ="))
            # and the other way round: a rim that wide is not a rimless case's
            swift = "calibres/220-swift.toml"
            c.edit(swift, 'kind = "semi-rimmed"', 'kind = "rimless"')
            self.assertProblem(c, swift, r"rimless case has a rim at most 0\.3 mm wider than its base",
                               line=c.line_of(swift, "rim ="))
        with Copy() as c:  # exactly 0.3 mm is still rimless, whatever binary floats make of 4.1 + 0.3
            c.edit(WIN, "rim = 11.9", "rim = 4.4")
            c.edit(WIN, "base = 11.9", "base = 4.1")
            self.assertFalse([p for p in c.problems() if "rimless case" in p[2]])

    def test_the_rimfire_category_follows_from_the_kind(self):
        # A file does not name its category: a rimfire case is in rimfire, a centrefire blank (the 9 mm PA Blanc)
        # under its gun, a black-powder rimfire round in black-powder and rimfire (2026-11-16).
        self.assertEqual(cartridges.categories(".22 LR"), ("Randfeuer", "Langwaffe", "Kurzwaffe"))
        self.assertEqual(cartridges.categories("9 mm PA Blanc"), ("Kurzwaffe",))
        self.assertEqual(cartridges.categories("10.4x38 mm R Vetterli"), ("Schwarzpulver", "Langwaffe", "Randfeuer"))

    def test_416_rigby_no_2_is_the_416_rigby_with_a_rim(self):
        # C.I.P. sheets: the No. 2 (2019) keeps the .416 Rigby's body, shoulder, neck and cone behind a 17 mm rim.
        by_name = {s["name"]: s for _, items in cartridges.ALL_CATALOGUE for s in items}
        rigby, no2 = by_name[".416 Rigby"], by_name[".416 Rigby No. 2"]
        self.assertEqual(no2["kind"], cartridges.RIMMED)
        for key in ("base", "shoulder", "sh_at", "neck", "case"):
            self.assertAlmostEqual(no2[key], rigby[key], delta=0.1, msg=key)
        self.assertGreater(no2["rim"], rigby["rim"] + 2)
        self.assertEqual(cartridges.shoulder_angle(".416 Rigby No. 2"), cartridges.shoulder_angle(".416 Rigby"))
        self.assertEqual(cartridges.lookalikes(".416 Rigby"), [".416 Rigby No. 2"])

    def test_problems_name_the_line_of_the_value(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_angle = 20", "shoulder_angle = 120")
            c.edit(LR, 'kind = "rimfire"', 'kind = "rimfre"')
            self.assertProblem(c, WIN, r"shoulder_angle is the angle", line=c.line_of(WIN, "shoulder_angle = 120"))
            self.assertProblem(c, LR, r"kind 'rimfre'", line=c.line_of(LR, "kind ="))
        with Copy() as c:
            c.edit(LR, 'kind = "rimfire"', 'kind = "rimfire')
            self.assertProblem(c, LR, r"not valid TOML", line=c.line_of(LR, "kind ="))

    def test_a_broken_file_is_reported_once(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            c.edit(LR, 'kind = "rimfire"', 'kind = "rimfire')
            self.assertEqual({p[0] for p in c.problems()}, {WIN, LR})

    def test_hidden_files_are_ignored(self):
        with Copy() as c:
            c.write("calibres/.DS_Store", "x")
            c.write("calibres/.hidden.toml", "x")
            self.assertEqual(c.problems(), [])

    def test_origin_sources_go_with_an_origin(self):
        with Copy() as c:
            c.edit(WIN, "origin_sources = [", "origin_sourcez = [")
            self.assertProblem(c, WIN, r"origin needs origin_sources", line=c.line_of(WIN, 'origin = "US"'))
        with Copy() as c:
            c.edit(WIN, '"book:ammo-encyclopedia-2 p. 327"', '"book:ammo p. 327"')
            self.assertProblem(c, WIN, r"origin_sources source 'book:ammo p. 327' names no book")
        with Copy() as c:
            c.edit(WIN, 'origin = "US"\n', "")
            self.assertProblem(c, WIN, r"origin_sources without origin")
        with Copy() as c:
            c.edit(WIN, 'origin_sources = [\n  "https://en.wikipedia.org/wiki/.308_Winchester",\n  "book:ammo-encyclopedia-2 p. 327",\n'
                        '  "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf",\n]',
                   'origin_sources = "https://en.wikipedia.org/wiki/.308_Winchester"')
            self.assertProblem(c, WIN, r"origin_sources must be a list of web addresses")
        hisp = "calibres/20x110-mm-hispano.toml"
        with Copy() as c:
            c.edit(hisp, "origin_sources = []\n", "")
            self.assertProblem(c, hisp, r"origin needs origin_sources", line=c.line_of(hisp, "origin_candidates ="))

    def test_misspelt_top_level_key(self):
        with Copy() as c:
            c.edit(LR, "worldwide = true", "worldwilde = true")
            self.assertProblem(c, LR, r"unknown key 'worldwilde'.*did you mean \"worldwide\"")

    def test_a_case_head_can_give_the_rim_thickness_alone(self):
        with Copy() as c:
            c.edit(WIN, "ramp_top = 3.85\ngroove_diameter = 10.39\nramp_angle = 36.0\ngroove_width = 1.4\n", "")
            self.assertEqual(c.problems(), [])
            t = load(c.dir)
            self.assertEqual(t["RIM_THICKNESS"][".308 Winchester"][0], 1.37)
            self.assertNotIn(".308 Winchester", t["CASE_HEADS"])

    def test_a_case_head_has_the_whole_groove_or_none(self):
        with Copy() as c:
            c.edit(WIN, "ramp_angle = 36.0\n", "")
            self.assertProblem(c, WIN, r"ramp_top, groove_diameter and ramp_angle together, or only rim_thickness")

    def test_a_belt_wider_than_the_rim_has_its_diameter(self):
        files = [f"calibres/{f}.toml" for f in ("378-weatherby-magnum", "460-a-square-short", "416-weatherby-magnum",
                                                "300-winchester-magnum", "300-h-h-magnum", "23x152-mm-b-vya")]
        wby, short, wide, win_mag, hh, cannon = files
        with Copy() as c:
            c.edit(wby, "belt = 15.33\n", "")                             # a rim of 14.7 under a body of 14.8
            c.edit(short, "belt = 15.33", "belt = 14.78")                 # no wider than its body
            c.edit(wide, "belt = 15.33", "belt = 18.33")                  # a slip of the pen: a fifth wider than the body
            c.edit(win_mag, "rim = 13.51\n", "rim = 13.51\nbelt = 13.2\n")  # narrower than its rim
            c.edit(WIN, "rim = 11.9\n", "rim = 11.9\nbelt = 12.5\n")       # a rimless case
            c.edit(hh, "rim = 13.5\n", "rim = 13.5\nbelt = 13.56\n")       # stays valid: R3 on its sheet, 0.05 over R1
            c.edit(cannon, "rim = 33.38\n", "")                           # stays valid: a cannon round without its rim
            self.assertEqual(sorted((p[0], p[1], p[2].split(":")[0]) for p in c.problems()), sorted([
                (wby, c.line_of(wby, "rim ="), "a belted case with a rim narrower than its base needs [mm] belt (R3 on the C.I.P. sheets)"),
                (short, c.line_of(short, "belt ="), "[mm] belt 14.78 is the belt's diameter (R3 on the C.I.P. sheets) where it is wider than the rim"),
                (wide, c.line_of(wide, "belt ="), "[mm] belt 18.33 is the belt's diameter (R3 on the C.I.P. sheets) where it is wider than the rim"),
                (win_mag, c.line_of(win_mag, "belt ="), "[mm] belt 13.2 is the belt's diameter (R3 on the C.I.P. sheets) where it is wider than the rim"),
                (WIN, c.line_of(WIN, "belt ="), "only a belted case has a [mm] belt"),
            ]))

    def test_a_shot_shell_head_has_only_its_rim_thickness(self):
        # The C.I.P. Tab. VII sheets give a shot shell's rim thickness (t), no extractor groove (2026-11-16).
        with Copy() as c:
            shell = "calibres/12-70.toml"
            c.edit(shell, "rim_thickness = 1.85\n", "rim_thickness = 1.85\nramp_top = 2.0\ngroove_diameter = 20.0\n"
                                                     "ramp_angle = 30.0\n")
            self.assertProblem(c, shell, r"a shot case has no extractor groove")
        with Copy() as c:
            ball = "calibres/58-minie.toml"
            c.write(ball, c.read(ball) + '\n[case_head]\nrim_thickness = 1.5\nsources = ["https://saami.org/"]\n')
            self.assertProblem(c, ball, r"a minie calibre has no \[case_head\]")

    def test_a_rimmed_case_head_has_no_groove(self):
        with Copy() as c:
            c.edit(LR, "rim_thickness = 1.02\n", "rim_thickness = 1.02\nramp_top = 2.0\ngroove_diameter = 6.0\n"
                                                  "ramp_angle = 30.0\n")
            self.assertProblem(c, LR, r"a rimfire case has no extractor groove")

    def test_only_a_rimmed_case_has_a_foot_and_it_stays_under_the_rim(self):
        gras = "calibres/11x59-mm-r-gras.toml"
        with Copy() as c:
            c.edit(WIN, "rim_thickness = 1.37\n", "rim_thickness = 1.37\nfoot = 0.5\n")
            self.assertProblem(c, WIN, r"only a rimmed case has a foot under its rim")
        with Copy() as c:
            c.edit(LR, "rim_thickness = 1.02\n", "rim_thickness = 1.02\nfoot = 0.3\n")
            self.assertProblem(c, LR, r"only a rimmed case has a foot under its rim")
        # Gras: rim_thickness 1.9. 1.6 is over 1.5 mm; 1.45 leaves the rim only 0.45 mm.
        for foot in ("1.6", "1.45"):
            with Copy() as c:
                c.edit(gras, "foot = 1.0\n", f"foot = {foot}\n")
                self.assertProblem(c, gras, r"foot is at most 1.5 mm and leaves the rim at least 0.5 mm")
        with Copy() as c:
            c.edit(gras, "foot = 1.0\n", "foot = 0\n")
            self.assertProblem(c, gras, r"\[case_head\] foot must be a number above 0")
        with Copy() as c:  # leaves exactly 0.5 mm
            c.edit(gras, "foot = 1.0\n", "foot = 1.4\n")
            self.assertEqual(c.problems(), [])

    def test_misspelt_table(self):
        with Copy() as c:
            c.edit(WIN, "[case_head]", "[case_haed]")
            self.assertProblem(c, WIN, r"unknown table \[case_haed\].*case_head")

    def test_values_that_are_not_allowed(self):
        cases = [(LR, 'kind = "rimfire"', 'kind = "rimfre"', r"kind 'rimfre'.*did you mean \"rimfire\""),
                 (LR, 'profile = "round"', 'profile = "rond"', r"profile 'rond'"),
                 (WIN, 'size = "large-rifle"', 'size = "large rifle"', r"\[primer\] size 'large rifle'"),
                 (LR, 'type = "lead"', 'type = "fmj"', r"\[bullet\] type 'fmj' is not one of jacketed"),
                 (LR, 'origin = "US"', 'origin = "USA"', r"origin 'USA' is not a code in countries.toml"),
                 (LR, "rim = 7.06", 'rim = "7.06"', r"\[mm\] rim must be a number"),
                 (LR, "rim = 7.06", "rim = -7.06", r"\[mm\] rim must be a number above 0"),
                 (LR, "year = 1887", "year = 18887", r"year must be a year"),
                 (LR, "worldwide = true", 'worldwide = "yes"', r"worldwide must be true or false"),
                 (WIN, "shoulder_angle = 20", "shoulder_angle = 120", r"shoulder_angle is the angle to the case axis")]
        for rel, old, new, pattern in cases:
            with self.subTest(new), Copy() as c:
                c.edit(rel, old, new)
                self.assertProblem(c, rel, pattern)

    def test_aliases_that_are_not_a_list(self):
        with Copy() as c:
            c.edit(LR, 'aliases = ["22lr", "22", "kk", "22l.r."]', "aliases = 5")
            self.assertOnlyProblems(c, LR, r"aliases must be a list")

    def test_an_alias_is_never_the_name_of_another_calibre(self):
        with Copy() as c:
            c.edit(WIN, 'aliases = ["308", "308win"]', 'aliases = ["308", "308win", ".22 lr"]')
            self.assertProblem(c, WIN, r"alias '.22 lr' is the name of the calibre '.22 LR'", line=c.line_of(WIN, "aliases"))

    def test_a_file_with_a_byte_order_mark_is_fine(self):
        with Copy() as c:
            c.write(LR, "\ufeff" + c.read(LR))
            self.assertEqual(c.problems(), [])

    def test_sources_must_be_web_addresses(self):
        with Copy() as c:
            c.edit(LR, '"https://en.wikipedia.org/wiki/.22_Long_Rifle"]\n\n[case_head]', '"Wikipedia"]\n\n[case_head]')
            self.assertProblem(c, LR, r"source 'Wikipedia' is not a https:// web address")

    def test_a_source_can_be_a_page_of_a_book_in_books_toml(self):
        with Copy() as c:
            c.edit(LR, LR_MM, 'sources = [\n  "book:cotw-18 p. 670",\n  "https://saami.org/",\n]')
            self.assertEqual(c.problems(), [])
            self.assertEqual(load(c.dir)["SOURCES"][(".22 LR", "mm")], ["book:cotw-18 p. 670", "https://saami.org/"])
        self.assertEqual(sources(".22 LR", "mm"), [
            "https://saami.org/wp-content/uploads/2026/05/SAAMI-Z299.1-R2026-Rimfire-FINAL-Approved-2026-05-08.pdf#page=22",
            "book:janes-ammo-2002 p. 681", "book:cotw-18 p. 670", "book:tm-43-0001-27 p. 3-5"])
        self.assertEqual(cartridges.BOOKS["cotw-18"]["isbn"], "978-1-959265-46-7")

    def test_a_manual_numbered_by_chapter_has_pages_like_14_13(self):
        with Copy() as c:
            c.edit(LR, LR_MM, 'sources = ["book:tm-43-0001-27 p. 14-13"]')
            self.assertEqual(c.problems(), [])

    def test_a_book_source_names_a_book_in_books_toml_and_a_page(self):
        for source, pattern in [("book:cotw-81 p. 670", r"names no book in books.toml \(did you mean"),
                                ("book:cotw-18 page 670", r"must be written book:<id> p. <page>"),
                                ("book:cotw-18 p. 0", r"must be written book:<id> p. <page>"),
                                ("book:tm-43-0001-27 p. 14-", r"must be written book:<id> p. <page>"),
                                ("book:tm-43-0001-27 p. 14-0", r"must be written book:<id> p. <page>"),
                                ("book:tm-43-0001-27 p. 14-13-2", r"must be written book:<id> p. <page>"),
                                ("book:cotw-18", r"must be written book:<id> p. <page>")]:
            with self.subTest(source), Copy() as c:
                c.edit(LR, LR_MM, f'sources = ["{source}"]')
                self.assertProblem(c, LR, pattern, line=c.line_of(LR, f'["{source}"]'))
                self.assertOnlyProblems(c, LR, pattern)

    def test_own_measurement_is_a_source(self):
        # One's own caliper measurement counts as a source, with one's GitHub username.
        for source in ("measured:ravench 2026-11-08", "measured:some-one 2026-11-08",
                       "measured:" + "a" * 39 + " 2026-11-08"):
            with self.subTest(source), Copy() as c:
                c.edit(LR, LR_MM, f'sources = ["{source}"]')
                self.assertEqual(c.problems(), [])
        for source in ("measured:ravench", "measured:ravench 8.11.2026", "measured:-someone 2026-11-08",
                       "measured:some--one 2026-11-08", "measured: 2026-11-08", "measured:someone- 2026-11-08",
                       "measured:some_one 2026-11-08", "measured:" + "a" * 40 + " 2026-11-08"):
            with self.subTest(source), Copy() as c:
                c.edit(LR, LR_MM, f'sources = ["{source}"]')
                self.assertProblem(c, LR, r"must be written measured:<GitHub username> <YYYY-MM-DD>", line=c.line_of(LR, f'["{source}"]'))

    def test_a_book_page_can_source_every_table_but_only_once(self):
        with Copy() as c:
            c.edit(LR, 'sources = ["https://en.wikipedia.org/wiki/.22_Long_Rifle"]',
                   'sources = ["https://en.wikipedia.org/wiki/.22_Long_Rifle", "book:cotw-18 p. 670"]')
            self.assertEqual(c.problems(), [])
            c.edit(LR, LR_MM, 'sources = ["book:cotw-18 p. 670", "book:cotw-18 p. 670"]')
            self.assertOnlyProblems(c, LR, r"\[mm\] lists a source twice")

    def test_isbn_check_digits(self):
        for isbn in ("978-1-959265-46-7", "9781959265467", "0-910676-95-X", "0-89141-116-X"):
            self.assertTrue(cartridges._isbn_ok(isbn), isbn)
        for isbn in ("978-1-959265-46-8", "0-910676-95-1", "978-1-959265-46-7-", "978--1959265467", 9781959265467):
            self.assertFalse(cartridges._isbn_ok(isbn), isbn)

    def test_a_missing_books_toml_is_one_problem(self):
        with Copy() as c:
            os.remove(c.path("books.toml"))
            self.assertEqual(c.problems(), [("books.toml", None, "missing")])

    def test_a_broken_books_toml_is_reported_there_only(self):
        for text, pattern in [("# nothing\n", r"lists no books"),
                              ("[cotw-18]\nyear = 2026\n", r"\[cotw-18\] needs 'title'"),
                              ('[cotw-18]\ntitle = "Cartridges of the World"\nyear = "2026"\n', r"year must be"),
                              ('[cotw-18]\ntitle = "Cartridges of the World"\nyear = 2026\nisbn = "978-1-959265-46-8"\n',
                               r"not a valid ISBN"),
                              ('[COTW]\ntitle = "Cartridges of the World"\nyear = 2026\n', r"lower case"),
                              ('[cotw-18]\ntitle = "Cartridges of the World"\nyear = 2026\npages = 720\n',
                               r"unknown key 'pages'"),
                              ('cotw-18 = "Cartridges of the World"\n', r"must be a table"),
                              ('[cotw-18]\ntitle = "Cartridges of the World\n', r"not valid TOML")]:
            with self.subTest(text), Copy() as c:
                c.write("books.toml", text)
                self.assertOnlyProblems(c, "books.toml", pattern)

    def test_fired_by_lists_the_firearms_of_a_round(self):
        self.assertEqual(cartridges.FIRED_BY["7.5x53.5 mm Swiss (Patrone Modell 1890)"],
                         (("Schmidt-Rubin M1889",), "https://en.wikipedia.org/wiki/7.5×55mm_Swiss"))
        self.assertEqual(sources(".577 Snider", "fired_by"), ["https://en.wikipedia.org/wiki/.577_Snider"])
        self.assertNotIn(".308 Winchester", cartridges.FIRED_BY)
        files = {s["name"]: f"calibres/{slug(s['name'])}.toml"
                 for cat, items in cartridges.CATALOGUE for s in items}
        with Copy() as c:  # without them, every other table but SOURCES (the apps' catalogue too) is the same
            for name in cartridges.FIRED_BY:
                text = c.read(files[name])
                start = text.index("\n[fired_by]\n")
                end = text.find("\n[", start + 2)
                c.write(files[name], text[:start] + (text[end:] if end != -1 else "\n"))
            t = load(c.dir)
        self.assertEqual(t.pop("FIRED_BY"), {})
        same = lambda tables: {k: v for k, v in tables.items() if k not in ("FIRED_BY", "SOURCES")}  # noqa: E731
        self.assertEqual(same(t), same(cartridges._t))

    def test_fired_by_problems(self):
        arms = 'firearms = ["Lebel M1886", "Berthier"]'
        rel = "calibres/8x50-mm-r-lebel.toml"
        for new, pattern in [('firearms = []', r"firearms lists one or more firearm names"),
                             ('firearms = "Lebel M1886"', r"firearms lists one or more firearm names"),
                             ('firearms = ["Lebel M1886", " "]', r"firearms lists one or more firearm names"),
                             ('firearms = ["Lebel M1886", "Lebel M1886 "]', r"without spaces around them"),
                             ('firearms = ["Lebel M1886", "lebel m1886"]', r"firearms lists a firearm twice"),
                             ('firearm = ["Lebel M1886"]', r"unknown key 'firearm'.*did you mean \"firearms\"")]:
            with self.subTest(new), Copy() as c:
                c.edit(rel, arms, new)
                self.assertProblem(c, rel, pattern, line=c.line_of(rel, new))
        with Copy() as c:
            c.edit(rel, arms + '\nsources = ["https://en.wikipedia.org/wiki/8×50mmR_Lebel"]\n', arms + "\n")
            self.assertProblem(c, rel, r"\[fired_by\] needs sources")

    def test_colour_codes_are_for_the_catalogue_only(self):
        self.assertEqual(cartridges.COLOUR_CODES[".50 BMG"][0],
                         {"part": "tip", "colours": ("black",), "meaning": ("armour-piercing",), "description": "M2",
                          "descriptions": {},  # a designation is the same in every language
                          "countries": ("US",), "sources": ["https://en.wikipedia.org/wiki/.50_BMG", "book:labbett p. 80"]})
        # A description in words comes in Kaliberfinder's other languages too.
        swiss = next(t for t in cartridges.COLOUR_CODES[".50 BMG"] if t["description"] == "US M8, Swiss M.64")
        self.assertEqual(swiss["descriptions"], {"de": "M8 (USA), M.64 (Schweiz)", "fr": "M8 (États-Unis), M.64 (Suisse)",
                                                 "it": "M8 (Stati Uniti), M.64 (Svizzera)", "es": "M8 (Estados Unidos), M.64 (Suiza)"})
        for name, codes in cartridges.COLOUR_CODES.items():
            for t in codes:
                self.assertIn(sorted(t["descriptions"]), ([], ["de", "es", "fr", "it"]), name)
                self.assertNotIn("ß", "".join(t["descriptions"].values()), f"{name}: Swiss spelling, ss")
        self.assertNotIn(".308 Winchester", cartridges.COLOUR_CODES)
        self.assertEqual([(t["part"], t["colours"], t["meaning"]) for t in cartridges.COLOUR_CODES["7.5x55 mm Swiss (GP 11)"]],
                         [("tip", ("red",), ("tracer",)), ("base", ("red",), ("tracer",)),
                          ("base", ("purple",), ("armour-piercing",))])
        uk = [(t["colours"], t["meaning"]) for t in cartridges.COLOUR_CODES[".303 British"] if t["part"] == "annulus"]
        self.assertIn((("yellow",), ("proof",)), uk)
        sweden = cartridges.COLOUR_CODES["6.5x55 mm Swedish"]
        self.assertIn(("base", ("reduced-charge",)), [(t["part"], t["meaning"]) for t in sweden])
        files = {s["name"]: f"calibres/{slug(s['name'])}.toml"
                 for cat, items in cartridges.CATALOGUE for s in items}
        with Copy() as c:  # without them, every other table (the apps' catalogue too) is the same
            for name in cartridges.COLOUR_CODES:
                text = c.read(files[name])
                c.write(files[name], text[:text.index("\n[[colour_codes]]")] + "\n")
            t = load(c.dir)
        self.assertEqual(t.pop("COLOUR_CODES"), {})
        self.assertEqual(t, {k: v for k, v in cartridges._t.items() if k != "COLOUR_CODES"})

    def test_colour_code_problems(self):
        first = '\n[[colour_codes]]\npart = "tip"\ncolours = ["red"]\nmeaning = ["tracer"]\nsources = ["book:labbett p. 80"]\n'
        cases = [('colours = ["black"]', 'colours = ["blak"]', r"colours lists one or more of .*did you mean \"black\""),
                 ('colours = ["black"]', "colours = []", r"colours lists one or more of"),
                 ('colours = ["black"]', 'colours = ["black", "black"]', r"colours lists 'black' twice"),
                 ('meaning = ["armour-piercing"]', 'meaning = ["armor-piercing"]', r"did you mean \"armour-piercing\""),
                 ('meaning = ["armour-piercing"]', 'meaning = "armour-piercing"', r"meaning lists one or more of"),
                 ('meaning = ["armour-piercing"]\n', "", r"\[\[colour_codes\]\] needs 'meaning'"),
                 ('part = "tip"\ncolours = ["black"]', 'colours = ["black"]', r"\[\[colour_codes\]\] needs 'part'"),
                 ('part = "tip"\ncolours = ["black"]', 'part = "bas"\ncolours = ["black"]', r"part is \"tip\", \"base\" or \"annulus\".*did you mean \"base\""),
                 ('part = "tip"\ncolours = ["black"]', 'part = "base"\ncolours = ["black", "red"]', r"a base has one colour, not 2"),
                 ('part = "tip"\ncolours = ["black"]', 'part = "annulus"\ncolours = ["black", "red"]', r"an annulus has one colour, not 2"),
                 ('part = "tip"\ncolours = ["black"]', 'part = ["tip"]\ncolours = ["black"]', r"part is \"tip\", \"base\" or \"annulus\""),
                 ('sources = ["https://en.wikipedia.org/wiki/7.62×51mm_NATO"]', "sources = []",
                  r"\[\[colour_codes\]\] needs at least one source"),
                 ('sources = ["https://en.wikipedia.org/wiki/7.62×51mm_NATO"]\n', "", r"\[\[colour_codes\]\] needs sources"),
                 ('colours = ["black"]', 'colours = ["black"]\ncolor = "black"', r"unknown key 'color'.*did you mean \"colours\""),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription = " "', r"description must be text"),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription = "Ball"\ndescription_de = " "\n'
                  'description_fr = "Balle"\ndescription_it = "Palla"\ndescription_es = "Ordinaria"', r"description_de must be text"),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription = "Ball"\ndescription_de = "Standardgeschoss"',
                  r"comes with the English description and all of description_de, description_fr, description_it"),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription = "Ball"\ndescription_de = "Standardgeschoss"\n'
                  'description_fr = "Balle"\ndescription_it = "Palla"',  # Spanish since 2026-11-19
                  r"all of description_de, description_fr, description_it, description_es"),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription_de = "Standardgeschoss"\n'
                  'description_fr = "Balle"\ndescription_it = "Palla"\ndescription_es = "Ordinaria"', r"comes with the English description"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = ["USA"]', r"country 'USA' is not a code"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = []', r"countries lists one or more"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = ["US", "US"]', r"countries lists a country twice")]
        for old, new, pattern in cases:
            with self.subTest(new), Copy() as c:
                c.write(WIN, c.read(WIN) + first + TIP)
                self.assertEqual(c.problems(), [])
                c.edit(WIN, old, new)
                second = [i for i, l in enumerate(c.read(WIN).split("\n"), 1) if l == "[[colour_codes]]"][1]
                found = [p for p in c.problems() if re.search(pattern, p[2])]
                self.assertTrue(found, c.problems())
                self.assertGreaterEqual(found[0][1], second)  # the line in the second table
                self.assertOnlyProblems(c, WIN, r"colour_codes")
                self.assertEqual(len(c.problems()), 1)

    def test_colour_codes_are_listed_once_and_only_for_bullets(self):
        with Copy() as c:
            c.write(WIN, c.read(WIN) + TIP + TIP.replace("]\nsources", ']\ncountries = ["US"]\nsources'))
            self.assertOnlyProblems(c, WIN, r"black tip with this meaning is already on line \d+: list all its countries there")
        with Copy() as c:
            c.write(WIN, c.read(WIN) + TIP + TIP.replace('["black"]', '["red", "black"]'))
            self.assertEqual(c.problems(), [])
        with Copy() as c:  # the same colour on the base is another code
            c.write(WIN, c.read(WIN) + TIP + TIP.replace('"tip"', '"base"'))
            self.assertEqual(c.problems(), [])
        with Copy() as c:
            c.write(WIN, 'colour_codes = "black"\n' + c.read(WIN))
            self.assertOnlyProblems(c, WIN, r"each colour code is a \[\[colour_codes\]\] table")
        with Copy() as c:  # one problem for a [colour_codes] written with single brackets
            c.write(WIN, c.read(WIN) + TIP.replace("[[colour_codes]]", "[colour_codes]"))
            self.assertOnlyProblems(c, WIN, r"each colour code is a \[\[colour_codes\]\] table")
            self.assertEqual(len(c.problems()), 1)
        for rel in ("calibres/12-70.toml", "calibres/4-5-mm-diabolo-177.toml"):
            with self.subTest(rel), Copy() as c:
                c.write(rel, c.read(rel) + TIP)
                self.assertOnlyProblems(c, rel, r"\[\[colour_codes\]\] is only for cartridges with a bullet")

    def test_cannon_rounds_need_only_the_bullet_and_case_length(self):
        rel = "calibres/20x138-mm-b.toml"
        with Copy() as c:
            c.edit(rel, "rim = 26.86\nbelt = 28.48\nbase = 26.86\nshoulder = 25.49\nshoulder_at = 102.93\nneck_at = 128\nneck_base = 20.7\n", "")
            c.edit(rel, "shoulder_angle = 5.5\n", "")  # with the shoulder, so its cite goes too
            c.edit(rel, 'cite.shoulder_angle = ["https://municion.org/producto/20-x-138-b-rheinmetall-flak-30-38/"]\n', "")
            c.edit(rel, "overall_length = 202.7\n", "")
            c.write(rel, c.read(rel) + TIP)  # colour codes too
            self.assertEqual(c.problems(), [])
            c.edit(rel, "case_length = 138.0\n", "")
            self.assertOnlyProblems(c, rel, r"\[mm\] needs 'case_length'")
        with Copy() as c:  # nothing the apps read whole
            c.edit(rel, 'aliases = ["20x138b"', 'display_aliases = ["20 mm"]\naliases = ["20x138b"')
            self.assertOnlyProblems(c, rel, r"display_aliases are for the apps, which do not show cannon calibres yet")
        with Copy() as c:
            c.write(rel, c.read(rel) + '\n[primer]\nsize = "large-rifle"\nsources = []\n')
            self.assertOnlyProblems(c, rel, r"a cannon round has no \[primer\]")
        with Copy() as c:
            c.write(LOOK, c.read(LOOK) + '\n[[group]]\nname = "x"\ndiffer_by = ["bore"]\ncalibres = [".50 BMG", "20x138 mm B"]\n')
            self.assertOnlyProblems(c, LOOK, r"'20x138 mm B' is a cannon calibre, which the apps do not show yet")
        with Copy() as c:  # a group of cannon rounds only is fine: it stays out of the apps' groups
            c.write(LOOK, c.read(LOOK) + '\n[[group]]\nname = "20 mm"\ndiffer_by = ["gun"]\n'
                                         'calibres = ["20x139 mm", "20x139 mm FMK"]\n')
            self.assertEqual(c.problems(), [])
        with Copy() as c:  # other categories still need every measurement
            c.edit(WIN, "neck = 8.7\n", "")
            self.assertOnlyProblems(c, WIN, r"\[mm\] needs 'neck'")
        with Copy() as c:  # and a primer
            c.edit(WIN, '[primer]\nsize = "large-rifle"\nsources = ["https://en.wikipedia.org/wiki/.308_Winchester"]\n', "")
            self.assertOnlyProblems(c, WIN, r"needs a \[primer\] table")

    def test_cannon_rounds_are_20_to_57_mm(self):
        # Up to 57 mm, the largest rounds in Rapid Fire's table.
        rel = "calibres/57x348-mm-sr.toml"
        for bullet, ok in (("57.0", True), ("57.5", False), ("75.0", False)):
            with Copy() as c:
                c.edit(rel, "bullet = 57.0", f"bullet = {bullet}")
                if ok:
                    self.assertEqual(c.problems(), [])
                else:
                    self.assertProblem(c, rel, r"cannon holds the 20 to 57 mm cannon rounds",
                                       line=c.line_of(rel, f"bullet = {bullet}"))
        with Copy() as c:  # a heavy machine gun round belongs with the rifles
            c.edit("calibres/20x138-mm-b.toml", "bullet = 20.0", "bullet = 14.5")
            self.assertOnlyProblems(c, "calibres/20x138-mm-b.toml", r"20 to 57 mm cannon rounds: bullet is 20 to 57")

    def test_a_year_needs_a_source(self):
        with Copy() as c:
            c.edit(LR, 'year = 1887\nsources = ["https://en.wikipedia.org/wiki/.22_Long_Rifle"]', "year = 1887\nsources = []")
            self.assertProblem(c, LR, r"\[introduced\] year needs at least one source")

    def test_sources_written_as_text_are_one_problem(self):
        with Copy() as c:
            c.edit(LR, 'year = 1887\nsources = ["https://en.wikipedia.org/wiki/.22_Long_Rifle"]',
                   'year = 1887\nsources = "https://en.wikipedia.org/wiki/.22_Long_Rifle"')
            self.assertOnlyProblems(c, LR, r"\[introduced\] sources must be a list")
            self.assertEqual(len(c.problems()), 1)

    def test_measurements_need_a_sources_list(self):
        with Copy() as c:
            c.edit(LR, LR_MM + "\n", "")
            self.assertProblem(c, LR, r"\[mm\] needs a sources list")

    def test_unsourced_lists_the_measurements_without_a_source(self):
        self.assertEqual(cartridges.unsourced(".56-52 Spencer Necked"), ("shoulder_at",))
        self.assertEqual(cartridges.unsourced(".308 Winchester"), ())
        with Copy() as c:  # no source at all: every measurement is without one (no calibre is in that state today)
            c.edit(LR, LR_MM, "sources = []")
            self.assertEqual(load(c.dir)["UNSOURCED"][".22 LR"],
                             ("rim", "base", "neck", "case_length", "overall_length", "bullet"))
        for name, keys in cartridges.UNSOURCED.items():
            self.assertTrue(keys, name)
        for path in os.listdir(os.path.join(ROOT, "calibres")):  # the list replaced these notes (2026-11-14)
            if not path.endswith(".toml"):
                continue
            with open(os.path.join(ROOT, "calibres", path), encoding="utf-8") as f:
                self.assertNotIn("No source yet for", f.read(), path)
        wrong, whole = r"\[mm\] unsourced lists the measurements of this \[mm\]", r"when none has, leave it out"
        for old, new, problem in [
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = ["neck"]\n', None),
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = ["shoulder"]\n', wrong),  # not in this [mm]
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = ["neck", "neck"]\n', wrong),
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = ["sources"]\n', wrong),
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = []\n', wrong),
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = "neck"\n', wrong),
                ("neck = 5.7\n", 'neck = 5.7\nunsourced = ["rim", "base", "neck", "case_length", "overall_length", '
                                 '"bullet"]\n', whole),
                (LR_MM, 'unsourced = ["neck"]\nsources = []', whole),
                (LR_MM, 'unsourced = ["neck"]', r"\[mm\] needs a sources list")]:  # the one problem
            with self.subTest(new), Copy() as c:
                c.edit(LR, old, new)
                if problem:
                    self.assertProblem(c, LR, problem)
                    self.assertEqual(len(c.problems()), 1)
                else:
                    self.assertEqual(c.problems(), [])

    def test_missing_measurement(self):
        with Copy() as c:
            c.edit(LR, "neck = 5.7\n", "")
            self.assertProblem(c, LR, r"\[mm\] needs 'neck'")

    def test_shoulder_without_its_position(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = 39.62\n", "")
            self.assertProblem(c, WIN, r"both shoulder and shoulder_at")

    def test_shoulder_angle_in_mm(self):
        cite = 'cite.shoulder_angle = ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"]'
        mm_sources = '"book:cotw-18 p. 176",\n  "https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf",'
        for old, new, problem in [
                (cite, "", None),  # the [mm] sources then cover the angle
                (cite + "\n", "", None),
                (cite, 'cite.shoulder_angle = ["book:cotw-18 p. 176", '
                       '"https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"]', r"repeats the \[mm\] sources"),
                (cite, 'cite.neck_angle = ["https://example.org/a"]', r"cite.neck_angle names no measurement"),
                (cite, 'cite.sources = ["https://example.org/a"]', r"cite.sources names no measurement"),
                (cite, 'cite.shoulder_angle = []', r"\[mm\] cite.shoulder_angle needs at least one source"),
                (cite, 'cite.shoulder_angle = ["book:cotw-18 p. 176", "book:cotw-18 p. 176"]', r"cite.shoulder_angle lists a source twice"),
                (cite, 'cite.shoulder_angle = ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf", '
                       '"book:cotw-18 p. 176"]', r"repeats the \[mm\] sources"),  # in another order
                (cite, 'cite.neck = ["https://example.org/a"]', None),  # any measurement may name its own
                (cite, 'unsourced = 5', r"\[mm\] unsourced lists the measurements"),  # reported, no crash
                (cite, 'cite.shoulder_angle = ["example.org"]', r"is not a https:// web address"),
                (cite, 'cite = "https://example.org/a"', r"cite names a measurement's own sources"),
                (cite, 'unsourced = ["shoulder_angle"]', r"shoulder_angle needs a source"),
                (cite, 'unsourced = ["shoulder_angle"]\n' + cite, r"in unsourced and has a cite"),
                ("shoulder_angle = 20", "shoulder_angle = 0", r"must be a number above 0"),
                ("shoulder_angle = 20", "shoulder_angle = 90", r"above 0 and below 90"),
                ("shoulder_angle = 20", 'shoulder_angle = "20"', r"must be a number")]:
            with self.subTest(new), Copy() as c:
                c.edit(WIN, old, new)
                if problem:
                    self.assertProblem(c, WIN, problem)
                else:
                    self.assertEqual(c.problems(), [])
        with Copy() as c:  # [mm] without sources: the cited angle still has one
            c.edit(WIN, mm_sources, "")
            self.assertEqual(c.problems(), [])
            t = load(c.dir)
            self.assertNotIn("shoulder_angle", t["UNSOURCED"][".308 Winchester"])
            self.assertEqual(t["SOURCES"][(".308 Winchester", "shoulder_angle")],
                             ["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"])
        with Copy() as c:  # cite is for [mm] only
            c.edit(WIN, "\n[case_head]\n", '\n[case_head]\ncite.rim_thickness = ["https://example.org/a"]\n')
            self.assertProblem(c, WIN, r"unknown key 'cite' in \[case_head\]")
        with Copy() as c:  # no source anywhere
            c.edit(WIN, cite + "\n", "")
            c.edit(WIN, mm_sources, "")
            self.assertProblem(c, WIN, r"\[mm\] shoulder_angle needs a source")
        with Copy() as c:  # a straight case has no shoulder angle
            c.edit("calibres/45-acp.toml", "case_length", "shoulder_angle = 20\ncase_length")
            self.assertProblem(c, "calibres/45-acp.toml", r"shoulder_angle is for bottleneck cases")
        with Copy() as c:  # the old table
            c.edit(WIN, "\n[case_head]", "\n[shoulder_angle]\ndegrees = 20\nsources = []\n\n[case_head]")
            self.assertProblem(c, WIN, r"\[shoulder_angle\] is now part of \[mm\]")

    def test_neck_start(self):
        self.assertEqual(cartridges.NECKS[".308 Winchester"], (43.48, 8.72))  # C.I.P. L2 and H1
        acp = "calibres/45-acp.toml"
        with Copy() as c:
            c.edit(WIN, "neck_at = 43.48", "neck_at = 52.0")      # past the mouth (case 51.2)
            c.edit(WIN, "neck_base = 8.72", "neck_base = 8.5")    # 0.2 under the neck of 8.7
            c.edit(acp, "neck = 12.01\n", "neck = 12.01\nneck_at = 20.0\n")  # a straight case
            self.assertProblem(c, WIN, r"neck_at 52.0 is where the neck starts")
            self.assertProblem(c, WIN, r"neck_base 8.5 is the neck's diameter")
            self.assertProblem(c, acp, r"neck_at and neck_base are for bottleneck cases")
        with Copy() as c:
            c.edit(WIN, "neck_base = 8.72\n", "")
            self.assertProblem(c, WIN, r"neck_at and neck_base together")
        with Copy() as c:
            c.edit(WIN, "neck_base = 8.72", "neck_base = 8.56")   # within NECK_SLACK of the neck
            self.assertEqual(c.problems(), [])

    def test_nose_length(self):
        self.assertEqual(cartridges.nose("5.6 mm GP 90"), 10.6)  # the AECC 5.56x45 drawing
        self.assertEqual(cartridges.nose("7.5 mm Kadettenpatrone"), 6.4)  # a round nose, the maintainer's round
        self.assertIsNone(cartridges.nose(".308 Winchester"))
        colt, acp = "calibres/45-colt.toml", "calibres/45-acp.toml"
        with Copy() as c:
            c.edit(WIN, "bullet = 7.85\n", "bullet = 7.85\nnose = 20.0\n")   # 19.92 out of the case
            c.edit(colt, "bullet = 11.53\n", "bullet = 11.53\nnose = 8.0\n")  # a flat point
            c.edit(acp, "bullet = 11.48\n", "bullet = 11.48\nnose = 5.0\n")  # a round nose under half its width
            self.assertProblem(c, WIN, r"nose 20.0 is longer than the bullet out of the case \(19.92")
            self.assertProblem(c, colt, r'nose is for pointed and round bullets \(profile = "spitzer" or "round"\)')
            self.assertProblem(c, acp, r"nose 5.0 is shorter than half the bullet width \(5.74\): that is no round nose")
        with Copy() as c:
            c.edit(WIN, "bullet = 7.85\n", "bullet = 7.85\nnose = 5.0\n")   # under the 7.85 width
            self.assertProblem(c, WIN, r"nose 5.0 is shorter than the bullet width \(\S+\): that is no pointed nose")
        for path, ok in ((WIN, "15.0"), (WIN, "19.92"), (acp, "6.0")):  # up to all of the bullet out of the case
            with Copy() as c:
                width = "7.85" if path == WIN else "11.48"
                c.edit(path, f"bullet = {width}\n", f"bullet = {width}\nnose = {ok}\n")
                self.assertEqual(c.problems(), [])
        self.assertEqual(cartridges.sources("5.6 mm GP 90", "nose"), ["https://municion.org/producto/556-x-45-otan/"])
        self.assertEqual(cartridges.sources("7.5 mm Kadettenpatrone", "nose"), ["measured:ravench 2026-11-08"])

    def test_flat_width(self):
        # The flat of a flat nose is a field too (the .45 Colt's AECC drawing: about 5 of 11.53).
        self.assertEqual(cartridges.flat(".45 Colt"), 5.0)
        self.assertEqual(cartridges.sources(".45 Colt", "flat"), ["https://municion.org/producto/45-long-colt-d-a/"])
        self.assertIsNone(cartridges.flat(".308 Winchester"))
        colt = "calibres/45-colt.toml"
        with Copy() as c:
            c.edit(WIN, "bullet = 7.85\n", "bullet = 7.85\nflat = 3.0\n")  # a pointed bullet
            c.edit(colt, "flat = 5.0", "flat = 11.53")                    # as wide as the bullet
            self.assertProblem(c, WIN, r'flat is for flat-nosed bullets \(profile = "flat"\)')
            self.assertProblem(c, colt, r"flat 11.53 is not narrower than the bullet \(11.53\)")
        with Copy() as c:
            c.edit(colt, "flat = 5.0", "flat = 0")
            self.assertProblem(c, colt, r"flat must be a number above 0")
        with Copy() as c:
            c.edit(colt, "flat = 5.0", "flat = 11.5")                     # just under the bullet
            self.assertEqual(c.problems(), [])

    # Calibres whose [mm] shoulder is not the sheet's P2, so the shoulder drawn at the sheet's angle ends short of
    # the sheet's L2. Their shoulders come from other pages; fix them to P2 and empty this.
    SHOULDER_NOT_P2 = {".22 Remington Jet", ".35 Remington", ".35 Winchester", ".400/350 Nitro Express", ".45-75 Winchester", "8x56 mm R Mannlicher", ".500/465 Nitro Express"}

    def test_neck_start_agrees_with_the_shoulder_angle(self):
        # Where the angle and the measurements come from the same sheet, the shoulder run in from shoulder_at at that
        # angle reaches neck_base at neck_at (a misread L2 or H1 shows up here), and the neck is at least 1.2 mm long.
        # An AECC drawing listed after another source (Cartridges of the World) gives the neck, not that source's
        # shoulder, so it is not held to it.
        entries = {e["name"]: e for _, items in cartridges.ALL_CATALOGUE for e in items}
        checked = set()
        for name, (at, base) in cartridges.NECKS.items():
            e = entries[name]
            self.assertGreaterEqual(e["case"] - at, 1.2, name)
            if name not in cartridges.SHOULDER_ANGLES:
                continue
            degrees, url = cartridges.SHOULDER_ANGLES[name]
            mm = cartridges.sources(name, "mm")
            if url not in mm or ("municion.org" in url and url != mm[0]):
                continue
            run = (e["shoulder"] - base) / 2 / math.tan(math.radians(degrees))
            off = abs(at - e["sh_at"] - run) > 0.3
            self.assertEqual(off, name in self.SHOULDER_NOT_P2, f"{name}: L2 {at}, shoulder ends at {e['sh_at'] + run:.2f}")
            checked.add(name)
        self.assertGreater(len(checked), 80)

    def test_a_sheet_names_the_origin_of_one_calibre(self):
        # A C.I.P. sheet shared by several calibres counts as an origin source only for the one it is titled after.
        seen = {}
        for name, urls in ((n, cartridges.sources(n, "origin")) for n in cartridges.ORIGIN):
            for u in urls:
                if "cip-bobp.org" in u:
                    self.assertNotIn(u, seen, f"{name} and {seen.get(u)}")
                    seen[u] = name
        self.assertEqual(seen["https://bobp.cip-bobp.org/uploads/tdcc/tab-i/tabical-en-page125.pdf"], ".308 Winchester")

    def test_groove_width(self):
        self.assertEqual(cartridges.GROOVE_WIDTHS[".308 Winchester"][0], 1.4)  # C.I.P. e min
        self.assertEqual(cartridges.GROOVE_WIDTHS["25x137 mm"][0], 4.09)  # AECC drawing GW
        with Copy() as c:
            # ramp_top 3.85 less the 1.37 rim and the 36° ramp from 10.39 up to the 11.9 base leaves 1.44
            c.edit(WIN, "groove_width = 1.4", "groove_width = 1.6")
            self.assertProblem(c, WIN, r"groove_width is the groove's floor: from 0.3 to the 1.59")
        with Copy() as c:
            c.edit(WIN, "groove_width = 1.4", "groove_width = 0.1")
            self.assertProblem(c, WIN, r"groove_width is the groove's floor")
        with Copy() as c:
            c.edit(WIN, "ramp_top = 3.85\ngroove_diameter = 10.39\nramp_angle = 36.0\n", "")
            self.assertProblem(c, WIN, r"groove_width goes with the groove")

    def test_cannon_neck(self):
        # A cannon round's [mm] (shape partial) may give the neck start too: the 25x137 mm's AECC drawing has
        # NL 12.4 and NØ 26.14, so neck_at is case_length 137 less 12.4.
        self.assertEqual(cartridges.NECKS["25x137 mm"], (124.6, 26.14))

    def test_a_case_narrows_from_its_base_to_its_mouth(self):
        acp, rem, blank = "calibres/45-acp.toml", "calibres/223-remington.toml", "calibres/22-sh-5-6-11.toml"
        with Copy() as c:
            c.edit(WIN, "shoulder = 11.5", "shoulder = 11.95")  # over its base of 11.9
            c.edit(rem, "neck = 6.43", "neck = 9.03")           # over its shoulder of 9.0
            c.edit(blank, "mouth = 3.4", "mouth = 5.8")         # a blank's crimp over its base of 5.74
            c.edit(acp, "neck = 12.01", "neck = 12.15")         # a straight case: 0.06 over its base of 12.09
            c.edit(LR, "neck = 5.7", "neck = 5.75")             # 0.05 over its base is still within MOUTH_SLACK
            c.edit("calibres/30-06-springfield.toml", "base = 12.0", "base = -12.0")  # reported as a number only
            why = ": a case narrows from its base to its mouth"
            self.assertEqual(sorted(p for p in c.problems() if "narrows" in p[2]), [
                (blank, c.line_of(blank, "mouth ="), "[mm] mouth 5.8 is wider than base 5.74" + why),
                (rem, c.line_of(rem, "neck ="), "[mm] neck 9.03 is wider than shoulder 9.0" + why),
                (WIN, c.line_of(WIN, "shoulder ="), "[mm] shoulder 11.95 is wider than base 11.9" + why),
                (acp, c.line_of(acp, "neck ="), "[mm] neck 12.15 is more than 0.05 wider than base 12.09" + why),
            ])

    def test_a_crimp_length_is_drawable_and_cited(self):
        hilti = "calibres/6-8-11.toml"
        for value, shown in (("11.0", "11.0"), ("0.2", "0.2")):  # into the rim, or folding back under the turn-in
            with self.subTest(value), Copy() as c:
                c.edit(hilti, "crimp_length = 4.3", "crimp_length = " + value)
                self.assertProblem(c, hilti, rf"crimp_length {shown} is the crimp's length from the mouth back: 0.5 to "
                                             rf"half the length \(5.5\)")
        with Copy() as c:
            c.edit(hilti, "crimp_length = 4.3", "crimp_length = 0")
            found = [p for p in c.problems() if "crimp_length" in p[2]]
            self.assertEqual(len(found), 1, found)  # only the number check, not the range too
        with Copy() as c:  # no sheet gives it: its own cite or unsourced, never the [mm] sources
            c.edit(hilti, 'cite.crimp_length = ["measured:ravench 2026-11-20"]\n', "")
            self.assertProblem(c, hilti, r"crimp_length comes from no sheet")
        with Copy() as c:
            c.edit(WIN, "bullet = ", "crimp_length = 3.0\nbullet = ")
            self.assertProblem(c, WIN, r"crimp_length")  # only blanks have a crimp

    def test_names_write_numbers_and_units_one_way(self):
        for name, pattern in [("7.62x51mm Test", r"a space between the number and the unit"),
                              (".450/400 Test 3inch", r"a space between the number and the unit"),
                              (".450/400 Test 3¼inch", r"a space between the number and the unit"),
                              ("9 MM Test", r"the unit in lower case"),
                              ("9X19 mm Test", r"a plain lower-case x"),
                              ("7,62x51 mm Test", r"a decimal point, not a comma"),
                              ("7.62×51 mm Test", r"a plain lower-case x"),
                              ("7.62 x 51 mm Test", r"no spaces around the x")]:
            with self.subTest(name), Copy() as c:
                text = c.read(WIN).replace('name = ".308 Winchester"', f"name = {name!r}")
                rel = f"calibres/{slug(name)}.toml"
                c.write(rel, re.sub(r"(?m)^aliases = .*$", "aliases = []", text))
                self.assertOnlyProblems(c, rel, f"the name '{re.escape(name)}' needs {pattern}")

    def test_file_name_must_follow_the_name(self):
        with Copy() as c:
            os.rename(c.path(LR), c.path("calibres/long-rifle.toml"))
            self.assertProblem(c, "calibres/long-rifle.toml", r"must be called 22-lr.toml")

    def test_broken_toml_names_the_line(self):
        with Copy() as c:
            c.edit(LR, 'kind = "rimfire"', 'kind = "rimfire')
            self.assertProblem(c, LR, r"not valid TOML")

    def test_alias_used_by_two_calibres(self):
        with Copy() as c:
            c.edit(WIN, 'aliases = ["308", "308win"]', 'aliases = ["308", "308win", "22lr"]')
            found = c.problems()
            self.assertTrue(any("'22lr' is also an alias of" in p[2] for p in found), found)

    def test_primer_on_a_rimfire_and_none_on_a_centrefire(self):
        with Copy() as c:
            c.edit(LR, "[bullet]", '[primer]\nsize = "small-rifle"\nsources = []\n\n[bullet]')
            c.edit(WIN, '[primer]\nsize = "large-rifle"', '[primerx]\nsize = "large-rifle"')
            self.assertProblem(c, LR, r"a rimfire calibre has no primer")
            self.assertProblem(c, WIN, r"needs a \[primer\] table", line=False)

    def test_miniature_primer_has_its_own_diameter(self):
        with Copy() as c:
            k = "calibres/2-7-mm-kolibri.toml"
            c.edit(k, "diameter = 2.2\n", "")
            c.edit(WIN, 'size = "large-rifle"', 'size = "large-rifle"\ndiameter = 12')
            self.assertProblem(c, k, r"'miniature' size needs its diameter")
            self.assertProblem(c, WIN, r"within 0.5 of its size's nominal one")
        with Copy() as c:
            c.edit("calibres/2-7-mm-kolibri.toml", "diameter = 2.2", "diameter = 4.5")
            c.edit(WIN, 'size = "large-rifle"', 'size = "large-rifle"\ndiameter = 5.5')
            self.assertOnlyProblems(c, "calibres/2-7-mm-kolibri.toml", r"for a miniature primer")
        with Copy() as c:
            k = "calibres/2-7-mm-kolibri.toml"
            c.edit(k, 'sources = ["https://municion.org/producto/27-mm-kolibri/"]', "sources = []")
            self.assertOnlyProblems(c, k, r"a measured diameter needs a source")

    def test_a_case_material_needs_a_source(self):
        # [case] is written only where a source shows or names the material, brass too; without it the
        # material is unknown and the outline draws brass.
        self.assertNotIn(".308 Winchester", cartridges.CASES)
        self.assertEqual(cartridges.case_material(".308 Winchester"), cartridges.BRASS)
        with Copy() as c:
            c.edit(WIN, "[current_cases]", '[case]\nmaterial = "brass"\nsources = []\n\n[current_cases]')
            c.edit("calibres/12-70.toml", "[mm]", '[case]\nmaterial = "brass"\nsources = ["https://example.org"]\n\n[mm]')
            self.assertProblem(c, WIN, r"\[case\] needs at least one source")
            self.assertProblem(c, "calibres/12-70.toml", r"a shot calibre has no metal case")

    def test_today_differs_from_the_original(self):
        gp11, makarov = "calibres/7-5x55-mm-swiss-gp-11.toml", "calibres/9x18-mm-makarov.toml"
        today = '\n\n[today]\n# A note.\n{}\nsources = ["https://example.org"]\n'
        with Copy() as c:
            c.edit(gp11, 'jacket = "copper"', 'jacket = "cupronickel"')
            c.edit(makarov, 'case = "steel"', 'case = "brass"')
            c.write(WIN, c.read(WIN) + today.format('case = "aluminium"'))
            c.write(LR, c.read(LR) + today.format('jacket = "copper"'))
            c.write("calibres/9x19-mm.toml", c.read("calibres/9x19-mm.toml") + today.format('jacket = "gold"'))
            c.write("calibres/45-acp.toml", c.read("calibres/45-acp.toml") + today.format(""))
            self.assertProblem(c, gp11, r"\[today\] jacket is the original one")
            self.assertProblem(c, makarov, r"\[today\] case is the original one")
            self.assertProblem(c, WIN, r"\[today\] case is one of the \[current_cases\] materials")
            self.assertProblem(c, LR, r"only a bullet with a jacket .* has a \[today\] jacket")
            self.assertProblem(c, "calibres/9x19-mm.toml", r"\[today\] jacket 'gold' is not one of copper, cupronickel, steel")
            self.assertProblem(c, "calibres/45-acp.toml", r"\[today\] names the jacket or the case")
        with Copy() as c:  # no note above the key; no metal case
            c.edit(makarov, "# Most rounds sold today are Russian, in lacquered, zinc- or polymer-coated steel cases.\n", "")
            c.write("calibres/12-70.toml", c.read("calibres/12-70.toml") + today.format('case = "steel"'))
            self.assertProblem(c, makarov, r"a comment above \[today\] case says what the source shows")
            self.assertProblem(c, "calibres/12-70.toml", r"a shot calibre has no metal case: no \[today\] case")

    def test_every_bullet_names_its_type(self):
        ball = "calibres/50-rundkugel-490.toml"
        HORNADY_490 = 'sources = ["https://www.hornady.com/muzzleloading/browse/50-cal-490-lead-balls"]'
        with Copy() as c:
            c.edit(LR, '[bullet]\ntype = "lead"', '[projectile]\nmaterial = "lead"')
            c.edit(WIN, 'type = "softpoint"', 'type = "plastic"')
            c.edit(ball, 'type = "lead"', 'type = "softpoint"')
            c.edit("calibres/12-70.toml", "[mm]", '[bullet]\ntype = "lead"\nsources = []\n\n[mm]')
            self.assertProblem(c, LR, r"unknown table \[projectile\]")
            self.assertProblem(c, LR, r'needs a \[bullet\] table: type = "jacketed"', line=False)
            self.assertProblem(c, WIN, r"a rimless calibre's \[bullet\] type is one of jacketed, lead")
            self.assertProblem(c, ball, r"a ball calibre's \[bullet\] type is one of lead, steel, plastic")
            self.assertProblem(c, "calibres/12-70.toml", r"shot shells, blanks and cannon rounds have no \[bullet\]")
        blank, cannon = "calibres/22-sh-5-6-11.toml", "calibres/20x102-mm.toml"
        pak = "calibres/9-mm-pa-blanc.toml"
        with Copy() as c:
            c.edit(ball, f'type = "lead"\n{HORNADY_490}', 'type = "steel"\nsources = []')
            c.edit("calibres/6-mm-airsoft-bb.toml", 'type = "plastic"\nsources = ["https://en.wikipedia.org/wiki/Airsoft_pellets"]',
                   'type = "plastic"\nsources = []')
            c.edit(blank, "[mm]", '[bullet]\ntype = "lead"\nsources = []\n\n[mm]')
            c.edit(cannon, "[mm]", '[bullet]\ntype = "jacketed"\nsources = []\n\n[mm]')
            c.edit(pak, "[mm]", '[bullet]\ntype = "jacketed"\nsources = []\n\n[mm]')
            self.assertProblem(c, ball, r"\[bullet\] type 'steel' needs a source")
            self.assertProblem(c, "calibres/6-mm-airsoft-bb.toml", r"\[bullet\] type 'plastic' needs a source")
            for rel in (blank, cannon, pak):
                self.assertProblem(c, rel, r"shot shells, blanks and cannon rounds have no \[bullet\]")
        with Copy() as c:
            c.edit(ball, f'[bullet]\ntype = "lead"\n{HORNADY_490}\n', '')
            self.assertProblem(c, ball, r'needs a \[bullet\] table: type = "lead"', line=False)

    def test_a_jacket_other_than_copper(self):
        with Copy() as c:
            c.edit(LR, '[bullet]\ntype = "lead"', '[bullet]\ntype = "lead"\njacket = "cupronickel"')
            c.edit(WIN, 'type = "softpoint"', 'type = "softpoint"\njacket = "silver"')
            self.assertProblem(c, LR, r"only a bullet with a jacket \(jacketed, softpoint, polymer, hollowpoint\)")
            self.assertProblem(c, WIN, r"\[bullet\] jacket 'silver' is not one of cupronickel, steel")
        with Copy() as c:
            c.edit(WIN, 'type = "softpoint"', 'type = "softpoint"\njacket = "steel"')
            self.assertEqual(c.problems(), [])

    def test_a_patch_length(self):
        vetterli = "calibres/10-4x38-mm-r-vetterli.toml"
        noted = 'type = "paper"\n# Patch: measured on a round of 1878\npatch_length = '
        with Copy() as c:
            c.edit(vetterli, 'type = "paper"', noted + "9.4")
            self.assertEqual(c.problems(), [])
            self.assertEqual(load(c.dir)["PATCH_LENGTHS"]["10.4x38 mm R Vetterli"][0], 9.4)
        with Copy() as c:
            c.edit(vetterli, 'type = "paper"', noted + "18.1")
            c.edit(WIN, 'type = "softpoint"', 'type = "softpoint"\npatch_length = 5')
            self.assertProblem(c, vetterli, r"patch_length is the paper showing above the case mouth in mm: above 0 "
                                            r"and below the exposed bullet \(18.01\)",
                               line=c.line_of(vetterli, "patch_length ="))
            self.assertProblem(c, WIN, r'only a paper-patched bullet \(type = "paper"\) of a cartridge has a \[bullet\] patch_length$')
        with Copy() as c:
            gp, ball = "calibres/7-5x53-5-mm-swiss-patrone-modell-1890.toml", "calibres/36-rundkugel-375.toml"
            c.edit(gp, 'type = "paper"', 'type = "paper"\npatch_length = 5')
            c.edit(ball, 'type = "lead"', 'type = "lead"\npatch_length = 2')
            c.edit(vetterli, 'type = "paper"', noted + "0")
            self.assertProblem(c, gp, r"GP 1890's patched profile draws its paper to the 1892 drawing: no patch_length")
            self.assertProblem(c, ball, r"only a paper-patched bullet .* of a cartridge has a \[bullet\] patch_length$")
            self.assertProblem(c, vetterli, r"patch_length is the paper showing above the case mouth")
        with Copy() as c:
            c.edit(vetterli, 'type = "paper"\nsources = ["https://en.wikipedia.org/wiki/.41_Swiss"]',
                   noted + "9.4\nsources = []")
            self.assertProblem(c, vetterli, r"\[bullet\] a patch_length needs a source")
        with Copy() as c:  # the bullet's sources name the type; the length's own source goes in a comment above it
            c.edit(vetterli, 'type = "paper"', 'type = "paper"\npatch_length = 9.4')
            self.assertOnlyProblems(c, vetterli, r"a comment above patch_length names the source")
        with Copy() as c:  # a mistyped length is one problem of the [mm] keys, not a crash of the range check
            c.edit(vetterli, "overall_length = 56.22", "overal_length = 56.22")
            c.edit(vetterli, 'type = "paper"', noted + "9.4")
            self.assertProblem(c, vetterli, r"overall_length")
            self.assertFalse([p for p in c.problems() if "patch_length" in p[2]], c.problems())

    def test_order_toml_names_without_a_file(self):
        with Copy() as c:
            c.edit("order.toml", '".22 LR"', '".22 LRR"')
            self.assertProblem(c, "order.toml", r"'.22 LRR' is not a calibre whose first category is rimfire \(did you mean \".22 LR\"\?\)")
        with Copy() as c:
            c.edit("order.toml", '  ".308 Winchester",\n', '  ".308 Winchester",\n  ".22 LR",\n')
            self.assertProblem(c, "order.toml", r"'.22 LR' is not a calibre whose first category is rifle \(its first category is rimfire\)")

    def test_an_empty_order_toml_does_not_empty_the_catalogue(self):
        with Copy() as c:
            c.write("order.toml", "# nothing\n")
            found = c.problems()
            self.assertEqual(len(found), len(cartridges.CATEGORIES), found)
            self.assertTrue(all(p[2].startswith("misses the category") for p in found), found)
        with Copy() as c:
            shutil.rmtree(c.path("calibres"))
            self.assertProblem(c, "calibres", r"missing", line=False)

    def test_a_broken_countries_toml_is_reported_there_only(self):
        for text, pattern in [("# nothing\n", r"lists no countries"),
                              ('[CH]\nflag = "x"\n', r"\[CH\] needs name"),
                              ('[CH]\nname = "Switzerland"\nde = "Schweiz"\nfr = "Suisse"\nes = "Suiza"\n', r"\[CH\] needs 'it'"),
                              ('[CH]\nname = "Switzerland"\nde = "Schweiz"\nfr = "Suisse"\nit = "Svizzera"\n', r"\[CH\] needs 'es'"),
                              ('[CH]\nname = "Switzerland"\nde = ""\nfr = "Suisse"\nit = "Svizzera"\nes = "Suiza"\n', r"\[CH\] de must be the name"),
                              ('[CH]\nname = "Switzerland"\nde = "Schweiz"\nfr = "Suisse"\nit = "Svizzera"\nes = "Suiza"\nflag = 5\n', r"\[CH\] flag must be")]:
            with self.subTest(text), Copy() as c:
                c.write("countries.toml", text)
                self.assertOnlyProblems(c, "countries.toml", pattern)

    def test_a_misspelt_category_in_order_toml(self):
        with Copy() as c:
            c.edit("order.toml", "air-gun = [", "air-gn = [")
            found = c.problems()
            self.assertEqual(len(found), 2, found)
            self.assertProblem(c, "order.toml", r"'air-gn' is not one of rimfire, handgun, .* \(did you mean \"air-gun\"\?\)")
            self.assertProblem(c, "order.toml", r"misses the category 'air-gun'", line=False)

    def test_the_old_german_category_names_point_to_the_english_ones(self):
        with Copy() as c:
            c.edit("order.toml", "rifle = [", "Langwaffe = [")
            self.assertProblem(c, "order.toml", r"'Langwaffe' is not one of .* \(write rifle for Langwaffe\)")
        with Copy() as c:
            c.edit(WIN, 'guns = ["rifle"]', 'guns = ["Langwaffe"]')
            self.assertOnlyProblems(c, WIN, r"gun 'Langwaffe' is not one of .* \(write rifle for Langwaffe\)")

    def test_guns_problems(self):
        old = 'guns = ["rifle"]'
        for new, pattern in [('guns = []', r"guns names at least one gun \(only a black-powder or rimfire round"),
                             ('guns = "rifle"', r"guns must be a list of handgun, rifle, shotgun, air-gun, cannon"),
                             ('guns = ["rifles"]', r"gun 'rifles' is not one of handgun, .* \(did you mean \"rifle\"\?\)"),
                             ('guns = ["black-powder"]', r"gun 'black-powder' is not one of .* \(write black_powder = true"),
                             ('guns = ["Schwarzpulver"]', r"gun 'Schwarzpulver' is not one of .* \(write black_powder = true"),
                             ('guns = ["rimfire", "rifle"]', r"gun 'rimfire' is not one of .* \(a rimfire round has kind"),
                             ('guns = ["rifle", "rifle"]', r"guns lists a gun twice"),
                             ('guns = ["rifle"]\nblack_powder = "yes"', r"black_powder must be true or false"),
                             ('categories = ["rifle"]', r"categories is now worked out from guns, black_powder and kind"),
                             ('', r"needs 'guns'")]:
            with self.subTest(new), Copy() as c:
                c.edit(WIN, old, new)
                self.assertProblem(c, WIN, pattern, line=bool(new))

    def test_black_powder_on_a_cartridge_still_in_regular_production_is_a_problem(self):
        problem = r"black_powder is only for a cartridge that is no longer in regular production"
        colt, short, minie, pellet = (f"calibres/{n}.toml" for n in ("45-colt", "380-short", "58-minie", "4-5-mm-diabolo-177"))
        with Copy() as c:
            c.edit(colt, 'guns = ["handgun", "rifle"]', 'guns = ["handgun", "rifle"]\nblack_powder = true')
            self.assertProblem(c, colt, problem, line=c.line_of(colt, "black_powder"))
        with Copy() as c:  # a black-powder cartridge that someone makes again leaves the shelf
            c.edit(short, "obsolete = true\n", "")
            self.assertProblem(c, short, problem, line=c.line_of(short, "black_powder"))
        with Copy() as c:  # a muzzle-loader's bullet may still be made and is black powder all the same
            c.edit(minie, "obsolete = true\n", "")
            self.assertEqual(c.problems(), [])
        with Copy() as c:  # an air-gun pellet is no muzzle-loader's bullet
            c.edit(pellet, 'guns = ["air-gun"]', 'guns = ["air-gun"]\nblack_powder = true')
            self.assertProblem(c, pellet, problem)
        for old, new, said in (('guns = ["handgun", "rifle"]', 'guns = ["handgun", "rifle"]\nobsolete = "true"', r"obsolete must be"),
                               ('kind = "rimmed"', 'kind = "rimed"', r"kind 'rimed' is not one of")):
            with self.subTest(new), Copy() as c:  # a wrong obsolete or kind is reported as that, not as this too
                c.edit(colt, 'guns = ["handgun", "rifle"]', 'guns = ["handgun", "rifle"]\nblack_powder = true')
                c.edit(colt, old, new)
                self.assertProblem(c, colt, said)
                self.assertFalse([p for p in c.problems() if re.search(problem, p[2])])

    def test_a_black_powder_or_rimfire_round_may_name_no_gun(self):
        with Copy() as c:
            c.edit(LR, 'guns = ["rifle", "handgun"]', 'guns = []')
            c.edit("calibres/380-short.toml", 'guns = ["rifle", "handgun"]', 'guns = []')
            t = load(c.dir)
            self.assertEqual(t["CALIBRE_CATEGORIES"][".22 LR"], ("Randfeuer",))
            self.assertEqual(t["CALIBRE_CATEGORIES"][".380 Short"], ("Schwarzpulver",))
            self.assertEqual(t["CALIBRE_GUNS"][".380 Short"], ())

    def test_a_bad_gun_on_a_cannon_round_is_its_only_problem(self):
        rel = "calibres/20x138-mm-b.toml"
        with Copy() as c:
            c.edit(rel, 'guns = ["cannon"]', 'guns = ["cannon", "rifles"]')
            self.assertOnlyProblems(c, rel, r"'rifles' is not one of")

    def test_cannon_rounds_are_fired_by_nothing_else(self):
        rel = "calibres/20x138-mm-b.toml"
        for new in ('guns = ["cannon", "rifle"]', 'guns = ["rifle", "cannon"]', 'guns = ["cannon"]\nblack_powder = true'):
            with self.subTest(new), Copy() as c:
                c.edit(rel, 'guns = ["cannon"]', new)
                self.assertProblem(c, rel, r"cannon is not in the apps yet: a calibre fired by it is fired by nothing else")

    def test_categories_of_an_unknown_name(self):
        self.assertEqual(cartridges.categories("no such calibre"), ())
        self.assertEqual(cartridges.guns("no such calibre"), ())
        self.assertFalse(cartridges.is_black_powder("no such calibre"))

    def test_a_calibre_is_listed_under_its_category_only(self):
        with Copy() as c:
            c.edit(WIN, 'guns = ["rifle"]', 'guns = ["rifle", "handgun"]')
            t = load(c.dir)
            self.assertEqual(t["CALIBRE_CATEGORIES"][".308 Winchester"], ("Langwaffe", "Kurzwaffe"))
            self.assertEqual(t["CALIBRE_GUNS"][".308 Winchester"], ("rifle", "handgun"))
            self.assertEqual(t["ALL_CATALOGUE"], cartridges.ALL_CATALOGUE)  # listed once, as before
            c.edit(WIN, 'guns = ["rifle", "handgun"]', 'guns = ["rifle"]\nblack_powder = true\nobsolete = true')
            self.assertProblem(c, "order.toml", r"'.308 Winchester' is not a calibre whose first category is rifle "
                                                r"\(its first category is black-powder\)")
            c.edit("order.toml", '  ".308 Winchester",\n', "")
            t = load(c.dir)
            catalogue = dict(t["ALL_CATALOGUE"])
            self.assertIn(".308 Winchester", [s["name"] for s in catalogue["Schwarzpulver"]])
            self.assertNotIn(".308 Winchester", [s["name"] for s in catalogue["Langwaffe"]])
            self.assertIn(".308 Winchester", t["BLACK_POWDER"])

    def test_a_category_without_calibres(self):
        with Copy() as c:
            for fn in os.listdir(c.path("calibres")):
                if c.read(f"calibres/{fn}").count('guns = ["shotgun"'):
                    os.remove(c.path(f"calibres/{fn}"))
            self.assertProblem(c, "order.toml", r"no calibre has 'shotgun' as its first category")

    def test_calibre_files_are_not_in_folders(self):
        with Copy() as c:
            os.makedirs(c.path("calibres/rifle"))
            os.rename(c.path(WIN), c.path("calibres/rifle/308-winchester.toml"))
            self.assertProblem(c, "calibres/rifle", r"calibre files go straight into calibres/", line=False)

    def test_profile_today(self):
        rel = "calibres/303-british.toml"
        with Copy() as c:
            c.edit(rel, 'profile_today = "spitzer"', 'profile_today = "round"')
            self.assertOnlyProblems(c, rel, r"profile_today is the same as profile: leave it out")
        with Copy() as c:
            c.edit(rel, 'profile_today = "spitzer"', 'profile_today = "spitz"')
            self.assertOnlyProblems(c, rel, r"profile_today 'spitz' is not one of .*did you mean \"spitzer\"")
            self.assertProblem(c, rel, "profile_today", line=c.line_of(rel, "profile_today"))

    def test_lookalike_groups_name_existing_calibres_once(self):
        with Copy() as c:
            c.edit(LOOK, '"7.62x51 mm NATO"]', '"7.62x51 mm NAT0"]')
            self.assertProblem(c, LOOK, r"'7.62x51 mm NAT0' is not a calibre \(did you mean \"7.62x51 mm NATO\"\?\)",
                               line=c.line_of(LOOK, "NAT0"))
        with Copy() as c:
            first = c.line_of(LOOK, '"7.62x51 mm NATO"') - 3
            c.write(LOOK, c.read(LOOK) + '\n[[group]]\nname = "x"\ndiffer_by = ["rim"]\ncalibres = [".22 LR", ".308 Winchester"]\n')
            self.assertProblem(c, LOOK, rf"'.308 Winchester' is already in the group on line {first}$",
                               line=c.read(LOOK).count("\n"))

    def test_lookalike_groups(self):
        # Each case breaks the 7.62x51 mm group, which is not the first. The problem is on the
        # group's line (0 its first key, name; -1 its [[group]]; 1 and 2 the next keys).
        with open(os.path.join(ROOT, LOOK), encoding="utf-8") as f:
            gp90_line = f.read().split("\n").index('calibres = [".223 Remington", "5.56x45 mm NATO", "5.56 Commercial", "5.6 mm GP 90"]') - 2
        cases = [('differ_by = ["load"]', 'differ_by = ["lode"]', r'differ_by lists one or more of .*did you mean "load"', 1),
                 ('differ_by = ["load"]', "differ_by = 5", r"differ_by lists one or more of", 1),
                 ('differ_by = ["load"]', 'diff_by = ["load"]', r"unknown key 'diff_by'.*did you mean \"differ_by\"", 1),
                 ('differ_by = ["load"]\n', "", r"\[\[group\]\] needs 'differ_by'", -1),
                 ('\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]', "", r"\[\[group\]\] needs 'calibres'", -1),
                 ('calibres = [".308 Winchester", "7.62x51 mm NATO"]', 'calibres = [".308 Winchester"]',
                  r"calibres lists two or more", 2),
                 ('name = "7.62x51 mm"\n', "", r"\[\[group\]\] needs 'name'", -1),
                 ('name = "7.62x51 mm"', "name = 5", r"name is the group's name, as text", 0),
                 ('name = "7.62x51 mm"', 'name = " 7.62x51 mm"', r"without spaces around it", 0),
                 ('name = "7.62x51 mm"', 'name = "5.56x45 mm"',
                  rf"name '5.56x45 mm' is already the name of the group on line {gp90_line}$", 0),
                 ('name = "7.62x51 mm"', 'name = ".30-06 Springfield"',
                  r"name '.30-06 Springfield' names the calibre '.30-06 Springfield', which is not in this group", 0),
                 ('name = "7.62x51 mm"', 'name = "30-06"',
                  r"name '30-06' names the calibre '.30-06 Springfield', which is not in this group", 0)]
        for old, new, pattern, offset in cases:
            with self.subTest(new), Copy() as c:
                text = c.read(LOOK)
                first = text[:text.index(NATO_GROUP)].count("\n") + 1
                self.assertGreater(first, c.line_of(LOOK, "[[group]]") + 1)
                c.edit(LOOK, NATO_GROUP, NATO_GROUP.replace(old, new))
                self.assertEqual({p[0] for p in c.problems()}, {LOOK})
                self.assertProblem(c, LOOK, pattern, line=first + offset)
        with Copy() as c:
            c.write(LOOK, c.read(LOOK) + "\n[extra]\nx = 1\n")
            self.assertProblem(c, LOOK, r"unknown key 'extra'", line=c.line_of(LOOK, "[extra]"))
        for text in ('[group]\nname = "x"\ndiffer_by = ["load"]\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]\n',
                     "group = 5\n", "group = [1, 2]\n"):
            with self.subTest(text), Copy() as c:
                c.write(LOOK, "# Lookalikes\n" + text)
                self.assertOnlyProblems(c, LOOK, r"each group is a \[\[group\]\] table")
                self.assertProblem(c, LOOK, "each group", line=2)
        with Copy() as c:
            c.edit(LOOK, NATO_GROUP, '[[grup]]\n' + NATO_GROUP)
            self.assertProblem(c, LOOK, r"unknown key 'grup' \(did you mean \"group\"\?\)",
                               line=c.line_of(LOOK, "[[grup]]"))
        with Copy() as c:
            c.write(LOOK, 'group = [{name = "x", differ_by = ["lode"], calibres = [".308 Winchester", "7.62x51 mm NATO"]}]\n')
            self.assertProblem(c, LOOK, "differ_by lists", line=1)
        for text in ("# Lookalikes\n", "group = []\n"):
            with self.subTest(text), Copy() as c:
                c.write(LOOK, text)
                self.assertOnlyProblems(c, LOOK, r"lists no groups")
        with Copy() as c:
            os.remove(c.path(LOOK))
            self.assertOnlyProblems(c, LOOK, r"missing")

    def test_lookalikes_are_read_from_one_file(self):
        groups = {tuple(names): diff for diff, names in cartridges.ALL_LOOKALIKES}
        self.assertEqual(groups[(".308 Winchester", "7.62x51 mm NATO")], ("load",))
        with open(os.path.join(ROOT, LOOK), encoding="utf-8") as f:
            self.assertEqual(len(groups), sum(l == "[[group]]" for l in f.read().split("\n")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "lookalikes")))

    def test_check_script_reports_and_fails(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            out = io.StringIO()
            with redirect_stdout(out):
                code = check.main(c.dir)
            self.assertEqual(code, 1)
            self.assertRegex(out.getvalue(), r"calibres/308-winchester.toml:\d+: unknown key 'shoulder_ad'")

    def test_check_script_writes_github_annotations(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            env = dict(os.environ, GITHUB_ACTIONS="true")
            run = subprocess.run([sys.executable, os.path.join(ROOT, "check.py"), c.dir], capture_output=True, text=True, env=env)
            self.assertEqual(run.returncode, 1)
            self.assertRegex(run.stdout, r"::error file=calibres/308-winchester.toml,line=\d+,title=Calibre data::unknown key")

    def test_check_script_reports_its_own_repository_broken(self):
        # As in CI: check.py next to the broken files, so importing cartridges already fails.
        with Copy() as c:
            for f in ("cartridges.py", "check.py"):
                shutil.copy(os.path.join(ROOT, f), c.dir)
            c.edit(LR, "worldwide = true", "worldwilde = true")
            run = subprocess.run([sys.executable, c.path("check.py")], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertIn("calibres/22-lr.toml:", run.stdout)
            self.assertIn("unknown key 'worldwilde'", run.stdout)

    def test_check_script_passes_on_the_repository(self):
        run = subprocess.run([sys.executable, os.path.join(ROOT, "check.py")], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn("calibre files are fine", run.stdout)

    def test_ci_runs_the_check(self):
        with open(os.path.join(ROOT, ".github", "workflows", "test.yml")) as f:
            self.assertIn("run: python3 check.py", f.read())


if __name__ == "__main__":
    unittest.main()
