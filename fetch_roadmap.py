"""
Microsoft 365 Roadmap - fetch & verwerk
- Laadt bestaande vertalingen uit data.json als cache
- Controleert of gecachede items daadwerkelijk Nederlands zijn
- Vertaalt ALLEEN items die nieuw, gewijzigd, of nog niet correct vertaald zijn
- Slaat items op die deze week Launched of Cancelled zijn geworden
- Slaat een archief op in archive/YYYY-MM-DD.json (max 3 maanden bewaard)
"""

import csv, json, io, datetime, re, time, os
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="nl")

def translate(text, retries=3):
    if not text or not text.strip():
        return text
    for attempt in range(retries):
        try:
            result = translator.translate(text[:4800])
            return result if result else text
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                print(f"    ⚠ Vertaling mislukt, origineel behouden: {e}")
                return text

# ── Nederlandse taaldetectie ──────────────────────────────────────────────
NL_INDICATORS = [
    "de ", "het ", "een ", "van ", "voor ", "naar ", "met ", "zijn ", "worden ",
    "kunnen ", "wordt ", "door ", "dat ", "dit ", "ook ", "heeft ", "niet ",
    "maar ", "meer ", "om ", "als ", "bij ", "over ", "aan ", "uit ", "op ",
    "waardoor", "waarmee", "waarbij", "hierdoor", "hiermee"
]

def is_dutch(text):
    if not text or len(text) < 10:
        return False
    text_lower = text.lower()
    return sum(1 for w in NL_INDICATORS if w in text_lower) >= 2

# ── App-detectie ──────────────────────────────────────────────────────────
APP_LABELS = {
    "copilot": "Copilot", "teams": "Teams", "outlook": "Outlook",
    "excel": "Excel", "word": "Word", "powerpoint": "PowerPoint",
    "sharepoint": "SharePoint", "purview": "Purview",
    "viva": "Viva", "edge": "Edge", "onedrive": "OneDrive",
    "exchange": "Exchange", "forms": "Forms", "intune": "Intune",
    "entra": "Entra", "planner": "Planner", "other": "Overig"
}

def app_key(p):
    p = p.lower()
    for k in ["copilot","teams","outlook","excel","word","powerpoint","sharepoint",
              "purview","viva","edge","onedrive","exchange","forms","intune","entra","planner"]:
        if k in p: return k
    return "other"

def make_label(product, key):
    label = product.split(",")[0].strip().replace("Microsoft ", "").split("(")[0].strip()
    return label if label and len(label) <= 30 else APP_LABELS.get(key, "Overig")

# ── Actie-classificatie ───────────────────────────────────────────────────
ADMIN_PATTERNS = [
    r"admin", r"tenant", r"policy", r"governance", r"powershell",
    r"it pro", r"configure", r"admin center", r"compliance",
    r"default.*off", r"off by default", r"disabled by default",
    r"enable.*admin", r"admin.*enable", r"manage.*organization",
    r"global admin", r"permission"
]
USER_PATTERNS = [
    r"users? can", r"opt.in", r"choose.*setting",
    r"personal preference", r"user.*setting", r"turn.*off.*if",
    r"can be turned off", r"users will be able"
]

def classify_action(title, desc):
    text = (title + " " + desc).lower()
    for p in ADMIN_PATTERNS:
        if re.search(p, text): return "admin", "IT-beheerder actie vereist"
    for p in USER_PATTERNS:
        if re.search(p, text): return "user", "Gebruiker kan instellen"
    return "none", "Automatisch beschikbaar"

