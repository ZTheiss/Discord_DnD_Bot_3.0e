import json
import csv

with open("./data/loot.json", "r", encoding="utf-8") as f:
    items = json.load(f)

with open("./data/loot.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["name", "category", "type", "hands", "damage", "range", "magical", "crit", "damage_type", "description", "discovery_location", "quantity", "owner", "link"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in items.values():
        writer.writerow({
            "name": item.get("name"),
            "category": item.get("category", ""),
            "type": item.get("type", ""),
            "hands": item.get("hands", ""),
            "damage": item.get("damage", ""),
            "range": item.get("range", ""),
            "magical": item.get("magical", False),
            "crit": item.get("crit", ""),
            "damage_type": item.get("damage_type", ""),
            "description": item.get("description", ""),
            "discovery_location": item.get("discovery_location", ""),
            "quantity": item.get("quantity", 1),
            "owner": item.get("owner", ""),
            "link": item.get("link", "")
        })

