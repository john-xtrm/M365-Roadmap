# 📋 Microsoft 365 Roadmap Dashboard

Een automatisch bijgewerkt overzicht van Microsoft 365-updates voor niet-technische medewerkers. De pagina toont alle items met status **"In ontwikkeling"** en **"Wordt uitgerold"**, rechtstreeks opgehaald van de officiële Microsoft-roadmap.

🔗 **Live pagina:** `https://[jouw-gebruikersnaam].github.io/M365-Roadmap`

---

## Hoe het werkt

```
Microsoft (officiele roadmap CSV)
        ↓  elke maandag automatisch
GitHub Actions (fetch_roadmap.py)
        ↓  schrijft naar
data.json  (in deze repository)
        ↓  leest bij elk bezoek
index.html (de pagina die collega's zien)
```

**Elke maandag om 07:00 NL-tijd** draait GitHub automatisch een script dat:
1. De officiële Microsoft roadmap ophaalt via de publieke Microsoft API
2. Filtert op Worldwide-items met status "In development" of "Rolling out"
3. Het resultaat opslaat als `data.json` in deze repository
4. De pagina toont bij het volgende bezoek automatisch de nieuwe data

Niemand hoeft hier iets voor te doen — het werkt volledig automatisch.

---

## Bestanden in deze repository

| Bestand | Waarvoor |
|---|---|
| `index.html` | De pagina die collega's zien (via GitHub Pages) |
| `data.json` | Automatisch gegenereerd — bevat de actuele roadmap-items |
| `fetch_roadmap.py` | Het Python-script dat de Microsoft API uitleest en `data.json` aanmaakt |
| `.github/workflows/update-roadmap.yml` | De automatische planning (elke maandag) |

---

## Onderhoud

### De pagina werkt niet meer / data is verouderd

1. Ga naar het tabblad **Actions** in deze repository
2. Klik op **"Ververs Microsoft 365 Roadmap"**
3. Klik op **"Run workflow"** → **"Run workflow"**
4. Wacht 30 seconden — bij groen vinkje is `data.json` bijgewerkt

### De workflow geeft een fout

Klik op de rode workflow-run en open de logs. Veelvoorkomende oorzaken:

| Fout | Oplossing |
|---|---|
| `403 Forbidden` bij ophalen CSV | Microsoft blokkeert tijdelijk — probeer het een dag later opnieuw |
| `Permission denied` bij git push | Ga naar **Settings → Actions → General** en zet "Workflow permissions" op "Read and write" |
| `data.json not found` op de pagina | Workflow is nog nooit gedraaid — start hem handmatig via Actions |

### Handmatig items toevoegen of aanpassen

Items in `data.json` worden elke maandag overschreven door de workflow — handmatige aanpassingen daarin gaan verloren. Als je een item wil aanpassen (bijv. een betere Nederlandse beschrijving of actielabel), doe dit dan in `index.html` via de `OVERRIDES`-tabel bovenaan het script. *(Nog niet aanwezig — vraag de beheerder dit toe te voegen als dat nodig is.)*

### De pagina aanpassen (opmaak, filters, tekst)

Bewerk `index.html` en commit de wijziging. GitHub Pages toont de nieuwe versie binnen 1–2 minuten.

### Iemand anders toegang geven

Ga naar **Settings → Collaborators** en voeg de persoon toe. Zij kunnen dan ook de workflow handmatig starten of bestanden bewerken.

---

## Teams-tabblad instellen of vervangen

1. Ga naar het gewenste Teams-kanaal
2. Klik op **+** naast de tabbladen → **Website**
3. Vul de GitHub Pages-URL in: `https://[jouw-gebruikersnaam].github.io/M365-Roadmap`
4. Geef het tabblad een naam, bijv. *M365 Roadmap*
5. Klik op **Opslaan**

Het tabblad laadt altijd de meest recente versie — je hoeft het nooit opnieuw in te stellen.

---

## Kosten

Niets. GitHub Pages en GitHub Actions zijn gratis voor publieke repositories. Microsoft's roadmap-API is gratis en publiek toegankelijk. Er zijn geen abonnementen of API-sleutels nodig.

---

## Vragen of problemen?

Maak een **Issue** aan in deze repository of neem contact op met de IT-afdeling.
