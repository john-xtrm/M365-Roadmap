/* ═══════════════════════════════════════════════════════════════════════
   shared.js — Gedeelde functies voor alle M365 Roadmap pagina's
   Laad NA app-meta.js (breidt APP_META/APP_ORDER uit en voegt toe)

   Bevat:
   · APP_META uitgebreid naar 28 producten (bug-fix: was 17 op meerdere pagina's)
   · APP_ORDER volledig
   · renderNav()   — injecteert navigatie met juiste aria-current
   · toggleTheme() — licht/donker modus
   · Gedeelde constanten: LINK_ICON, ACTION_LABEL, ACTION_ICON
   · Locale helpers: MAANDEN, MONTHS, NL_MAANDEN, EN_MONTHS
   · CACHE_KEY
   · Hulpfuncties: esc, daysAgo, weekStart/End, isoWeek, inSameWeek,
                   fmtDate, nlRelease, parseReleaseDate, parseRelease,
                   highlight, fetchWithTimeout
   ═══════════════════════════════════════════════════════════════════════ */
'use strict';

/* ══════════════════════════════════════════════════════════════════════════
   APP_META — uitgebreid naar 28 producten (was inconsistent: 17 vs 28)
   Overschrijft de versie uit app-meta.js (die minder producten had)
   ══════════════════════════════════════════════════════════════════════════ */
var APP_META = {
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
};

/* ── APP_ORDER — volledige volgorde (was ook inconsistent) ─────────────── */
var APP_ORDER = [
  'copilot','teams','outlook','excel','word','powerpoint',
  'sharepoint','purview','viva','edge','onedrive','exchange',
  'forms','intune','entra','planner',
  'loop','whiteboard','todo','bookings','stream',
  'automate','powerapps','powerbi','yammer',
  'defender','search','project','visio','windows'
];

/* ══════════════════════════════════════════════════════════════════════════
   NAVIGATIE — renderNav(activePage)
   Injecteert de volledige navigatie in <nav id="main-nav">.
   WCAG: aria-current="page" op actieve link, aria-label per link.
   ══════════════════════════════════════════════════════════════════════════ */
var _NAV_ITEMS = [
  {
    id: 'index',
    href: 'index.html',
    label: 'Roadmap',
    ariaLabel: 'Terug naar de hoofdpagina',
    activeAriaLabel: 'Huidige pagina: Roadmap',
    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
  },
  {
    id: 'kalender',
    href: 'kalender.html',
    label: 'Kalender',
    ariaLabel: 'Bekijk de releasekalender',
    activeAriaLabel: 'Huidige pagina: Kalender',
    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
  },
  {
    id: 'archief',
    href: 'archief.html',
    label: 'Archief',
    ariaLabel: 'Bekijk het archief van verdwenen items',
    activeAriaLabel: 'Huidige pagina: Archief',
    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/></svg>'
  },
  {
    id: 'presentatie',
    href: 'presentatie.html',
    label: 'Presentatie',
    ariaLabel: 'Bekijk de presentatiegenerator',
    activeAriaLabel: 'Huidige pagina: Presentatie',
    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>'
  },
  {
    id: 'architectuur',
    href: 'architectuur.html',
    label: 'Architectuur',
    ariaLabel: 'Bekijk de architectuurkaart',
    activeAriaLabel: 'Huidige pagina: Architectuur',
    icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="6" height="6" rx="1"/><rect x="16" y="3" width="6" height="6" rx="1"/><rect x="9" y="15" width="6" height="6" rx="1"/><line x1="5" y1="9" x2="5" y2="12"/><line x1="19" y1="9" x2="19" y2="12"/><line x1="5" y1="12" x2="19" y2="12"/><line x1="12" y1="12" x2="12" y2="15"/></svg>'
  }
];

var _THEME_BTN =
  '<button id="theme-btn" class="theme-btn" onclick="toggleTheme()" aria-label="Schakel naar donker thema" title="Thema wisselen">' +
    '<svg class="icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>' +
    '<svg class="icon-sun"  width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>' +
  '</button>';

/**
 * Injecteert de navigatie in <nav id="main-nav">.
 * @param {string} activePage - 'index' | 'kalender' | 'archief' | 'presentatie' | 'architectuur'
 */
