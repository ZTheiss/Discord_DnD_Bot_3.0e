import json

def json_to_human_readable_txt(json_file, txt_file):
    # Load JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(txt_file, "w", encoding="utf-8") as out:
        for key, item in data.items():
            out.write(f"{item.get('name', key)}\n")
            out.write("-" * len(item.get("name", key)) + "\n")

            for field, value in item.items():
                # Skip repeating the name field
                if field == "name":
                    continue

                # Format long descriptions as paragraphs
                if field == "description":
                    out.write(f"\nDescription:\n{value}\n\n")
                else:
                    out.write(f"{field.replace('_', ' ').title()}: {value}\n")

            out.write("\n" + "=" * 40 + "\n\n")  # separator between items


# Example usage
json_to_human_readable_txt("loot.json", "loot_output.txt")
