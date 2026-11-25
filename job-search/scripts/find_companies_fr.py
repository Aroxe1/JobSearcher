#!/usr/bin/env python3
"""Find active French companies by sector and place, for unsolicited applications.

Uses the official, free French company directory API (recherche-entreprises.api.gouv.fr,
no key needed). Standard library only.

Usage:
    python find_companies_fr.py --out companies.json --naf 62.01Z,62.02A --commune 44109
    python find_companies_fr.py --out companies.json --q "agence web" --departement 44 --tailles 11,12,21

Sector: --naf (NAF codes, comma-separated) and/or --q (keywords) and/or --section (NAF section letter).
Place:  --commune (INSEE commune code, not the postcode), --code-postal or --departement (lists allowed).
Writes a JSON list of companies, ready for export_offers.py. Only open local establishments are
kept; sole traders and people who opted out of public listing are left out (personal data).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://recherche-entreprises.api.gouv.fr/search"
FICHE = "https://annuaire-entreprises.data.gouv.fr/etablissement/"
USER_AGENT = "job-search-skill (https://github.com/Aroxe1/JobSearcher)"

# INSEE headcount ranges (tranche_effectif_salarie)
SIZES = {
    "00": "0 salarié", "01": "1-2", "02": "3-5", "03": "6-9", "11": "10-19", "12": "20-49",
    "21": "50-99", "22": "100-199", "31": "200-249", "32": "250-499", "41": "500-999",
    "42": "1000-1999", "51": "2000-4999", "52": "5000-9999", "53": "10000+",
}


def size_label(code):
    return SIZES.get(code or "", "non renseigné")


def fetch(params, retries=2):
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt < retries:  # rate limit: 7 requests/second
                time.sleep(2 * (attempt + 1))
                continue
            raise


def usable(etab):
    return (etab.get("etat_administratif") == "A"
            and etab.get("caractere_employeur") != "N"
            and etab.get("statut_diffusion_etablissement") in (None, "O"))  # "P": owner opted out of listing


def rows_from(results, naf=None):
    """One row per company: an open, listed, employing establishment in the searched place.

    The directory filters on the company's main activity; a local office can do something else,
    so an office whose own activity is in `naf` is preferred, and both codes are shown.
    """
    wanted = {code.strip() for code in (naf or "").split(",") if code.strip()}
    rows = []
    for company in results:
        if company.get("nature_juridique") == "1000":  # sole trader: the company is a private person
            continue
        etabs = [e for e in company.get("matching_etablissements") or [] if usable(e)]
        if not etabs:
            continue
        etab = next((e for e in etabs if e.get("activite_principale") in wanted), etabs[0])
        rows.append({
            "Entreprise": company.get("nom_complet") or "",
            "Activité locale (NAF)": etab.get("activite_principale") or "",
            "Activité entreprise (NAF)": company.get("activite_principale") or "",
            "Adresse": etab.get("adresse") or "",
            "Ville": etab.get("libelle_commune") or "",
            "Effectif local": size_label(etab.get("tranche_effectif_salarie")),
            "Effectif entreprise": size_label(company.get("tranche_effectif_salarie")),
            "Siège ici": "oui" if etab.get("est_siege") else "non",
            "Création": company.get("date_creation") or "",
            "SIRET": etab.get("siret") or "",
            "Fiche officielle": FICHE + (etab.get("siret") or ""),
        })
    return rows


def search(params, limit, fetch=fetch, pause=0.2):
    """Return (rows, total matches, truncated): truncated means `limit` left matches unread."""
    rows, page = [], 1
    while True:
        data = fetch({**params, "page": page})
        total = data.get("total_results", 0)
        rows += rows_from(data.get("results") or [], params.get("activite_principale"))
        last_page = page >= (data.get("total_pages") or 1)
        if last_page or len(rows) >= limit:
            return rows[:limit], total, len(rows) > limit or not last_page
        page += 1
        time.sleep(pause)


def build_params(args):
    params = {
        "etat_administratif": "A",
        "per_page": 25,
        "limite_matching_etablissements": 10,
        "q": args.q,
        "activite_principale": args.naf,
        "section_activite_principale": args.section,
        "code_commune": args.commune,
        "code_postal": args.code_postal,
        "departement": args.departement,
        "tranche_effectif_salarie": args.tailles,
    }
    return {k: v for k, v in params.items() if v}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find active French companies by sector and place")
    parser.add_argument("--out", required=True, help="output JSON file")
    parser.add_argument("--naf", help="NAF codes, e.g. 62.01Z,62.02A")
    parser.add_argument("--q", help="keywords, e.g. 'agence web'")
    parser.add_argument("--section", help="NAF section letter, e.g. J")
    parser.add_argument("--commune", help="INSEE commune code(s), e.g. 44109 for Nantes")
    parser.add_argument("--code-postal", dest="code_postal", help="postcode(s), e.g. 44000,44200")
    parser.add_argument("--departement", help="department code(s), e.g. 44")
    parser.add_argument("--tailles", help="headcount codes of the whole company (not the local office), e.g. 11,12,21 = 10 to 99")
    parser.add_argument("--max", type=int, default=40, help="max companies (default 40)")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # accents in paths must not crash a Windows console
        sys.stdout.reconfigure(errors="replace")
    if not (args.naf or args.q or args.section):
        parser.error("give a sector: --naf, --q or --section")
    if not (args.commune or args.code_postal or args.departement):
        parser.error("give a place: --commune, --code-postal or --departement")

    try:
        rows, total, truncated = search(build_params(args), args.max)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        sys.exit(f"Company directory unreachable or invalid answer: {error}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print(f"{len(rows)} companies written to {args.out} ({total} matches in the directory)")
    if truncated:
        print(f"Stopped at --max {args.max}: more matches remain, in the directory's order (not by fit). "
              "To see others, narrow the search (fewer communes, more precise --naf, --tailles) or raise --max.")
    elif total > len(rows):
        print("All matches were read; the others have no open, listed, employing office in this place, "
              "or are sole traders.")


if __name__ == "__main__":
    main()
