# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard dat Microsoft 365 roadmap-items vertaalt naar begrijpelijk Nederlands, inclusief een uitleg wat elke update betekent voor de organisatie.

**Live:** [john-xtrm.github.io/M365-Roadmap](https://john-xtrm.github.io/M365-Roadmap/)

---

## Pagina-overzicht

| Pagina | Functie |
|---|---|
| `index.html` | Hoofdpagina — alle actieve roadmap-items met filters |
| `kalender.html` | Releasekalender — kort (6 mnd) en lang (per kwartaal) |
| `archief.html` | Archief — verdwenen items (uitgerold of geannuleerd) per week |
| `presentatie.html` | Presentatiegenerator — download klantgerichte .pptx per product/week |
| `architectuur.html` | Architectuurkaart — C4-model van de volledige oplossing |
| `shared.css` | Gedeeld design system — kleuren, tokens, componenten |
| `fetch_roadmap.py` | Data-pipeline — haalt CSV op, vertaalt, schrijft JSON |

**Navigatievolgorde (alle pagina's):** Roadmap · Kalender · Archief · Presentatie · Architectuur · Thema

---

## Architectuur

```
Microsoft CSV API
    ↓ (maandag 06:00 UTC, GitHub Actions)
fetch_roadmap.py
    ↓ vertalen via Google Translate
data.json + archive/YYYY-MM-DD.json
    ↓ (GitHub Pages CDN)
Browser → index.html / kalender.html / archief.html / presentatie.html
```

### Stack

| Laag | Technologie |
|---|---|
| Hosting | GitHub Pages (gratis, HTTPS) |
| Automatisering | GitHub Actions (cron maandag 06:00 UTC) |
| Data-bron | Microsoft publieke CSV feed (`aka.ms/MSRoadmapCSV`) |
| Vertaling | Google Translate via `deep_translator` (gratis tier) |
| Presentatie | PptxGenJS (Node.js) |
| Frontend | Vanilla HTML/CSS/JS — geen framework |
| Kosten | **€0/maand** |

---

## Functionaliteit

### Hoofdpagina — `index.html`
- Standaard filter: **Vorige kalenderweek**
- Filters: product (16 iconen inline base64), actie, periode, status (incl. ⭐ Nieuw), sortering
- Legenda voor actie-types direct onder de filterbalk
- Zoekbalk met trefwoord of `?id=` directe links
- Directe item-link: kopieer-knop per kaart → `?id=123` URL
- Bij `?id=` navigatie: scroll naar item met blauwe pulse-animatie
- Lege staat bij "Vorige week": suggestieknop "Toon alle periodes"
- Statistiekenbalk: pills links, "Bijgewerkt: datum · items" rechts
- Slimme SessionStorage-cache: ongeldig na maandag 06:00 UTC of na 30 minuten

### Releasekalender — `kalender.html`
- **Korte termijn**: per maand, exacte datums, komende 6 maanden
- **Lange termijn**: per kwartaal, periodfilter (huidig+toekomst / jaar / alles)
- Details-knop via `?id=` terug naar index.html

### Archiefpagina — `archief.html`
- Toont per week welke items van de roadmap zijn **verdwenen** (uitgerold of geannuleerd)
- Zoekbalk filtert verdwenen items op titel binnen de geselecteerde week
- Weekknoppen alleen zichtbaar als het bestand daadwerkelijk verdwenen items bevat (gevalideerd via fetch vóór weergave)
- Kaarten gegroepeerd: ✅ Uitgerold / ❌ Geannuleerd
- Maximaal 3 maanden terug bewaard

### Presentatiegenerator — `presentatie.html`
- Selecteer producten, week en klantnaam
- Genereert klantgerichte `.pptx` direct in de browser via PptxGenJS
- Week-tabs voor recente weken
- Preview-statistieken per selectie

### Architectuurkaart — `architectuur.html`
- C4-model (C1–C4): Context · Container · Component · Code
- Klikbare nodes met detailpanels
- Trust boundary zones
- Consistent met design system (dark mode, CSS-variabelen)

---

## Data-pipeline — `fetch_roadmap.py`

```
1. Laad bestaande vertalingen uit data.json als cache
2. Haal Microsoft CSV op (Accept-Language: en-US voor botdetectie)
3. Detecteer actie-type: none / admin / user
4. Vertaal ALLEEN nieuwe/gewijzigde items via Google Translate
5. Schrijf data.json (alle actieve items + removed[])
6. Schrijf archive/YYYY-MM-DD.json (alleen als removed[] niet leeg)
7. Verwijder lege archiefbestanden (removed:[])
8. Bijwerk archive/index.json (max 3 maanden)
9. Schrijf GitHub Actions Step Summary
```

### Verdwenen items detectie
Items die in de vorige `data.json` stonden maar niet meer in de CSV zijn:
- Status `launched` → Uitgerold
- Status `cancelled` → Geannuleerd
- Worden opgeslagen in `removed[]` van het archiefbestand

### Archief-weekknoppen
Vóór het tonen van weekknoppen haalt `archief.html` elk archiefbestand op en controleert of `removed.length > 0`. Lege weken krijgen geen knop. `fetch_roadmap.py` slaat ook alleen een archiefbestand op als er verdwenen items zijn.

---

## GitHub Actions

**Workflow:** `.github/workflows/update-roadmap.yml`

- **Trigger:** `cron: '0 6 * * 1'` (maandag 06:00 UTC) + `workflow_dispatch`
- **Stappen:** checkout → pip install → fetch_roadmap.py → git commit → git push
- **Step Summary:** na elke run een samenvatting in de Actions-tab met item-aantallen en verdwenen items

---

## Navigatie & WCAG

- **WCAG 3.2.3 Consistent Navigation (AA):** identieke volgorde op alle pagina's
- **aria-current="page":** actieve pagina gemarkeerd voor screenreaders
- **Actieve stijl:** donkere achtergrond (`var(--text)`) + `color: var(--surface)`
- **WCAG 2.5.8 Target Size:** alle knoppen minimaal 44×44px

---

## Design system — `shared.css`

| Token | Gebruik |
|---|---|
| `--bg`, `--surface`, `--surface2` | Achtergronden |
| `--text`, `--muted`, `--faint` | Tekstniveaus |
| `--border`, `--border-s` | Randen |
| `--blue-t`, `--blue-bg` | Primaire accentkleur |
| `--green-*`, `--amber-*`, `--red-*` | Status-kleuren |
| `--c-none`, `--c-admin`, `--c-user` | Actie-indicatoren |
| `--radius-sm/md/lg/pill` | Afrondingen |
| `--font` | Inter, systeem-fallback |

**Dark mode:** automatisch via `prefers-color-scheme` + handmatig via `localStorage` toggle.

---

## Terminologie

| Term | Betekenis |
|---|---|
| **Automatisch** | Geen actie nodig — Microsoft voert dit door |
| **IT-beheerder** | Technische actie of beoordeling vereist |
| **Medewerker** | Medewerker kan dit zelf instellen of kiezen |
| **Uitgerold** | Item is beschikbaar gekomen (Launched) |
| **Geannuleerd** | Item is ingetrokken door Microsoft (Cancelled) |
| **Verdwenen** | Item staat niet meer op de actieve roadmap |

---

## Actuele functies (april 2026)

| Functie | Beschrijving |
|---|---|
| Directe item-link | Kopieer-knop per kaart → `?id=123` URL. Scroll + highlight bij navigatie. |
| Slimme cache | SessionStorage ongeldig na maandag 06:00 UTC of 30 minuten. |
| Lege staat periode | Bij geen resultaten voor "Vorige week": suggestieknop voor alle periodes. |
| Legenda | Compact overzicht van actie-types onder de filterbalk. |
| Zoeken in archief | Zoekbalk filtert verdwenen items op titel binnen de geselecteerde week. |
| Status-filter Nieuw | Filter ⭐ Nieuw toont alleen items die deze week zijn toegevoegd/gewijzigd. |
| GitHub Step Summary | Samenvatting na elke workflow-run in de Actions-tab. |
| Opschonen archieven | Lege archiefbestanden worden automatisch verwijderd bij volgende run. |
| Presentatiegenerator | Download klantgerichte .pptx direct vanuit de browser. |

---

## Lokaal testen

1. Kloon de repository
2. Open in VS Code
3. Installeer extensie **Live Server** (Ritwick Dey)
4. Rechtermuisknop op `index.html` → **Open with Live Server**

Voor de data-pipeline lokaal draaien:
```bash
pip install deep-translator
python fetch_roadmap.py
```

---

## Repository structuur

```
/
├── index.html          # Hoofdpagina
├── kalender.html       # Releasekalender
├── archief.html        # Archief verdwenen items
├── presentatie.html    # Presentatiegenerator
├── architectuur.html   # C4-architectuurkaart
├── shared.css          # Gedeeld design system
├── fetch_roadmap.py    # Data-pipeline
├── data.json           # Gegenereerde roadmap-data (auto)
├── archive/
│   ├── index.json      # Lijst beschikbare archiefweken (auto)
│   └── YYYY-MM-DD.json # Verdwenen items per week (auto, alleen als niet leeg)
└── .github/
    └── workflows/
        └── update-roadmap.yml
```
