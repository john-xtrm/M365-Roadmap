# Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt dashboard dat Microsoft 365-roadmap updates toont in begrijpelijk Nederlands. Bedoeld voor niet-technische medewerkers en organisaties die willen weten wat er aan te komen is en wat dat voor hen betekent.

**Volledig gratis** — GitHub Pages + GitHub Actions (gratis tier) + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Wat doet het?

- Haalt elke **maandag en woensdag** automatisch de actuele Microsoft 365 roadmap op
- **Vertaalt** alle items naar Nederlands (alleen nieuwe of gewijzigde items worden vertaald)
- **Categoriseert** items per product (Teams, Outlook, SharePoint, Copilot, etc.)
- Geeft voor elk item aan **wat het betekent voor de organisatie** en **of er actie nodig is**
- Toont welke items deze week **beschikbaar zijn gekomen of geannuleerd** zijn
- Bewaart een **archief** van de laatste 3 maanden
- **Releasekalender** met maand- en kwartaalweergave voor planning

---

## Bestanden

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap met filters, zoekbalk en weekbadge |
| `archief.html` | Archiefpagina — momentopnamen van vorige weken (max 3 maanden) |
| `kalender.html` | Releasekalender — per maand (kort) of per kwartaal (lang) |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `fetch_roadmap.py` | Python-script dat de CSV ophaalt, vertaalt en `data.json` aanmaakt |
| `data.json` | Gegenereerde data (automatisch bijgewerkt, niet handmatig bewerken) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Archief per week (automatisch aangemaakt, max 3 maanden) |

---

## Installatie

### 1. Repository aanmaken

Maak een nieuwe **publieke** GitHub-repository aan (bijv. `M365-Roadmap`).

### 2. Bestanden uploaden

Upload de volgende bestanden naar de root van de repository:

```
index.html
archief.html
kalender.html
shared.css
fetch_roadmap.py
```

Maak ook de mapstructuur aan voor de workflow:

```
.github/
  workflows/
    update-roadmap.yml
```

### 3. GitHub Pages inschakelen

Ga naar **Settings → Pages** en stel in:
- **Source**: Deploy from a branch
- **Branch**: `main` / `(root)`

Na een minuut is de pagina bereikbaar op:
```
https://<gebruikersnaam>.github.io/<repository-naam>/
```

### 4. Eerste run starten

Ga naar **Actions → Ververs Microsoft 365 Roadmap → Run workflow** om de eerste keer handmatig te starten. Dit genereert `data.json` en de eerste archiefbestanden.

### 5. Teams-tabblad instellen (optioneel)

1. Open het gewenste Teams-kanaal
2. Klik op **+** bovenaan het kanaal
3. Kies **Website**
4. Vul de GitHub Pages URL in en klik op **Opslaan**

---

## Hoe werkt de workflow?

```
Microsoft CSV API (publiek, gratis)
         │
         ▼
  GitHub Actions
  (maandag + woensdag 06:00 UTC)
         │
         ├─ fetch_roadmap.py
         │    ├── Haalt roadmap.csv op via curl
         │    ├── Laadt vertalingen uit cache (data.json)
         │    ├── Vertaalt alleen nieuwe/gewijzigde items
         │    ├── Detecteert Launched/Cancelled items
         │    ├── Slaat op als data.json
         │    └── Slaat archief op als archive/YYYY-MM-DD.json
         │
         └─ git push → GitHub Pages
                  │
                  ├── index.html     (actuele lijst)
                  ├── kalender.html  (releasekalender)
                  └── archief.html   (weekoverzichten)
```

### Automatische schedule

| Dag | Tijd | Doel |
|---|---|---|
| Maandag | 06:00 UTC | Primaire wekelijkse update |
| Woensdag | 06:00 UTC | Fallback bij mislukte maandagrun |

Handmatig starten kan altijd via **Actions → Run workflow**.

---

## Pagina's en functies

### Hoofdpagina (`index.html`)

