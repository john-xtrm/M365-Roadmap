#!/usr/bin/env python3
"""
patch_multipill_hotfix.py — Herstel NameError: title_en not defined
Uitvoeren vanuit repo-root:  python patch_multipill_hotfix.py
"""
import os

PATH = 'fetch_roadmap.py'

# De huidige (foutieve) regel zoals door vorig script geplaatst
OLD = (
    '    product  = row.get("Tags - Product", "")\n'
    '    key      = app_key_from_title(title_en) if title_en else app_key(product)\n'
    '    title_en = row.get("Description", "").strip()\n'
)

# Correct: title_en eerst definiëren, dan pas key bepalen
NEW = (
    '    product  = row.get("Tags - Product", "")\n'
    '    title_en = row.get("Description", "").strip()\n'
    '    key      = app_key_from_title(title_en) if title_en else app_key(product)\n'
)

def main():
    print('patch_multipill_hotfix.py\n')

    if not os.path.exists(PATH):
        print(f'FOUT: {PATH} niet gevonden.')
        return

    with open(PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if OLD not in content:
        print('FOUT: verwacht patroon niet gevonden.')
        print('Controleer of de vorige patch correct is uitgevoerd.')
        return

    content = content.replace(OLD, NEW, 1)

    with open(PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print('✓  Volgorde gecorrigeerd: title_en nu vóór key gedefinieerd')
    print(f'\n✅ {PATH} opgeslagen.')
    print('\nVolgende stap: commit + push, dan opnieuw uitvoeren.')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
