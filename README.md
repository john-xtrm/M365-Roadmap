# Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt overzicht van aankomende Microsoft 365-updates, gebouwd op GitHub Pages met Vanilla HTML/CSS/JS. Gratis gehost, geen server nodig.

🔗 **Live:** `https://john-xtrm.github.io/M365-Roadmap/`

---

## Wat het doet

Elke **maandag om 06:00 UTC** haalt een GitHub Actions workflow de publieke Microsoft 365 roadmap op, vertaalt de items naar het Nederlands en slaat het resultaat op als `data.json`. De vijf HTML-pagina's laden deze data client-side en tonen een gefilterd, doorzoekbaar overzicht.

| Pagina | Doel |
|---|---|
| `index.html` | Hoofdoverzicht met filters (product, actie, periode, status) |
| `kalender.html` | Releasekalender per maand of kwartaal |
| `archief.html` | Weekarchief van verdwenen roadmap-items |
| `presentatie.html` | PowerPoint-generator op basis van selectie |
| `architectuur.html` | C4-architectuurkaart van het dashboard zelf |

---

## Bestandsstructuur

```
M365-Roadmap/
├── .github/
│   └── workflows/
│       ├── update-roadmap.yml      # Wekelijks: data ophalen + vertalen
│
├── archive/                        # Weekbestanden (automatisch, max 3 mnd)
│   ├── index.json
│   └── YYYY-MM-DD.json
│
├── index.html                      # Hoofdpagina
├── kalender.html                   # Releasekalender
├── archief.html                    # Weekarchief
├── presentatie.html                # PPTX-generator
├── architectuur.html               # C4-architectuurkaart
│
├── shared.css                      # Gedeelde stijlen, design tokens, dark mode
├── archief.css                     # Paginaspecifieke stijlen
├── kalender.css
├── presentatie.css
├── architectuur.css
│
├── app-meta.js                     # Product-iconen (base64) en APP_ICONS object
├── shared.js                       # Gedeelde JS: renderNav, toggleTheme,
│                                   # hulpfuncties, APP_META, APP_ORDER
│
├── fetch_roadmap.py                # Wekelijks script: CSV → data.json
└── data.json                       # Actuele roadmap-data (automatisch bijgewerkt)
```

### Gedeelde JavaScript — twee lagen

| Bestand | Bevat | Geladen door |
|---|---|---|
| `app-meta.js` | `APP_ICONS` (base64 product-iconen) | Alle 5 HTML-pagina's |
| `shared.js` | `renderNav()`, `toggleTheme()`, `APP_META`, `APP_ORDER`, `cardHTML()`, `buildProductPills()`, hulpfuncties | Alle 5 HTML-pagina's |

### Uniforme kaartcomponent

`cardHTML(item, opts, query)` in `shared.js` genereert één kaarttype voor index, kalender en archief. Per pagina bepaalt een opts-object wat zichtbaar is:

| Optie | index | kalender | archief |
|---|---|---|---|
| ⭐ Nieuw badge | ✅ | — | — |
| Beschrijving | ✅ | ✅ | ✅ |
| Actieblok | ✅ | ✅ | — |
| Releasedatum | ✅ | ✅ | — |
| Technische details | ✅ | — | — |
| Toegevoegd/gewijzigd datums | ✅ | — | — |
| Details-link → index | — | ✅ | — |
| Kopieer-link | ✅ | — | — |
| Microsoft roadmap-link | ✅ | ✅ | ✅ |

### Badge "⭐ Nieuw"

Een item krijgt het Nieuw-badge als `added` valt in de **vorige kalenderweek** — dezelfde definitie als de "Vorige week" periodefilter. Na de volgende maandag-run verdwijnt het badge automatisch.

Elke pagina laadt beide bestanden bovenaan het body-script:
```html
<script src="app-meta.js"></script>
<script src="shared.js"></script>
```

De browser cachet beide bestanden — icons worden dus **één keer** geladen, niet meer per pagina. Navigatie en thema-toggle zijn gecentraliseerd in `shared.js`.