# ── Voordeel-omschrijvingen ───────────────────────────────────────────────
BENEFIT_TEMPLATES = {
    ("copilot",    "agent mode"):   "Medewerkers kunnen Copilot via een gesprek meerdere stappen achter elkaar laten uitvoeren — zonder elke stap zelf te hoeven aansturen.",
    ("copilot",    "search"):       "Medewerkers vinden informatie en collega's sneller doordat Copilot slimmer zoekt in bedrijfsdata.",
    ("copilot",    "memory"):       "Copilot onthoudt context over gesprekken heen, waardoor antwoorden persoonlijker en relevanter worden.",
    ("copilot",    "prompt"):       "Medewerkers werken efficiënter met toegang tot kant-en-klare prompts die aansluiten bij dagelijkse taken.",
    ("copilot",    "watermark"):    "Organisaties kunnen AI-gegenereerde inhoud herkennen en traceren, wat bijdraagt aan transparantie en naleving.",
    ("copilot",    "video"):        "Medewerkers maken snel professionele video's via Copilot — geen video-ervaring vereist.",
    ("copilot",    "image"):        "Afbeeldingen bewerken of aanmaken gaat sneller doordat Copilot dit rechtstreeks in de app ondersteunt.",
    ("copilot",    "email"):        "Medewerkers houden hun inbox sneller bij doordat Copilot de meest urgente e-mails automatisch naar voren brengt.",
    ("copilot",    "dashboard"):    "Beheerders en managers krijgen beter inzicht in hoe Copilot wordt gebruikt binnen de organisatie.",
    ("copilot",    "tuning"):       "Organisaties kunnen Copilot afstemmen op eigen processen en schrijfstijl, waardoor de AI direct bruikbare output levert.",
    ("teams",      "meeting"):      "Vergaderingen verlopen gestructureerder en medewerkers besteden minder tijd aan notuleren of terugzoeken.",
    ("teams",      "recap"):        "Medewerkers die een vergadering gemist hebben, lezen de samenvatting in plaats van de volledige opname terug te kijken.",
    ("teams",      "channel"):      "Teams-kanalen worden overzichtelijker en medewerkers vinden gesprekken en vergaderingen sneller terug.",
    ("teams",      "chat"):         "Communiceren in Teams gaat soepeler door verbeterde berichtopties en slimmere weergaven.",
    ("teams",      "room"):         "Vergaderzalen worden beter benut en medewerkers reserveren ruimtes eenvoudiger.",
    ("teams",      "phone"):        "Medewerkers met meerdere rollen of regio's zijn makkelijker bereikbaar via meerdere telefoonnummers.",
    ("teams",      "transcri"):     "Vergaderingen worden automatisch getranscribeerd, wat terugzoeken en naleving eenvoudiger maakt.",
    ("teams",      "skill"):        "Medewerkers vinden sneller de juiste collega voor een vraag of samenwerking dankzij zichtbare vaardigheidspagina's.",
    ("teams",      "notif"):        "Medewerkers houden zelf controle over welke meldingen ze ontvangen, wat afleiding vermindert.",
    ("teams",      "webinar"):      "Grote online evenementen zijn beter te organiseren en bij te wonen via Teams.",
    ("teams",      "external"):     "Samenwerken met externe partijen blijft veilig en controleerbaar voor de IT-afdeling.",
    ("teams",      "annotation"):   "Deelnemers kunnen direct op gedeelde inhoud reageren zonder dat de presentator het bureaublad hoeft te delen.",
    ("outlook",    "calendar"):     "Vergaderingen plannen gaat sneller doordat agenda's van collega's direct zichtbaar zijn.",
    ("outlook",    "copilot"):      "Medewerkers werken efficiënter in Outlook doordat Copilot e-mails en agenda's samenvat en acties voorstelt.",
    ("outlook",    "draft"):        "Medewerkers kunnen e-mails of vergaderverzoeken starten en later afmaken, zonder dat er iets per ongeluk verstuurd wordt.",
    ("outlook",    "rule"):         "E-mailbeheer wordt eenvoudiger door uitgebreidere regelopties in Outlook.",
    ("sharepoint", "template"):     "Nieuwe intranetpagina's aanmaken gaat sneller en ziet er meteen professioneel uit, zonder grafisch ontwerper.",
    ("sharepoint", "agent"):        "Medewerkers vinden intranetinformatie sneller via een Copilot-agent in SharePoint of Teams.",
    ("sharepoint", "news"):         "Organisatienieuws delen via het intranet gaat sneller en eenvoudiger.",
    ("sharepoint", "brand"):        "De huisstijl van het intranet is consistent en centraal beheerbaar door de IT-afdeling.",
    ("sharepoint", "governance"):   "Beheerders houden beter overzicht over toegang en beveiliging van SharePoint-inhoud.",
    ("purview",    "dlp"):          "Gevoelige informatie wordt automatisch beschermd, waardoor het risico op datalekken afneemt.",
    ("purview",    "insider"):      "De organisatie detecteert sneller risicovol gedrag rondom bedrijfsdata, zonder de privacy van medewerkers te schaden.",
    ("purview",    "label"):        "Gevoelige documenten worden automatisch geclassificeerd, waardoor naleving van databeleid eenvoudiger wordt.",
    ("purview",    "ediscovery"):   "Juridische onderzoeken verlopen sneller door beter overzicht over bewaard materiaal.",
    ("purview",    "risk"):         "Risicovol gedrag rondom bedrijfsdata wordt eerder gesignaleerd en centraal beheerd.",
    ("word",       "agent"):        "Documenten opstellen, samenvatten en verbeteren gaat sneller doordat Copilot direct in Word meewerkt.",
    ("excel",      "copilot"):      "Spreadsheetanalyses die vroeger uren kostten, zijn straks een kwestie van minuten.",
    ("powerpoint", "agent"):        "Presentaties aanpassen gaat sneller doordat Copilot opdrachten opvolgt terwijl de huisstijl behouden blijft.",
    ("powerpoint", "copilot"):      "Medewerkers maken sneller aansprekende presentaties, ook zonder uitgebreide presentatievaardigheden.",
    ("viva",       "insight"):      "Managers en medewerkers krijgen beter inzicht in werkpatronen, waardoor samenwerking en welzijn verbeteren.",
    ("viva",       "glint"):        "Medewerkersfeedback wordt sneller verzameld en geanalyseerd, zodat de organisatie gericht kan verbeteren.",
    ("viva",       "engage"):       "Medewerkers blijven beter verbonden met de organisatie via nieuws, communities en evenementen.",
    ("viva",       "copilot"):      "Managers en HR krijgen AI-inzichten over Copilot-adoptie en medewerkerservaringen.",
    ("edge",       "copilot"):      "Medewerkers krijgen Copilot-hulp direct in de browser, zonder van tabblad te wisselen.",
    ("edge",       "security"):     "Organisaties kunnen browsersessies beter beveiligen en gevoelige data beschermen tegen lekken.",
    ("onedrive",   "sync"):         "Bestanden synchroniseren betrouwbaarder en medewerkers zien sneller wat er mis gaat.",
    ("exchange",   "moderat"):      "E-mailgoedkeuring werkt nu ook op mobiel, waardoor moderatoren overal bereikbaar zijn.",
    ("forms",      "copilot"):      "Enquêtes en formulieren opstellen gaat sneller doordat Copilot inhoud en analyses automatisch genereert.",
    ("intune",     "compliance"):   "IT-beheerders kunnen apparaten beter en consistenter beveiligen via centrale beleidsregels.",
    ("entra",      "account"):      "Medewerkers die toegang kwijt zijn kunnen veiliger herstellen zonder IT-tussenkomst.",
    ("entra",      "app"):          "IT-beheerders kunnen apps sneller en veiliger beheren, inclusief tijdelijk blokkeren.",
    ("planner",    "task"):         "Taken en projecten zijn beter te overzien en bij te houden voor teams.",
}

