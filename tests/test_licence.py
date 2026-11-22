"""LICENSE.md lists the data files: python3 -m unittest discover -s tests"""
import os, re, unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def data_list():
    """The names in LICENSE.md's list of data files ("- `calibres/` (...)" -> "calibres/")."""
    with open(os.path.join(ROOT, "LICENSE.md"), encoding="utf-8") as f:
        text = f.read()
    if "## The data" not in text:
        raise AssertionError('LICENSE.md has no "## The data" section')
    part = text.split("## The data", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^- `([^`]+)`", part, re.M))


class LicenceTest(unittest.TestCase):
    def test_every_data_file_is_under_the_odbl(self):
        # The data are the TOML files at the top and the calibres/ folder; a new one must be
        # listed, or it would fall under MIT with the code. (A top-level TOML file that is not
        # data, such as a pyproject.toml, would need this test to leave it out.)
        data = {f for f in os.listdir(ROOT) if f.endswith(".toml")} | {"calibres/"}
        self.assertEqual(data_list(), data)


if __name__ == "__main__":
    unittest.main()
