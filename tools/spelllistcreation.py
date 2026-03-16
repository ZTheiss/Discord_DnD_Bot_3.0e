# import requests
# from bs4 import BeautifulSoup
# import json

# url = "https://rpg20.com/index.php/spells/level/3e/1/full"

# headers = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/122.0.0.0 Safari/537.36"
#     )
# }

# response = requests.get(url, headers=headers, timeout=10)
# response.raise_for_status()

# soup = BeautifulSoup(response.text, "html.parser")

# table = soup.find("table", id="all_spell")

# if not table:
#     raise RuntimeError("Could not find table with id='all_spell'")

# spells = []
# rows = table.find_all("tr")

# # Skip header row if present
# for row in rows[1:]:
#     cols = row.find_all("td")
#     if not cols:
#         continue

#     # Adjust indexes if the table has more or fewer columns
#     spell = {
#         "name": cols[0].get_text(strip=True),
#         "level": cols[1].get_text(strip=True),
#         "components": cols[2].get_text(strip=True),
#         "castingtime": cols[3].get_text(strip=True),
#         "range": cols[4].get_text(strip=True),
#         "effect": cols[5].get_text(strip=True),
#         "area": cols[6].get_text(strip=True),
#         "duration": cols[7].get_text(strip=True),
#         "savingthrow": cols[8].get_text(strip=True),
#         "spellresistance": cols[9].get_text(strip=True),
#         "description": cols[10].get_text(strip=True),
#     }

#     spells.append(spell)

# with open("spellsCreated.json", "w", encoding="utf-8") as f:
#     json.dump(spells, f, indent=2, ensure_ascii=False)

# print(f"Extracted {len(spells)} spells.")

import requests
from bs4 import BeautifulSoup
import json

url = "https://rpg20.com/index.php/spells/level/3e/1/full"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", id="all_spell")
if not table:
    raise RuntimeError("Could not find table with id='all_spell'")

rows = table.find_all("tr")

# Extract header names
headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

spells = []

for row in rows[1:]:
    cols = row.find_all("td")
    if not cols:
        continue

    entry = {}
    for i, col in enumerate(cols):
        nested = col.find("table")
        j = 0

        if nested:
            # Cell contains a nested table
            for item in nested:
                entry[headers[j]] = {
                    "text": col.get_text(" ", strip=True),
                    "nested_table": [
                        [td.get_text(" ", strip=True) for td in row.find_all("td")]
                        for row in nested.find_all("tr")
                    ]
                }
            i += 1
        else:
            # Normal cell
            # entry[i] = col.get_text(" ", strip=True)
            if cols[0].get_text(strip=True) == "Plane Contacted" or cols[0].get_text(strip=True) == "Contact Other Plane" or cols[0].get_text(strip=True) == "(appropriate)" or cols[0].get_text(strip=True) == "Elemental Plane" \
                or cols[0].get_text(strip=True) == "Positive/Negative Energy Plane" or cols[0].get_text(strip=True) == "Astral Plane" or cols[0].get_text(strip=True) == "Outer Plane, demideity" or cols[0].get_text(strip=True) == "Outer Plane, lesser deity" \
                or cols[0].get_text(strip=True) == "Outer Plane, intermediate deity" or cols[0].get_text(strip=True) == "Outer Plane, greater deity":
                continue
            else:
                spell = {
                    "name": cols[0].get_text(strip=True),
                    "level": cols[1].get_text(strip=True),
                    "components": cols[2].get_text(strip=True),
                    "castingtime": cols[3].get_text(strip=True),
                    "range": cols[4].get_text(strip=True),
                    "target": cols[5].get_text(strip=True),
                    "effect": cols[6].get_text(strip=True),
                    "area": cols[7].get_text(strip=True),
                    "duration": cols[8].get_text(strip=True),
                    "savingthrow": cols[9].get_text(strip=True),
                    "spellresistance": cols[10].get_text(strip=True),
                    "description": cols[11].get_text(strip=True),
                }


    spells.append(spell)

with open("spellsCreated.json", "w", encoding="utf-8") as f:
    json.dump(spells, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(spells)} spells.")

with open("spellsCreated.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def fix_newlines(obj):
    if isinstance(obj, dict):
        return {k: fix_newlines(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_newlines(v) for v in obj]
    if isinstance(obj, str):
        return obj.replace("\\n", "\n")
    return obj

# Apply transformation
fixed = fix_newlines(data)

# Save updated JSON
with open("spellsCreated.json", "w", encoding="utf-8") as f:
    json.dump(fixed, f, indent=2, ensure_ascii=False)
