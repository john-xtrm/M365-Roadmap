import csv, json, io, datetime, sys

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
    key = app_key(product)
    items.append({
        "id":        int(row.get("Feature ID", 0) or 0),
        "title":     row.get("Description", "").strip(),
        "desc":      row.get("Details", "").strip(),
        "status":    "rolling" if "rolling" in status else "dev",
        "app":       key,
        "prodLabel": make_label(product, key),
        "added":     row.get("Added to Roadmap", "").strip(),
        "modified":  row.get("Last Modified", "").strip(),
        "release":   row.get("Release", "").strip(),
        "preview":   row.get("Preview", "").strip(),
    })

result = {
    "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "count": len(items),
    "items": items
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Klaar: {len(items)} items opgeslagen in data.json")
