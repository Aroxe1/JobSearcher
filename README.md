# job-search — Claude skill

🇫🇷 [Français](#-français) · 🇬🇧 [English](#-english)

---

## 🇫🇷 Français

Un skill Claude pour chercher une **alternance**, un **stage** ou un **emploi**. Il commence par **apprendre à vous connaître** (quelques questions courtes), enregistre vos réponses dans un **fichier de profil local**, puis cherche des **offres réelles et récentes** adaptées à votre profil. Aux sessions suivantes, Claude se souvient de vous et ne repose pas les mêmes questions.

Pour étudiants, jeunes diplômés, personnes en reconversion — tous domaines, tous pays.

### Ce qu'il fait
- **Onboarding** par petits groupes de questions (type de contrat, formation, poste visé, dates, lieu, compétences…). Les questions sensibles sont toujours facultatives.
- **Profil local** en Markdown, réutilisé à chaque session et modifiable à la main.
- **Recherche d'offres** sur plusieurs sources adaptées à votre pays (ex. France : France Travail, La Bonne Alternance, Welcome to the Jungle, Indeed, LinkedIn, JobTeaser…), présentées dans un tableau trié par pertinence, avec signalement des offres douteuses ou périmées. Aucune offre inventée.
- **Export Excel** : à la fin de chaque recherche, les offres sont enregistrées dans un fichier `.xlsx` (liens cliquables, colonnes filtrables) à côté de votre profil. Il faut seulement Python, sans rien installer de plus.
- **Candidatures** : adaptation du CV, lettre de motivation, mail de candidature, préparation d'entretien, relances.
- **Suivi** des candidatures (statut, prochaine action, date de relance).
- Claude **n'envoie jamais rien** à votre place sans votre accord explicite.

### Installation

**Claude Code (recommandé) — via le marketplace**, deux commandes à taper dans Claude Code :

```
/plugin marketplace add Aroxe1/JobSearcher
/plugin install job-search@job-search-skill
```

Ou, depuis un terminal : `claude plugin marketplace add Aroxe1/JobSearcher` puis `claude plugin install job-search@job-search-skill`. Mise à jour : `/plugin marketplace update job-search-skill`.

**Claude Code — copie manuelle** du dossier `job-search` dans vos skills :

```bash
git clone https://github.com/Aroxe1/JobSearcher.git
mkdir -p ~/.claude/skills
cp -r JobSearcher/job-search ~/.claude/skills/
```

Sous Windows (PowerShell) : `Copy-Item -Recurse JobSearcher\job-search $HOME\.claude\skills\`

Pour un seul projet : copiez-le plutôt dans `.claude/skills/` à la racine du projet.

**Claude.ai / application Claude** — compressez le dossier `job-search` en `.zip`, puis importez-le dans *Paramètres → Capacités → Skills*. (Sans accès aux fichiers, Claude vous donnera le profil à copier et à recoller la fois suivante.)

La recherche d'offres nécessite que la **recherche web** soit activée.

### Exemples de phrases qui le déclenchent
- « Je cherche une alternance en développement web à Lyon pour septembre »
- « Aide-moi à trouver un stage de 6 mois en marketing »
- « Trouve-moi des offres de CDI en comptabilité près de Nantes »
- « Peux-tu adapter mon CV pour cette offre ? »
- « Rédige une lettre de motivation pour ce poste »
- « Je dois relancer une entreprise, tu m'aides ? »
- « Je suis en reconversion, je ne sais pas quel métier viser »

### Confidentialité du profil
- Le profil est enregistré **sur votre ordinateur uniquement** : par défaut `~/.job-search/profile.md`, ou `job-search-profile.md` dans le dossier courant si vous le préférez.
- C'est un simple fichier texte : vous pouvez le lire, le modifier ou le supprimer à tout moment.
- Claude n'y enregistre **jamais** de mot de passe, numéro de sécurité sociale, pièce d'identité ou coordonnées bancaires.
- ⚠️ **Ne commitez jamais votre fichier de profil.** Le `.gitignore` de ce repo exclut `job-search-profile.md`, `.job-search/` ainsi que les `.pdf`/`.docx`/`.xlsx`/`.csv` (pour éviter de publier un CV ou vos exports d'offres par erreur) — mais les autres repos n'ont pas cette règle. Vérifiez avec `git status` avant chaque commit.

### Structure

```
.claude-plugin/                     # marketplace.json + plugin.json (installation via /plugin)
job-search/
├── SKILL.md                         # instructions du skill
├── references/
│   ├── onboarding-questions.md      # banque de questions détaillée
│   ├── job-sources.md               # sources d'offres par pays
│   ├── application-templates.md     # CV, lettre, mail, relance, entretien
│   └── application-tracking.md      # suivi des candidatures
├── scripts/
│   └── export_offers.py             # export des offres en .xlsx (Python standard)
└── templates/
    └── profile.md                   # modèle vierge du profil
```

Contributions bienvenues, en particulier pour ajouter des sources d'offres pour d'autres pays (`references/job-sources.md`).

### Licence
MIT — voir [LICENSE](LICENSE).

---

## 🇬🇧 English

A Claude skill to look for an **apprenticeship / work-study**, an **internship** or a **job**. It first **gets to know you** (a few short questions), saves your answers in a **local profile file**, then searches for **real, current offers** that fit your profile. Next time, Claude remembers you and doesn't ask the same questions again.

For students, recent graduates and career changers — any field, any country.

### What it does
- **Onboarding** in small groups of questions (contract type, studies, target role, dates, location, skills…). Sensitive questions are always optional.
- **Local profile** in Markdown, reused every session and editable by hand.
- **Job search** across several sources suited to your country (e.g. UK: Find an apprenticeship, Prospects, Indeed; US: Handshake, LinkedIn, USAJOBS…), shown in a table sorted by fit, with suspicious or expired offers flagged. No made-up offers.
- **Excel export**: after each search, offers are saved to an `.xlsx` file (clickable links, filterable columns) next to your profile. Only needs Python, nothing else to install.
- **Applications**: CV tailoring, cover letters, application emails, interview prep, follow-ups.
- **Tracking** of applications (status, next action, follow-up date).
- Claude **never sends anything** on your behalf without your explicit approval.

### Installation

**Claude Code (recommended) — via the marketplace**, two commands inside Claude Code:

```
/plugin marketplace add Aroxe1/JobSearcher
/plugin install job-search@job-search-skill
```

Or from a terminal: `claude plugin marketplace add Aroxe1/JobSearcher` then `claude plugin install job-search@job-search-skill`. Update with `/plugin marketplace update job-search-skill`.

**Claude Code — manual copy** of the `job-search` folder into your skills:

```bash
git clone https://github.com/Aroxe1/JobSearcher.git
mkdir -p ~/.claude/skills
cp -r JobSearcher/job-search ~/.claude/skills/
```

On Windows (PowerShell): `Copy-Item -Recurse JobSearcher\job-search $HOME\.claude\skills\`

For a single project: copy it into `.claude/skills/` at the project root instead.

**Claude.ai / Claude app** — zip the `job-search` folder and upload it in *Settings → Capabilities → Skills*. (Without file access, Claude gives you the profile to copy and paste back next time.)

Job search requires **web search** to be enabled.

### Example prompts that trigger it
- "I'm looking for a software engineering internship in Berlin for next summer"
- "Find me entry-level data analyst jobs near Manchester"
- "Help me find an apprenticeship in electrical engineering"
- "Can you tailor my CV to this job posting?"
- "Write a cover letter for this role"
- "I applied to Acme two weeks ago and heard nothing — help me follow up"
- "I'm changing careers and don't know which jobs to target"

### Profile privacy
- The profile is stored **on your computer only**: by default `~/.job-search/profile.md`, or `job-search-profile.md` in the current folder if you prefer.
- It's a plain text file: read, edit or delete it any time.
- Claude **never** stores passwords, social security/national ID numbers, ID documents or bank details in it.
- ⚠️ **Never commit your profile file.** This repo's `.gitignore` excludes `job-search-profile.md`, `.job-search/` and `.pdf`/`.docx`/`.xlsx`/`.csv` files (so a CV or offer export doesn't get published by mistake) — but other repos don't have that rule. Check `git status` before every commit.

### Contributing
Contributions welcome, especially job sources for more countries (`references/job-sources.md`).

### License
MIT — see [LICENSE](LICENSE).