GENERIC_BENEFIT = {
    "copilot":    "Medewerkers werken efficiënter doordat Copilot een nieuwe AI-functie krijgt die dagelijkse taken vereenvoudigt.",
    "teams":      "Samenwerken en communiceren via Teams wordt eenvoudiger of uitgebreider met deze update.",
    "outlook":    "E-mail en agendabeheer in Outlook wordt overzichtelijker en minder tijdrovend.",
    "sharepoint": "Het intranet in SharePoint wordt toegankelijker of makkelijker te beheren.",
    "purview":    "De beveiliging en naleving van bedrijfsdata wordt verbeterd met minder handmatig werk.",
    "word":       "Documenten maken en bewerken in Word gaat sneller en gemakkelijker.",
    "excel":      "Werken met data in Excel wordt slimmer en toegankelijker voor alle medewerkers.",
    "powerpoint": "Presentaties maken in PowerPoint gaat sneller, ook zonder uitgebreide vaardigheden.",
    "viva":       "Medewerkersbetrokkenheid en werkpatronen worden beter inzichtelijk via Viva.",
    "edge":       "Browsen wordt veiliger en productiever met nieuwe Edge-functies.",
    "onedrive":   "Bestanden opslaan en delen via OneDrive wordt betrouwbaarder en gebruiksvriendelijker.",
    "exchange":   "E-mailbeheer en -beveiliging wordt verbeterd voor de hele organisatie.",
    "forms":      "Enquêtes en formulieren zijn sneller te maken en te analyseren.",
    "intune":     "Apparaatbeheer en beveiliging worden eenvoudiger en consistenter voor IT-beheerders.",
    "entra":      "Identiteits- en toegangsbeheer wordt veiliger en makkelijker te beheren.",
    "planner":    "Taakoverzicht en samenwerking in projecten worden verbeterd.",
    "other":      "Deze update brengt een verbetering die medewerkers of beheerders direct ten goede komt.",
}

