# Finding companies for unsolicited applications

Goal: a short list of **real, active companies** in the user's target sector and area, each with a verified website and a way to apply, so the user can send unsolicited applications (candidatures spontanées). Many apprenticeships, internships and jobs are never posted; a well-targeted unsolicited application reaches them.

## 1. Define the target from the profile
- **Sector → activity**: in France, translate the target sector into 1–4 NAF codes (table below) and/or keywords. Companies hiring for a role are not always in the "obvious" sector (a web developer can work at a bank or an e-commerce retailer): add 1–2 related sectors if the user is open to it.
- **Place**: home city + acceptable radius → a list of communes or the département(s).
- **Size**: from the profile ("Company size"). Very small companies (under 10) rarely take apprentices or interns but do sometimes; don't exclude them unless the user wants to.

## 2. France: query the official company directory
Run the bundled script (absolute path to this skill's folder):

```
python <skill>/scripts/find_companies_fr.py --out <temp>/companies.json --naf 62.01Z,62.02A --commune 44109 --tailles 11,12,21,22 --max 40
```

- `--commune` takes the **INSEE commune code**, not the postcode (Nantes = 44109, postcode 44000). If unsure, use `--code-postal 44000,44100,44200,44300` or `--departement 44`.
- `--q "agence web"` searches by keywords (company name, brand) and can be combined with `--naf`.
- `--tailles` filters on the **whole company's** headcount (the local office's size is shown in the results, often "non renseigné"). Use it when the user has a size preference; to cut a long list, prefer fewer communes or more precise codes, so small companies aren't excluded without reason. Codes: 01 = 1–2, 02 = 3–5, 03 = 6–9, 11 = 10–19, 12 = 20–49, 21 = 50–99, 22 = 100–199, 31 = 200–249, 32 = 250–499, 41 = 500–999, 42 = 1000–1999, 51+ = 2000 and more.
- The script keeps only companies with an **open establishment in that place** (the head office is often elsewhere), leaves out sole traders and people who opted out of public listing, and gives the local address, local and total headcount, creation date and a link to the official record (annuaire-entreprises.data.gouv.fr). It does **not** give websites or contacts: step 4 does.
- The directory filters on the **company's** main activity; a local office can do something else (e.g. a software publisher's local office registered as a real-estate agency). The script prefers an office in the searched activity and shows both codes: drop companies whose local office clearly doesn't fit.
- Results come in the directory's own order (not by fit), capped by `--max`. When there are far more matches than results (the script says so), narrow the search (`--tailles`, fewer communes, more precise codes) or raise `--max` rather than keeping the first ones.
- If the directory can't be reached, say so and use the other sources below.

### Common NAF codes (France)
| Sector | NAF codes |
|---|---|
| Software, web, IT services | 62.01Z programming · 62.02A IT consulting · 62.03Z IT facilities management · 63.11Z data processing, hosting · 58.29C software publishing |
| Marketing, communication | 73.11Z advertising agencies · 70.21Z public relations and communication |
| Design | 74.10Z specialised design |
| Consulting, management | 70.22Z business and management consulting |
| Accounting, law | 69.20Z accounting · 69.10Z legal activities |
| Engineering, architecture | 71.12B engineering, technical studies · 71.11Z architecture |
| Construction, trades | 41.20A houses · 41.20B other buildings · 43.21A electrical installation |
| Industry, mechanics | 25.62B industrial mechanics · 28.99B special-purpose machinery · 33.12Z repair of machinery |
| Food trades | 10.71C bakery and pastry |
| Automotive | 45.20A car maintenance and repair |
| Retail | 47.11D supermarkets · 47.11F hypermarkets · 47.73Z pharmacies |
| Hotels, restaurants | 56.10A restaurants · 55.10Z hotels |
| Health, social care | 86.10Z hospitals · 88.10A home help · 75.00Z veterinary |
| Banking, insurance, real estate | 64.19Z banks · 65.12Z insurance · 68.31Z real estate agencies |
| Transport, logistics | 49.41A road freight · 52.29B freight forwarding |
| HR, training | 78.10Z recruitment agencies · 85.59A adult training |
| Media, audiovisual | 59.11A film and TV production |
| Beauty, sport, farming | 96.02A hairdressing · 93.12Z sports clubs · 01.11Z cereal farming |

