#!/usr/bin/env python3
"""
patch_multipill.py  —  Multi-product pills voor M365 Roadmap Dashboard
Uitvoeren vanuit de root van de repository:  python patch_multipill.py
"""
import os, sys, textwrap

# ── Bestanden ──────────────────────────────────────────────────────────────
HTML_FILES = [
    'index.html',
    'kalender.html',
    'archief.html',
    'presentatie.html',
]

# ── Nieuwe JS-helperfunctie ────────────────────────────────────────────────
FUNCTION_JS = """\

/* ── Multi-product pills ────────────────────────────────────────────────── */
/* Eerste pill = primair product (item.app / item.prodLabel).                */
/* Extra pills = item.tags (array van app-sleutels, gevuld door Python-      */
/* pipeline). Backward-compatible: als tags ontbreekt → alleen primaire      */
/* pill, identiek aan het oude gedrag.                                        */
function buildProductPills(obj) {
  var meta = APP_META[obj.app] || APP_META.other;
  var html = '<span class="pill ' + meta.cls + '">' +
             appIconHTML(obj.app) + esc(obj.prodLabel || meta.label) +
             '</span>';
  var seen = {}; seen[obj.app] = true;
  (obj.tags || []).forEach(function(key) {
    if (!key || seen[key] || !APP_META[key] || key === 'other') return;
    seen[key] = true;
    var m = APP_META[key];
    html += '<span class="pill ' + m.cls + '">' +
            appIconHTML(key) + esc(m.label) +
            '</span>';
  });
  return html;
}
"""

# ── Vervanging-paren (oud → nieuw) per variabelenaam ──────────────────────
# Elke tuple: (exacte string in bestand, vervanging)
REPLACEMENTS = [
    # Kaartweergave met variabele 'item'
    (
        "'<span class=\"pill '+meta.cls+'\">'+"
        "appIconHTML(item.app)+esc(item.prodLabel||meta.label)+'</span>'+",
        "buildProductPills(item)+"
    ),
    # Verwijderde items in changes-block / archief (variabele 'r')
    (
        "'<span class=\"pill '+meta.cls+'\">'+"
        "appIconHTML(r.app)+esc(r.prodLabel||meta.label)+'</span>'+",
        "buildProductPills(r)+"
    ),
    # Kalender/presentatie kunnen 'entry' of andere naam gebruiken
    # → extra patronen veiligheidshalve meenemen
    (
        "'<span class=\"pill '+meta.cls+'\">'+"
        "appIconHTML(entry.app)+esc(entry.prodLabel||meta.label)+'</span>'+",
        "buildProductPills(entry)+"
    ),
    (
        "'<span class=\"pill '+meta.cls+'\">'+"
        "appIconHTML(it.app)+esc(it.prodLabel||meta.label)+'</span>'+",
        "buildProductPills(it)+"
    ),
]

# Invoegpunten voor de nieuwe functie (eerste treffer wordt gebruikt)
INSERT_ANCHORS = [
    '/* ── Kaart HTML \u2500',          # index.html / kalender.html / archief.html
    '/* \u2500\u2500 Kaart HTML',       # alternatieve opmaak
    'function cardHTML(',
    'function buildCard(',
    'function renderCard(',
    'function renderItem(',
]