| Onderdeel | Omschrijving |
|---|---|
| **Weekbadge in header** | Toont actief weeknummer en datumrange, bijv. "Week 12 · 16 mrt – 22 mrt" |
| **Info-banner** | Uitleg van kleurcodering en filters — inklapbaar |
| **Kies een product** | Filter op applicatie — toont live aantallen |
| **Is er actie nodig?** | Automatisch / IT-beheerder / Medewerker zelf |
| **Status** | Alles / Wordt uitgerold / In ontwikkeling |
| **Sorteren op** | Toegevoegd (standaard), releasedatum, gewijzigd, status |
| **Meer filteropties** | Datum toegevoegd (standaard: deze week), datum gewijzigd, nieuw/al bekend |
| **Zoekbalk** | Vrij zoeken in titel en voordeel (200ms debounce) |
| **Wijzigingen** | Inklapbaar blok met Launched/Cancelled items van deze week |
| **Kalender-knop** | Header-link naar `kalender.html` |
| **Archief-knop** | Header-link naar `archief.html` |

**Standaard filterinstelling:** alleen items die in de huidige ISO-kalenderweek aan de Microsoft roadmap zijn toegevoegd (`Toegevoegd: Week XX`). Op maandag reset het filter automatisch naar de nieuwe week.

**Weekdefinitie:** de pagina gebruikt ISO-kalenderweken (maandag t/m zondag). De actieve week staat altijd zichtbaar als badge in de header én op de filterknoppen, zodat direct duidelijk is welke periode getoond wordt.

**"Nieuw"-badge:** een item krijgt de ⭐-badge als het in de huidige kalenderweek aan de roadmap is toegevoegd. Dit is consistent met het weekfilter en geldt voor alle gebruikers gelijk.

**URL-parameters:**
- `?id=123456` — opent de pagina met dat MS-ID direct gefilterd (alle andere filters worden gereset); gebruikt vanuit de releasekalender
- `?zoek=Teams` — opent de pagina met die zoekterm vooringevuld

### Releasekalender (`kalender.html`)

| Onderdeel | Omschrijving |
|---|---|
| **Info-banner** | Uitleg van de twee weergaves |
| **Korte termijn** | Per maand, komende 6 maanden, alleen exacte maanddatums |
| **Lange termijn** | Per kwartaal, huidig kwartaal t/m toekomst (of alle jaren) |
| **Periodfilter** | Huidig + toekomst (standaard), specifiek jaar, of alles — alleen bij lange termijn |
| **Productfilter** | Per product filteren |
| **Actiefilter** | Automatisch / IT-beheerder / Medewerker |
| **Mini-uitsplitsing** | Periodeheader toont #IT, #medewerker, #auto per maand/kwartaal |
| **Details-knop** | Stuurt via `?id=` door naar de hoofdpagina voor het volledige item |
| **Ook in maandweergave** | Badge op items met exacte datum die ook in korte termijn verschijnen |

**Lange termijn begint altijd bij het huidige kwartaal** — verleden kwartalen zijn verborgen tenzij u "Alles" selecteert in de periodfilter.

### Archiefpagina (`archief.html`)

- Info-banner met uitleg over het archief
- Weekknoppen voor alle beschikbare weken (laatste 3 maanden)
- De meest recente week wordt automatisch geladen
- Productfilter per week
- Statistieken en gewijzigde items per week

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.3.1 Koppen-hiërarchie | h1 header → h2 secties → h3 kaarttitels |
| 1.4.3 Kleurcontrast ≥4.5:1 | Alle kleuren getest, ook in dark mode |
| 1.4.4 Tekst schaalbaar | Alle font-sizes in `rem`, schaalt met browservoorkeur |
| 2.4.1 Skip-link | "Ga naar hoofdinhoud" als eerste element op alle pagina's |
| 2.4.7 Focusindicator | Zichtbare focus-ring op alle interactieve elementen |
| 2.4.11 Focus niet verborgen | `scroll-margin-top` voorkomt dat sticky header focus bedekt |
| 2.5.8 Raakdoelgrootte ≥24px | Alle knoppen minimaal 44px hoog |
| 3.1.1 Taal | `lang="nl"` op elk HTML-document |
| 3.3.2 Formulierlabels | Alle invoervelden en filtergroepen gelabeld |
| 4.1.2 Naam/rol/waarde | `aria-pressed`, `aria-expanded`, `aria-live`, `aria-label` |
| 4.1.3 Statusberichten | `aria-live` op resultatenbalken, weekbadge en paginatellers |

