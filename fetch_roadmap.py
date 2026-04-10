"""
Microsoft 365 Roadmap - fetch & verwerk
- Laadt bestaande vertalingen uit data.json als cache
- Controleert of gecachede items daadwerkelijk Nederlands zijn
- Vertaalt ALLEEN items die nieuw, gewijzigd, of nog niet correct vertaald zijn
- Genereert organisatie-impacttekst (benefit) via GitHub Models (gpt-4o-mini)
- Valt terug op Google Translate + keyword-templates als GITHUB_TOKEN niet beschikbaar is
- Slaat items op die deze week Launched of Cancelled zijn geworden
- Slaat een archief op in archive/YYYY-MM-DD.json (max 3 maanden bewaard)
"""

import csv, json, io, datetime, re, time, os, urllib.request, urllib.error
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="nl")

# -- GitHub Models API --------------------------------------------------------
# Gebruikt het automatisch beschikbare GITHUB_TOKEN in GitHub Actions.
# Gratis: 15 requests/min, 150 requests/dag voor gpt-4o-mini.
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
GH_MODELS_URL   = "https://models.github.ai/inference/chat/completions"
GH_MODEL        = "openai/gpt-4o-mini"

AI_MIN_INTERVAL     = 6.0   # seconden tussen aanroepen (max 10/min, ruim onder 15/min)
_last_ai_call       = 0.0
_ai_quota_exhausted = False  # True na eerste 429 => rest van run via fallback

def _ai_rate_limit_wait():
    global _last_ai_call
    elapsed = time.time() - _last_ai_call
    if elapsed < AI_MIN_INTERVAL:
        time.sleep(AI_MIN_INTERVAL - elapsed)
    _last_ai_call = time.time()

