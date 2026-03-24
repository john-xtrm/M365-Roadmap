# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard voor Microsoft 365-roadmap updates in begrijpelijk Nederlands. Geoptimaliseerd voor niet-technische medewerkers die willen weten wat er aankomt en of er actie nodig is.

**Volledig gratis** — GitHub Pages + GitHub Actions + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Bestanden

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

> Alle 16 product-iconen zijn als geoptimaliseerde base64 PNG (64×64 px) direct in elke HTML-pagina ingebouwd. Geen losse bestanden, geen externe afhankelijkheden, werkt ook in sandboxed Teams-tabs.

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
         │    ├── Vertalingen laden uit cache
         │    ├── Alleen nieuwe/gewijzigde items vertalen
         │    ├── Launched/Cancelled items detecteren
         │    ├── data.json wegschrijven
         │    └── archive/YYYY-MM-DD.json opslaan
         │
         └─ git push → GitHub Pages
```

---

## Hoofdpagina (`index.html`)

### Filters

| Filter | Standaard | Omschrijving |
|---|---|---|
| Product | Alle producten | Icoon + naam + live aantal. Verborgen als 0 items. |
| Actie nodig? | Alles | Automatisch / IT-beheerder / Medewerker |
| Sorteren | Toegevoegd: nieuwste eerst | 5 opties |
| Periode | Afgelopen week | Items toegevoegd én gewijzigd in de vorige kalenderweek. De workflow draait op maandag — nieuwe data gaat altijd over de afgelopen week. Opties: Alle · Afgelopen week · Deze maand. |
| Status | Alles | Uitgerold / In ontwikkeling |

**Weekbadge in header:** toont altijd de vorige kalenderweek, consistent met de workflow die op maandag de data van de afgelopen week ophaalt.

**"Nieuw" badge:** item is nieuw als het in de huidige kalenderweek is toegevoegd of gewijzigd.

**URL-parameters:**
- `?id=123456` — filtert direct op MS-ID; alle datumfilters worden gereset
- `?zoek=Teams` — vult de zoekbalk voor

### Statistiekenbalk
Toont: totaal items · wordt uitgerold · in ontwikkeling · nieuw deze week. Bij actieve zoekopdracht ook een zoekterm-pill.

---

## Releasekalender (`kalender.html`)

| Onderdeel | Omschrijving |
|---|---|
| Korte termijn | Per maand, komende 6 maanden, exacte maanddatums |
| Lange termijn | Per kwartaal, start bij huidig kwartaal |
| Periodfilter | Huidig + toekomst / specifiek jaar / alles — alleen bij lange termijn |
| Productfilter | Met officieel icoon per product |
| Actiefilter | Automatisch / IT-beheerder / Medewerker |
| Mini-uitsplitsing | Periodeheader toont #IT, #medewerker, #auto |
| Details-knop | Stuurt via `?id=` naar hoofdpagina |
| "Ook in maandweergave" | Badge op exacte maanddatums in lange-termijn weergave |

---

## Archiefpagina (`archief.html`)

- Laadt `archive/index.json` voor de lijst van beschikbare weken
- Meest recente week automatisch geladen
- Weekknoppen voor alle beschikbare weken (max 3 maanden terug)
- Productfilter per week met officieel icoon en icoon-tekst scheiding
- Statistiekenbalk per week (totaal, uitgerold, in ontwikkeling)
- Kaarten gegroepeerd per status (uitgerold / in ontwikkeling)

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.1.1 Afbeeldingen | Alle iconen `aria-hidden="true"` + leeg `alt=""` |
| 1.3.1 Koppen-hiërarchie | h1 → h2 → h3, geen gaten |
| 1.4.3 Kleurcontrast ≥4.5:1 | Getest incl. dark mode |
| 1.4.4 Tekst schaalbaar | Alle font-sizes in `rem` |
| 2.4.1 Skip-link | Op alle pagina's als eerste element |
| 2.4.7 Focusindicator | `:focus-visible` op alle interactieve elementen |
| 2.4.11 Focus niet verborgen | `scroll-margin-top` via shared.css |
| 2.5.8 Raakdoelgrootte ≥24px | Min. 44px hoogte op alle knoppen |
| 3.1.1 Taal | `lang="nl"` op elk document |
| 4.1.2 Naam/rol/waarde | `aria-pressed`, `aria-expanded`, `aria-live`, `aria-label` |
| 4.1.3 Statusberichten | `aria-live` op statistiekenbalk en weekbadge |

Aanvullend: dark mode, reduced-motion, noscript-fallback.

---

## Performance

- **Iconen inline:** geen externe HTTP-requests; browser cachet de HTML inclusief iconen
- **SessionStorage-cache:** `data.json` 30 min gecached — herlaad is direct
- **Cache-buster:** `?v=timestamp` omzeilt GitHub Pages CDN-cache
- **Fetch-timeout:** 12 seconden; daarna foutmelding
- **Debounce:** zoekbalk 200ms
- **Event delegation:** één listener per filtergroep
- **innerHTML batch:** alle renders bouwen eerst een volledige HTML-string, dan één DOM-write

---

## Kosten

**€0 per maand** — GitHub Pages + Actions (gratis tier, ~3-5 min/week) + Microsoft CSV + Google Translate.

---

## Onderhoud

**Workflow mislukt?** Actions → mislukte run → Re-run. Woensdag pikt maandagfouten op.

**Vertaling corrigeren?** Pas `title` of `benefit` aan in `data.json`. Blijft behouden zolang Microsoft het item niet wijzigt.

**Nieuw product toevoegen?** Voeg een entry toe aan `DETECT_PATTERNS` in `fetch_roadmap.py`, aan `APP_META`/`APP_ORDER`/`APP_ICONS` in elk van de drie HTML-pagina's, en voeg een pill-klasse toe in `shared.css`.
