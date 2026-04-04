# Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt dashboard dat Microsoft 365 roadmap-updates vertaalt naar Nederlands en visualiseert voor medewerkers en IT-beheerders. Gratis gehost op GitHub Pages, zonder server of database.

🔗 **Live:** https://john-xtrm.github.io/M365-Roadmap/

---

## Inhoud

- [Functionaliteit](#functionaliteit)
- [Pagina-overzicht](#pagina-overzicht)
- [Architectuur](#architectuur)
- [Data-pipeline](#data-pipeline)
- [CSS-structuur](#css-structuur)
- [Installatie en gebruik](#installatie-en-gebruik)
- [Producten uitbreiden](#producten-uitbreiden)
- [Toegankelijkheid](#toegankelijkheid)
- [Kosten](#kosten)

---

## Functionaliteit

- **Wekelijks automatisch bijgewerkt** — elke maandag 06:00 UTC via GitHub Actions
- **Nederlandstalig** — titels en beschrijvingen vertaald via Google Translate
- **Filteren** op product, actie-type, periode en status
- **Actie-classificatie** per item: Automatisch · IT-beheerder · Medewerker
- **Releasekalender** — korte termijn (maanden) en lange termijn (kwartalen)
- **Archief** — verdwenen items (uitgerold of geannuleerd) tot 3 maanden terug
- **PowerPoint-generator** — wekelijkse klantpresentatie als .pptx downloaden
- **Dark mode** — automatisch via systeemvoorkeur of handmatig te schakelen
- **Teams-tab** — werkt als Microsoft Teams Website-tab zonder aanpassingen
- **WCAG 2.2 AA** — toegankelijk voor alle gebruikers, score 9.2/10

---

## Pagina-overzicht

| Pagina | Beschrijving |
|---|---|
| `index.html` | Hoofdpagina — roadmap-overzicht met filters, zoeken en statistieken |
| `kalender.html` | Releasekalender per maand of kwartaal met deep-link naar items |
| `archief.html` | Verdwenen items per week, lazy-loaded via archive/index.json |
| `presentatie.html` | PowerPoint-generator op maat per klant, gegenereerd in de browser |
| `architectuur.html` | Interactief C4-architectuurdiagram (C1–C4 niveaus, klikbare nodes) |

---

## Architectuur

Het systeem volgt het **C4-model** (Simon Brown):

```
Microsoft CSV API ──► fetch_roadmap.py ──► data.json ──► GitHub Pages ──► Browser
Google Translate ──►         │               archive/
                             └──► GitHub Actions (maandag 06:00 UTC)
```

### C1 · Context
- **Medewerker** — raadpleegt updates, filtert op actie-type, opent als Teams-tab
- **IT-beheerder** — beoordeelt actiepunten, beheert repository en Teams-tab
- **Microsoft CSV API** — publieke roadmap-feed zonder authenticatie
- **Google Translate** — machinale EN→NL vertaling via deep_translator

### C2 · Container
| Container | Type | Beschrijving |
|---|---|---|
| GitHub Actions | CI/CD | Wekelijkse pipeline: ophalen → vertalen → opslaan → publiceren |
| fetch_roadmap.py | Script | Data-pipeline in Python |
| data.json | Storage | Actueel snapshot met items, removed[] en vertaalcache |
| archive/ | Storage | Weekbestanden van verdwenen items + index.json |
| GitHub Pages | Hosting | CDN, HTTPS, gratis voor publieke repositories |
| HTML-pagina's (5x) | Frontend | Vanilla HTML/CSS/JS, geen framework |

### C3 · Component — Pipeline
| Component | Functie |
|---|---|
| CSV Fetcher | Haalt Microsoft CSV op via curl met browser-headers |
| Vertaalcache | Delta-detectie via SHA-256 hash, voorkomt dubbele vertalingen |
| Vertaalmodule | Vertaalt gewijzigde items via GoogleTranslator(en→nl) |
| Product- & statusdetectie | Matcht ProductFamily op 16 producten via DETECT_PATTERNS |
| Data Writer | Schrijft data.json, weekarchief en index.json, dan git push |

### C3 · Component — Frontend
| Component | Functie |
|---|---|
| index.html | Filters, SessionStorage cache (30 min), URL-params voor deep-linking |
| kalender.html | Korte/lange termijn weergave, periodfilter, ?id= deep-link |
| archief.html | loadIndex() + loadWeek() lazy loading, Promise.allSettled validatie |
| presentatie.html | PptxGenJS in browser, productselectie, automatische paginering |
| architectuur.html | Interactieve C4-diagram, ND-detaildata per component |
| CSS (5x) | shared.css + 4 paginaspecifieke bestanden |

---

## Data-pipeline

### Hoe het werkt

1. GitHub Actions checkt de repository uit
2. `pip install deep_translator` installeert de enige externe dependency
3. `python fetch_roadmap.py` voert de volledige pipeline uit:
   - CSV ophalen van aka.ms/MSRoadmapCSV
   - Bestaande data.json + vertaalcache laden
   - Delta detecteren (nieuwe/gewijzigde items via SHA-256 hash)
   - Gewijzigde items vertalen via Google Translate
   - Producten en status detecteren
   - data.json, weekarchief en index.json schrijven
4. `git add/commit/push` → GitHub Pages herdeployt automatisch

### data.json structuur

```json
{
  "generated": "ISO-timestamp",
  "count": 42,
  "items": [ RoadmapItem ],
  "removed": [ RoadmapItem ],
  "translation_cache": {
    "<id>": { "title_nl": "...", "benefit_nl": "...", "hash": "..." }
  }
}
```

### RoadmapItem velden

| Veld | Type | Beschrijving |
|---|---|---|
| `id` | string | Microsoft roadmap-ID (uniek) |
| `title_nl` | string | Vertaalde titel |
| `benefit_nl` | string | Vertaalde beschrijving |
| `title_en` | string | Originele Engelse titel |
| `app` | string | Product, bijv. `"teams"`, `"copilot"` |
| `status` | enum | `"rolling"` of `"dev"` |
| `action` | enum | `"none"` · `"admin"` · `"user"` |
| `release` | string | Leesbare releasedatum, bijv. `"mei 2026"` |
| `added` | string | ISO-datum eerste verschijning |
| `modified` | string | ISO-datum laatste wijziging |
| `moreInfoLink` | string | URL naar Microsoft docs |

### Archief

- `archive/YYYY-MM-DD.json` — verdwenen items van die week
- `archive/index.json` — gesorteerde lijst van beschikbare datums
- Bestanden ouder dan 90 dagen worden automatisch verwijderd
- Een weekbestand wordt alleen aangemaakt als `removed[]` niet leeg is

---

## CSS-structuur

De stijlen zijn opgesplitst in één gedeeld bestand en vier paginaspecifieke bestanden:

| Bestand | Scope | Inhoud |
|---|---|---|
| `shared.css` | Alle pagina's | Design tokens, knoppensysteem, kaarten, header, dark mode, WCAG |
| `kalender.css` | kalender.html | Periodeblokken, kalenderkaarten, weergave-schakelaar |
| `archief.css` | archief.html | Weekkiezer, archief-inhoud, gewijzigde-items blok |
| `presentatie.css` | presentatie.html | Hero, stappenblokken, productgrid, genereer-knop |
| `architectuur.css` | architectuur.html | Zones, nodes, pijlen, detail-panel, code-blokken |

### Design tokens aanpassen

Alle kleuren, radii en typografie staan als CSS custom properties in `shared.css`:

```css
:root {
  --bg:        #f5f4f0;   /* paginaachtergrond */
  --surface:   #ffffff;   /* kaarten, header */
  --surface2:  #f0ede8;   /* hover-achtergrond */
  --text:      #1a1916;   /* primaire tekst */
  --muted:     #5a5750;   /* secundaire tekst */
  --faint:     #605c58;   /* labels, meta — 5.0:1 contrast */
  --blue-t:    #143d82;   /* actiekleur / knoppen actief */
  --radius-pill: 100px;   /* pill-knoppen */
  /* ... */
}
```

Dark mode tokens staan direct eronder en worden automatisch toegepast via `prefers-color-scheme` of de thema-wisselknop.

---

## Installatie en gebruik

### Vereisten

- GitHub-account (gratis)
- Python 3.x (alleen voor lokale test)

### Opzetten

1. Fork of clone deze repository
2. Activeer GitHub Pages: **Settings → Pages → Source: main branch, root**
3. Controleer dat GitHub Actions is ingeschakeld: **Actions → Enable**
4. Optioneel: pas het cron-schema aan in `.github/workflows/update-roadmap.yml`

### Handmatig bijwerken

Ga naar **Actions → Update Roadmap → Run workflow** om buiten de planning een nieuwe datafetch te starten.

### Lokaal testen

```bash
pip install deep_translator
python fetch_roadmap.py
# Open index.html in een browser (via lokale webserver vanwege fetch-calls)
python -m http.server 8000
```

### Als Microsoft Teams-tab

1. Ga naar het gewenste Teams-kanaal
2. Klik op **+** → **Website**
3. Plak de GitHub Pages URL: `https://<gebruiker>.github.io/<repo>/`

---

## Producten uitbreiden

Om een nieuw M365-product toe te voegen:

1. **`fetch_roadmap.py`** — voeg het product toe aan `DETECT_PATTERNS`:
   ```python
   DETECT_PATTERNS = {
       "NieuwProduct": ["nieuwproduct", "alternatief"],
       # ...
   }
   ```

2. **Alle HTML-pagina's** — voeg het product toe aan `APP_META`, `APP_ORDER` en `APP_ICONS` (base64 PNG).

3. **`shared.css`** — voeg een pill-klasse toe:
   ```css
   .p-nieuwproduct { background: var(--teal-bg); color: var(--teal-t); }
   ```

---

## Toegankelijkheid

Het dashboard voldoet aan **WCAG 2.2 AA** (score: 9.2/10 via WAVE).

| Criterium | Status | Implementatie |
|---|---|---|
| 1.3.1 Info and Relationships | ✅ | `<article>`, `<section>`, `<h2>`, `<nav>`, ARIA-rollen |
| 1.4.3 Contrast (Minimum) | ✅ | Alle kleuren ≥ 4.5:1 getest, incl. `--faint` (#605c58) |
| 1.4.4 Resize Text | ✅ | Rem-gebaseerde typografie, schaalt met browservoorkeur |
| 2.1.1 Keyboard | ✅ | Alle interactieve elementen bereikbaar via Tab/Enter/Spatie |
| 2.4.3 Focus Order | ✅ | Logische tabvolgorde, skip-link aanwezig |
| 2.4.7 Focus Visible | ✅ | `:focus-visible` outline op alle elementen |
| 2.4.11 Focus Not Obscured | ✅ | `scroll-margin-top` compenseert sticky header |
| 2.5.3 Label in Name | ✅ | Zichtbare tekst in accessible name |
| 2.5.8 Target Size | ✅ | Alle knoppen `min-height: 2.75rem` (44px) |
| 3.1.1 Language of Page | ✅ | `lang="nl"` op alle pagina's |
| 3.2.3 Consistent Navigation | ✅ | Identieke navigatievolgorde op alle pagina's |
| 4.1.2 Name, Role, Value | ✅ | `aria-pressed`, `aria-current`, `aria-label`, `aria-live` |
| Reduced Motion | ✅ | `prefers-reduced-motion` ondersteund |
| Dark Mode | ✅ | `prefers-color-scheme` + handmatige schakelaar |

---

## Kosten

| Component | Kosten |
|---|---|
| GitHub Pages | €0 (gratis voor publieke repos) |
| GitHub Actions | €0 (gratis tier, ~5 min/week) |
| Microsoft CSV API | €0 (publiek, geen auth) |
| Google Translate | €0 (deep_translator gratis tier) |
| **Totaal** | **€0/maand** |

---

## Licentie

MIT — vrij te gebruiken, aan te passen en te distribueren.
