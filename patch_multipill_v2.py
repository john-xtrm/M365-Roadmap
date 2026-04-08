#!/usr/bin/env python3
"""
patch_multipill_v2.py — Herstel primaire app + vul tags correct
Uitvoeren vanuit repo-root:  python patch_multipill_v2.py

Problemen die dit oplost:
  1. Primaire app werd bepaald via Tags-Product kolom → Copilot won te vaak
     Fix: gebruik de titelprefix (voor de dubbele punt) als primaire bron
  2. tags werd gevuld via tagsContainer (JSON API-veld, niet in CSV)
     Fix: gebruik Tags-Product kolom voor extra tags
"""
import os

PATH = 'fetch_roadmap.py'

# ── Nieuwe helperfunctie: primaire app uit titelprefix ─────────────────────
# Invoegen direct na de bestaande app_key() functie
INSERT_AFTER = '''    return "other"

def make_label(product, key):'''

NEW_FUNCTION = '''    return "other"

def app_key_from_title(title):
    """Leidt de primaire app-sleutel af uit de titelprefix (voor de ':')."""
    if ':' in title:
        prefix = title.split(':', 1)[0].strip()
        return app_key(prefix)
    return app_key(title)

def extra_tags(product_field, primary_key):
    """Alle herkende app-sleutels uit Tags-Product, behalve de primaire."""
    seen = {primary_key}
    tags = []
    for part in product_field.replace(';', ',').split(','):
        k = app_key(part.strip())
        if k and k != 'other' and k not in seen:
            seen.add(k)
            tags.append(k)
    return tags

def make_label(product, key):'''

# ── Vervanging in de verwerkingsloop ──────────────────────────────────────
# Oud: key afgeleid uit product-tag
LOOP_OLD = (
    '    product  = row.get("Tags - Product", "")\n'
    '    key      = app_key(product)\n'
)

# Nieuw: key afgeleid uit titelprefix, fallback naar product-tag
LOOP_NEW = (
    '    product  = row.get("Tags - Product", "")\n'
    '    key      = app_key_from_title(title_en) if title_en else app_key(product)\n'
)

# ── Vervanging van de tags-regel in items.append() ────────────────────────
# Oud: leunde op tagsContainer (JSON API-veld, bestaat niet in CSV)
TAGS_OLD = (
    '        "tags":        [\n'
    '            s for s in (\n'
    '                PRODUCT_SLUG.get(p.get("tagName", "").lower().strip())\n'
    '                for p in item.get("tagsContainer", {}).get("products", [])\n'
    '            ) if s and s != key\n'
    '        ],'
)

# Nieuw: tags uit de product-kolom van de CSV
TAGS_NEW = '        "tags":        extra_tags(product, key),'


def main():
    print('patch_multipill_v2.py\n')

    if not os.path.exists(PATH):
        print(f'FOUT: {PATH} niet gevonden.')
        return

    with open(PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Stap 1: nieuwe helperfuncties invoegen
    if 'app_key_from_title' not in content:
        if INSERT_AFTER not in content:
            print('FOUT: invoegpunt voor app_key_from_title niet gevonden.')
            return
        content = content.replace(INSERT_AFTER, NEW_FUNCTION, 1)
        print('✓  app_key_from_title() en extra_tags() toegevoegd')
        changed = True
    else:
        print('ℹ  app_key_from_title() al aanwezig')

    # Stap 2: key bepalen via titelprefix
    if 'app_key_from_title(title_en)' not in content:
        if LOOP_OLD not in content:
            print('FOUT: verwerkingsloop-regel niet gevonden.')
            print(f'  Zoekt naar: {LOOP_OLD!r}')
            return
        content = content.replace(LOOP_OLD, LOOP_NEW, 1)
        print('✓  Primaire app nu afgeleid uit titelprefix')
        changed = True
    else:
        print('ℹ  Titelprefix-logica al aanwezig')

    # Stap 3: tags via product-kolom (vervangt tagsContainer-aanpak)
    if 'extra_tags(product, key)' not in content:
        if TAGS_OLD in content:
            content = content.replace(TAGS_OLD, TAGS_NEW, 1)
            print('✓  tags nu gevuld via Tags-Product kolom')
            changed = True
        elif '"tags":' in content:
            print('⚠  tags-regel gevonden maar patroon wijkt af.')
            print('   Vervang handmatig de "tags": [...] regel door:')
            print(f'   {TAGS_NEW}')
        else:
            print('⚠  Geen tags-regel gevonden — voeg handmatig toe na "app": key:')
            print(f'   {TAGS_NEW}')
    else:
        print('ℹ  tags via extra_tags() al aanwezig')

    if changed:
        with open(PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'\n✅ {PATH} opgeslagen.')
    else:
        print(f'\nℹ  Geen wijzigingen nodig.')

    print('\nVolgende stap: commit + push, dan fetch_roadmap.py uitvoeren.')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
