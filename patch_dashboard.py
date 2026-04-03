#!/usr/bin/env python3
"""
patch_dashboard.py — M365 Roadmap Dashboard
Pas toe vanuit de root van de GitHub checkout:
  python3 patch_dashboard.py
"""
import re, sys

def patch(path, replacements):
    try:
        with open(path, encoding="utf-8") as f: h = f.read()
    except FileNotFoundError:
        print(f"  ⚠  {path} niet gevonden — sla over"); return
    ok = True
    for old, new in replacements:
        if old in h:
            h = h.replace(old, new, 1)
            print(f"  ✓  {path}: {old[:55]!r}")
        else:
            print(f"  ⚠  {path}: patroon niet gevonden — {old[:55]!r}")
            ok = False
    with open(path, "w", encoding="utf-8") as f: f.write(h)
    return ok

ARCH_NORMAL  = '<a href="architectuur.html" class="hdr-archive-link" aria-label="Bekijk de architectuurkaart"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="6" height="6" rx="1"/><rect x="16" y="3" width="6" height="6" rx="1"/><rect x="9" y="15" width="6" height="6" rx="1"/><line x1="5" y1="9" x2="5" y2="12"/><line x1="19" y1="9" x2="19" y2="12"/><line x1="5" y1="12" x2="19" y2="12"/><line x1="12" y1="12" x2="12" y2="15"/></svg> Architectuur</a>'
ARCH_CURRENT = '<a href="architectuur.html" class="hdr-archive-link" aria-current="page" aria-label="Huidige pagina: Architectuur"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="6" height="6" rx="1"/><rect x="16" y="3" width="6" height="6" rx="1"/><rect x="9" y="15" width="6" height="6" rx="1"/><line x1="5" y1="9" x2="5" y2="12"/><line x1="19" y1="9" x2="19" y2="12"/><line x1="5" y1="12" x2="19" y2="12"/><line x1="12" y1="12" x2="12" y2="15"/></svg> Architectuur</a>'
PRES_NORMAL  = '\n      <a href="presentatie.html" class="hdr-archive-link" aria-label="Genereer een wekelijkse presentatie"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> Presentatie</a>'

print("\n── kalender.html ────────────────────────────────────────")
patch("kalender.html", [(ARCH_NORMAL, ARCH_NORMAL + PRES_NORMAL)])

print("\n── archief.html ─────────────────────────────────────────")
patch("archief.html",  [(ARCH_NORMAL, ARCH_NORMAL + PRES_NORMAL)])

print("\n── architectuur.html ────────────────────────────────────")
STRAY = "<\n    'code-cache':  { badge:'📦 Cache', bc:'#2a5c2a',\n      title:'loadData() / Cache', sub:'SessionStorage + maandag-invalidatie',\n      fn:'Laadt data.json met slimme caching. Cache ongeldig na maandag 06:00 UTC of na 30 minuten.',\n      logic:'Vergelijkt cache timestamp met laatste maandag-run. Bij twijfel: verse fetch.',\n      tech:'sessionStorage. _ts timestamp. lastMonRun berekening. CACHE_KEY versie-key.' },\n"
CSS_NODE = '        <div class="node" onclick="selectNode(\'comp-css\')" id="n-comp-css">\n          <div class="nicon" style="font-size:1rem">🎨</div><div class="ntitle" style="font-size:0.75rem">shared.css</div>\n          <div class="nsub">Design tokens · WCAG 2.2 AA · dark mode · reduced-motion</div>\n        </div>'
PRES_NODE = '        <div class="node" onclick="selectNode(\'comp-presentatie\')" id="n-comp-presentatie">\n          <div class="nicon" style="font-size:1rem">📊</div><div class="ntitle" style="font-size:0.75rem">presentatie.html</div>\n          <div class="nsub">PptxGenJS CDN · weekkeuze · productfilter · XTRM-branding</div>\n        </div>'
COMP_PRES = "  'comp-presentatie': {badge:'📊 Frontend',bc:'var(--teal-bg)',btc:'var(--teal-t)',title:'presentatie.html',sub:'Wekelijkse PPTX-generator',fn:'Genereert branded .pptx in de browser. Klantgegevens, weekkeuze (4 weken), productfilter, 10 slides met XTRM-stijl.',logic:'waitForPptx() → loadData() → buildWeekRanges() → buildProductGrid() → generatePptx() → PptxGenJS.writeFile().',tech:'PptxGenJS 4.0.1 CDN. SessionStorage cache 30min. Embedded base64 assets (logos, achtergronden). Barlow fonts.'},\n  "
CODE_CACHE = "  'code-cache':      {badge:'📦 Cache',bc:'#2a5c2a',btc:'#d4eda0',title:'loadData() / Cache',sub:'SessionStorage + maandag-invalidatie',fn:'Laadt data.json met slimme caching. Cache ongeldig na maandag 06:00 UTC of na 30 minuten.',logic:'Vergelijkt cache timestamp met laatste maandag-run. Bij twijfel: verse fetch.',tech:'sessionStorage. _ts timestamp. lastMonRun berekening. CACHE_KEY versie-key.'},\n  "
patch("architectuur.html", [
    (STRAY,        ""),
    (ARCH_CURRENT, ARCH_CURRENT + PRES_NORMAL),
    (CSS_NODE,     PRES_NODE + "\n" + CSS_NODE),
    ("  \'comp-archief\':", COMP_PRES + "\'comp-archief\':"),
    ("  \'code-fetch-fn\':", CODE_CACHE + "\'code-fetch-fn\':"),
    ("index · archief · kalender + shared.css",
     "index · archief · kalender · presentatie + shared.css"),
])

print("\n── presentatie.html ─────────────────────────────────────")
with open("presentatie.html", encoding="utf-8") as f: ph = f.read()
old_tag = re.search(r'<a href="presentatie\.html" class="hdr-archive-link"[^>]+>', ph)
if old_tag:
    new_tag = '<a href="presentatie.html" class="hdr-archive-link" aria-current="page" aria-label="Huidige pagina: Presentatie">'
    ph = ph.replace(old_tag.group(), new_tag, 1)
    with open("presentatie.html", "w", encoding="utf-8") as f: f.write(ph)
    print("  ✓  presentatie.html: aria-current + aria-label gecorrigeerd")
else:
    print("  ⚠  presentatie.html: self-link niet gevonden")

print("\nKlaar. Commit de gewijzigde bestanden naar GitHub.")
