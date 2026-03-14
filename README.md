# Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt dashboard dat Microsoft 365-updates begrijpelijk presenteert voor niet-technische medewerkers. De pagina toont items met status **"In ontwikkeling"** en **"Wordt uitgerold"**, rechtstreeks opgehaald van de officiële Microsoft-roadmap en vertaald naar het Nederlands.

🔗 **Live pagina:** `https://[jouw-gebruikersnaam].github.io/M365-Roadmap`

---

## Hoe het werkt

```
Microsoft (officiële roadmap CSV — gratis, publiek)
        ↓  elke maandag automatisch via GitHub Actions
fetch_roadmap.py
  → filtert op Worldwide + In Development / Rolling Out
  → vertaalt titels en beschrijvingen naar Nederlands (Google Translate, gratis)
  → classificeert wie actie moet ondernemen (IT-beheerder / gebruiker / niemand)
  → genereert een voordeel-omschrijving per item op basis van trefwoorden
        ↓  slaat op als
data.json  (in deze repository, elke maandag overschreven)
        ↓  wordt gelezen door
index.html → de pagina die collega's zien via GitHub Pages
```

**Elke maandag om 07:00 NL-tijd** (06:00 UTC) draait GitHub Actions automatisch. Daarna is de pagina bijgewerkt zonder dat iemand iets hoeft te doen.

---

## Bestanden

| Bestand | Omschrijving |
|---|---|
| `index.html` | De dashboard-pagina. Leest `data.json` en toont de kaarten met filters. |
| `data.json` | Automatisch gegenereerd door de workflow. Bevat alle vertaalde roadmap-items. Handmatige aanpassingen worden elke maandag overschreven. |
| `fetch_roadmap.py` | Python-script dat de Microsoft CSV verwerkt: filteren, vertalen, classificeren en opslaan als `data.json`. |
| `.github/workflows/update-roadmap.yml` | GitHub Actions workflow: haalt wekelijks de CSV op en voert `fetch_roadmap.py` uit. |

---

## Wat de pagina toont per item

- **Titel** — vertaald naar Nederlands
- **Voordeel voor de organisatie** — automatisch gegenereerd op basis van trefwoorden (app + onderwerp)
- **Technische details** — ingeklapt, voor wie dat wil lezen; vertaald naar Nederlands
- **Status** — Wordt uitgerold / In ontwikkeling
- **Verwachte releasedatum** — in het Nederlands
- **Actie-indicator** — groen (geen actie), geel (IT-beheerder), blauw (gebruiker)
- **⭐ Nieuw** — items die er vorige week nog niet in stonden, bijgehouden via de browser
- **Link naar Microsoft Roadmap** — rechtstreeks naar het officiële item via het roadmap-ID

### Beschikbare filters
- Status (wordt uitgerold / in ontwikkeling)
- Nieuw / al bekend
- Toegevoegd aan roadmap (deze week / deze maand / alle)
- Gewijzigd (deze week / deze maand / alle)
- Applicatie (Copilot, Teams, Outlook, SharePoint, Purview, Word, Overig)
- Sortering (verwachte release, laatst gewijzigd, status)

---

## Onderhoud

### De workflow handmatig starten

1. Ga naar **Actions** in deze repository
2. Klik op **"Ververs Microsoft 365 Roadmap"**
3. Klik op **"Run workflow"** → **"Run workflow"**
4. Wacht ~3–5 minuten (inclusief vertaling van alle items)

### Veelvoorkomende fouten

| Fout in de logs | Oorzaak | Oplossing |
|---|---|---|
| `403 Forbidden` bij curl | Microsoft blokkeert tijdelijk het IP van GitHub | Probeer het een dag later opnieuw |
| `Permission denied` bij git push | Workflow heeft geen schrijfrechten | Ga naar **Settings → Actions → General → Workflow permissions** → zet op "Read and write" |
| `data.json not found` op de pagina | Workflow heeft nog nooit gedraaid | Start de workflow handmatig via Actions |
| Vertaling mislukt voor een item | Google Translate tijdelijk onbereikbaar | Het script behoudt automatisch de Engelse tekst en probeert het de volgende keer opnieuw |

### Actie-classificatie aanpassen

De actie-badges (IT-beheerder / gebruiker / geen actie) worden automatisch bepaald op basis van trefwoorden in de Engelse originele tekst. Dit werkt goed voor de meeste items maar is niet altijd perfect. De trefwoorden staan bovenaan in `fetch_roadmap.py` in de lijsten `ADMIN_PATTERNS` en `USER_PATTERNS`. Die kun je uitbreiden als classificatie structureel onjuist is voor bepaalde typen items.

### Voordeel-omschrijvingen aanpassen

Voordeel-omschrijvingen staan in de `BENEFIT_TEMPLATES`-woordenboek in `fetch_roadmap.py`. Per combinatie van applicatie en trefwoord is er een vaste Nederlandse zin. Ontbreekt er een combinatie, dan valt het script terug op een generieke zin per app uit `GENERIC_BENEFIT`. Beide woordenboeken zijn eenvoudig uit te breiden.

### Pagina-opmaak aanpassen

Bewerk `index.html` direct in GitHub (potlood-icoon) en commit de wijziging. GitHub Pages toont de nieuwe versie binnen 1–2 minuten. De data komt altijd uit `data.json` — de opmaak en de data staan volledig los van elkaar.

---

## Teams-tabblad instellen

1. Ga naar het gewenste Teams-kanaal
2. Klik op **+** → **Website**
3. Vul in: `https://[jouw-gebruikersnaam].github.io/M365-Roadmap`
4. Naam: *M365 Roadmap* → **Opslaan**

Het tabblad toont altijd de meest recente versie. Je hoeft het nooit opnieuw in te stellen.

---

## Kosten

Alles is gratis:

| Onderdeel | Kosten |
|---|---|
| GitHub Pages | Gratis voor publieke repositories |
| GitHub Actions | Gratis (2.000 minuten/maand — de workflow gebruikt ~3–5 minuten per week) |
| Microsoft Roadmap CSV | Gratis, publiek toegankelijk via `microsoft.com/releasecommunications/api/v2/m365` |
| Vertaling via Google Translate | Gratis via de `deep_translator` Python-bibliotheek (geen API-sleutel vereist) |

Er zijn geen abonnementen, API-sleutels of betaalaccounts nodig.
