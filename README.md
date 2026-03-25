# Microsoft 365 Roadmap Dashboard

Automatisch bijgewerkt dashboard dat Microsoft 365 roadmap-updates vertaalt naar begrijpelijk Nederlands. Gebouwd voor medewerkers en IT-beheerders die zonder technische kennis willen weten wat er aankomt en of er actie nodig is.

**Volledig gratis** — GitHub Pages · GitHub Actions · Microsoft publieke CSV API · Google Translate via `deep_translator`

---

## Bestanden

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap met filters |
| `archief.html` | Weekoverzichten tot 3 maanden terug |
| `kalender.html` | Releasekalender per maand of kwartaal |
| `architectuur.html` | Interactieve C4-architectuurkaart |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `fetch_roadmap.py` | Python-pipeline: ophalen, vertalen, opslaan |
| `data.json` | Gegenereerde roadmapdata (niet handmatig bewerken) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Weekarchief (automatisch, max 3 maanden) |

---

## Installatie

### 1. Repository aanmaken
Maak een nieuwe **publieke** GitHub-repository aan.

### 2. Bestanden uploaden
```
index.html
archief.html
kalender.html
architectuur.html
shared.css
fetch_roadmap.py
.github/workflows/update-roadmap.yml
```

### 3. GitHub Pages inschakelen
**Settings → Pages → Source:** Deploy from a branch → `main` / `(root)`

URL: `https://<gebruikersnaam>.github.io/<repository-naam>/`

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
  GitHub Actions (maandag 06:00 UTC)
         │
         └─ fetch_roadmap.py
              ├── CSV ophalen (curl + browser-headers)
              ├── Vertaalcache laden (hash-vergelijking)
              ├── Alleen nieuw/gewijzigd vertalen
              ├── Producten detecteren (DETECT_PATTERNS)
              ├── data.json schrijven
              └── archive/YYYY-MM-DD.json opslaan
                       │
                       └─ git push → GitHub Pages
```

Zie `architectuur.html` voor de interactieve C4-kaart (C1 t/m C4).

---

## Pagina's

### Hoofdpagina — `index.html`

| Filter | Standaard | Toelichting |
|---|---|---|
| Product | Alle producten | Icoon + naam + live-telling. Toont alleen producten mét items. |
| Actie nodig? | Alles | Automatisch · IT-beheerder · Medewerker |
| Sorteren | Toegevoegd: nieuwste eerst | 5 opties |
| Periode | Vorige week | Items toegevoegd/gewijzigd in de vorige kalenderweek. Consistent met de maandag-workflow. |
| Status | Alles | Uitgerold · In ontwikkeling |

**URL-parameters:**
- `?id=123456` — opent item direct; alle datumfilters worden gereset
- `?zoek=Teams` — vult zoekbalk voor

---

### Releasekalender — `kalender.html`

Korte termijn: per maand, komende 6 maanden, exacte datums.
Lange termijn: per kwartaal vanaf huidig kwartaal. Periodfilter: huidig+toekomst / jaar / alles.
Details-knop stuurt via `?id=` naar de hoofdpagina.

---

### Archiefpagina — `archief.html`

Weekoverzichten tot 3 maanden terug. Meest recente week automatisch geladen.
Productfilter per week met icoon. Statistiekenbalk en gewijzigde items per week.

---

### Architectuurkaart — `architectuur.html`

Interactieve C4-kaart: klik elk component voor details over functie, logica en implementatie.
- C1 Context — systeem en externe afhankelijkheden
- C2 Container — deploybare onderdelen en datastromen
- C3 Component — interne bouwblokken
- C4 Code — functies, schema's en datastructuren

---

## Technische details

### Thema (licht/donker)
Elke pagina heeft een thema-knop (☀/🌙) in de header. Keuze wordt opgeslagen in `localStorage`. Zonder expliciete keuze volgt het systeem de OS-voorkeur (`prefers-color-scheme`).

### Product-iconen
16 officiële iconen inline als base64 PNG (64×64 px, ~80 KB totaal). Geen externe HTTP-requests. Werkt offline en in sandboxed Teams-tabs. Gebruik `appIconHTML(key)` om een `<img>` te genereren.

### data.json-schema
```json
{
  "generated": "ISO-timestamp",
  "count": 819,
  "items": [{
    "id": "string",
    "title_nl": "Vertaalde titel",
    "benefit_nl": "Vertaald voordeel",
    "title_en": "Original title",
    "product": "teams",
    "status": "rolling | dev",
    "action": "none | admin | user",
    "release": "April CY2026",
    "added": "2026-03-17",
    "modified": "2026-03-17",
    "moreInfoLink": "https://..."
  }],
  "removed": [{ "...": "Launched/Cancelled items t.o.v. vorige run" }],
  "translation_cache": {
    "<id>": { "title_nl": "...", "benefit_nl": "...", "hash": "..." }
  }
}
```

### Periodefilter — weekberekening
ISO-kalenderweken (ma–zo). Standaard "Vorige week" is consistent met de maandagse workflow-run.

| Functie | Werking |
|---|---|
| `isoWeek(date)` | Weeknummer 1–53 |
| `weekStart(date)` | Maandag 00:00 van die week |
| `weekEnd(date)` | Zondag 23:59:59 van die week |
| `inPrevWeek(d)` | Valt datum in de vorige kalenderweek? |

---

## Performance

| Maatregel | Details |
|---|---|
| SessionStorage-cache | `data.json` 30 min gecached (key: `m365_data_v1`) |
| Cache-buster | `?v=Date.now()` omzeilt CDN-cache |
| Fetch-timeout | AbortController na 12 seconden |
| Debounce | Zoekbalk 200ms |
| Event delegation | Één listener per filtergroep |
| innerHTML-batch | Één DOM-write per render |

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.1.1 Afbeeldingen | Alle iconen `aria-hidden="true"` + leeg `alt=""` |
| 1.3.1 Koppen | h1 → h2 → h3, geen gaten |
| 1.4.3 Contrast ≥4.5:1 | Getest voor licht én donker thema |
| 1.4.4 Schaalbaar | Alle `font-size` in `rem` |
| 2.4.1 Skip-link | Op alle pagina's |
| 2.4.7 Focus | `:focus-visible` overal |
| 2.4.11 Focus zichtbaar | `scroll-margin-top` via shared.css |
| 2.5.8 Raakdoel | Min. 44px knoppen |
| 3.1.1 Taal | `lang="nl"` op elk document |
| 4.1.2 Naam/rol | `aria-pressed`, `aria-expanded`, `aria-live`, `aria-label` |

Aanvullend: dark mode · `prefers-reduced-motion` · `noscript`-fallback.

---

## Kosten

**€0 per maand** — GitHub Pages + Actions (gratis tier) + Microsoft CSV + Google Translate.

---

## Onderhoud

**Workflow mislukt?** Actions → mislukte run → Re-run.

**Vertaling corrigeren?** Pas `title_nl` of `benefit_nl` aan in `data.json`. De hash-cache bewaart uw correctie zolang Microsoft het item niet wijzigt.

**Nieuw product toevoegen:**
1. `DETECT_PATTERNS` in `fetch_roadmap.py`
2. `APP_META`, `APP_ORDER`, `APP_ICONS` in alle HTML-pagina's
3. Pill-klasse in `shared.css`

---

## Privacy en beveiliging

- Geen cookies, geen tracking, geen analytics
- Geen login vereist
- Alle data is publiek beschikbaar via Microsoft
- Werkt in sandboxed Teams-tabs
