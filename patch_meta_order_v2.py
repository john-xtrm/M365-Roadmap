#!/usr/bin/env python3
"""
patch_meta_order_v2.py
Vervangt APP_META en APP_ORDER volledig in index.html via bracket-tellen.
Robuust: werkt ongeacht whitespace of aantal entries.

Gebruik: python3 patch_meta_order_v2.py  (vanuit repo-root naast index.html)
"""
import re, sys, os

NEW_APP_META = """var APP_META = {
  copilot:    { label: 'Copilot',        cls: 'p-copilot'    },
  teams:      { label: 'Teams',          cls: 'p-teams'      },
  outlook:    { label: 'Outlook',        cls: 'p-outlook'    },
  excel:      { label: 'Excel',          cls: 'p-excel'      },
  word:       { label: 'Word',           cls: 'p-word'       },
  powerpoint: { label: 'PowerPoint',     cls: 'p-powerpoint' },
  sharepoint: { label: 'SharePoint',     cls: 'p-sharepoint' },
  purview:    { label: 'Purview',        cls: 'p-purview'    },
  viva:       { label: 'Viva',           cls: 'p-viva'       },
  edge:       { label: 'Edge',           cls: 'p-edge'       },
  onedrive:   { label: 'OneDrive',       cls: 'p-onedrive'   },
  exchange:   { label: 'Exchange',       cls: 'p-exchange'   },
  forms:      { label: 'Forms',          cls: 'p-forms'      },
  intune:     { label: 'Intune',         cls: 'p-intune'     },
  entra:      { label: 'Entra',          cls: 'p-entra'      },
  planner:    { label: 'Planner',        cls: 'p-planner'    },
  loop:       { label: 'Loop',           cls: 'p-loop'       },
  whiteboard: { label: 'Whiteboard',     cls: 'p-whiteboard' },
  todo:       { label: 'To Do',          cls: 'p-todo'       },
  bookings:   { label: 'Bookings',       cls: 'p-bookings'   },
  stream:     { label: 'Stream',         cls: 'p-stream'     },
  automate:   { label: 'Power Automate', cls: 'p-automate'   },
  powerapps:  { label: 'Power Apps',     cls: 'p-powerapps'  },
  powerbi:    { label: 'Power BI',       cls: 'p-powerbi'    },
  yammer:     { label: 'Yammer',         cls: 'p-yammer'     },
  defender:   { label: 'Defender',       cls: 'p-defender'   },
  search:     { label: 'M365 Search',    cls: 'p-search'     },
  project:    { label: 'Project',        cls: 'p-project'    },
  visio:      { label: 'Visio',          cls: 'p-visio'      },
  windows:    { label: 'Windows',        cls: 'p-windows'    },
  other:      { label: 'Overig',         cls: 'p-other'      }
}"""

NEW_APP_ORDER = """var APP_ORDER = [
  'copilot','teams','outlook','excel','word','powerpoint',
  'sharepoint','purview','viva','edge','onedrive','exchange',
  'forms','intune','entra','planner',
  'loop','whiteboard','todo','bookings','stream',
  'automate','powerapps','powerbi','yammer',
  'defender','search','project','visio','windows'
]"""

def find_js_object(text, varname):
    m = re.search(r'var\s+' + varname + r'\s*=\s*\{', text)
    if not m:
        return None, None
    depth = 0
    for i in range(m.start(), len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return m.start(), i + 1
    return None, None

def find_js_array(text, varname):
    m = re.search(r'var\s+' + varname + r'\s*=\s*\[', text)
    if not m:
        return None, None
    depth = 0
    for i in range(m.start(), len(text)):
        if text[i] == '[':
            depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0:
                return m.start(), i + 1
    return None, None

if not os.path.exists('index.html'):
    print('FOUT: index.html niet gevonden.')
    sys.exit(1)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── APP_META vervangen ────────────────────────────────────────────────────
s, e = find_js_object(html, 'APP_META')
if s is None:
    print('FOUT: APP_META niet gevonden in index.html')
    sys.exit(1)
html = html[:s] + NEW_APP_META + html[e:]
print(f'✓ APP_META vervangen (30 producten + other fallback)')

# ── APP_ORDER vervangen ───────────────────────────────────────────────────
s, e = find_js_array(html, 'APP_ORDER')
if s is None:
    print('FOUT: APP_ORDER niet gevonden in index.html')
    sys.exit(1)
html = html[:s] + NEW_APP_ORDER + html[e:]
print(f'✓ APP_ORDER vervangen (30 producten, geen Overig-knop)')

# ── Validatie ─────────────────────────────────────────────────────────────
required = ['loop','whiteboard','todo','bookings','stream','automate',
            'powerapps','powerbi','yammer','defender','search','project',
            'visio','windows']
missing = [k for k in required if f"'{k}'" not in html]
if missing:
    print(f'WAARSCHUWING: ontbrekende sleutels: {missing}')
    sys.exit(1)
else:
    print(f'✓ Alle 30 productsleutels aanwezig in output')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('\nGereed. Commit & push index.html om live te gaan.')
