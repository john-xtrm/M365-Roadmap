#!/usr/bin/env python3
"""
patch_multipill.py — Voeg tags-array toe aan fetch_roadmap.py
Uitvoeren vanuit repo-root:  python patch_multipill.py
"""
import os

SLUG_BLOCK = '''
# ── Multi-product slug-mapping (voor tags-array in data.json) ─────────────
PRODUCT_SLUG = {
    "microsoft teams": "teams",           "teams": "teams",
    "microsoft outlook": "outlook",       "outlook": "outlook",
    "microsoft excel": "excel",           "excel": "excel",
    "microsoft word": "word",             "word": "word",
    "microsoft powerpoint": "powerpoint", "powerpoint": "powerpoint",
    "microsoft sharepoint": "sharepoint", "sharepoint": "sharepoint",
    "microsoft 365 copilot": "copilot",   "microsoft copilot": "copilot",
    "copilot": "copilot",
    "microsoft viva": "viva",             "viva": "viva",
    "microsoft purview": "purview",       "purview": "purview",
    "microsoft edge": "edge",             "edge": "edge",
    "microsoft onedrive": "onedrive",     "onedrive": "onedrive",
    "microsoft exchange": "exchange",     "exchange": "exchange",
    "microsoft forms": "forms",           "forms": "forms",
    "microsoft intune": "intune",         "intune": "intune",
    "microsoft entra": "entra",           "entra id": "entra",
    "microsoft planner": "planner",       "planner": "planner",
    "microsoft loop": "loop",             "loop": "loop",
    "microsoft whiteboard": "whiteboard", "whiteboard": "whiteboard",
    "microsoft to do": "todo",            "to do": "todo",
    "microsoft bookings": "bookings",     "bookings": "bookings",
    "microsoft stream": "stream",         "stream": "stream",
    "power automate": "automate",         "microsoft power automate": "automate",
    "power apps": "powerapps",            "microsoft power apps": "powerapps",
    "power bi": "powerbi",                "microsoft power bi": "powerbi",
    "yammer": "yammer",                   "viva engage": "yammer",
    "microsoft defender": "defender",     "defender": "defender",
    "microsoft search": "search",
    "microsoft project": "project",       "project": "project",
    "microsoft visio": "visio",           "visio": "visio",
    "windows": "windows",
}
'''

# Exact zoals het in de broncode staat (met uitlijningsspaties)
ANCHOR   = 'def app_key(p):'
APP_OLD  = '        "app":         key,'
APP_NEW  = ('        "app":         key,\n'
            '        "tags":        [\n'
            '            s for s in (\n'
            '                PRODUCT_SLUG.get(p.get("tagName", "").lower().strip())\n'
            '                for p in item.get("tagsContainer", {}).get("products", [])\n'
            '            ) if s and s != key\n'
            '        ],')

PATH = 'fetch_roadmap.py'

def main():
    print('patch_multipill.py\n')

    if not os.path.exists(PATH):
        print(f'FOUT: {PATH} niet gevonden. Uitvoeren vanuit repo-root?')
        return

    with open(PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Stap 1: PRODUCT_SLUG toevoegen vóór app_key()
    if 'PRODUCT_SLUG' not in content:
        if ANCHOR not in content:
            print(f'FOUT: "{ANCHOR}" niet gevonden.')
            return
        content = content.replace(ANCHOR, SLUG_BLOCK + ANCHOR, 1)
        print('✓  PRODUCT_SLUG toegevoegd')
        changed = True
    else:
        print('ℹ  PRODUCT_SLUG al aanwezig')

    # Stap 2: tags-veld toevoegen in items.append({...})
    if '"tags":' not in content:
        if APP_OLD not in content:
            print(f'FOUT: exacte regel niet gevonden:')
            print(f'  {APP_OLD!r}')
            print('Controleer of de uitlijning in fetch_roadmap.py is gewijzigd.')
            return
        content = content.replace(APP_OLD, APP_NEW, 1)
        print('✓  tags-veld toegevoegd')
        changed = True
    else:
        print('ℹ  tags-veld al aanwezig')

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
