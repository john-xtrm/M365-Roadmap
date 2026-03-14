import csv, json, io, datetime, re, time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="nl")

def translate(text, retries=3):
    """Vertaal tekst naar Nederlands, met automatische herpoging bij fouten."""
    if not text or not text.strip():
        return text
    for attempt in range(retries):
        try:
            # Google Translate heeft een limiet van ~5000 tekens per aanroep
            if len(text) > 4800:
                text = text[:4800] + "…"
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  Vertaling mislukt, origineel behouden: {e}")
                return text

# ── App-detectie ───────────────────────────────────────────────────────────
APP_LABELS = {
    "copilot": "Copilot", "teams": "Teams", "outlook": "Outlook",
    "excel": "Excel", "word": "Word", "powerpoint": "PowerPoint",
    "sharepoint": "SharePoint", "purview": "Purview", "other": "Overig"
}

def app_key(p):
    p = p.lower()
    for k in ["copilot","teams","outlook","excel","word","powerpoint","sharepoint","purview"]:
        if k in p: return k
    return "other"

def make_label(product, key):
    label = product.split(",")[0].strip().replace("Microsoft ", "").split("(")[0].strip()
    return label if label and len(label) <= 30 else APP_LABELS.get(key, "Overig")

# ── Actie-classificatie ────────────────────────────────────────────────────
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
        if re.search(p, text): return "user",  "Gebruiker kan instellen"
    return "none", "Automatisch beschikbaar"

# ── Voordeel-omschrijving ──────────────────────────────────────────────────
BENEFIT_TEMPLATES = {
    ("copilot", "agent mode"):    "Medewerkers kunnen Copilot via een gesprek meerdere stappen achter elkaar laten uitvoeren — zonder elke stap zelf te hoeven aansturen.",
    ("copilot", "search"):        "Medewerkers vinden informatie en collega's sneller doordat Copilot slimmer zoekt in bedrijfsdata.",
    ("copilot", "memory"):        "Copilot onthoudt context over gesprekken heen, waardoor antwoorden persoonlijker en relevanter worden.",
    ("copilot", "prompt"):        "Medewerkers werken efficiënter met toegang tot kant-en-klare prompts die aansluiten bij dagelijkse taken.",
    ("copilot", "watermark"):     "Organisaties kunnen AI-gegenereerde inhoud herkennen en traceren, wat bijdraagt aan transparantie en naleving.",
    ("copilot", "video"):         "Medewerkers maken snel professionele video's via Copilot — geen video-ervaring vereist.",
    ("copilot", "image"):         "Afbeeldingen bewerken of aanmaken gaat sneller doordat Copilot dit rechtstreeks in de app ondersteunt.",
    ("copilot", "email"):         "Medewerkers houden hun inbox sneller bij doordat Copilot de meest urgente e-mails automatisch naar voren brengt.",
    ("copilot", "dashboard"):     "Beheerders en managers krijgen beter inzicht in hoe Copilot wordt gebruikt binnen de organisatie.",
    ("copilot", "tuning"):        "Organisaties kunnen Copilot afstemmen op eigen processen en schrijfstijl, waardoor de AI direct bruikbare output levert.",
    ("teams",   "meeting"):       "Vergaderingen verlopen gestructureerder en medewerkers besteden minder tijd aan notuleren of terugzoeken.",
    ("teams",   "recap"):         "Medewerkers die een vergadering gemist hebben, lezen de samenvatting in plaats van de volledige opname terug te kijken.",
    ("teams",   "channel"):       "Teams-kanalen worden overzichtelijker en medewerkers vinden gesprekken en vergaderingen sneller terug.",
    ("teams",   "chat"):          "Communiceren in Teams gaat soepeler door verbeterde berichtopties en slimmere weergaven.",
    ("teams",   "room"):          "Vergaderzalen worden beter benut en medewerkers reserveren ruimtes eenvoudiger.",
    ("teams",   "phone"):         "Medewerkers met meerdere rollen of regio's zijn makkelijker bereikbaar via meerdere telefoonnummers.",
    ("teams",   "transcri"):      "Vergaderingen worden automatisch getranscribeerd, wat terugzoeken en naleving eenvoudiger maakt.",
    ("teams",   "skill"):         "Medewerkers vinden sneller de juiste collega voor een vraag of samenwerking dankzij zichtbare vaardigheidspagina's.",
    ("teams",   "notif"):         "Medewerkers houden zelf controle over welke meldingen ze ontvangen, wat afleiding vermindert.",
    ("teams",   "webinar"):       "Grote online evenementen zijn beter te organiseren en bij te wonen via Teams.",
    ("teams",   "external"):      "Samenwerken met externe partijen blijft veilig en controleerbaar voor de IT-afdeling.",
    ("teams",   "annotation"):    "Deelnemers kunnen direct op gedeelde inhoud reageren zonder dat de presentator het bureaublad hoeft te delen.",
    ("outlook", "calendar"):      "Vergaderingen plannen gaat sneller doordat agenda's van collega's direct zichtbaar zijn.",
    ("outlook", "copilot"):       "Medewerkers werken efficiënter in Outlook doordat Copilot e-mails en agenda's samenvat en acties voorstelt.",
    ("outlook", "draft"):         "Medewerkers kunnen e-mails of vergaderverzoeken starten en later afmaken, zonder dat er iets per ongeluk verstuurd wordt.",
    ("outlook", "rule"):          "E-mailbeheer wordt eenvoudiger door uitgebreidere regelopties in Outlook.",
    ("sharepoint", "template"):   "Nieuwe intranetpagina's aanmaken gaat sneller en ziet er meteen professioneel uit, zonder grafisch ontwerper.",
    ("sharepoint", "agent"):      "Medewerkers vinden intranetinformatie sneller via een Copilot-agent in SharePoint of Teams.",
    ("sharepoint", "news"):       "Organisatienieuws delen via het intranet gaat sneller en eenvoudiger.",
    ("sharepoint", "brand"):      "De huisstijl van het intranet is consistent en centraal beheerbaar door de IT-afdeling.",
    ("sharepoint", "governance"): "Beheerders houden beter overzicht over toegang en beveiliging van SharePoint-inhoud.",
    ("purview",  "dlp"):          "Gevoelige informatie wordt automatisch beschermd, waardoor het risico op datalekken afneemt.",
    ("purview",  "insider"):      "De organisatie detecteert sneller risicovol gedrag rondom bedrijfsdata, zonder de privacy van medewerkers te schaden.",
    ("purview",  "label"):        "Gevoelige documenten worden automatisch geclassificeerd, waardoor naleving van databeleid eenvoudiger wordt.",
    ("purview",  "ediscovery"):   "Juridische onderzoeken verlopen sneller door beter overzicht over bewaard materiaal.",
    ("purview",  "risk"):         "Risicovol gedrag rondom bedrijfsdata wordt eerder gesignaleerd en centraal beheerd.",
    ("word",     "agent"):        "Documenten opstellen, samenvatten en verbeteren gaat sneller doordat Copilot direct in Word meewerkt.",
    ("excel",    "copilot"):      "Spreadsheetanalyses die vroeger uren kostten, zijn straks een kwestie van minuten.",
    ("powerpoint","agent"):       "Presentaties aanpassen gaat sneller doordat Copilot opdrachten opvolgt terwijl de huisstijl behouden blijft.",
    ("powerpoint","copilot"):     "Medewerkers maken sneller aansprekende presentaties, ook zonder uitgebreide presentatievaardigheden.",
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
    "other":      "Deze update brengt een verbetering die medewerkers of beheerders direct ten goede komt.",
}

