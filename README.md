# Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt dashboard dat Microsoft 365-roadmap updates toont in begrijpelijk Nederlands. Bedoeld voor niet-technische medewerkers en organisaties die willen weten wat er aan te komen is en wat dat voor hen betekent.

**Volledig gratis** — GitHub Pages + GitHub Actions (gratis tier) + Microsoft publieke CSV API + Google Translate via `deep_translator`.

---

## Wat doet het?

- Haalt elke **maandag en woensdag** automatisch de actuele Microsoft 365 roadmap op
- **Vertaalt** alle items naar Nederlands (alleen nieuwe of gewijzigde items worden vertaald)
- **Categoriseert** items per product met officiële Microsoft-iconen
- Geeft voor elk item aan **wat het betekent voor de organisatie** en **of er actie nodig is**
- Toont welke items deze week **beschikbaar zijn gekomen of geannuleerd** zijn
- Bewaart een **archief** van de laatste 3 maanden
- **Releasekalender** met maand- en kwartaalweergave voor planning

---

## Bestanden

| Bestand | Omschrijving |
|---|---|
| `index.html` | Hoofdpagina — actuele roadmap met vereenvoudigd filterblok en product-iconen |
| `archief.html` | Archiefpagina — momentopnamen van vorige weken (max 3 maanden) |
| `kalender.html` | Releasekalender — per maand (kort) of per kwartaal (lang) |
| `shared.css` | Gedeelde stijlen voor alle pagina's (WCAG 2.2 AA) |
| `fetch_roadmap.py` | Python-script dat de CSV ophaalt, vertaalt en `data.json` aanmaakt |
| `data.json` | Gegenereerde data (automatisch bijgewerkt, niet handmatig bewerken) |
| `icons/*.png` | Officiële Microsoft product-iconen (16 stuks) |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow |
| `archive/index.json` | Index van beschikbare archiefdatums |
| `archive/YYYY-MM-DD.json` | Archief per week (automatisch aangemaakt, max 3 maanden) |

### Iconen (`icons/`)

| Bestandsnaam | Product |
|---|---|
| `copilot.png` | Microsoft 365 Copilot |
| `teams.png` | Microsoft Teams |
| `outlook.png` | Microsoft Outlook |
| `excel.png` | Microsoft Excel |
| `word.png` | Microsoft Word |
| `powerpoint.png` | Microsoft PowerPoint |
| `sharepoint.png` | Microsoft SharePoint |
| `purview.png` | Microsoft Purview |
| `viva.png` | Microsoft Viva |
| `edge.png` | Microsoft Edge |
| `onedrive.png` | Microsoft OneDrive |
| `exchange.png` | Microsoft Exchange |
| `forms.png` | Microsoft Forms |
| `intune.png` | Microsoft Intune |
| `entra.png` | Microsoft Entra |
| `planner.png` | Microsoft Planner |

---

## Installatie

### 1. Repository aanmaken

Maak een nieuwe **publieke** GitHub-repository aan (bijv. `M365-Roadmap`).

### 2. Bestanden uploaden

Upload de volgende bestanden en mappen naar de repository:

