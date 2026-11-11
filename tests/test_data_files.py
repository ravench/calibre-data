"""The TOML files and their checks: python3 -m unittest discover -s tests"""
import io, os, re, shutil, subprocess, sys, tempfile, tomllib, unittest
from contextlib import redirect_stdout

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import cartridges  # noqa: E402
import check  # noqa: E402
from cartridges import load, slug, DataError, sources  # noqa: E402

LR = "calibres/rimfire/22-lr.toml"
LR_MM = ('sources = [\n  "book:janes-ammo-2002 p. 681",\n  "book:cotw-18 p. 670",\n'
         '  "book:tm-43-0001-27 p. 3-5",\n]')  # the sources of .22 LR's [mm]
WIN = "calibres/rifle/308-winchester.toml"
FOLDER = {app: folder for folder, app in cartridges.CATEGORIES.items()}
LOOK = "lookalikes.toml"
NATO_GROUP = 'differ_by = ["load"]\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]'
TIP = ('\n[[tip_colours]]\ncolours = ["black"]\nmeaning = ["armour-piercing"]\n'
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
        for cat, items in cartridges.CATALOGUE:
            for s in items:
                with self.subTest(s["name"]):
                    self.assertTrue(os.path.exists(os.path.join(ROOT, "calibres", FOLDER[cat], slug(s["name"]) + ".toml")))

    def test_slugs(self):
        self.assertEqual(slug(".22 LR"), "22-lr")
        self.assertEqual(slug(".450/400 Nitro Express 3¼ inch"), "450-400-nitro-express-3-1-4-inch")
        self.assertEqual(slug("9.5x57 mm Mannlicher-Schönauer"), "9-5x57-mm-mannlicher-schonauer")

    def test_catalogue_follows_order_toml(self):
        with open(os.path.join(ROOT, "order.toml"), "rb") as f:
            order = tomllib.load(f)
        self.assertEqual([FOLDER[cat] for cat, _ in cartridges.ALL_CATALOGUE], list(order))
        for cat, items in cartridges.ALL_CATALOGUE:
            names = [s["name"] for s in items]
            listed = order[FOLDER[cat]]
            self.assertEqual(names[:len(listed)], listed)
            self.assertEqual(names[len(listed):], sorted(names[len(listed):]))

    def test_categories_are_english_folders_and_the_apps_names(self):
        self.assertEqual(sorted(os.listdir(os.path.join(ROOT, "calibres"))), sorted(cartridges.CATEGORIES))
        self.assertEqual([cat for cat, _ in cartridges.CATALOGUE],
                         ["Randfeuer", "Kurzwaffe", "Langwaffe", "Schwarzpulver", "Flinte", "Luftdruck"])

    def test_cannon_rounds_are_in_the_catalogue_but_not_in_the_apps(self):
        self.assertEqual([cat for cat, _ in cartridges.ALL_CATALOGUE][-1], "Kanone")
        self.assertEqual(cartridges.ALL_CATALOGUE[:-1], cartridges.CATALOGUE)
        cannon = dict(cartridges.ALL_CATALOGUE)["Kanone"]
        self.assertIn("20x138 mm B", [s["name"] for s in cannon])
        self.assertIsNone(next(s for s in cannon if s["name"] == "20x138 mm B")["sh_at"])  # no source gives it
        self.assertNotIn("20x138 mm B", cartridges.PRIMERS)
        self.assertTrue(all(20 <= s["bullet"] <= 40 for s in cannon))
        self.assertLessEqual({"20x102 mm", "35x228 mm", "40x365 mm R"}, {s["name"] for s in cannon})

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
        keys |= set(cartridges.TIP_KEYS[0]) | set(cartridges.TIP_KEYS[1])
        self.assertRegex(text, r"(?m)^# \[\[tip_colours\]\]$")
        for k in keys | set(cartridges.COLOURS) | set(cartridges.MEANINGS):
            self.assertRegex(text, rf"\b{k}\b", k)

    def test_empty_primer_sources_mean_unverified(self):
        self.assertIn("9 mm P.A.K.", cartridges.PRIMER_UNVERIFIED)
        self.assertNotIn("9 mm P.A.K.", cartridges.PRIMER_SOURCES)

    def test_empty_bullet_sources_mean_inferred(self):
        self.assertIn("8.5x55 mm Blaser", cartridges.BULLET_INFERRED)
        self.assertEqual(cartridges.BULLETS["8.5x55 mm Blaser"], ("softpoint", None))

    def test_short_forms_build_the_same_dicts_as_the_helpers(self):
        self.assertEqual(next(s for _, i in cartridges.CATALOGUE for s in i if s["name"] == "12/70"),
                         cartridges.shot("12/70", 20.6, 22.3, 64.0, ["12", "12/70", "12ga", "12gauge"], 70.0))
        blank = next(s for _, i in cartridges.CATALOGUE for s in i if s["name"] == ".22 Blank (6.8/11)")
        self.assertEqual((blank["neck"], blank["oal"], blank["profile"]), (3.4, 11.0, "crimped"))


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

    def test_problems_name_the_line_of_the_value(self):
        with Copy() as c:
            c.edit(WIN, "degrees = 20", "degrees = 120")
            c.edit(LR, 'kind = "rimfire"', 'kind = "rimfre"')
            self.assertProblem(c, WIN, r"degrees is the angle", line=c.line_of(WIN, "degrees = 120"))
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
            c.write("calibres/rimfire/.DS_Store", "x")
            self.assertEqual(c.problems(), [])

    def test_misspelt_top_level_key(self):
        with Copy() as c:
            c.edit(LR, "worldwide = true", "worldwilde = true")
            self.assertProblem(c, LR, r"unknown key 'worldwilde'.*did you mean \"worldwide\"")

    def test_a_case_head_can_give_the_rim_thickness_alone(self):
        with Copy() as c:
            c.edit(WIN, "ramp_top = 3.85\ngroove_diameter = 10.39\nramp_angle = 36.0\n", "")
            self.assertEqual(c.problems(), [])
            t = load(c.dir)
            self.assertEqual(t["RIM_THICKNESS"][".308 Winchester"][0], 1.37)
            self.assertNotIn(".308 Winchester", t["CASE_HEADS"])

    def test_a_case_head_has_the_whole_groove_or_none(self):
        with Copy() as c:
            c.edit(WIN, "ramp_angle = 36.0\n", "")
            self.assertProblem(c, WIN, r"ramp_top, groove_diameter and ramp_angle together, or only rim_thickness")

    def test_a_shot_shell_has_no_case_head(self):
        with Copy() as c:
            shell = "calibres/shotgun/12-70.toml"
            c.write(shell, c.read(shell) + '\n[case_head]\nrim_thickness = 1.5\nsources = ["https://saami.org/"]\n')
            self.assertProblem(c, shell, r"a shot calibre has no \[case_head\]")

    def test_a_rimmed_case_head_has_no_groove(self):
        with Copy() as c:
            c.edit(LR, "rim_thickness = 1.02\n", "rim_thickness = 1.02\nramp_top = 2.0\ngroove_diameter = 6.0\n"
                                                  "ramp_angle = 30.0\n")
            self.assertProblem(c, LR, r"a rimfire case has no extractor groove")

    def test_misspelt_table(self):
        with Copy() as c:
            c.edit(WIN, "[shoulder_angle]", "[shoulder_angel]")
            self.assertProblem(c, WIN, r"unknown table \[shoulder_angel\].*shoulder_angle")

    def test_values_that_are_not_allowed(self):
        cases = [(LR, 'kind = "rimfire"', 'kind = "rimfre"', r"kind 'rimfre'.*did you mean \"rimfire\""),
                 (LR, 'profile = "round"', 'profile = "rond"', r"profile 'rond'"),
                 (WIN, 'size = "large-rifle"', 'size = "large rifle"', r"\[primer\] size 'large rifle'"),
                 (LR, 'type = "lead"', 'type = "jacketed"', r"leave \[bullet\] out for a full metal jacket"),
                 (LR, 'origin = "US"', 'origin = "USA"', r"origin 'USA' is not a code in countries.toml"),
                 (LR, "rim = 6.9", 'rim = "6.9"', r"\[mm\] rim must be a number"),
                 (LR, "rim = 6.9", "rim = -6.9", r"\[mm\] rim must be a number above 0"),
                 (LR, "year = 1887", "year = 18887", r"year must be a year"),
                 (LR, "worldwide = true", 'worldwide = "yes"', r"worldwide must be true or false"),
                 (WIN, "degrees = 20", "degrees = 120", r"degrees is the angle to the case axis")]
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
        self.assertEqual(sources(".22 LR", "mm"), ["book:janes-ammo-2002 p. 681", "book:cotw-18 p. 670",
                                                   "book:tm-43-0001-27 p. 3-5"])
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
                self.assertProblem(c, LR, pattern, line=c.line_of(LR, source))
                self.assertOnlyProblems(c, LR, pattern)

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
        self.assertEqual(cartridges.FIRED_BY["7.5x53.5 mm Swiss (GP 1890)"],
                         (("Schmidt-Rubin M1889",), "https://en.wikipedia.org/wiki/7.5×55mm_Swiss"))
        self.assertEqual(sources(".577 Snider", "fired_by"), ["https://en.wikipedia.org/wiki/.577_Snider"])
        self.assertNotIn(".308 Winchester", cartridges.FIRED_BY)
        files = {s["name"]: f"calibres/{FOLDER[cat]}/{slug(s['name'])}.toml"
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
        rel = "calibres/rifle/8x50-mm-r-lebel.toml"
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

    def test_tip_colours_are_for_the_catalogue_only(self):
        self.assertEqual(cartridges.TIP_COLOURS[".50 BMG"][0],
                         {"colours": ("black",), "meaning": ("armour-piercing",), "description": "M2",
                          "countries": ("US",), "sources": ["https://en.wikipedia.org/wiki/.50_BMG", "book:labbett p. 80"]})
        self.assertNotIn(".308 Winchester", cartridges.TIP_COLOURS)
        files = {s["name"]: f"calibres/{FOLDER[cat]}/{slug(s['name'])}.toml"
                 for cat, items in cartridges.CATALOGUE for s in items}
        with Copy() as c:  # without them, every other table (the apps' catalogue too) is the same
            for name in cartridges.TIP_COLOURS:
                text = c.read(files[name])
                c.write(files[name], text[:text.index("\n[[tip_colours]]")] + "\n")
            t = load(c.dir)
        self.assertEqual(t.pop("TIP_COLOURS"), {})
        self.assertEqual(t, {k: v for k, v in cartridges._t.items() if k != "TIP_COLOURS"})

    def test_tip_colour_problems(self):
        first = '\n[[tip_colours]]\ncolours = ["red"]\nmeaning = ["tracer"]\nsources = ["book:labbett p. 80"]\n'
        cases = [('colours = ["black"]', 'colours = ["blak"]', r"colours lists one or more of .*did you mean \"black\""),
                 ('colours = ["black"]', "colours = []", r"colours lists one or more of"),
                 ('colours = ["black"]', 'colours = ["black", "black"]', r"colours lists 'black' twice"),
                 ('meaning = ["armour-piercing"]', 'meaning = ["armor-piercing"]', r"did you mean \"armour-piercing\""),
                 ('meaning = ["armour-piercing"]', 'meaning = "armour-piercing"', r"meaning lists one or more of"),
                 ('meaning = ["armour-piercing"]\n', "", r"\[\[tip_colours\]\] needs 'meaning'"),
                 ('sources = ["https://en.wikipedia.org/wiki/7.62×51mm_NATO"]', "sources = []",
                  r"\[\[tip_colours\]\] needs at least one source"),
                 ('sources = ["https://en.wikipedia.org/wiki/7.62×51mm_NATO"]\n', "", r"\[\[tip_colours\]\] needs sources"),
                 ('colours = ["black"]', 'colours = ["black"]\ncolor = "black"', r"unknown key 'color'.*did you mean \"colours\""),
                 ('colours = ["black"]', 'colours = ["black"]\ndescription = " "', r"description must be text"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = ["USA"]', r"country 'USA' is not a code"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = []', r"countries lists one or more"),
                 ('colours = ["black"]', 'colours = ["black"]\ncountries = ["US", "US"]', r"countries lists a country twice")]
        for old, new, pattern in cases:
            with self.subTest(new), Copy() as c:
                c.write(WIN, c.read(WIN) + first + TIP)
                self.assertEqual(c.problems(), [])
                c.edit(WIN, old, new)
                second = [i for i, l in enumerate(c.read(WIN).split("\n"), 1) if l == "[[tip_colours]]"][1]
                found = [p for p in c.problems() if re.search(pattern, p[2])]
                self.assertTrue(found, c.problems())
                self.assertGreaterEqual(found[0][1], second)  # the line in the second table
                self.assertOnlyProblems(c, WIN, r"tip_colours")
                self.assertEqual(len(c.problems()), 1)

    def test_tip_colours_are_listed_once_and_only_for_bullets(self):
        with Copy() as c:
            c.write(WIN, c.read(WIN) + TIP + TIP.replace("]\nsources", ']\ncountries = ["US"]\nsources'))
            self.assertOnlyProblems(c, WIN, r"black with this meaning is already on line \d+: list all its countries there")
        with Copy() as c:
            c.write(WIN, c.read(WIN) + TIP + TIP.replace('["black"]', '["red", "black"]'))
            self.assertEqual(c.problems(), [])
        with Copy() as c:
            c.write(WIN, 'tip_colours = "black"\n' + c.read(WIN))
            self.assertOnlyProblems(c, WIN, r"each tip colour is a \[\[tip_colours\]\] table")
        with Copy() as c:  # one problem for a [tip_colours] written with single brackets
            c.write(WIN, c.read(WIN) + TIP.replace("[[tip_colours]]", "[tip_colours]"))
            self.assertOnlyProblems(c, WIN, r"each tip colour is a \[\[tip_colours\]\] table")
            self.assertEqual(len(c.problems()), 1)
        for rel in ("calibres/shotgun/12-70.toml", "calibres/air-gun/4-5-mm-diabolo-177.toml"):
            with self.subTest(rel), Copy() as c:
                c.write(rel, c.read(rel) + TIP)
                self.assertOnlyProblems(c, rel, r"\[\[tip_colours\]\] is only for cartridges with a bullet")

    def test_cannon_rounds_need_only_the_bullet_and_case_length(self):
        rel = "calibres/cannon/20x138-mm-b.toml"
        with Copy() as c:
            c.edit(rel, "rim = 28.48\nbase = 26.86\nshoulder = 25.5\n", "")
            c.edit(rel, "overall_length = 202.7\n", "")
            c.write(rel, c.read(rel) + TIP)  # tip colours too
            self.assertEqual(c.problems(), [])
            c.edit(rel, "case_length = 138.0\n", "")
            self.assertOnlyProblems(c, rel, r"\[mm\] needs 'case_length'")
        with Copy() as c:  # nothing the apps read whole
            c.edit(rel, 'aliases = ["20x138b"', 'display_aliases = ["20 mm"]\naliases = ["20x138b"')
            self.assertOnlyProblems(c, rel, r"display_aliases are for the apps, which do not show calibres/cannon/ yet")
        with Copy() as c:
            c.write(rel, c.read(rel) + '\n[primer]\nsize = "large-rifle"\nsources = []\n')
            self.assertOnlyProblems(c, rel, r"calibres/cannon/ has no \[primer\]")
        with Copy() as c:
            c.write(LOOK, c.read(LOOK) + '\n[[group]]\ndiffer_by = ["bore"]\ncalibres = [".50 BMG", "20x138 mm B"]\n')
            self.assertOnlyProblems(c, LOOK, r"'20x138 mm B' is in calibres/cannon/, which the apps do not show yet")
        with Copy() as c:  # other categories still need every measurement
            c.edit(WIN, "neck = 8.7\n", "")
            self.assertOnlyProblems(c, WIN, r"\[mm\] needs 'neck'")
        with Copy() as c:  # and a primer
            c.edit(WIN, '[primer]\nsize = "large-rifle"\nsources = ["https://en.wikipedia.org/wiki/.308_Winchester"]\n', "")
            self.assertOnlyProblems(c, WIN, r"needs a \[primer\] table")

    def test_cannon_rounds_are_20_to_40_mm(self):
        rel = "calibres/cannon/40x365-mm-r.toml"
        for bullet, ok in (("40.0", True), ("40.5", False), ("57.0", False)):
            with Copy() as c:
                c.edit(rel, "bullet = 40.0", f"bullet = {bullet}")
                if ok:
                    self.assertEqual(c.problems(), [])
                else:
                    self.assertProblem(c, rel, r"calibres/cannon/ holds the 20 to 40 mm cannon rounds",
                                       line=c.line_of(rel, f"bullet = {bullet}"))
        with Copy() as c:  # a heavy machine gun round belongs with the rifles
            c.edit("calibres/cannon/20x138-mm-b.toml", "bullet = 20.0", "bullet = 14.5")
            self.assertOnlyProblems(c, "calibres/cannon/20x138-mm-b.toml", r"20 to 40 mm cannon rounds: bullet is 20 to 40")

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

    def test_missing_measurement(self):
        with Copy() as c:
            c.edit(LR, "neck = 5.7\n", "")
            self.assertProblem(c, LR, r"\[mm\] needs 'neck'")

    def test_shoulder_without_its_position(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = 39.62\n", "")
            self.assertProblem(c, WIN, r"both shoulder and shoulder_at")

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
                rel = f"calibres/rifle/{slug(name)}.toml"
                c.write(rel, re.sub(r"(?m)^aliases = .*$", "aliases = []", text))
                self.assertOnlyProblems(c, rel, f"the name '{re.escape(name)}' needs {pattern}")

    def test_file_name_must_follow_the_name(self):
        with Copy() as c:
            os.rename(c.path(LR), c.path("calibres/rimfire/long-rifle.toml"))
            self.assertProblem(c, "calibres/rimfire/long-rifle.toml", r"must be called 22-lr.toml")

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

    def test_order_toml_names_without_a_file(self):
        with Copy() as c:
            c.edit("order.toml", '".22 LR"', '".22 LRR"')
            self.assertProblem(c, "order.toml", r"'.22 LRR' has no file in calibres/rimfire/")
        with Copy() as c:
            c.edit("order.toml", '  ".308 Winchester",\n', '  ".308 Winchester",\n  ".22 LR",\n')
            self.assertProblem(c, "order.toml", r"'.22 LR' has no file in calibres/rifle/ \(it is in calibres/rimfire/\)")

    def test_an_empty_order_toml_does_not_empty_the_catalogue(self):
        with Copy() as c:
            c.write("order.toml", "# nothing\n")
            found = c.problems()
            self.assertEqual(len(found), len(os.listdir(c.path("calibres"))), found)
            self.assertTrue(all(p[2].endswith("is not in order.toml") for p in found), found)
        with Copy() as c:
            shutil.rmtree(c.path("calibres"))
            self.assertProblem(c, "calibres", r"missing", line=False)

    def test_a_broken_countries_toml_is_reported_there_only(self):
        for text, pattern in [("# nothing\n", r"lists no countries"),
                              ('[CH]\nflag = "x"\n', r"\[CH\] needs name"),
                              ('[CH]\nname = "Switzerland"\nflag = 5\n', r"\[CH\] flag must be")]:
            with self.subTest(text), Copy() as c:
                c.write("countries.toml", text)
                self.assertOnlyProblems(c, "countries.toml", pattern)

    def test_a_misspelt_category_in_order_toml(self):
        with Copy() as c:
            c.edit("order.toml", "air-gun = [", "air-gn = [")
            found = c.problems()
            self.assertEqual(len(found), 2, found)
            self.assertProblem(c, "order.toml", r"'air-gn' is not one of rimfire, handgun, .* \(did you mean \"air-gun\"\?\)")
            self.assertProblem(c, "calibres/air-gun", r"not in order.toml \(did you mean \"air-gn\"\?\)", line=False)

    def test_the_old_german_category_names_point_to_their_folders(self):
        with Copy() as c:
            c.edit("order.toml", "rifle = [", "Langwaffe = [")
            self.assertProblem(c, "order.toml", r"'Langwaffe' is not one of .* \(the folder of Langwaffe is rifle\)")

    def test_a_folder_the_apps_do_not_know_stays_out_of_the_catalogue(self):
        with Copy() as c:
            os.makedirs(c.path("calibres/rifles"))
            shutil.copy(c.path(WIN), c.path("calibres/rifles/test.toml"))
            c.write("order.toml", c.read("order.toml") + "\nrifles = []\n")
            self.assertOnlyProblems(c, "order.toml", r"'rifles' is not one of rimfire, .* \(did you mean \"rifle\"\?\)")

    def test_a_category_the_apps_know_without_a_folder(self):
        with Copy() as c:
            shutil.rmtree(c.path("calibres/shotgun"))
            self.assertOnlyProblems(c, "order.toml", r"'shotgun' has no folder calibres/shotgun/")

    def test_unknown_category_folder(self):
        with Copy() as c:
            os.makedirs(c.path("calibres/rifles"))
            self.assertProblem(c, "calibres/rifles", r"not in order.toml \(did you mean \"rifle\"\?\)", line=False)

    def test_lookalike_groups_name_existing_calibres_once(self):
        with Copy() as c:
            c.edit(LOOK, '"7.62x51 mm NATO"]', '"7.62x51 mm NAT0"]')
            self.assertProblem(c, LOOK, r"'7.62x51 mm NAT0' is not a calibre \(did you mean \"7.62x51 mm NATO\"\?\)",
                               line=c.line_of(LOOK, "NAT0"))
        with Copy() as c:
            first = c.line_of(LOOK, '"7.62x51 mm NATO"') - 2
            c.write(LOOK, c.read(LOOK) + '\n[[group]]\ndiffer_by = ["rim"]\ncalibres = [".22 LR", ".308 Winchester"]\n')
            self.assertProblem(c, LOOK, rf"'.308 Winchester' is already in the group on line {first}$",
                               line=c.read(LOOK).count("\n"))

    def test_lookalike_groups(self):
        # Each case breaks the .308 Winchester group, which is not the first. The problem is on the
        # group's line (0 its first key, -1 its [[group]], 1 the next key).
        cases = [('differ_by = ["load"]', 'differ_by = ["lode"]', r'differ_by lists one or more of .*did you mean "load"', 0),
                 ('differ_by = ["load"]', "differ_by = 5", r"differ_by lists one or more of", 0),
                 ('differ_by = ["load"]', 'diff_by = ["load"]', r"unknown key 'diff_by'.*did you mean \"differ_by\"", 0),
                 ('differ_by = ["load"]\n', "", r"\[\[group\]\] needs 'differ_by'", -1),
                 ('\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]', "", r"\[\[group\]\] needs 'calibres'", -1),
                 ('calibres = [".308 Winchester", "7.62x51 mm NATO"]', 'calibres = [".308 Winchester"]',
                  r"calibres lists two or more", 1)]
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
        for text in ('[group]\ndiffer_by = ["load"]\ncalibres = [".308 Winchester", "7.62x51 mm NATO"]\n',
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
            c.write(LOOK, 'group = [{differ_by = ["lode"], calibres = [".308 Winchester", "7.62x51 mm NATO"]}]\n')
            self.assertProblem(c, LOOK, "differ_by lists", line=1)
        for text in ("# Lookalikes\n", "group = []\n"):
            with self.subTest(text), Copy() as c:
                c.write(LOOK, text)
                self.assertOnlyProblems(c, LOOK, r"lists no groups")
        with Copy() as c:
            os.remove(c.path(LOOK))
            self.assertOnlyProblems(c, LOOK, r"missing")

    def test_lookalikes_are_read_from_one_file(self):
        groups = {tuple(names): diff for diff, names in cartridges.LOOKALIKES}
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
            self.assertRegex(out.getvalue(), r"calibres/rifle/308-winchester.toml:\d+: unknown key 'shoulder_ad'")

    def test_check_script_writes_github_annotations(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            env = dict(os.environ, GITHUB_ACTIONS="true")
            run = subprocess.run([sys.executable, os.path.join(ROOT, "check.py"), c.dir], capture_output=True, text=True, env=env)
            self.assertEqual(run.returncode, 1)
            self.assertRegex(run.stdout, r"::error file=calibres/rifle/308-winchester.toml,line=\d+,title=Calibre data::unknown key")

    def test_check_script_reports_its_own_repository_broken(self):
        # As in CI: check.py next to the broken files, so importing cartridges already fails.
        with Copy() as c:
            for f in ("cartridges.py", "check.py"):
                shutil.copy(os.path.join(ROOT, f), c.dir)
            c.edit(LR, "worldwide = true", "worldwilde = true")
            run = subprocess.run([sys.executable, c.path("check.py")], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertIn("calibres/rimfire/22-lr.toml:", run.stdout)
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
