# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard voor Microsoft 365-roadmap updates in begrijpelijk Nederlands. Bedoeld voor niet-technische medewerkers die willen weten wat er aan te komen is en of er actie nodig is.

**Volledig gratis** — GitHub Pages + GitHub Actions + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Bestanden in de repository

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap met filters en product-iconen |
| `archief.html` | Archiefpagina — weekoverzichten tot 3 maanden terug |
| `kalender.html` | Releasekalender — per maand (kort) of per kwartaal (lang) |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `fetch_roadmap.py` | Python-script dat de CSV ophaalt, vertaalt en `data.json` aanmaakt |
| `data.json` | Gegenereerde roadmapdata (automatisch bijgewerkt, niet handmatig bewerken) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Archief per week (automatisch aangemaakt, max 3 maanden) |

> **Geen `icons/` map of `app-meta.js` nodig.** Alle product-iconen (16 stuks, 64×64 px) zijn als geoptimaliseerde base64 data-URI direct in elke HTML-pagina ingebouwd. Dit voorkomt laadproblemen in sandboxed omgevingen zoals Teams-tabs en maakt de repository eenvoudiger.

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

De pagina is bereikbaar op:
```
https://<gebruikersnaam>.github.io/<repository-naam>/
```

### 4. Eerste run starten
**Actions → Ververs Microsoft 365 Roadmap → Run workflow**

Dit genereert `data.json` en de eerste archiefbestanden.

### 5. Teams-tabblad instellen (optioneel)
Kanaal → **+** → **Website** → GitHub Pages URL → Opslaan

---

## Architectuur

```
Microsoft CSV API (publiek, gratis)
         │
         ▼
  GitHub Actions (maandag + woensdag 06:00 UTC)
         │
         ├─ fetch_roadmap.py
         │    ├── CSV ophalen via curl (met browser-headers)
         │    ├── Vertalingen laden uit cache (data.json)
         │    ├── Alleen nieuwe/gewijzigde items vertalen
         │    ├── Launched/Cancelled items detecteren
         │    ├── data.json wegschrijven
         │    └── archive/YYYY-MM-DD.json opslaan
         │
         └─ git push → GitHub Pages
                  │
                  ├── index.html     (actuele roadmap)
                  ├── kalender.html  (releasekalender)
                  └── archief.html   (weekoverzichten)
```

---

## Hoofdpagina (`index.html`)

### Filters

| Filter | Standaard | Omschrijving |
|---|---|---|
| Product | Alle producten | Officieel icoon + naam + live aantal. Alleen producten met items worden getoond. |
| Actie nodig? | Alles | Automatisch / IT-beheerder / Medewerker |
| Sorteren | Toegevoegd: nieuwste eerst | 5 opties |
| Periode | Deze week | Filtert op items toegevoegd én gewijzigd in de kalenderweek. Toont weeknummer + datumrange op knop en in header. |
| Status | Alles | Uitgerold / In ontwikkeling |

### Weekfilter
Gebruikt ISO-kalenderweken (maandag t/m zondag). Op maandag reset het filter automatisch naar de nieuwe week. De actieve week is altijd zichtbaar als badge in de header en op de filterknop.

### "Nieuw"-badge
Een item is nieuw als het in de huidige kalenderweek aan de roadmap is **toegevoegd of gewijzigd**. Dit is consistent met het weekfilter.

### URL-parameters
- `?id=123456` — opent de pagina met dat MS-ID direct gefilterd; alle datumfilters worden gereset zodat het item altijd gevonden wordt. Wordt gebruikt vanuit de releasekalender.
- `?zoek=Teams` — vult de zoekbalk voor met de opgegeven term.

---

## Releasekalender (`kalender.html`)