def generate_benefit(app, title, desc):
    text = (title + " " + desc).lower()
    for (a, keyword), benefit in BENEFIT_TEMPLATES.items():
        if a == app and keyword in text:
            return benefit
    return GENERIC_BENEFIT.get(app, GENERIC_BENEFIT["other"])

STATUS_NL = {
    "launched":  "Beschikbaar",
    "cancelled": "Geannuleerd",
    "unknown":   "Verwijderd uit roadmap",
}

# ── Cache laden ───────────────────────────────────────────────────────────
prev_items = {}
cache = {}

if os.path.exists("data.json"):
    try:
        with open("data.json", encoding="utf-8") as f:
            existing = json.load(f)
        loaded = skipped = 0
        for item in existing.get("items", []):
            item_id  = item["id"]
            modified = item.get("modified", "")
            prev_items[item_id] = item
            if is_dutch(item.get("title", "")):
                cache[(item_id, modified)] = {"title": item["title"], "desc": item.get("desc", "")}
                loaded += 1
            else:
                skipped += 1
        print(f"Cache geladen: {loaded} Nederlandse items, {skipped} overgeslagen")
    except Exception as e:
        print(f"Cache kon niet worden geladen: {e}")
else:
    print("Geen bestaande data.json — alles wordt vertaald")

# ── CSV inlezen ───────────────────────────────────────────────────────────
print("\nCSV inlezen...")
with open("roadmap.csv", encoding="utf-8-sig") as f:
    raw = f.read()

reader = csv.DictReader(io.StringIO(raw))
all_csv_rows = list(reader)

csv_status_by_id = {}
for row in all_csv_rows:
    fid = int(row.get("Feature ID", 0) or 0)
    if fid:
        csv_status_by_id[fid] = row.get("Status", "").strip()

active_rows = []
for row in all_csv_rows:
    status = row.get("Status", "").strip().lower()
    cloud  = row.get("Tags - Cloud instance", "")
    if status not in ("in development", "rolling out"):
        continue
    if "Worldwide (Standard Multi-Tenant)" not in cloud:
        continue
    active_rows.append(row)

active_ids = {int(r.get("Feature ID", 0) or 0) for r in active_rows}
print(f"{len(active_rows)} actieve items gevonden")

# ── Verwijderde items detecteren ──────────────────────────────────────────
removed = []
for item_id, prev_item in prev_items.items():
    if item_id not in active_ids:
        raw_status = csv_status_by_id.get(item_id, "unknown").lower()
        if "launch" in raw_status:
            new_status = "launched"
        elif "cancel" in raw_status:
            new_status = "cancelled"
        else:
            new_status = "unknown"
        removed.append({
            "id":        item_id,
            "title":     prev_item.get("title", ""),
            "app":       prev_item.get("app", "other"),
            "prodLabel": prev_item.get("prodLabel", ""),
            "status":    new_status,
            "statusNl":  STATUS_NL[new_status],
        })
        print(f"  → [{STATUS_NL[new_status]}] {prev_item.get('title','')[:70]}")

if not removed:
    print("Geen items verwijderd")

# ── Verwerken en vertalen ─────────────────────────────────────────────────
print(f"\nVerwerken en vertalen...")
items = []
cached_count = new_count = retrans_count = 0

for i, row in enumerate(active_rows):
    product  = row.get("Tags - Product", "")
    key      = app_key(product)
    title_en = row.get("Description", "").strip()
    desc_en  = row.get("Details", "").strip()
    item_id  = int(row.get("Feature ID", 0) or 0)
    modified = row.get("Last Modified", "").strip()
    cache_key = (item_id, modified)

    if cache_key in cache:
        nl_title = cache[cache_key]["title"]
        nl_desc  = cache[cache_key]["desc"]
        cached_count += 1
        print(f"  [{i+1}/{len(active_rows)}] ✓ {title_en[:65]}")
    else:
        if any(k[0] == item_id for k in cache):
            retrans_count += 1
            print(f"  [{i+1}/{len(active_rows)}] ↺ Hertalen: {title_en[:65]}")
        else:
            new_count += 1
            print(f"  [{i+1}/{len(active_rows)}] ↻ Nieuw:    {title_en[:65]}")
        nl_title = translate(title_en)
        nl_desc  = translate(desc_en[:800])
        time.sleep(0.3)

    action_key, action_label = classify_action(title_en, desc_en)
    benefit = generate_benefit(key, title_en, desc_en)

    items.append({
        "id":          item_id,
        "title":       nl_title,
        "desc":        nl_desc,
        "benefit":     benefit,
        "status":      "rolling" if "rolling" in row.get("Status", "").lower() else "dev",
        "app":         key,
        "prodLabel":   make_label(product, key),
        "added":       row.get("Added to Roadmap", "").strip(),
        "modified":    modified,
        "release":     row.get("Release", "").strip(),
        "preview":     row.get("Preview", "").strip(),
        "action":      action_key,
        "actionLabel": action_label,
    })

