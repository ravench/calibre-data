"""The TOML files and their checks: python3 -m unittest discover -s tests"""
import io, os, re, shutil, subprocess, sys, tempfile, tomllib, unittest
from contextlib import redirect_stdout

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import cartridges  # noqa: E402
import check  # noqa: E402
from cartridges import load, slug, DataError, sources  # noqa: E402

LR = "calibres/Randfeuer/22-lr.toml"
WIN = "calibres/Langwaffe/308-winchester.toml"
NATO = "lookalikes/308-winchester.toml"


class Copy:
    """A copy of the data files to break on purpose."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        for d in ("calibres", "lookalikes"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(self.dir, d))
        for f in ("order.toml", "countries.toml"):
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
                    self.assertTrue(os.path.exists(os.path.join(ROOT, "calibres", cat, slug(s["name"]) + ".toml")))

    def test_slugs(self):
        self.assertEqual(slug(".22 LR"), "22-lr")
        self.assertEqual(slug(".450/400 Nitro Express 3¼ inch"), "450-400-nitro-express-3-1-4-inch")
        self.assertEqual(slug("9.5x57 mm Mannlicher-Schönauer"), "9-5x57-mm-mannlicher-schonauer")

    def test_catalogue_follows_order_toml(self):
        with open(os.path.join(ROOT, "order.toml"), "rb") as f:
            order = tomllib.load(f)
        self.assertEqual([cat for cat, _ in cartridges.CATALOGUE], list(order))
        for cat, items in cartridges.CATALOGUE:
            self.assertEqual([s["name"] for s in items], order[cat])

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
            c.edit(LR, "bullet = 5.7\nsources = []", 'bullet = 5.7\nsources = ["https://saami.org/"]')
            t = load(c.dir)
            self.assertEqual(t["SOURCES"][(".22 LR", "introduced")],
                             ["https://en.wikipedia.org/wiki/.22_Long_Rifle", "https://municion.org/producto/22-long-rifle/"])
            self.assertEqual(t["INTRODUCED"][".22 LR"], (1887, "https://en.wikipedia.org/wiki/.22_Long_Rifle"))
            self.assertEqual(t["SOURCES"][(".22 LR", "mm")], ["https://saami.org/"])

    def test_sources_function(self):
        self.assertEqual(sources(".22 LR", "introduced"), ["https://en.wikipedia.org/wiki/.22_Long_Rifle"])
        self.assertEqual(sources(".22 LR", "shoulder_angle"), [])
        self.assertEqual(sources("No such calibre", "mm"), [])

    def test_empty_primer_sources_mean_unverified(self):
        self.assertIn("9 mm P.A.K.", cartridges.PRIMER_UNVERIFIED)
        self.assertNotIn("9 mm P.A.K.", cartridges.PRIMER_SOURCES)

    def test_empty_bullet_sources_mean_inferred(self):
        self.assertIn("8.5x55 mm Blaser", cartridges.BULLET_INFERRED)
        self.assertEqual(cartridges.BULLETS["8.5x55 mm Blaser"], ("softpoint", None))

    def test_short_forms_build_the_same_dicts_as_the_helpers(self):
        self.assertEqual(next(s for _, i in cartridges.CATALOGUE for s in i if s["name"] == "12/70"),
                         cartridges.shot("12/70", 20.6, 22.3, 64.0, ["12", "12/70", "12ga", "12gauge"]))
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
            c.write("calibres/Randfeuer/.DS_Store", "x")
            self.assertEqual(c.problems(), [])

    def test_misspelt_top_level_key(self):
        with Copy() as c:
            c.edit(LR, "worldwide = true", "worldwilde = true")
            self.assertProblem(c, LR, r"unknown key 'worldwilde'.*did you mean \"worldwide\"")

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
            c.edit(LR, '"https://en.wikipedia.org/wiki/.22_Long_Rifle"]\n\n[bullet]', '"Wikipedia"]\n\n[bullet]')
            self.assertProblem(c, LR, r"source 'Wikipedia' is not a https:// web address")

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
            c.edit(LR, "bullet = 5.7\nsources = []", "bullet = 5.7")
            self.assertProblem(c, LR, r"\[mm\] needs a sources list")

    def test_missing_measurement(self):
        with Copy() as c:
            c.edit(LR, "neck = 5.7\n", "")
            self.assertProblem(c, LR, r"\[mm\] needs 'neck'")

    def test_shoulder_without_its_position(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = 39.62\n", "")
            self.assertProblem(c, WIN, r"both shoulder and shoulder_at")

    def test_file_name_must_follow_the_name(self):
        with Copy() as c:
            os.rename(c.path(LR), c.path("calibres/Randfeuer/long-rifle.toml"))
            self.assertProblem(c, "calibres/Randfeuer/long-rifle.toml", r"must be called 22-lr.toml")

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
            self.assertProblem(c, "order.toml", r"'.22 LRR' has no file in calibres/Randfeuer/")
        with Copy() as c:
            c.edit("order.toml", '  ".308 Winchester",\n', '  ".308 Winchester",\n  ".22 LR",\n')
            self.assertProblem(c, "order.toml", r"'.22 LR' has no file in calibres/Langwaffe/ \(it is in calibres/Randfeuer/\)")

    def test_an_empty_order_toml_does_not_empty_the_catalogue(self):
        with Copy() as c:
            c.write("order.toml", "# nothing\n")
            found = c.problems()
            self.assertEqual(len(found), len(os.listdir(c.path("calibres"))), found)
            self.assertTrue(all("is not in order.toml" in p[2] for p in found), found)
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
            c.edit("order.toml", "Luftdruck = [", "Luftdruk = [")
            found = c.problems()
            self.assertEqual(len(found), 2, found)
            self.assertProblem(c, "order.toml", r"'Luftdruk' has no folder calibres/Luftdruk/ \(did you mean \"Luftdruck\"\?\)")
            self.assertProblem(c, "calibres/Luftdruck", r"not in order.toml \(did you mean \"Luftdruk\"\?\)", line=False)

    def test_unknown_category_folder(self):
        with Copy() as c:
            os.makedirs(c.path("calibres/Langwaffen"))
            self.assertProblem(c, "calibres/Langwaffen", r"not in order.toml \(did you mean \"Langwaffe\"\?\)", line=False)

    def test_lookalike_groups_name_existing_calibres_once(self):
        with Copy() as c:
            c.edit(NATO, '"7.62x51 mm NATO"]', '"7.62x51 mm NAT0"]')
            self.assertProblem(c, NATO, r"'7.62x51 mm NAT0' is not a calibre \(did you mean \"7.62x51 mm NATO\"\?\)",
                               line=c.line_of(NATO, "calibres ="))
        with Copy() as c:
            c.write("lookalikes/22-lr.toml", 'differ_by = ["rim"]\ncalibres = [".22 LR", ".308 Winchester"]\n')
            self.assertProblem(c, NATO, r"'.308 Winchester' is already in lookalikes/22-lr.toml")

    def test_lookalike_group_files(self):
        cases = [('differ_by = ["load"]', 'differ_by = ["lode"]', r'differ_by lists one or more of .*did you mean "load"',
                  "differ_by ="),
                 ('differ_by = ["load"]', "differ_by = 5", r"differ_by lists one or more of", "differ_by ="),
                 ('differ_by = ["load"]', 'diff_by = ["load"]', r"unknown key 'diff_by'.*did you mean \"differ_by\"",
                  "diff_by ="),
                 ('calibres = [".308 Winchester", "7.62x51 mm NATO"]', 'calibres = [".308 Winchester"]',
                  r"calibres lists two or more", "calibres ="),
                 ('calibres = [".308 Winchester", "7.62x51 mm NATO"]', 'calibres = ["7.62x51 mm NATO", ".308 Winchester"]',
                  r"the group of '7.62x51 mm NATO' must be called 7-62x51-mm-nato.toml", "calibres =")]
        for old, new, pattern, line in cases:
            with self.subTest(new), Copy() as c:
                c.edit(NATO, old, new)
                self.assertEqual({p[0] for p in c.problems()}, {NATO})
                self.assertProblem(c, NATO, pattern, line=c.line_of(NATO, line))
        with Copy() as c:
            c.write(NATO, c.read(NATO) + "\n[extra]\nx = 1\n")
            self.assertProblem(c, NATO, r"unknown key 'extra'", line=c.line_of(NATO, "[extra]"))
        with Copy() as c:
            shutil.rmtree(c.path("lookalikes"))
            self.assertOnlyProblems(c, "lookalikes", r"missing")
        with Copy() as c:
            c.write("lookalikes/notes.txt", "x")
            c.write("lookalikes/.DS_Store", "x")
            self.assertOnlyProblems(c, "lookalikes/notes.txt", r"only .toml files")

    def test_lookalikes_are_read_from_the_folder(self):
        groups = {tuple(names): diff for diff, names in cartridges.LOOKALIKES}
        self.assertEqual(groups[(".308 Winchester", "7.62x51 mm NATO")], ("load",))
        self.assertEqual(len(groups), len(os.listdir(os.path.join(ROOT, "lookalikes"))))

    def test_check_script_reports_and_fails(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            out = io.StringIO()
            with redirect_stdout(out):
                code = check.main(c.dir)
            self.assertEqual(code, 1)
            self.assertRegex(out.getvalue(), r"calibres/Langwaffe/308-winchester.toml:\d+: unknown key 'shoulder_ad'")

    def test_check_script_writes_github_annotations(self):
        with Copy() as c:
            c.edit(WIN, "shoulder_at = ", "shoulder_ad = ")
            env = dict(os.environ, GITHUB_ACTIONS="true")
            run = subprocess.run([sys.executable, os.path.join(ROOT, "check.py"), c.dir], capture_output=True, text=True, env=env)
            self.assertEqual(run.returncode, 1)
            self.assertRegex(run.stdout, r"::error file=calibres/Langwaffe/308-winchester.toml,line=\d+,title=Calibre data::unknown key")

    def test_check_script_reports_its_own_repository_broken(self):
        # As in CI: check.py next to the broken files, so importing cartridges already fails.
        with Copy() as c:
            for f in ("cartridges.py", "check.py"):
                shutil.copy(os.path.join(ROOT, f), c.dir)
            c.edit(LR, "worldwide = true", "worldwilde = true")
            run = subprocess.run([sys.executable, c.path("check.py")], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            self.assertIn("calibres/Randfeuer/22-lr.toml:", run.stdout)
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