function renderNav(activePage) {
  var nav = document.getElementById('main-nav');
  if (!nav) return;
  var html = _NAV_ITEMS.map(function(item) {
    var isActive = item.id === activePage;
    return '<a href="' + item.href + '" class="hdr-archive-link"' +
      (isActive ? ' aria-current="page"' : '') +
      ' aria-label="' + (isActive ? item.activeAriaLabel : item.ariaLabel) + '">' +
      item.icon + ' ' + item.label + '</a>';
  }).join('');
  nav.innerHTML = html + _THEME_BTN;
  /* Thema-knop label direct correct zetten op basis van huidige staat */
  var html2 = document.documentElement;
  var sys = window.matchMedia('(prefers-color-scheme: dark)').matches;
  var isDark = html2.getAttribute('data-theme') === 'dark' || (!html2.getAttribute('data-theme') && sys);
  var btn = document.getElementById('theme-btn');
  if (btn) btn.setAttribute('aria-label', isDark ? 'Schakel naar licht thema' : 'Schakel naar donker thema');
}

/* ══════════════════════════════════════════════════════════════════════════
   THEMA-TOGGLE
   ══════════════════════════════════════════════════════════════════════════ */
function toggleTheme() {
  var html    = document.documentElement;
  var current = html.getAttribute('data-theme');
  var sys     = window.matchMedia('(prefers-color-scheme: dark)').matches;
  var isDark  = current === 'dark' || (!current && sys);
  var next    = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  var btn = document.getElementById('theme-btn');
  if (btn) btn.setAttribute('aria-label', next === 'dark' ? 'Schakel naar licht thema' : 'Schakel naar donker thema');
}

/* ══════════════════════════════════════════════════════════════════════════
   GEDEELDE CONSTANTEN
   ══════════════════════════════════════════════════════════════════════════ */
var LINK_ICON = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

var DETAIL_ICON = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';

var ACTION_LABEL = {
  none:  'Gaat automatisch',
  admin: 'IT-beheerder actie vereist',
  user:  'Medewerker kan zelf instellen'
};

var ACTION_ICON = { none: '🟢', admin: '🟡', user: '🔵' };

var CACHE_KEY = 'm365_data_v1';

/* ── Locale helpers ────────────────────────────────────────────────────── */
var MAANDEN = {
  january:'januari', february:'februari', march:'maart',    april:'april',
  may:'mei',         june:'juni',         july:'juli',      august:'augustus',
  september:'september', october:'oktober', november:'november', december:'december'
};

var MONTHS = {
  january:0,  february:1, march:2,    april:3,
  may:4,      june:5,     july:6,     august:7,
  september:8,october:9,  november:10,december:11,
  januari:0,  februari:1, maart:2,    /* april:3 same */
  mei:4,      juni:5,     juli:6,     augustus:7,
  /* september, oktober, november, december same as English */
  oktober:9
};

var NL_MAANDEN = [
  'januari','februari','maart','april','mei','juni',
  'juli','augustus','september','oktober','november','december'
];

var EN_MONTHS = {
  january:0, february:1, march:2,    april:3,    may:4,      june:5,
  july:6,    august:7,   september:8,october:9,  november:10,december:11
};

/* ══════════════════════════════════════════════════════════════════════════
   HULPFUNCTIES
   ══════════════════════════════════════════════════════════════════════════ */

/** HTML-escape */
function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/** Aantal dagen geleden */
function daysAgo(d) {
  return d ? (Date.now() - new Date(d).getTime()) / 864e5 : 9999;
}

/** Maandag van de week van date */
function weekStart(date) {
  var d = new Date(date);
  var day = d.getDay();
  var diff = (day === 0 ? -6 : 1 - day);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + diff);
  return d;
}

/** Zondag (einde) van de week van date */
function weekEnd(date) {
  var ws = weekStart(date);
  var we = new Date(ws);
  we.setDate(we.getDate() + 6);
  we.setHours(23, 59, 59, 999);
  return we;
}

/** ISO weeknummer */
function isoWeek(date) {
  var d = new Date(date);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + 3 - (d.getDay() + 6) % 7);
  var w1 = new Date(d.getFullYear(), 0, 4);
  return 1 + Math.round(((d - w1) / 864e5 - 3 + (w1.getDay() + 6) % 7) / 7);
}

/** True als datum d in dezelfde week valt als refDate */
function inSameWeek(d, refDate) {
  if (!d) return false;
  var dt = new Date(d);
  return dt >= weekStart(refDate) && dt <= weekEnd(refDate);
}

/** Datum formatteren als "1 jan. 2025" */
function fmtDate(d) {
  return d ? new Date(d).toLocaleDateString('nl-NL', { day:'numeric', month:'short', year:'numeric' }) : '';
}

/** Engelstalige maanden in release-string vertalen naar Nederlands */
function nlRelease(s) {
  if (!s) return '\u2013';
  return s.replace(
    /\b(january|february|march|april|may|june|july|august|september|october|november|december)\b/gi,
    function(m) { return MAANDEN[m.toLowerCase()] || m; }
  ).replace(/\bCY(\d{4})\b/, '$1');
}

/**
 * Parseert een release-string naar een Date voor sortering (index.html).
 * Voorbeeld: "April CY2026" → new Date(2026, 3, 1)
 */