| Onderdeel | Omschrijving |
|---|---|
| **Korte termijn** | Per maand, komende 6 maanden, alleen items met exacte maanddatum |
| **Lange termijn** | Per kwartaal, start bij huidig kwartaal |
| **Periodfilter** | Huidig + toekomst (standaard), specifiek jaar, of alles — alleen zichtbaar bij lange termijn |
| **Productfilter** | Met officieel icoon per product |
| **Actiefilter** | Automatisch / IT-beheerder / Medewerker |
| **Mini-uitsplitsing** | Periodeheader toont #IT, #medewerker, #auto per periode |
| **Details-knop** | Stuurt via `?id=` naar de hoofdpagina voor de volledige beschrijving |
| **"Ook in maandweergave"** | Badge op items met exacte maanddatum in de lange-termijn weergave |
| **Lege maanden** | Compact en gedimpt weergegeven |
| **Kwartaalblok** | Standaard open, items visueel gedimpt om onzekerheid aan te geven |

---

## Archiefpagina (`archief.html`)

- Laadt `archive/index.json` voor de lijst van beschikbare weken
- Meest recente week automatisch geladen
- Weekknoppen voor alle beschikbare weken (max 3 maanden terug)
- Productfilter per week met officieel icoon
- Statistieken en gewijzigde items per week

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.3.1 Koppen-hiërarchie | h1 header → h2 secties → h3 kaarttitels |
| 1.4.3 Kleurcontrast ≥4.5:1 | Alle kleuren getest incl. dark mode |
| 1.4.4 Tekst schaalbaar | Alle font-sizes in `rem` |
| 2.4.1 Skip-link | Op alle pagina's als eerste element |
| 2.4.7 Focusindicator | `:focus-visible` op alle interactieve elementen |
| 2.4.11 Focus niet verborgen | `scroll-margin-top` via shared.css |
| 2.5.8 Raakdoelgrootte ≥24px | Min. 44px hoogte op alle knoppen |
| 3.1.1 Taal | `lang="nl"` op elk document |
| 4.1.2 Naam/rol/waarde | `aria-pressed`, `aria-expanded`, `aria-live`, `aria-label` |
| 4.1.3 Statusberichten | `aria-live` op resultatenbalken en weekbadge |

**Product-iconen:** alle iconen zijn `aria-hidden="true"` — de tekst van de knop is de toegankelijke naam.

---

## Technische details

### Iconen
Alle 16 product-iconen zijn opgeslagen als base64-gecodeerde PNG (64×64 px, geoptimaliseerd) direct in elke HTML-pagina. Voordelen:
- Werkt altijd, ook in sandboxed omgevingen (Teams-tabs, previews)
- Geen aparte HTTP-requests per icoon
- Browser cachet de gehele pagina inclusief iconen

### Performance
- **SessionStorage-cache**: `data.json` 30 minuten gecached — herlaad is direct
- **Cache-buster**: `?v=timestamp` om GitHub Pages CDN-cache te omzeilen
- **Fetch-timeout**: verzoeken afgebroken na 12 seconden met foutmelding
- **Debounce**: zoekbalk 200ms na laatste toetsaanslag
- **Event delegation**: één listener per filtergroep

### Weekberekening
- `isoWeek(date)` — ISO-weeknummer (1–53)
- `weekStart(date)` — maandag 00:00 van die week
- `weekEnd(date)` — zondag 23:59:59 van dezelfde week
- `inSameWeek(d, ref)` — controleert of datum `d` in dezelfde kalenderweek valt als `ref`

---

## Kosten

**€0 per maand** — GitHub Pages + Actions (gratis tier, ~3-5 min/week) + Microsoft CSV + Google Translate.

---

## Onderhoud

**Workflow mislukt?** Actions → mislukte run → Re-run. De woensdag-run pikt maandagfouten automatisch op.

**Vertaling corrigeren?** Pas `title` of `benefit` aan in `data.json`. De cache herkent het item op `(id, modified)` — uw correctie blijft behouden zolang Microsoft het item niet wijzigt.

**Product niet herkend?** Voeg het toe aan `DETECT_PATTERNS` in `fetch_roadmap.py` en update `APP_META` en `APP_ORDER` in de drie HTML-pagina's.