---

## Architectuur

```
Microsoft CSV API (aka.ms/MSRoadmapCSV)
        │  maandag 06:00 UTC
        ▼
GitHub Actions → fetch_roadmap.py
        │  EN→NL vertaling (Google Translate / deep_translator)
        ▼
data.json + archive/
        │  git push → GitHub Pages
        ▼
Browser → index.html / kalender.html / archief.html / ...
              ├── app-meta.js  (iconen, gecached)
              └── shared.js    (nav, functies, gecached)
```

Zie de live [Architectuurkaart](https://john-xtrm.github.io/M365-Roadmap/architectuur.html) voor het volledige C4-model.

---

## Producten

28 producten worden herkend en weergegeven met icoon:
Copilot · Teams · Outlook · Excel · Word · PowerPoint · SharePoint · Purview · Viva · Edge · OneDrive · Exchange · Forms · Intune · Entra · Planner · Loop · Whiteboard · To Do · Bookings · Stream · Power Automate · Power Apps · Power BI · Yammer · Defender · M365 Search · Project · Visio · Windows

---

## Kosten

**€0/maand** — GitHub Pages (hosting) + GitHub Actions (weekelijkse run) + Microsoft CSV API (geen auth) + Google Translate via `deep_translator` (gratis tier).

---

## Ontwikkeling

### Lokaal draaien

```bash
# Stap 1: clone de repo
git clone https://github.com/john-xtrm/M365-Roadmap.git
cd M365-Roadmap

# Stap 2: start een lokale server (vereist omdat fetch() werkt op file://)
python3 -m http.server 8080
# of: npx serve .

# Stap 3: open in browser
# http://localhost:8080
```

`data.json` is al aanwezig in de repo — je ziet direct echte data.

### Wijzigingen deployen

Push naar `main` → GitHub Pages deployt automatisch binnen ~1 minuut.

### Nieuwe pagina toevoegen

1. Maak `pagina.html` op basis van een bestaande pagina
2. Voeg `<script src="app-meta.js"></script>` + `<script src="shared.js"></script>` toe
3. Roep `renderNav('pagina')` aan als eerste JS-regel
4. Voeg de pagina toe aan `_NAV_ITEMS` in `shared.js`
5. Maak eventueel `pagina.css` aan voor paginaspecifieke stijlen

### Nieuw product toevoegen

1. Voeg het icoon (base64 PNG) toe aan `APP_ICONS` in `app-meta.js`
2. Voeg een entry toe aan `APP_META` in `shared.js`
3. Voeg de key toe aan `APP_ORDER` in `shared.js`
4. Voeg een `.p-{product}` klasse toe aan `shared.css` indien nodig
5. Voeg het product toe aan `APP_LABELS` + `DETECT_PATTERNS` in `fetch_roadmap.py`

### WCAG

Alle pagina's voldoen aan WCAG 2.2 AA. Bij elke wijziging controleren:
- `aria-current="page"` op actieve nav-link (via `renderNav()`)
- `aria-label` op interactieve elementen zonder zichtbare tekst
- Kleurcontrast ≥ 4.5:1 (tokens in `shared.css`)
- `prefers-reduced-motion` wordt gerespecteerd

---

## Data

`data.json` wordt elke maandag automatisch bijgewerkt via GitHub Actions. Schema:

```json
{
  "generated": "2026-04-01T06:12:34Z",
  "date": "2026-04-01",
  "count": 142,
  "items": [
    {
      "id": "string",
      "title_nl": "string",
      "benefit_nl": "string",
      "title_en": "string",
      "app": "teams | copilot | sharepoint | ...",
      "status": "rolling | dev",
      "action": "none | admin | user",
      "release": "April CY2026",
      "added": "2026-01-15",
      "modified": "2026-03-22",
      "moreInfoLink": "https://..."
    }
  ],
  "removed": [ /* items die verdwenen zijn t.o.v. vorige week */ ]
}
```
