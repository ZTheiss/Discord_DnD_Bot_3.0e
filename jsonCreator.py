import json
import re

def parse_spell_block(block):
    lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return None

    name = lines[0]
    idx = 1

    # Define possible field labels with regex patterns
    field_labels = {
        "level": [r'^level\s*:'],
        "components": [r'^components\s*:'],
        "casting_time": [r'^casting time\s*:'],
        "range": [r'^range\s*:'],
        "target": [r'^target\s*:', r'^targets\s*:', r'^area\s*:'],
        "effect": [r'^effect\s*:'],
        "duration": [r'^duration\s*:'],
        "saving_throw": [r'^saving throw\s*:'],
        "spell_resistance": [r'^spell resistance\s*:']
    }

    data = {
        "name": name,
        "school": "",
        "level": "",
        "components": "",
        "casting_time": "",
        "range": "",
        "target": "",
        "effect": "",
        "duration": "",
        "saving_throw": "",
        "spell_resistance": "",
        "description": ""
    }

    # Special: assume 2nd line is always school
    data["school"] = lines[idx]
    idx += 1

    current_field = None
    description_started = False
    desc_lines = []

    while idx < len(lines):
        line = lines[idx]
        idx += 1

        # If a blank line is found, treat it as ending the current field (like finding a label)
        if not line.strip():
            current_field = None
            continue

        if description_started:
            desc_lines.append(line)
            continue

        matched_field = None
        for field_key, patterns in field_labels.items():
            for pattern in patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    matched_field = field_key
                    content = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    data[field_key] = content
                    break
            if matched_field:
                break

        if matched_field:
            current_field = None  # Always single line for all fields except description
        else:
            # If not a field label, start description
            description_started = True
            desc_lines.append(line)

    data["description"] = ' '.join(desc_lines).strip()
    return data

def parse_spells_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content)
    spells = {}

    for block in blocks:
        spell = parse_spell_block(block)
        if spell:
            spells[spell["name"].lower()] = spell

    return spells

def main():
    filename = "spells.txt"
    spells = parse_spells_file(filename)
    with open("spells.json", "w", encoding="utf-8") as f:
        json.dump(spells, f, indent=2, ensure_ascii=False)
    print(f"✅ Parsed {len(spells)} spells and saved to spells.json")

if __name__ == "__main__":
    main()