Not listed? Search the code on insee.fr ("nomenclature NAF") or use `--q` keywords. Large groups often register their local offices under the group's code: complete with keyword searches and the sources below.

## 3. Other countries and extra sources
Official registries (free search; availability of filters varies, check what the site allows):
- **United Kingdom**: Companies House advanced search (filter by SIC code and location)
- **Belgium**: KBO/BCE Public Search (by activity code and postcode)
- **Switzerland**: Zefix (commercial register) · **Germany**: Unternehmensregister / Handelsregister
- **Other countries**: search "<country> business register search by activity"; OpenCorporates covers many registers (search by name)

Everywhere:
- **LinkedIn** company search (industry + location filters), which also shows size and recent posts
- **Google Maps** / local search: "<trade or sector> <city>"
- **Job boards' company pages** (e.g. Welcome to the Jungle in France) show culture, size and current openings
- **France, apprenticeships**: La Bonne Alternance lists companies "à fort potentiel d'embauche en alternance" even without a posted offer (JavaScript site: give the user a link if it can't be read)
- Chambers of commerce directories, clusters / competitiveness hubs, startup directories, trade-show exhibitor lists, the school's partner companies and alumni

## 4. Research each shortlisted company
From the list, pick the 10–15 that fit best (sector, distance, size, deal-breakers; a borderline deal-breaker case stays in with ⚠️ and a reason, so the user decides), then for each:
1. **Find its website** (web search on the exact name + city) and open it. Check it's the same company (name, city or SIRET in the legal notice). Registered names often differ from brand names, and some companies only have a page on their parent group's site: that's fine when the page clearly covers this company or office.
2. **Find how to apply**: careers / jobs / "nous rejoindre" page (on the company's site or its page on a job board), or a recruitment email or form published by the company. A general contact address ("hello@…") is a last resort; say so if it's the only channel, and use the unsolicited email template, whose subject line makes the purpose clear. If the company currently posts a matching offer, point to that offer instead: it's no longer an unsolicited application.
3. **Note one concrete hook** for the letter: a product, client, project, value, recent news, or apprentices/interns already hosted.
4. If you can't find a website or contact, keep the company with "to find" rather than guessing.

**Contacts and privacy:**
- Never invent or guess an email address (no "firstname.lastname@" patterns). Use only channels the company publishes.
- Prefer company channels (careers page, recruitment email, contact form). A named person (HR, hiring manager) is fine only if their professional role is publicly listed (company site, LinkedIn); record name and role only, never personal phone numbers or private emails.
- Don't use the directory's list of directors as contacts; that's not what it's for.

## 5. Present the results
Table, best fit first:

| # | Company | Activity | City | Size (local) | Website | How to apply | Why it fits |
|---|---------|----------|------|--------------|---------|--------------|-------------|

Below it: how many companies the directory returned vs. how many were shortlisted, and what was left out and why (too far, too small, deal-breaker sector…). If very few match, suggest widening (nearby communes, related sectors, other sizes).

Then export to Excel with the same script as for offers, as a separate file: `entreprises-YYYY-MM-DD.xlsx` (French) or `companies-YYYY-MM-DD.xlsx`, sheet name like "Entreprises 2026-11-25". Columns: the table's columns plus "Official record" (registry link), "Verified" (yes / to find) and "Alert".

## 6. Next steps
- Offer to draft unsolicited letters/emails (`application-templates.md`, "Unsolicited application"), personalised with each company's hook. Batch-writing identical letters gets poor results: suggest starting with the top 3–5.
- Add the companies the user picks to the tracking table: Role = "Unsolicited – <target role>", status "To apply".
- Set expectations honestly: unsolicited applications get fewer answers than replies to offers; personalisation and one polite follow-up after 7–10 days make the difference.
