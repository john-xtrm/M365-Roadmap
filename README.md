# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard voor Microsoft 365-roadmap updates in begrijpelijk Nederlands.

**Volledig gratis** — GitHub Pages + GitHub Actions + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Bestanden in de repository

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap |
| `archief.html` | Archiefpagina — weekoverzichten tot 3 maanden terug |
| `kalender.html` | Releasekalender — per maand of per kwartaal |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `fetch_roadmap.py` | Python-script voor de workflow |
| `data.json` | Gegenereerde roadmapdata (automatisch bijgewerkt) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Archief per week (max 3 maanden) |

> **Geen `icons/` map of `app-meta.js` nodig.** Alle product-iconen zijn als geoptimaliseerde base64 data-URI direct in elke HTML-pagina ingebouwd. Dit maakt de repository eenvoudiger en voorkomt laadproblemen in sandboxed omgevingen zoals Teams-tabs.

---

## Installatie

### 1. Repository aanmaken
Maak een nieuwe **publieke** GitHub-repository aan (bijv. `M365-Roadmap`).

### 2. Bestanden uploaden
```
index.html
archief.html
kalender.html
shared.css
fetch_roadmap.py
.github/workflows/update-roadmap.yml
```

### 3. GitHub Pages inschakelen
**Settings → Pages → Source**: Deploy from a branch → `main` / `(root)`

### 4. Eerste run starten
**Actions → Ververs Microsoft 365 Roadmap → Run workflow**

### 5. Teams-tabblad instellen (optioneel)
Kanaal → **+** → **Website** → GitHub Pages URL → Opslaan

---

## Filterblok (`index.html`)

| Filter | Standaard | Omschrijving |
|---|---|---|
| Product | Alle producten | Icoon + naam + live aantal |
| Actie nodig? | Alles | Automatisch / IT-beheerder / Medewerker |
| Sorteren | Toegevoegd: nieuwste eerst | 5 sorteeropties |
| Periode | Deze week | Filtert op items toegevoegd én gewijzigd in de geselecteerde kalenderweek |
| Status | Alles | Uitgerold / In ontwikkeling |

**Kalenderweek:** ISO-weeknummers (ma t/m zo). Op maandag reset het filter naar de nieuwe week.

**URL-parameters:**
- `?id=123456` — filtert direct op MS-ID (alle datumfilters gereset)
- `?zoek=Teams` — vult zoekbalk voor

---

## Toegankelijkheid (WCAG 2.2 AA)

Alle pagina's: skip-link, `lang="nl"`, noscript, `aria-pressed`, `aria-live`, `aria-label`, `:focus-visible`, `scroll-margin-top`, minimale raakdoelgrootte 44px, alle font-sizes in `rem`, dark mode, reduced-motion.

Product-iconen zijn `aria-hidden="true"` — de tekst van de knop is de toegankelijke naam.

---

## Kosten

**€0 per maand** — GitHub Pages + Actions (gratis tier) + Microsoft CSV + Google Translate.

---

## Onderhoud

**Workflow mislukt?** Actions → mislukte run → Re-run. Woensdag-run pikt maandagfouten op.

**Vertaling corrigeren?** Pas `title` of `benefit` aan in `data.json`. Blijft behouden zolang Microsoft het item niet wijzigt.