function parseReleaseDate(s) {
  if (!s) return new Date(9999, 0, 1);
  var m = s.toLowerCase().match(/(\w+)\s+(\d{4})/);
  return (m && MONTHS[m[1]] !== undefined)
    ? new Date(parseInt(m[2]), MONTHS[m[1]], 1)
    : new Date(9999, 0, 1);
}

/**
 * Parseert een release-string naar een object voor kalendergroepering (kalender.html).
 * Voorbeeld: "April CY2026" → { year:2026, month:3, quarter:2, exact:'month' }
 */
function parseRelease(s) {
  if (!s || !s.trim()) return null;
  var t = s.trim();
  var mM = t.match(/([a-z]+)\s+CY(\d{4})/i);
  if (mM) {
    var mo = EN_MONTHS[mM[1].toLowerCase()];
    if (mo !== undefined) return { year: parseInt(mM[2]), month: mo, quarter: Math.floor(mo / 3) + 1, exact: 'month' };
  }
  var mQ1 = t.match(/Q([1-4])\s+CY(\d{4})/i);
  var mQ2 = t.match(/CY(\d{4})\s+Q([1-4])/i);
  var mQ  = mQ1 || mQ2;
  if (mQ) {
    var q = mQ1 ? parseInt(mQ1[1]) : parseInt(mQ2[2]);
    var y = mQ1 ? parseInt(mQ1[2]) : parseInt(mQ2[1]);
    return { year: y, quarter: q, month: (q - 1) * 3, exact: 'quarter' };
  }
  var mY = t.match(/CY(\d{4})/i);
  if (mY) return { year: parseInt(mY[1]), quarter: 1, month: 0, exact: 'year' };
  return null;
}

/** Zoekterm markeren in tekst */
function highlight(text, query) {
  if (!query) return esc(text);
  return esc(text).replace(
    new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'),
    '<mark>$1</mark>'
  );
}

/** fetch met AbortController-timeout */
function fetchWithTimeout(url, ms) {
  ms = ms || 10000;
  var ctrl  = new AbortController();
  var timer = setTimeout(function() { ctrl.abort(); }, ms);
  return fetch(url, { signal: ctrl.signal }).finally(function() { clearTimeout(timer); });
}

/* ══════════════════════════════════════════════════════════════════════════
   KAART-COMPONENTEN — gedeeld door index, kalender en archief
   ══════════════════════════════════════════════════════════════════════════ */

var _STATUS_CFG = {
  rolling:   { label: 'Wordt uitgerold', cls: 'p-rolling' },
  dev:       { label: 'In ontwikkeling', cls: 'p-dev'     },
  launched:  { label: 'Uitgerold',       cls: 'p-rolling' },
  cancelled: { label: 'Geannuleerd',     cls: 'p-dev'     }
};

var _COPY_ICON =
  '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"' +
  ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<rect x="9" y="9" width="13" height="13" rx="2"/>' +
  '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';

/**
 * Bouwt productpillen voor een item. Toont primair product + eventuele tags.
 * Backward-compatible: als tags ontbreekt → alleen primaire pill.
 */
function buildProductPills(item) {
  var meta = APP_META[item.app] || APP_META.other;
  var html = '<span class="pill ' + meta.cls + '">' +
             appIconHTML(item.app) + esc(item.prodLabel || meta.label) +
             '</span>';
  var seen = {}; seen[item.app] = true;
  (item.tags || []).forEach(function(key) {
    if (!key || seen[key] || !APP_META[key] || key === 'other') return;
    seen[key] = true;
    var m = APP_META[key];
    html += '<span class="pill ' + m.cls + '">' + appIconHTML(key) + esc(m.label) + '</span>';
  });
  return html;
}

/**
 * Genereert een uniforme kaart-HTML voor index, kalender en archief.
 *
 * @param {Object}  item    - roadmap item
 * @param {Object}  [opts]  - weergave-opties (standaard = minimaal)
 *   opts.newBadge   {bool}   ⭐ Nieuw badge tonen
 *   opts.benefit    {bool}   Beschrijving tonen
 *   opts.action     {bool}   Actieblok tonen
 *   opts.details    {bool}   Uitklapbare technische details tonen
 *   opts.release    {bool}   Releasedatum tonen
 *   opts.dates      {bool}   Toegevoegd/gewijzigd datums tonen
 *   opts.copy       {bool}   Kopieer-link knop tonen
 *   opts.detailLink {bool}   "Details"-link naar index.html tonen
 *   opts.shortTerm  {bool}   📅 Kortetermijn badge tonen (kalender)
 *   opts.uncertain  {bool}   Onzekere releasedatum styling (kalender)
 * @param {string}  [query] - zoekterm voor tekst-markering
 */
