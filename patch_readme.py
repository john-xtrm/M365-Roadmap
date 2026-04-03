#!/usr/bin/env python3
"""patch_readme.py — Run vanuit root van GitHub checkout"""
import os

# Build README patch script
import os

README_NEW_SECTION = '''
### Presentatiepagina — `presentatie.html`

Genereert een branded `.pptx`-presentatie in de browser, klaar om te downloaden en te tonen aan klanten.

| Instelling | Opties | Toelichting |
|---|---|---|
| Weekkeuze | Week 1–4 terug | Selecteer de ISO-kalenderweek waarover gerapporteerd wordt |
| Producten | Per product | Selecteer welke M365-producten opgenomen worden |
| Klantgegevens | Vrij tekstveld | Klantnaam en eventuele notities voor de titelpagina |

**Slides die worden gegenereerd:**
1. Titelpagina met klantbranding (XTRM-logo, achtergrond)
2. Overzichtsslide met statistieken van de geselecteerde week
3–9. Productslides (één per geselecteerd product, automatisch gepagineerd bij >4 items)
10. Afsluiting met contactgegevens

**Technische details:**
- PptxGenJS 4.0.1 via CDN (volledig browser-side, geen server nodig)
- SessionStorage-cache (30 min + maandag-invalidatie) — zelfde mechanisme als index.html
- Embedded base64 assets (XTRM-logo wit/zwart, Utrecht-achtergrond)
- Barlow / Barlow Condensed / Barlow SemiCondensed fonts
- Sprekernotities automatisch gegenereerd per slide
- Werkt alleen via de GitHub Pages URL (niet als lokaal bestand)

**Functies:**
- `waitForPptx()` — wacht op PptxGenJS CDN-load (60 × 200 ms)
- `loadData()` — haalt roadmap-data op (met cache)
- `buildWeekRanges()` — berekent 4 vorige ISO-kalenderweken
- `buildProductGrid()` — bouwt productfilter met live-telling
- `generatePptx()` — construeert alle slides via PptxGenJS API
'''

# In README.md, the "Architectuurkaart" section is the last page section.
# We insert the Presentatie section before the "Technische details" section.
# Target: insert between "### Architectuurkaart" section and "## Technische details"

ANCHOR = "---\n\n## Technische details"
INSERT = README_NEW_SECTION + "\n---\n\n## Technische details"

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

if ANCHOR in readme:
    readme = readme.replace(ANCHOR, INSERT, 1)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("README.md bijgewerkt ✓")
else:
    # Fallback: append before "## Technische details" if the exact anchor differs
    # Try alternative anchor
    alt = "## Technische details"
    idx = readme.find(alt)
    if idx > 0:
        readme = readme[:idx] + README_NEW_SECTION.lstrip('\n') + '\n---\n\n' + readme[idx:]
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme)
        print("README.md bijgewerkt via fallback ✓")
    else:
        # Just append at end
        readme += README_NEW_SECTION
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme)
        print("README.md: sectie toegevoegd aan einde")
