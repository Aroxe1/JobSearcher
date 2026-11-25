"""Offline tests for the skill's scripts. Run: python -m unittest discover -s tests"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from unittest import mock
from xml.dom import minidom

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "job-search", "scripts"))
import export_offers  # noqa: E402
import find_companies_fr as fc  # noqa: E402


class ExportOffersTest(unittest.TestCase):
    def build(self, rows, name="Offres"):
        parts = export_offers.build(rows, export_offers.sheet_name(name))
        for xml in parts.values():  # every part must be well-formed XML
            minidom.parseString(xml.encode("utf-8"))
        return parts["xl/worksheets/sheet1.xml"], parts["xl/workbook.xml"]

    def test_values_links_numbers_and_escaping(self):
        sheet, _ = self.build([{"#": 1, "Entreprise": 'A & "B" <c>', "Lien": "https://ex.com/a?b=1&c=2"}])
        self.assertIn("A &amp; \"B\" &lt;c&gt;", sheet)
        self.assertIn('<c r="A2"><v>1</v></c>', sheet)
        self.assertIn('<f>HYPERLINK("https://ex.com/a?b=1&amp;c=2","https://ex.com/a?b=1&amp;c=2")</f>', sheet)

    def test_long_url_stays_plain_text(self):
        sheet, _ = self.build([{"Lien": "https://ex.com/" + "a" * 300}])
        self.assertNotIn("HYPERLINK", sheet)

    def test_columns_from_later_rows_and_control_chars(self):
        sheet, _ = self.build([{"A": "x\x07y"}, {"A": "z", "B": "only here"}])
        self.assertIn(">xy<", sheet)
        self.assertIn("only here", sheet)
        self.assertIn('autoFilter ref="A1:B3"', sheet)

    def test_empty_list_and_sheet_name(self):
        sheet, workbook = self.build([], name="Offres 25/11/2026: [test]")
        self.assertIn("(empty)", sheet)
        self.assertIn('name="Offres 25 11 2026   test"', workbook)
        self.assertEqual(export_offers.sheet_name(""), "Sheet1")
        self.assertLessEqual(len(export_offers.sheet_name("x" * 50)), 31)

    def test_main_writes_valid_xlsx(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "o.json"), os.path.join(tmp, "o.xlsx")
            with open(src, "w", encoding="utf-8") as f:
                json.dump([{"Poste": "Développeur·se", "Lien": "https://ex.com"}], f, ensure_ascii=False)
            argv = ["export_offers.py", src, out, "--sheet", "Offres"]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                export_offers.main()
            with zipfile.ZipFile(out) as z:
                self.assertIsNone(z.testzip())
                self.assertIn("Développeur·se", z.read("xl/worksheets/sheet1.xml").decode("utf-8"))


def etab(**kw):
    base = {"etat_administratif": "A", "caractere_employeur": "O", "statut_diffusion_etablissement": "O",
            "adresse": "1 RUE X 44000 NANTES", "libelle_commune": "NANTES", "siret": "12345678900011",
            "tranche_effectif_salarie": "12", "activite_principale": "62.01Z", "est_siege": False}
    base.update(kw)
    return base


def company(name, etabs, **kw):
    base = {"nom_complet": name, "nature_juridique": "5710", "tranche_effectif_salarie": "21",
            "date_creation": "2010-01-01", "matching_etablissements": etabs,
            "dirigeants": [{"nom": "PRIVATE", "prenoms": "Person"}]}
    base.update(kw)
    return base


class FindCompaniesTest(unittest.TestCase):
    def test_filters_and_fields(self):
        rows = fc.rows_from([
            company("OPEN", [etab(etat_administratif="F", siret="1"), etab(siret="2")]),
            company("ONLY CLOSED", [etab(etat_administratif="F")]),
            company("SOLE TRADER", [etab()], nature_juridique="1000"),
            company("OPTED OUT", [etab(statut_diffusion_etablissement="P")]),
            company("NO STAFF", [etab(caractere_employeur="N")]),
            company("NO ETAB", []),
        ])
        self.assertEqual([r["Entreprise"] for r in rows], ["OPEN"])
        row = rows[0]
        self.assertEqual(row["SIRET"], "2")  # skipped the closed establishment
        self.assertEqual(row["Effectif local"], "20-49")
        self.assertEqual(row["Effectif entreprise"], "50-99")
        self.assertEqual(row["Fiche officielle"], fc.FICHE + "2")
        self.assertNotIn("PRIVATE", json.dumps(rows))  # directors are never copied

    def test_prefers_local_office_in_searched_activity(self):
        results = [company("GROUP", [etab(siret="1", activite_principale="68.31Z"), etab(siret="2", activite_principale="62.02A")],
                           activite_principale="62.01Z")]
        row = fc.rows_from(results, "62.01Z, 62.02A")[0]
        self.assertEqual((row["SIRET"], row["Activité locale (NAF)"], row["Activité entreprise (NAF)"]), ("2", "62.02A", "62.01Z"))
        row = fc.rows_from(results)[0]  # no NAF given: first usable office, both codes shown
        self.assertEqual((row["SIRET"], row["Activité locale (NAF)"]), ("1", "68.31Z"))

    def test_unknown_size(self):
        self.assertEqual(fc.size_label("NN"), "non renseigné")
        self.assertEqual(fc.size_label(None), "non renseigné")

    def test_search_paginates_and_respects_limit(self):
        calls = []

        def fake_fetch(params):
            calls.append(params["page"])
            return {"total_results": 60, "total_pages": 3,
                    "results": [company(f"C{params['page']}-{i}", [etab()]) for i in range(25)]}

        rows, total, truncated = fc.search({"q": "x"}, 30, fetch=fake_fetch, pause=0)
        self.assertEqual((len(rows), total, truncated, calls), (30, 60, True, [1, 2]))
        rows, _, truncated = fc.search({"q": "x"}, 500, fetch=fake_fetch, pause=0)
        self.assertEqual((len(rows), truncated), (75, False))  # read every page: nothing left out by --max
        rows, _, truncated = fc.search({"q": "x"}, 75, fetch=fake_fetch, pause=0)
        self.assertEqual((len(rows), truncated), (75, False))  # limit reached exactly on the last page

    def test_params_and_required_args(self):
        args = type("A", (), {"q": None, "naf": "62.01Z", "section": None, "commune": "44109",
                              "code_postal": None, "departement": None, "tailles": "11,12"})()
        params = fc.build_params(args)
        self.assertEqual(params["activite_principale"], "62.01Z")
        self.assertEqual(params["etat_administratif"], "A")
        self.assertNotIn("q", params)
        with contextlib.redirect_stderr(io.StringIO()):
            for argv in (["--out", "x.json", "--commune", "44109"], ["--out", "x.json", "--naf", "62.01Z"]):
                with self.assertRaises(SystemExit):
                    fc.main(argv)


if __name__ == "__main__":
    unittest.main()