def generate_benefit(app, title, desc):
    text = (title + " " + desc).lower()
    for (a, keyword), benefit in BENEFIT_TEMPLATES.items():
        if a == app and keyword in text:
            return benefit
    return GENERIC_BENEFIT.get(app, GENERIC_BENEFIT["other"])

# ── Hoofdscript ────────────────────────────────────────────────────────────
print("CSV inlezen...")
with open("roadmap.csv", encoding="utf-8-sig") as f:
    raw = f.read()

reader = csv.DictReader(io.StringIO(raw))
rows = []
for row in reader:
    status = row.get("Status", "").strip().lower()
    cloud  = row.get("Tags - Cloud instance", "")
    if status not in ("in development", "rolling out"):
        continue
    if "Worldwide (Standard Multi-Tenant)" not in cloud:
        continue
    rows.append(row)

print(f"{len(rows)} items gevonden, vertaling starten...")

items = []
for i, row in enumerate(rows):
    product = row.get("Tags - Product", "")
    key     = app_key(product)
    title   = row.get("Description", "").strip()
    desc    = row.get("Details", "").strip()

    # Vertaal titel en beschrijving naar Nederlands
    print(f"  [{i+1}/{len(rows)}] Vertalen: {title[:60]}...")
    nl_title = translate(title)
    nl_desc  = translate(desc[:800])   # max 800 tekens voor de beschrijving

    action_key, action_label = classify_action(title, desc)
    benefit = generate_benefit(key, title, desc)

    items.append({
        "id":          int(row.get("Feature ID", 0) or 0),
        "title":       nl_title,
        "desc":        nl_desc,
        "benefit":     benefit,
        "status":      "rolling" if "rolling" in status else "dev",
        "app":         key,
        "prodLabel":   make_label(product, key),
        "added":       row.get("Added to Roadmap", "").strip(),
        "modified":    row.get("Last Modified", "").strip(),
        "release":     row.get("Release", "").strip(),
        "preview":     row.get("Preview", "").strip(),
        "action":      action_key,
        "actionLabel": action_label,
    })

    # Kleine pauze om rate limiting te voorkomen
    time.sleep(0.3)

result = {
    "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "count":     len(items),
    "items":     items
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nKlaar: {len(items)} items opgeslagen in data.json")
