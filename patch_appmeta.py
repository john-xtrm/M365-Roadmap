#!/usr/bin/env python3
"""
patch_appmeta.py
Werkt APP_META en APP_ORDER bij in index.html:
- Voegt 14 nieuwe productsleutels toe aan APP_META
- Voegt 14 nieuwe productsleutels toe aan APP_ORDER
- Verwijdert 'other' uit APP_META en APP_ORDER
  (APP_ICONS behoudt 'other' als stille fallback)

Gebruik: python3 patch_appmeta.py  (vanuit repo-root naast index.html)
"""
import re, sys, os

if not os.path.exists('index.html'):
    print('FOUT: index.html niet gevonden. Voer dit script uit vanuit de repo-root.')
    sys.exit(1)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. Vervang APP_META volledig ─────────────────────────────────────────
NEW_META = """var APP_META = {
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
  search:     { label: 'Search',         cls: 'p-search'     },
  project:    { label: 'Project',        cls: 'p-project'    },
  visio:      { label: 'Visio',          cls: 'p-visio'      },
  windows:    { label: 'Windows',        cls: 'p-windows'    }
};"""

# ── 2. Vervang APP_ORDER volledig ────────────────────────────────────────
NEW_ORDER = """var APP_ORDER = [
  'copilot','teams','outlook','excel','word','powerpoint',
  'sharepoint','purview','viva','edge','onedrive','exchange',
  'forms','intune','entra','planner',
  'loop','whiteboard','todo','bookings','stream',
  'automate','powerapps','powerbi',
  'yammer','defender','search','project','visio','windows'
];"""

# Vervang APP_META
meta_match = re.search(r'var APP_META\s*=\s*\{.*?\};', html, re.DOTALL)
if not meta_match:
    print('FOUT: APP_META niet gevonden in index.html')
    sys.exit(1)
html = html[:meta_match.start()] + NEW_META + html[meta_match.end():]
print('✓ APP_META bijgewerkt (30 producten, geen "other")')

# Vervang APP_ORDER
order_match = re.search(r'var APP_ORDER\s*=\s*\[.*?\];', html, re.DOTALL)
if not order_match:
    print('FOUT: APP_ORDER niet gevonden in index.html')
    sys.exit(1)
html = html[:order_match.start()] + NEW_ORDER + html[order_match.end():]
print('✓ APP_ORDER bijgewerkt (30 producten, geen "other")')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('\nKlaar. Controleer index.html en commit + push.')