```
index.html
archief.html
kalender.html
shared.css
fetch_roadmap.py
icons/           ← map met alle 16 PNG-iconen
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

Ga naar **Actions → Ververs Microsoft 365 Roadmap → Run workflow**.

### 5. Teams-tabblad instellen (optioneel)

1. Open het gewenste Teams-kanaal → **+** → **Website**
2. Vul de GitHub Pages URL in en klik op **Opslaan**

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

---

## Filterblok hoofdpagina (`index.html`)

Het filterblok is vereenvoudigd ten opzichte van eerdere versies:

| Filter | Omschrijving |
|---|---|
| **Product** | Filter op applicatie — officieel icoon + naam + live aantal. Standaard: alle producten. |
| **Actie nodig?** | Automatisch / IT-beheerder / Medewerker. Korte labels. |
| **Sorteren** | Toegevoegd (standaard), releasedatum, gewijzigd, status. |
| **Periode** | Filtert op items _toegevoegd of gewijzigd_ in de geselecteerde periode. Standaard: huidige kalenderweek. |
| **Status** | Alles / Uitgerold / In ontwikkeling. |

**Verwijderd t.o.v. vorige versie:**
- Aparte "Toegevoegd aan roadmap" en "Gewijzigd op roadmap" filters — samengevoegd tot één "Periode"-filter
- "Bekendheid" (nieuw/al bekend) filter — overlapt met de periodefilter; de ⭐-badge op kaarten blijft

**Standaard:** periode = huidige ISO-kalenderweek. Op maandag reset het filter automatisch naar de nieuwe week.

**"Nieuw"-badge:** een item is nieuw als het in de huidige kalenderweek is toegevoegd of gewijzigd op de roadmap.

**URL-parameters:**
- `?id=123456` — opent met dat MS-ID direct gefilterd (alle datumfilters gereset); vanuit kalender
- `?zoek=Teams` — opent met die zoekterm vooringevuld

---

## Releasekalender (`kalender.html`)

| Onderdeel | Omschrijving |
|---|---|
| **Korte termijn** | Per maand, komende 6 maanden, exacte maanddatums |
| **Lange termijn** | Per kwartaal, huidig kwartaal t/m toekomst |
| **Periodfilter** | Huidig + toekomst (standaard), specifiek jaar, of alles |
| **Details-knop** | Stuurt via `?id=` door naar de hoofdpagina |

---

## Toegankelijkheid (WCAG 2.2 AA)

| Criterium | Oplossing |
|---|---|
| 1.3.1 Koppen-hiërarchie | h1 header → h2 secties → h3 kaarttitels |
| 1.4.3 Kleurcontrast ≥4.5:1 | Alle kleuren getest, ook in dark mode |
| 1.4.4 Tekst schaalbaar | Alle font-sizes in `rem` |
| 2.4.1 Skip-link | Aanwezig op alle pagina's |
| 2.4.7 Focusindicator | Zichtbare focus-ring op alle interactieve elementen |
| 2.4.11 Focus niet verborgen | `scroll-margin-top` voorkomt dat sticky header focus bedekt |
| 2.5.8 Raakdoelgrootte ≥24px | Alle knoppen minimaal 44px hoog |
| 3.1.1 Taal | `lang="nl"` op elk document |
| 4.1.2 Naam/rol/waarde | `aria-pressed`, `aria-expanded`, `aria-live`, `aria-label` |
| 4.1.3 Statusberichten | `aria-live` op resultatenbalken en weekbadge |

**Product-iconen:** alle iconen zijn `aria-hidden="true"` — de tekst van de knop is de toegankelijke naam.

---

## Technische details

### Performance

- **SessionStorage-cache**: `data.json` 30 minuten gecached
- **Cache-buster**: `?v=timestamp` om GitHub Pages CDN-cache te omzeilen
- **Fetch-timeout**: 12 seconden
- **Debounce**: zoekbalk 200ms
- **Event delegation**: één listener per filtergroep

### Weekberekening

- `isoWeek(date)` — ISO-weeknummer (1–53)
- `weekStart(date)` — maandag 00:00 van die week
- `weekEnd(date)` — zondag 23:59:59 van die week
- `inSameWeek(d, ref)` — controleert of datum in dezelfde week valt

---

## Kosten

| Onderdeel | Kosten |
|---|---|
| GitHub Pages | Gratis |
| GitHub Actions | Gratis (2.000 min/maand, ≈3-5 min/week) |
| Microsoft 365 Roadmap CSV API | Gratis (publiek) |
| Google Translate via `deep_translator` | Gratis |
| **Totaal** | **€0 per maand** |

---

## Onderhoud

**Workflow mislukt?** Ga naar Actions → bekijk de mislukte run → Re-run jobs. De woensdag-run pikt maandagfouten automatisch op.

**Vertalingen corrigeren?** Pas `title` of `benefit` aan in `data.json`. De cache herkent het item op `(id, modified)` — uw correctie blijft behouden zolang Microsoft het item niet wijzigt.

**Icoon vervangen?** Vervang het PNG-bestand in de `icons/`-map met dezelfde bestandsnaam. De pagina laadt het icoon automatisch.