# ─────────────────────────────────────────────────────────────────────────
def patch_file(path):
    if not os.path.exists(path):
        print(f'  ⚪ OVERGESLAGEN (bestand niet gevonden): {path}')
        return False

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    pills_replaced = 0

    # 1. Vervang single-pill renders → buildProductPills(...)
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            pills_replaced += 1
            var = old.split('appIconHTML(')[1].split('.app')[0]
            print(f'  ✓ Pill vervangen: buildProductPills({var})+')

    if pills_replaced == 0:
        print(f'  ⚠ Geen pill-patroon gevonden. Bestand ongewijzigd gelaten.')
        return False

    # 2. Voeg buildProductPills in (alleen als nog niet aanwezig)
    if 'function buildProductPills(' not in content:
        inserted = False
        for anchor in INSERT_ANCHORS:
            if anchor in content:
                content = content.replace(anchor, FUNCTION_JS + anchor, 1)
                inserted = True
                print(f'  ✓ buildProductPills() ingevoegd vóór "{anchor.strip()[:40]}"')
                break
        if not inserted:
            # Fallback: invoegen net vóór </script> (laatste voorkomen)
            tag = '</script>'
            pos = content.rfind(tag)
            if pos != -1:
                content = content[:pos] + FUNCTION_JS + '\n' + content[pos:]
                inserted = True
                print(f'  ✓ buildProductPills() ingevoegd vóór </script>')
            else:
                print(f'  ✗ Kon geen invoegpunt vinden — buildProductPills NIET ingevoegd!')
    else:
        print(f'  ℹ buildProductPills() al aanwezig, niet nogmaals ingevoegd.')

    if content == original:
        print(f'  ℹ Geen netto wijziging in {path}.')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✅ Opgeslagen: {path}')
    return True


# ─────────────────────────────────────────────────────────────────────────
def print_fetch_instructions():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STAP 2 — fetch_roadmap.py aanpassen (handmatig)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voeg onderaan de bestaande PRODUCT_MAP / APP_KEY-sectie
de volgende constante toe:

  PRODUCT_SLUG = {
      'microsoft teams': 'teams',       'teams': 'teams',
      'microsoft outlook': 'outlook',   'outlook': 'outlook',
      'microsoft excel': 'excel',       'excel': 'excel',
      'microsoft word': 'word',         'word': 'word',
      'microsoft powerpoint': 'powerpoint',
      'powerpoint': 'powerpoint',
      'microsoft sharepoint': 'sharepoint',
      'sharepoint': 'sharepoint',
      'microsoft 365 copilot': 'copilot',
      'microsoft copilot': 'copilot',   'copilot': 'copilot',
      'microsoft viva': 'viva',         'viva': 'viva',
      'microsoft purview': 'purview',   'purview': 'purview',
      'microsoft edge': 'edge',         'edge': 'edge',
      'microsoft onedrive': 'onedrive', 'onedrive': 'onedrive',
      'microsoft exchange': 'exchange', 'exchange': 'exchange',
      'microsoft forms': 'forms',       'forms': 'forms',
      'microsoft intune': 'intune',     'intune': 'intune',
      'microsoft entra': 'entra',       'entra id': 'entra',
      'microsoft planner': 'planner',   'planner': 'planner',
  }

Zoek daarna de plek waar je het item-dict opbouwt (de dict
met 'id', 'title', 'app', 'prodLabel', enz.) en voeg DIRECT
NA het bepalen van app_key de volgende regels toe:

  # Extra producttags (voor multi-pill weergave in dashboard)
  raw_products = [
      p.get('tagName', '')
      for p in item.get('tagsContainer', {}).get('products', [])
  ]
  seen_slugs = {app_key}
  extra_tags = []
  for prod in raw_products:
      slug = PRODUCT_SLUG.get(prod.lower().strip())
      if slug and slug not in seen_slugs and slug != 'other':
          seen_slugs.add(slug)
          extra_tags.append(slug)
  # ← voeg 'tags': extra_tags toe aan het item-dict

Voorbeeld (als je dict 'entry' heet):
  entry['tags'] = extra_tags

Na de volgende pipeline-run bevat data.json per item een
'tags'-array, en toont het dashboard automatisch meerdere pills.

BACKWARD-COMPATIBLE: als tags leeg is → alleen primaire pill
(identiek aan het huidige gedrag).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ─────────────────────────────────────────────────────────────────────────
def main():
    print('=' * 56)
    print('  patch_multipill.py  —  Multi-product pills')
    print('=' * 56)
    print()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_root)

    total = 0
    for fname in HTML_FILES:
        print(f'▶ {fname}')
        if patch_file(fname):
            total += 1
        print()

    print(f'HTML-patch klaar: {total}/{len(HTML_FILES)} bestand(en) aangepast.')
    print_fetch_instructions()


if __name__ == '__main__':
    main()