function cardHTML(item, opts, query) {
  opts  = opts  || {};
  query = query || '';

  var cfg  = _STATUS_CFG[item.status] || { label: item.status || '', cls: 'p-other' };
  var actCls = item.action ? ' act-' + item.action : '';

  /* ── Pills ── */
  var shortTermBadge = opts.shortTerm
    ? '<span class="short-term-badge" title="Heeft exacte maanddatum">' +
      '<span aria-hidden="true">📅</span> Ook in maandweergave</span>'
    : '';

  var pills =
    '<div class="card-pills">' +
      buildProductPills(item) +
      '<span class="pill ' + cfg.cls + '">' + cfg.label + '</span>' +
      (opts.newBadge && item.isNew
        ? '<span class="new-badge"><span aria-hidden="true">\u2B50</span> Nieuw</span>'
        : '') +
      shortTermBadge +
    '</div>';

  /* ── Titel ── */
  var title = '<h3 class="card-title">' +
    (query ? highlight(item.title, query) : esc(item.title)) +
    '</h3>';

  /* ── Beschrijving ── */
  var benefit = '';
  if (opts.benefit && item.benefit) {
    benefit =
      '<div class="card-benefit">' +
        '<span class="card-benefit-label">Wat betekent dit voor uw organisatie?</span>' +
        (query ? highlight(item.benefit, query) : esc(item.benefit)) +
      '</div>';
  }

  /* ── Actieblok ── */
  var action = '';
  if (opts.action && item.action) {
    action =
      '<div class="card-action act-' + item.action + '"' +
        ' aria-label="Actie: ' + esc(item.actionLabel || ACTION_LABEL[item.action] || '') + '">' +
        '<span aria-hidden="true">' + (ACTION_ICON[item.action] || '') + '</span>' +
        '<span>' + esc(item.actionLabel || ACTION_LABEL[item.action] || '') + '</span>' +
      '</div>';
  }

  /* ── Technische details ── */
  var details = '';
  if (opts.details && item.desc) {
    details =
      '<details>' +
        '<summary>Technische details lezen</summary>' +
        '<div class="card-desc">' + esc(item.desc) + '</div>' +
      '</details>';
  }

  /* ── Footer links ── */
  var footLeft = '';
  if (opts.release && item.release) {
    footLeft +=
      '<span class="release-badge">' +
        '<span aria-hidden="true">\uD83D\uDE80</span> ' +
        '<span class="sr-only">Release:</span>' +
        esc(nlRelease(item.release)) +
      '</span>';
  }
  if (opts.dates) {
    if (item.added) {
      footLeft +=
        '<span class="date-info">' +
          '<span class="sr-only">Toegevoegd:</span> \uD83D\uDCC5 ' + fmtDate(item.added) +
        '</span>';
    }
    if (item.modified && item.modified !== item.added) {
      footLeft +=
        '<span class="date-info" style="margin-left:10px">' +
          '<span class="sr-only">Gewijzigd:</span> \u270F\uFE0F ' + fmtDate(item.modified) +
        '</span>';
    }
  }

  /* ── Footer rechts ── */
  var footRight = '';
  if (opts.detailLink) {
    footRight +=
      '<a class="detail-link"' +
        ' href="index.html?id=' + item.id + '"' +
        ' aria-label="Bekijk details van \'' + esc(item.title) + '\' op de hoofdpagina">' +
        DETAIL_ICON + ' Details' +
      '</a>';
  }
  footRight +=
    '<a class="ms-link"' +
      ' href="https://www.microsoft.com/en-us/microsoft-365/roadmap?searchterms=' + item.id + '"' +
      ' target="_blank" rel="noopener noreferrer"' +
      ' aria-label="Bekijk ID ' + item.id + ' op de offici\u00eble Microsoft roadmap (opent in nieuw venster)">' +
      LINK_ICON + ' ID ' + item.id +
    '</a>';
  if (opts.copy) {
    footRight +=
      '<button class="copy-link-btn"' +
        ' onclick="copyItemLink(' + item.id + ')"' +
        ' aria-label="Kopieer directe link naar dit item"' +
        ' title="Kopieer directe link">' +
        _COPY_ICON +
      '</button>';
  }

  /* ── Samenvoegen ── */
  return '<article class="card' + actCls + '" id="item-' + item.id + '"' +
    ' aria-label="' + esc(item.title) + '"' +
    (opts.uncertain ? ' style="opacity:.75;border-left-style:dashed"' : '') + '>' +
    pills + title + benefit + action + details +
    '<div class="card-foot">' +
      '<div class="card-foot-left">' + (footLeft || '') + '</div>' +
      '<div class="card-foot-right">' + footRight + '</div>' +
    '</div>' +
  '</article>';
}