print(f"\nResultaat: {len(items)} actieve items")
print(f"  ✓ Uit cache:      {cached_count}")
print(f"  ↻ Nieuw vertaald: {new_count}")
print(f"  ↺ Hertaald:       {retrans_count}")
print(f"  ⚑ Verwijderd:     {len(removed)}")

today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

result = {
    "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "date":      today,
    "count":     len(items),
    "items":     items,
    "removed":   removed,
}

# ── data.json opslaan ─────────────────────────────────────────────────────
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\ndata.json opgeslagen ✓")

# ── Archief opslaan ───────────────────────────────────────────────────────
# Sla een kopie op in archive/YYYY-MM-DD.json
# Archief bevat alleen titels + metadata (geen volledige beschrijvingen) om ruimte te sparen
archive_dir = "archive"
os.makedirs(archive_dir, exist_ok=True)

archive_data = {
    "generated": result["generated"],
    "date":      today,
    "removed":   removed,   # Alleen verdwenen items (Launched of Cancelled)
}

if removed:
    archive_path = os.path.join(archive_dir, f"{today}.json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)
    print(f"Archief opgeslagen: {archive_path} ({len(removed)} verdwenen items) ✓")
else:
    print("Geen verdwenen items deze run — geen archiefbestand aangemaakt.")

# ── Archiefindex bijwerken ────────────────────────────────────────────────
# Maak een index van alle beschikbare archiefdatums voor de pagina
cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=92)).strftime("%Y-%m-%d")
# Verwijder archiefbestanden met lege removed[] (aangemaakt voor de nieuwe logica)
for fname in os.listdir(archive_dir):
    if fname.endswith(".json") and fname != "index.json":
        fpath = os.path.join(archive_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as _f:
                _d = json.load(_f)
            if not _d.get("removed"):
                os.remove(fpath)
                print(f"Leeg archiefbestand verwijderd: {fname}")
        except Exception:
            pass

archive_files = []
for fname in sorted(os.listdir(archive_dir), reverse=True):
    if fname.endswith(".json") and fname != "index.json":
        date_str = fname.replace(".json", "")
        if date_str >= cutoff:   # alleen laatste 3 maanden
            archive_files.append(date_str)

archive_index = {
    "updated": result["generated"],
    "dates":   archive_files,
}
with open(os.path.join(archive_dir, "index.json"), "w", encoding="utf-8") as f:
    json.dump(archive_index, f, ensure_ascii=False, indent=2)
print(f"Archiefindex bijgewerkt: {len(archive_files)} weken beschikbaar ✓")

# ── GitHub Actions Step Summary ──────────────────────────────────────────
summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if summary_path:
    with open(summary_path, "a", encoding="utf-8") as sf:
        sf.write("## 📊 Microsoft 365 Roadmap — Run samenvatting\n\n")
        sf.write(f"| | |\n|---|---|\n")
        sf.write(f"| 🗓️ Bijgewerkt | {result['generated']} |\n")
        sf.write(f"| 📋 Actieve items | {len(items)} |\n")
        sf.write(f"| 🆕 Nieuw vertaald | {sum(1 for i in items if not i.get('_cached', False))} |\n")
        sf.write(f"| 🚀 Verdwenen items | {len(removed)} |\n")
        sf.write(f"| 🗄️ Archiefweken | {len(archive_files)} |\n")
        if removed:
            sf.write("\n### Verdwenen items deze run\n\n")
            for r in removed:
                sf.write(f"- **{r['title']}** ({r['statusNl']})\n")
    print("GitHub Step Summary geschreven ✓")
