import csv, json, io, datetime, re

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
    r"tenant.*admin", r"global admin", r"permission"
]
USER_PATTERNS = [
    r"user.*can", r"users can", r"opt.in", r"choose.*setting",
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
# Per applicatie + thema een Nederlandse voordeelzin genereren.
BENEFIT_TEMPLATES = {
    # (app, trefwoord_in_titel_of_desc) → voordeel
    ("copilot", "agent mode"):       "Medewerkers kunnen Copilot via een gesprek meerdere stappen achter elkaar laten uitvoeren — zonder elke stap zelf te hoeven sturen.",
    ("copilot", "search"):           "Medewerkers vinden informatie en collega's sneller doordat Copilot slimmer zoekt in bedrijfsdata.",
    ("copilot", "memory"):           "Copilot onthoudt context over gesprekken heen, waardoor antwoorden persoonlijker en relevanter worden.",
    ("copilot", "prompt"):           "Medewerkers werken efficiënter doordat ze toegang krijgen tot kant-en-klare prompts die aansluiten bij dagelijkse taken.",
    ("copilot", "watermark"):        "Organisaties kunnen AI-gegenereerde inhoud herkennen en traceren, wat bijdraagt aan transparantie en naleving.",
    ("copilot", "video"):            "Medewerkers maken snel professionele video's via Copilot — geen videoervaring vereist.",
    ("copilot", "image"):            "Afbeeldingen bewerken of aanmaken gaat sneller doordat Copilot dit rechtstreeks in de app ondersteunt.",
    ("copilot", "email"):            "Medewerkers houden hun inbox sneller bij doordat Copilot de meest urgente e-mails automatisch naar voren brengt.",
    ("copilot", "dashboard"):        "Beheerders en managers krijgen beter inzicht in hoe Copilot wordt gebruikt binnen de organisatie.",
    ("teams",   "meeting"):          "Vergaderingen verlopen gestructureerder en medewerkers hoeven minder tijd te besteden aan notuleren of terugzoeken.",
    ("teams",   "recap"):            "Medewerkers die een vergadering gemist hebben, lezen de samenvatting in plaats van de volledige opname terug te kijken.",
    ("teams",   "channel"):          "Teams-kanalen worden overzichtelijker en medewerkers vinden gesprekken en vergaderingen sneller terug.",
    ("teams",   "chat"):             "Communiceren in Teams gaat soepeler door verbeterde berichtopties en slimmere weergaven.",
    ("teams",   "room"):             "Vergaderzalen worden beter benut en medewerkers reserveren ruimtes makkelijker.",
    ("teams",   "phone"):            "Medewerkers met meerdere rollen of regio's kunnen makkelijker bereikbaar zijn via meerdere nummers.",
    ("teams",   "transcri"):         "Vergaderingen worden automatisch getranscribeerd, wat terugzoeken en naleving eenvoudiger maakt.",
    ("teams",   "skill"):            "Medewerkers vinden sneller de juiste collega voor een vraag of samenwerking.",
    ("teams",   "notif"):            "Medewerkers houden zelf controle over welke meldingen ze ontvangen, wat afleiding vermindert.",
    ("teams",   "webinar"):          "Grote online evenementen zijn beter te organiseren en bij te wonen via Teams.",
    ("teams",   "external"):         "Samenwerken met externe partijen blijft veilig en controleerbaar voor de IT-afdeling.",
    ("outlook", "calendar"):         "Vergaderingen plannen gaat sneller doordat agenda's van collega's direct zichtbaar zijn.",
    ("outlook", "copilot"):          "Medewerkers werken efficiënter in Outlook doordat Copilot e-mails en agenda's samenvat en acties voorstelt.",
    ("outlook", "draft"):            "Medewerkers kunnen e-mails of vergaderverzoeken starten en later afmaken, zonder dat er iets per ongeluk verstuurd wordt.",
    ("outlook", "search"):           "Medewerkers vinden e-mails en regels sneller terug in Outlook.",
    ("outlook", "rule"):             "E-mailbeheer wordt eenvoudiger door uitgebreidere regelopties in Outlook.",
    ("sharepoint", "template"):      "Nieuwe intranetpagina's aanmaken gaat sneller en ziet er meteen professioneel uit, zonder grafisch ontwerper.",
    ("sharepoint", "agent"):         "Medewerkers vinden intranetinformatie sneller via een Copilot-agent in SharePoint of Teams.",
    ("sharepoint", "news"):          "Organisatienieuws delen via het intranet gaat sneller en makkelijker.",
    ("sharepoint", "brand"):         "De huisstijl van het intranet is consistent en centraal beheerbaar door de IT-afdeling.",
    ("sharepoint", "governance"):    "Beheerders houden beter overzicht over toegang en beveiliging van SharePoint-inhoud.",
    ("purview",  "dlp"):             "Gevoelige informatie wordt automatisch beschermd, waardoor het risico op datalekken afneemt.",
    ("purview",  "insider"):         "De organisatie detecteert sneller risicovol gedrag rondom bedrijfsdata, zonder de privacy van medewerkers te schaden.",
    ("purview",  "label"):           "Gevoelige documenten worden automatisch geclassificeerd, waardoor naleving van databeleid makkelijker wordt.",
    ("purview",  "ediscovery"):      "Juridische onderzoeken en compliancecontroles verlopen sneller door beter overzicht over bewaard materiaal.",
    ("purview",  "audit"):           "Beheerders zien sneller wat er met bedrijfsdata gebeurt, wat de naleving van regelgeving ondersteunt.",
    ("purview",  "risk"):            "Risicovol gedrag rondom bedrijfsdata wordt eerder gesignaleerd en centraal beheerd.",
    ("word",     "agent"):           "Documenten opstellen, samenvatten en verbeteren gaat sneller doordat Copilot direct in Word meewerkt.",
    ("word",     "copilot"):         "Medewerkers besteden minder tijd aan het schrijven en bewerken van documenten.",
    ("excel",    "copilot"):         "Spreadsheetanalyses die vroeger uren kostten, zijn straks een kwestie van minuten.",
    ("powerpoint","agent"):          "Presentaties aanpassen gaat sneller doordat Copilot opdrachten opvolgt terwijl de huisstijl bewaard blijft.",
    ("powerpoint","copilot"):        "Medewerkers maken sneller aansprekende presentaties zonder presentatieervaring.",
}

GENERIC_BENEFIT = {
    "copilot":    "Medewerkers werken efficiënter doordat Copilot een nieuwe AI-functie krijgt die dagelijkse taken vereenvoudigt.",
    "teams":      "Samenwerken en communiceren via Teams wordt eenvoudiger of uitgebreider met deze update.",
    "outlook":    "E-mail en agenda-beheer in Outlook wordt overzichtelijker en minder tijdrovend.",
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

# ── Eenvoudige vertaling van technisch jargon ──────────────────────────────
REPLACEMENTS = [
    (r"\brollout\b",         "uitrol"),
    (r"\btenant\b",          "organisatie"),
    (r"\badmin center\b",    "beheercentrum"),
    (r"\bend.?users?\b",     "medewerkers"),
    (r"\bIT admins?\b",      "IT-beheerders"),
    (r"\bpolicies\b",        "beleidsregels"),
    (r"\bcompliance\b",      "naleving"),
    (r"\bworkflow\b",        "werkproces"),
    (r"\bpermissions?\b",    "rechten"),
    (r"\bfeature\b",         "functie"),
    (r"\blicense[ds]?\b",    "licentie"),
    (r"\bSharePoint site\b", "SharePoint-pagina"),
]

def simplify(text):
    for pattern, replacement in REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

# ── Hoofdscript ────────────────────────────────────────────────────────────
with open("roadmap.csv", encoding="utf-8-sig") as f:
    raw = f.read()

reader = csv.DictReader(io.StringIO(raw))
items = []

for row in reader:
    status = row.get("Status", "").strip().lower()
    cloud  = row.get("Tags - Cloud instance", "")

    if status not in ("in development", "rolling out"):
        continue
    if "Worldwide (Standard Multi-Tenant)" not in cloud:
        continue

    product = row.get("Tags - Product", "")
    key     = app_key(product)
    title   = row.get("Description", "").strip()
    desc    = row.get("Details", "").strip()

    action_key, action_label = classify_action(title, desc)
    benefit = generate_benefit(key, title, desc)

    # Beschrijving beperken tot 400 tekens en jargon verminderen
    short_desc = simplify(desc[:400] + ("…" if len(desc) > 400 else ""))

    items.append({
        "id":          int(row.get("Feature ID", 0) or 0),
        "title":       title,
        "desc":        short_desc,
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

result = {
    "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "count":     len(items),
    "items":     items
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Klaar: {len(items)} items opgeslagen in data.json")
