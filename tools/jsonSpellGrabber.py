import json
import re
import csv

def find_and_sort_wiz_spells(data):
    results = []

    for spell_name, spell_data in data.items():
        level_field = spell_data.get("level", "")
        print(spell_data.get("name"))

        # Find all occurrences like "Wiz 6"
        matches = re.findall(r"Wiz\s*(\d+)", level_field)

        if matches:
            # Convert the first match to an integer
            wiz_level = int(matches[0])
            results.append((spell_name, wiz_level, spell_data))

    # Sort by the extracted wizard level
    results.sort(key=lambda x: x[1])

    return results

def export_to_csv(wiz_spells, filename="wiz_spells.csv"):
    # Extract all keys from the first spell to use as CSV headers
    headers = list(wiz_spells[0][2].keys())

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for level, name, spell_data in wiz_spells:
            writer.writerow(spell_data)


with open("data/spells.json", encoding="utf-8", mode="r") as f:
    spells = json.load(f)

sorted_wiz_spells = find_and_sort_wiz_spells(spells)
export_to_csv(sorted_wiz_spells)

for name, level, data in sorted_wiz_spells:
    print(f"Wiz {level}: {name}")