def ai_process_item(title_en, desc_en):
    """Vertaalt title+desc naar NL en genereert benefit via GitHub Models.
    Bij 429 schakelt de hele run direct over op Google Translate."""
    global _ai_quota_exhausted
    if not GITHUB_TOKEN or _ai_quota_exhausted:
        return None

    lines = [
        "Je verwerkt een Microsoft 365 roadmap-item voor een Nederlands zakelijk dashboard.",
        "",
        "Voer twee taken uit op basis van de onderstaande Engelse tekst:",
        "",
        "1. VERTALING: Vertaal de titel en beschrijving nauwkeurig naar het Nederlands.",
        "   - Behoud technische termen zoals tenant, admin center, DLP, rollout,",
        "     policy, compliance, PowerShell - vertaal deze NIET",
        "   - Vertaal alleen wat er staat, voeg niets toe en laat niets weg",
        "   - Schrijf lopende, professionele zinnen",
        "",
        "2. ORGANISATIE-IMPACT: Schrijf maximaal 2 korte Nederlandse zinnen die concreet",
        "   uitleggen wat deze update betekent voor de organisatie.",
        "   - Beantwoord: wie merkt dit, en wat gaat er concreet beter of makkelijker?",
        "   - Geen IT-jargon, gewone taal voor niet-technische medewerkers",
        "   - Strikt gebaseerd op de aangeleverde tekst, niets verzinnen of toevoegen",
        "   - Begin NIET met: Met deze update / Microsoft introduceert / Deze functie",
        "   - Schrijf vanuit de medewerker of organisatie, niet vanuit Microsoft",
        "",
        'Geef je antwoord UITSLUITEND als geldig JSON: {"title_nl": "...", "desc_nl": "...", "benefit": "..."}',
        "",
        "Engelse titel: " + title_en,
        "Engelse beschrijving: " + desc_en[:800],
    ]
    prompt = "\n".join(lines)

    payload = json.dumps({
        "model": GH_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.2
    }).encode("utf-8")

    _ai_rate_limit_wait()
    try:
        req = urllib.request.Request(
            GH_MODELS_URL,
            data=payload,
            headers={
                "Content-Type":  "application/json",
                "Authorization": "Bearer " + GITHUB_TOKEN,
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result  = json.loads(resp.read().decode("utf-8"))
            text    = result["choices"][0]["message"]["content"].strip()
            text    = re.sub(r"^```[a-z]*\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            parsed  = json.loads(text)
            if all(k in parsed for k in ("title_nl", "desc_nl", "benefit")):
                return parsed
            print("    Onvolledig AI-antwoord -- fallback")
            return None
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("    AI quota bereikt (429) -- rest van de run via Google Translate")
            _ai_quota_exhausted = True
            return None
        try:
            body = e.read().decode("utf-8")[:150]
        except Exception:
            body = ""
        print("    AI HTTP " + str(e.code) + " -- fallback: " + body)
        return None
    except Exception as e:
        print("    AI fout -- fallback: " + str(e))
        return None

# -- Google Translate fallback -------------------------------------------------
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
                print("    Vertaling mislukt, origineel behouden: " + str(e))
                return text

# -- Nederlandse taaldetectie --------------------------------------------------
NL_INDICATORS = [
    "de ", "het ", "een ", "van ", "voor ", "naar ", "met ", "zijn ", "worden ",
    "kunnen ", "wordt ", "door ", "dat ", "dit ", "ook ", "heeft ", "niet ",
    "maar ", "meer ", "om ", "als ", "bij ", "over ", "aan ", "uit ", "op ",
    "in ", "en ", "te ", "is ",
    "waardoor", "waarmee", "waarbij", "hierdoor", "hiermee"
]

def is_dutch(text):
    if not text or len(text) < 10:
        return False
    text_lower  = text.lower()
    threshold   = 1 if len(text) < 80 else 2
    return sum(1 for w in NL_INDICATORS if w in text_lower) >= threshold

# -- App-detectie --------------------------------------------------------------
APP_LABELS = {
    "copilot":    "Copilot",    "teams":      "Teams",
    "outlook":    "Outlook",    "excel":      "Excel",
    "word":       "Word",       "powerpoint": "PowerPoint",
    "sharepoint": "SharePoint", "purview":    "Purview",
    "viva":       "Viva",       "edge":       "Edge",
    "onedrive":   "OneDrive",   "exchange":   "Exchange",
    "forms":      "Forms",      "intune":     "Intune",
    "entra":      "Entra",      "planner":    "Planner",
    "loop":       "Loop",       "whiteboard": "Whiteboard",
    "todo":       "To Do",      "bookings":   "Bookings",
    "stream":     "Stream",     "automate":   "Power Automate",
    "powerapps":  "Power Apps", "powerbi":    "Power BI",
    "yammer":     "Yammer",     "defender":   "Defender",
    "search":     "Microsoft Search",
    "project":    "Project",    "visio":      "Visio",
    "windows":    "Windows",    "other":      "Overig",
}

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

def app_key(p):
    p = p.lower()
    if "power automate" in p: return "automate"
    if "power apps"     in p: return "powerapps"
    if "power bi"       in p: return "powerbi"
    if "microsoft search" in p: return "search"
    if "to do"          in p: return "todo"
    for k in [
        "copilot", "teams", "outlook", "excel", "word", "powerpoint",
        "sharepoint", "purview", "viva", "edge", "onedrive", "exchange",
        "forms", "intune", "entra", "planner", "loop", "whiteboard",
        "bookings", "stream", "yammer", "defender", "project", "visio",
        "windows",
    ]:
        if k in p:
            return k
    return "other"

def app_key_from_title(title):
    if ":" in title:
        return app_key(title.split(":", 1)[0].strip())
    return app_key(title)

def extra_tags(product_field, primary_key):
    seen = {primary_key}
    tags = []
    for part in product_field.replace(";", ",").split(","):
        k = app_key(part.strip())
        if k and k != "other" and k not in seen:
            seen.add(k)
            tags.append(k)
    return tags

def make_label(product, key):
    label = product.split(",")[0].strip().replace("Microsoft ", "").split("(")[0].strip()
    return label if label and len(label) <= 30 else APP_LABELS.get(key, "Overig")

# -- Actie-classificatie -------------------------------------------------------
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
        if re.search(p, text): return "user", "Medewerker kan instellen"
    return "none", "Automatisch beschikbaar"

# -- Benefit-templates (fallback zonder AI) ------------------------------------
BENEFIT_TEMPLATES = {
    ("copilot",    "agent mode"):   "Medewerkers kunnen Copilot via een gesprek meerdere stappen achter elkaar laten uitvoeren zonder elke stap zelf te hoeven aansturen.",
    ("copilot",    "search"):       "Medewerkers vinden informatie en collega's sneller doordat Copilot slimmer zoekt in bedrijfsdata.",
    ("copilot",    "memory"):       "Copilot onthoudt context over gesprekken heen, waardoor antwoorden persoonlijker en relevanter worden.",
    ("copilot",    "prompt"):       "Medewerkers werken efficienter met toegang tot kant-en-klare prompts die aansluiten bij dagelijkse taken.",
    ("copilot",    "watermark"):    "Organisaties kunnen AI-gegenereerde inhoud herkennen en traceren, wat bijdraagt aan transparantie en naleving.",
    ("copilot",    "video"):        "Medewerkers maken snel professionele videos via Copilot zonder video-ervaring.",
    ("copilot",    "image"):        "Afbeeldingen bewerken of aanmaken gaat sneller doordat Copilot dit rechtstreeks in de app ondersteunt.",
    ("copilot",    "email"):        "Medewerkers houden hun inbox sneller bij doordat Copilot de meest urgente e-mails automatisch naar voren brengt.",
    ("copilot",    "dashboard"):    "Beheerders en managers krijgen beter inzicht in hoe Copilot wordt gebruikt binnen de organisatie.",
    ("copilot",    "tuning"):       "Organisaties kunnen Copilot afstemmen op eigen processen en schrijfstijl.",
    ("teams",      "meeting"):      "Vergaderingen verlopen gestructureerder en medewerkers besteden minder tijd aan notuleren of terugzoeken.",
    ("teams",      "recap"):        "Medewerkers die een vergadering gemist hebben lezen de samenvatting in plaats van de volledige opname terug te kijken.",
    ("teams",      "channel"):      "Teams-kanalen worden overzichtelijker en medewerkers vinden gesprekken sneller terug.",
    ("teams",      "chat"):         "Communiceren in Teams gaat soepeler door verbeterde berichtopties.",
    ("teams",      "room"):         "Vergaderzalen worden beter benut en medewerkers reserveren ruimtes eenvoudiger.",
    ("teams",      "phone"):        "Medewerkers met meerdere rollen zijn makkelijker bereikbaar via meerdere telefoonnummers.",
    ("teams",      "transcri"):     "Vergaderingen worden automatisch getranscribeerd, wat terugzoeken eenvoudiger maakt.",
    ("teams",      "skill"):        "Medewerkers vinden sneller de juiste collega voor een vraag dankzij zichtbare vaardigheidspaginas.",
    ("teams",      "notif"):        "Medewerkers houden zelf controle over welke meldingen ze ontvangen.",
    ("teams",      "webinar"):      "Grote online evenementen zijn beter te organiseren via Teams.",
    ("teams",      "external"):     "Samenwerken met externe partijen blijft veilig en controleerbaar.",
    ("teams",      "annotation"):   "Deelnemers kunnen direct op gedeelde inhoud reageren zonder dat het bureaublad gedeeld hoeft te worden.",
    ("outlook",    "calendar"):     "Vergaderingen plannen gaat sneller doordat agendas van collega's direct zichtbaar zijn.",
    ("outlook",    "copilot"):      "Medewerkers werken efficienter in Outlook doordat AI e-mails samenvat en acties voorstelt.",
    ("outlook",    "draft"):        "Medewerkers kunnen e-mails starten en later afmaken zonder dat er iets per ongeluk verstuurd wordt.",
    ("outlook",    "rule"):         "E-mailbeheer wordt eenvoudiger door uitgebreidere regelopties in Outlook.",
    ("sharepoint", "template"):     "Nieuwe intranetpaginas aanmaken gaat sneller en ziet er meteen professioneel uit.",
    ("sharepoint", "agent"):        "Medewerkers vinden intranetinformatie sneller via een AI-agent in SharePoint of Teams.",
    ("sharepoint", "news"):         "Organisatienieuws delen via het intranet gaat sneller en eenvoudiger.",
    ("sharepoint", "brand"):        "De huisstijl van het intranet is consistent en centraal beheerbaar.",
    ("sharepoint", "governance"):   "Beheerders houden beter overzicht over toegang en beveiliging van SharePoint-inhoud.",
    ("purview",    "dlp"):          "Gevoelige informatie wordt automatisch beschermd, waardoor het risico op datalekken afneemt.",
    ("purview",    "insider"):      "De organisatie detecteert sneller risicovol gedrag rondom bedrijfsdata.",
    ("purview",    "label"):        "Gevoelige documenten worden automatisch geclassificeerd.",
    ("purview",    "ediscovery"):   "Juridische onderzoeken verlopen sneller door beter overzicht over bewaard materiaal.",
    ("purview",    "risk"):         "Risicovol gedrag rondom bedrijfsdata wordt eerder gesignaleerd.",
    ("word",       "agent"):        "Documenten opstellen en verbeteren gaat sneller doordat AI direct in Word meewerkt.",
    ("excel",      "copilot"):      "Spreadsheetanalyses die vroeger uren kostten zijn straks een kwestie van minuten.",
    ("powerpoint", "agent"):        "Presentaties aanpassen gaat sneller doordat AI opdrachten opvolgt.",
    ("powerpoint", "copilot"):      "Medewerkers maken sneller aansprekende presentaties.",
    ("viva",       "insight"):      "Managers krijgen beter inzicht in werkpatronen, waardoor samenwerking verbetert.",
    ("viva",       "glint"):        "Medewerkersfeedback wordt sneller verzameld en geanalyseerd.",
    ("viva",       "engage"):       "Medewerkers blijven beter verbonden via nieuws en communities.",
    ("viva",       "copilot"):      "Managers en HR krijgen AI-inzichten over adoptie en medewerkerservaringen.",
    ("edge",       "copilot"):      "Medewerkers krijgen AI-hulp direct in de browser.",
    ("edge",       "security"):     "Organisaties kunnen browsersessies beter beveiligen.",
    ("onedrive",   "sync"):         "Bestanden synchroniseren betrouwbaarder.",
    ("exchange",   "moderat"):      "E-mailgoedkeuring werkt nu ook op mobiel.",
    ("forms",      "copilot"):      "Enquetes en formulieren opstellen gaat sneller doordat AI inhoud genereert.",
    ("intune",     "compliance"):   "IT-beheerders kunnen apparaten beter beveiligen via centrale beleidsregels.",
    ("entra",      "account"):      "Medewerkers die toegang kwijt zijn kunnen veiliger herstellen.",
    ("entra",      "app"):          "IT-beheerders kunnen apps sneller en veiliger beheren.",
    ("planner",    "task"):         "Taken en projecten zijn beter te overzien voor teams.",
    ("loop",       "workspace"):    "Teams werken efficienter samen doordat content op een plek wordt bijgehouden.",
    ("loop",       "component"):    "Gedeelde Loop-componenten zorgen dat iedereen altijd de actuele versie ziet.",
    ("whiteboard", "copilot"):      "Brainstormsessies worden productiever doordat AI ideeen samenvat.",
    ("whiteboard", "template"):     "Teams starten sneller met een brainstorm via kant-en-klare sjablonen.",
    ("todo",       "task"):         "Medewerkers houden hun takenlijst overzichtelijk op alle apparaten.",
    ("todo",       "planner"):      "Taken uit Planner en To Do zijn op een plek zichtbaar.",
    ("bookings",   "appointment"):  "Klanten kunnen zelfstandig een afspraak inplannen.",
    ("bookings",   "virtual"):      "Online afspraken zijn eenvoudiger te plannen via Bookings en Teams.",
    ("stream",     "video"):        "Interne videos zijn eenvoudiger te vinden en te delen.",
    ("stream",     "transcript"):   "Video-opnames worden automatisch voorzien van een doorzoekbare transcriptie.",
    ("automate",   "flow"):         "Herhalende processen worden geautomatiseerd.",
    ("automate",   "copilot"):      "Medewerkers bouwen sneller automatiseringen doordat AI helpt.",
    ("powerapps",  "canvas"):       "Teams bouwen zakelijke apps zonder uitgebreide programmeerkennis.",
    ("powerapps",  "copilot"):      "Apps bouwen gaat sneller doordat AI schermen en logica genereert.",
    ("powerbi",    "report"):       "Rapporten worden sneller gemaakt en gedeeld.",
    ("powerbi",    "copilot"):      "Medewerkers krijgen direct antwoord op datavragen in gewone taal.",
    ("yammer",     "community"):    "Medewerkers vinden sneller de juiste community voor kennisdeling.",
    ("yammer",     "leadership"):   "Leiderschapscommunicatie bereikt medewerkers breder.",
    ("defender",   "threat"):       "Beveiligingsteams detecteren sneller cyberdreigingen.",
    ("defender",   "endpoint"):     "Endpoints worden beter beschermd via uitgebreidere beleidsopties.",
    ("search",     "result"):       "Medewerkers vinden informatie sneller via verbeterde zoekresultaten.",
    ("search",     "bookmark"):     "Veelgebruikte resources zijn sneller te vinden via beheerde bladwijzers.",
    ("project",    "task"):         "Projectplanning verloopt overzichtelijker voor projectmanagers.",
    ("project",    "copilot"):      "Projectplanningen worden sneller opgesteld doordat AI taken genereert.",
    ("visio",      "diagram"):      "Procesdiagrammen zijn eenvoudiger te maken en te delen.",
    ("visio",      "template"):     "Teams starten sneller met een professioneel diagram.",
    ("windows",    "update"):       "Windows-updates verbeteren prestaties of beveiliging.",
    ("windows",    "copilot"):      "Medewerkers krijgen AI-hulp direct in Windows.",
}

GENERIC_BENEFIT = {
    "copilot":    "Medewerkers werken efficienter doordat Copilot een nieuwe AI-functie krijgt die dagelijkse taken vereenvoudigt.",
    "teams":      "Samenwerken en communiceren via Teams wordt eenvoudiger met deze update.",
    "outlook":    "E-mail en agendabeheer in Outlook wordt overzichtelijker en minder tijdrovend.",
    "sharepoint": "Het intranet in SharePoint wordt toegankelijker of makkelijker te beheren.",
    "purview":    "De beveiliging en naleving van bedrijfsdata wordt verbeterd.",
    "word":       "Documenten maken en bewerken in Word gaat sneller.",
    "excel":      "Werken met data in Excel wordt slimmer en toegankelijker.",
    "powerpoint": "Presentaties maken in PowerPoint gaat sneller.",
    "viva":       "Medewerkersbetrokkenheid en werkpatronen worden beter inzichtelijk via Viva.",
    "edge":       "Browsen wordt veiliger en productiever.",
    "onedrive":   "Bestanden opslaan en delen via OneDrive wordt betrouwbaarder.",
    "exchange":   "E-mailbeheer en -beveiliging wordt verbeterd.",
    "forms":      "Enquetes en formulieren zijn sneller te maken en te analyseren.",
    "intune":     "Apparaatbeheer en beveiliging worden eenvoudiger voor IT-beheerders.",
    "entra":      "Identiteits- en toegangsbeheer wordt veiliger.",
    "planner":    "Taakoverzicht en samenwerking in projecten worden verbeterd.",
    "loop":       "Teams werken efficienter samen via gedeelde werkruimten in Loop.",
    "whiteboard": "Creatieve samenwerking wordt eenvoudiger via Whiteboard.",
    "todo":       "Medewerkers beheren hun dagelijkse taken overzichtelijker.",
    "bookings":   "Klanten kunnen eenvoudiger zelfstandig afspraken inplannen.",
    "stream":     "Videos delen en bekijken wordt eenvoudiger via Stream.",
    "automate":   "Repetitieve processen worden geautomatiseerd.",
    "powerapps":  "Teams bouwen eenvoudig zakelijke apps.",
    "powerbi":    "Organisaties krijgen beter inzicht in data via Power BI.",
    "yammer":     "Medewerkers blijven beter verbonden via Yammer.",
    "defender":   "De organisatie is beter beschermd tegen cyberdreigingen.",
    "search":     "Medewerkers vinden informatie sneller via Microsoft Search.",
    "project":    "Projectplanning wordt overzichtelijker via Microsoft Project.",
    "visio":      "Procesdiagrammen zijn eenvoudiger te maken via Visio.",
    "windows":    "Windows-updates verbeteren prestaties of beveiliging.",
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

# -- Cache laden ---------------------------------------------------------------
prev_items = {}
cache = {}

if os.path.exists("data.json"):
    try:
        with open("data.json", encoding="utf-8") as f:
            existing = json.load(f)
        loaded = needs_retrans = 0
        for item in existing.get("items", []):
            item_id  = item["id"]
            modified = item.get("modified", "")
            prev_items[item_id] = item
            dutch = is_dutch(item.get("title", ""))
            cache[(item_id, modified)] = {
                "title":       item["title"],
                "desc":        item.get("desc", ""),
                "benefit":     item.get("benefit", ""),
                "retranslate": not dutch,
            }
            if dutch:
                loaded += 1
            else:
                needs_retrans += 1
        print("Cache geladen: " + str(loaded) + " Nederlandse items, " + str(needs_retrans) + " gemarkeerd voor hervertaling")
    except Exception as e:
        print("Cache kon niet worden geladen: " + str(e))
else:
    print("Geen bestaande data.json -- alles wordt verwerkt")

if GITHUB_TOKEN:
    print("AI vertaling: actief -- GitHub Models (gpt-4o-mini)")
else:
    print("AI vertaling: niet geconfigureerd -- Google Translate + templates als fallback")

# -- CSV inlezen ---------------------------------------------------------------
print("\nCSV inlezen...")
with open("roadmap.csv", encoding="utf-8-sig") as f:
    raw = f.read()

reader       = csv.DictReader(io.StringIO(raw))
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
print(str(len(active_rows)) + " actieve items gevonden")

# -- Verwijderde items detecteren ----------------------------------------------
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
            "id":          item_id,
            "title":       prev_item.get("title", ""),
            "benefit":     prev_item.get("benefit", ""),
            "app":         prev_item.get("app", "other"),
            "prodLabel":   prev_item.get("prodLabel", ""),
            "action":      prev_item.get("action", "none"),
            "actionLabel": prev_item.get("actionLabel", ""),
            "release":     prev_item.get("release", ""),
            "status":      new_status,
            "statusNl":    STATUS_NL[new_status],
        })
        print("  -> [" + STATUS_NL[new_status] + "] " + prev_item.get("title", "")[:70])

if not removed:
    print("Geen items verwijderd")

# -- Verwerken, vertalen en benefit genereren ----------------------------------
print("\nVerwerken...")
items = []
cached_count = new_count = retrans_count = 0
ai_count = fallback_count = 0

for i, row in enumerate(active_rows):
    product  = row.get("Tags - Product", "")
    title_en = row.get("Description", "").strip()
    key      = app_key_from_title(title_en) if title_en else app_key(product)
    desc_en  = row.get("Details", "").strip()
    item_id  = int(row.get("Feature ID", 0) or 0)
    modified = row.get("Last Modified", "").strip()
    cache_key = (item_id, modified)

    needs_processing = False
    needs_benefit    = False
    if cache_key in cache:
        cached_entry = cache[cache_key]
        if cached_entry.get("retranslate", False):
            retrans_count += 1
            print("  [" + str(i+1) + "/" + str(len(active_rows)) + "] Hervertalen: " + title_en[:65])
            needs_processing = True
        else:
            nl_title = cached_entry["title"]
            nl_desc  = cached_entry["desc"]
            benefit  = cached_entry.get("benefit", "")
            cached_count += 1
            print("  [" + str(i+1) + "/" + str(len(active_rows)) + "] OK " + title_en[:65])
            if not benefit:
                needs_benefit = True
    else:
        new_count += 1
        print("  [" + str(i+1) + "/" + str(len(active_rows)) + "] Nieuw: " + title_en[:65])
        needs_processing = True

    if needs_processing:
        ai_result = ai_process_item(title_en, desc_en)
        if ai_result:
            nl_title  = ai_result["title_nl"]
            nl_desc   = ai_result["desc_nl"]
            benefit   = ai_result["benefit"]
            ai_count += 1
        else:
            nl_title      = translate(title_en)
            nl_desc       = translate(desc_en[:800])
            needs_benefit = True
            time.sleep(0.3)

    if needs_benefit:
        ai_result = ai_process_item(title_en, desc_en)
        if ai_result:
            benefit   = ai_result["benefit"]
            ai_count += 1
        else:
            benefit        = generate_benefit(key, title_en, desc_en)
            fallback_count += 1
            time.sleep(0.3)

    action_key, action_label = classify_action(title_en, desc_en)

    items.append({
        "id":          item_id,
        "title":       nl_title,
        "desc":        nl_desc,
        "benefit":     benefit,
        "status":      "rolling" if "rolling" in row.get("Status", "").lower() else "dev",
        "app":         key,
        "tags":        extra_tags(product, key),
        "prodLabel":   make_label(product, key),
        "added":       row.get("Added to Roadmap", "").strip(),
        "modified":    modified,
        "release":     row.get("Release", "").strip(),
        "preview":     row.get("Preview", "").strip(),
        "action":      action_key,
        "actionLabel": action_label,
    })

print("\nResultaat: " + str(len(items)) + " actieve items")
print("  OK Uit cache:          " + str(cached_count))
print("  ++ Nieuw verwerkt:     " + str(new_count))
print("  ~~ Herverwerkt:        " + str(retrans_count))
print("  AI Via GitHub Models:  " + str(ai_count))
print("  FB Via fallback:       " + str(fallback_count))
print("  -- Verwijderd:         " + str(len(removed)))

today  = datetime.datetime.utcnow().strftime("%Y-%m-%d")
result = {
    "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "date":      today,
    "count":     len(items),
    "items":     items,
    "removed":   removed,
}

# -- data.json opslaan ---------------------------------------------------------
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\ndata.json opgeslagen OK")

# -- Archief opslaan -----------------------------------------------------------
archive_dir  = "archive"
os.makedirs(archive_dir, exist_ok=True)
archive_data = {"generated": result["generated"], "date": today, "removed": removed}

if removed:
    archive_path = os.path.join(archive_dir, today + ".json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)
    print("Archief opgeslagen: " + archive_path + " (" + str(len(removed)) + " verdwenen items) OK")
else:
    print("Geen verdwenen items deze run -- geen archiefbestand aangemaakt.")

# -- Archiefindex bijwerken ----------------------------------------------------
cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=92)).strftime("%Y-%m-%d")
for fname in os.listdir(archive_dir):
    if fname.endswith(".json") and fname != "index.json":
        fpath = os.path.join(archive_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as _f:
                _d = json.load(_f)
            if not _d.get("removed"):
                os.remove(fpath)
                print("Leeg archiefbestand verwijderd: " + fname)
        except Exception:
            pass

archive_files = []
for fname in sorted(os.listdir(archive_dir), reverse=True):
    if fname.endswith(".json") and fname != "index.json":
        date_str = fname.replace(".json", "")
        if date_str >= cutoff:
            archive_files.append(date_str)

with open(os.path.join(archive_dir, "index.json"), "w", encoding="utf-8") as f:
    json.dump({"updated": result["generated"], "dates": archive_files}, f, ensure_ascii=False, indent=2)
print("Archiefindex bijgewerkt: " + str(len(archive_files)) + " weken beschikbaar OK")

# -- GitHub Actions Step Summary -----------------------------------------------
summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if summary_path:
    with open(summary_path, "a", encoding="utf-8") as sf:
        sf.write("## Microsoft 365 Roadmap - Run samenvatting\n\n")
        sf.write("| | |\n|---|---|\n")
        sf.write("| Bijgewerkt | " + result["generated"] + " |\n")
        sf.write("| Actieve items | " + str(len(items)) + " |\n")
        sf.write("| Via GitHub Models | " + str(ai_count) + " |\n")
        sf.write("| Via fallback | " + str(fallback_count) + " |\n")
        sf.write("| Uit cache | " + str(cached_count) + " |\n")
        sf.write("| Verdwenen items | " + str(len(removed)) + " |\n")
        sf.write("| Archiefweken | " + str(len(archive_files)) + " |\n")
        if removed:
            sf.write("\n### Verdwenen items deze run\n\n")
            for r in removed:
                sf.write("- **" + r["title"] + "** (" + r["statusNl"] + ")\n")
    print("GitHub Step Summary geschreven OK")