Aanvullend:
- **Dark mode** via `@media (prefers-color-scheme: dark)` — alle kleuren herberekend voor ≥4.5:1
- **Verminderde beweging** via `@media (prefers-reduced-motion: reduce)`
- **Noscript-fallback** voor browsers zonder JavaScript

---

## Technische details

### `fetch_roadmap.py`

- Filtert op **Worldwide (Standard Multi-Tenant)** en status **In Development** of **Rolling Out**
- **Vertaalcache**: slaat vertalingen op per `(id, modified)` — vertaalt alleen bij wijziging
- **Taaldetectie**: controleert of gecachede items daadwerkelijk Nederlands zijn
- **Verwijderde items**: vergelijkt vorige `data.json` met nieuwe CSV, detecteert Launched/Cancelled
- **Archief**: slanke kopie als `archive/YYYY-MM-DD.json` (zonder volledige beschrijvingen)
- **Archiefindex**: schrijft `archive/index.json` bij met datums van de laatste 3 maanden

### `update-roadmap.yml`

- `permissions: contents: write` voor git push
- `curl` met browser-headers om 403-fout op Microsoft CDN te omzeilen
- `find archive/ -mtime +92 -delete` verwijdert bestanden ouder dan 3 maanden
- `git diff --cached --quiet` — commit alleen als er echte wijzigingen zijn

### Performance (browser)

- **SessionStorage-cache**: `data.json` 30 minuten gecached — herlaad is direct
- **Cache-buster**: `?v=timestamp` om GitHub Pages CDN-cache te omzeilen
- **Fetch-timeout**: verzoeken afgebroken na 12 seconden met foutmelding
- **Debounce**: zoekbalk wacht 200ms na laatste toetsaanslag
- **Event delegation**: één listener per filtergroep in plaats van per knop
- **shared.css**: gedeelde stijlen — browser cachet dit over alle pagina's

### Weekberekening (`index.html`)

De pagina gebruikt drie JavaScript-hulpfuncties voor weekberekening:

- `isoWeek(date)` — berekent het ISO-weeknummer (1–53)
- `weekStart(date)` — geeft de maandag 00:00 van de week van die datum
- `weekEnd(date)` — geeft de zondag 23:59:59 van dezelfde week
- `inSameWeek(d, refDate)` — controleert of datum `d` in dezelfde kalenderweek valt als `refDate`

Deze functies worden gebruikt voor zowel het weekfilter als de ⭐ Nieuw-badge.

---

## Bekende gedragingen

| Gedrag | Uitleg |
|---|---|
| Weekfilter reset op maandag | Op maandag valt de vorige week buiten het filter — nieuw toegevoegde items van die dag zijn direct zichtbaar |
| Sorteren op datum werkt niet bij lege releasedatums | Items zonder datum komen altijd achteraan (datum = jaar 9999) |
| Lange termijn start bij huidig kwartaal | Verleden kwartalen verborgen — gebruik "Alles" in periodfilter om ze te zien |
| Kalender toont enkel items met datum | Items zonder releasedatum staan in het inklapbare blok onderaan |
| `?id=` reset alle filters | Bij openen via kalender-link worden datumfilters gereset zodat het item altijd gevonden wordt |

---

## Kosten

| Onderdeel | Kosten |
|---|---|
| GitHub Pages (statische hosting) | Gratis |
| GitHub Actions (CI/CD) | Gratis (2.000 min/maand, workflow ≈ 3-5 min/week) |
| Microsoft 365 Roadmap CSV API | Gratis (publiek) |
| Google Translate via `deep_translator` | Gratis (geen API-sleutel vereist) |
| **Totaal** | **€0 per maand** |

---

## Onderhoud

### Vertalingen corrigeren

Zoek het roadmap-ID op in `data.json` en pas `title` of `benefit` handmatig aan. De cache herkent het item op `(id, modified)` — uw correctie blijft behouden zolang Microsoft het item niet wijzigt.

### Workflow mislukt?

1. Ga naar **Actions** en bekijk de mislukte run
2. Veelvoorkomende oorzaken: Microsoft CSV tijdelijk onbereikbaar (403), Google Translate rate limit
3. Klik op **Re-run jobs** om opnieuw te proberen
4. De woensdag-run pikt dit automatisch op als de maandag mislukt

### Archief leeg?

Het archief wordt aangemaakt na de eerste succesvolle workflow-run. Daarna verschijnt er automatisch een weekknop per run.
