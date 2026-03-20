# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard voor Microsoft 365-roadmap updates in begrijpelijk Nederlands.

**Volledig gratis** — GitHub Pages + GitHub Actions + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Bestanden

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap met vereenvoudigd filterblok |
| `archief.html` | Archiefpagina — weekoverzichten tot 3 maanden terug |
| `kalender.html` | Releasekalender — per maand of per kwartaal |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `app-meta.js` | Gedeelde product-metadata + iconen (base64, geen losse bestanden) |
| `fetch_roadmap.py` | Python-script dat CSV ophaalt, vertaalt en `data.json` aanmaakt |
| `data.json` | Gegenereerde data (automatisch, niet handmatig bewerken) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Archief per week (max 3 maanden) |

> **Geen `icons/` map nodig** — alle product-iconen zijn als geoptimaliseerde base64 data-URI embedded in `app-meta.js`. Dit voorkomt laadproblemen in Teams-tabs en sandboxed omgevingen en vereenvoudigt de repository-structuur.

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
app-meta.js
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

## Architectuur

```
Microsoft CSV API (publiek, gratis)
         │
         ▼
  GitHub Actions (ma + wo 06:00 UTC)
         │
         ├─ fetch_roadmap.py
         │    ├── CSV ophalen
         │    ├── Cache laden + vertalen (alleen nieuw/gewijzigd)
         │    ├── Launched/Cancelled detecteren
         │    ├── data.json wegschrijven
         │    └── archive/YYYY-MM-DD.json opslaan
         │
         └─ git push → GitHub Pages
```

---

## Filterblok (`index.html`)

| Filter | Standaard | Omschrijving |
|---|---|---|
| Product | Alle producten | Icoon + naam + live aantal |
| Actie nodig? | Alles | Automatisch / IT-beheerder / Medewerker |
| Sorteren | Toegevoegd: nieuwste eerst | 5 sorteeropties |
| Periode | Deze week | Filtert op toegevoegd én gewijzigd. Toont weeknummer + datumrange. |
| Status | Alles | Uitgerold / In ontwikkeling |

**Kalenderweek-filter:** gebruikt ISO-weeknummers (ma t/m zo). Op maandag reset het filter automatisch.

**"Nieuw" badge:** item is nieuw als het in de huidige kalenderweek toegevoegd of gewijzigd is.

**URL-parameters:**
- `?id=123456` — filtert direct op MS-ID, reset alle datumfilters
- `?zoek=Teams` — vult zoekbalk voor

---

## `app-meta.js`

Gedeeld door alle pagina's via `<script src="app-meta.js">`. Bevat:

- `APP_META` — labels en pill-kleuren per product
- `APP_ORDER` — volgorde productfilter
- `APP_ICONS` — base64 PNG-iconen (64×64 px, geoptimaliseerd, ~80 KB totaal)
- `appIconHTML(key)` — geeft `<img>`-element terug voor gebruik in buttons en pills
- `appLabelHTML(key, label)` — icoon + label gecombineerd

**Icoon vervangen:** converteer het nieuwe PNG naar base64 en vervang de waarde in `APP_ICONS` in `app-meta.js`.

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.3.1 Koppen-hiërarchie | h1 → h2 → h3 |
| 1.4.3 Kleurcontrast ≥4.5:1 | Getest, incl. dark mode |
| 1.4.4 Tekst schaalbaar | Alle font-sizes in `rem` |
| 2.4.1 Skip-link | Op alle pagina's |
| 2.4.7 Focusindicator | `:focus-visible` overal |
| 2.4.11 Focus niet verborgen | `scroll-margin-top` via shared.css |
| 2.5.8 Raakdoelgrootte | Min. 44px op alle knoppen |
| 3.1.1 Taal | `lang="nl"` |
| 4.1.2 Naam/rol/waarde | `aria-pressed`, `aria-expanded`, `aria-live` |
| Product-iconen | `aria-hidden="true"` — tekst van knop is de naam |

---

## Kosten

**€0 per maand** — GitHub Pages + Actions (gratis tier, ~3-5 min/week) + Microsoft CSV + Google Translate.

---

## Onderhoud

**Workflow mislukt?** Actions → mislukte run → Re-run. Woensdag-run pikt maandagfouten op.

**Vertaling corrigeren?** Pas `title` of `benefit` aan in `data.json`. Blijft behouden zolang Microsoft het item niet wijzigt.

**Icoon vervangen?** PNG → base64 → vervang waarde in `APP_ICONS` in `app-meta.js`.
