import csv
import re
from datetime import datetime
import os

# export function from chatgpt. formats it very nicely to put in sql database
def export_to_csv(results, filepath, mode='w', filename="nutrition_breakdown.csv"):
    """
    Parses a list of (item_name, nutrition_text) tuples into a CSV
    with columns Name, Serving Size, each nutrient, and Ingredients.
    """
    
    all_nutrients = set()
    parsed_rows = []

    for item_name, text in results:
        row = {"Name": item_name}
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        # skip metadata header lines
        lines = lines[2:]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Extract Ingredients line (this is where we handle the Ingredients column)
            # <--- Ingredients extraction starts here
            if line.startswith("Ingredients:"):
                ingredients = line.split("Ingredients:", 1)[1].strip()
                row["Ingredients"] = ingredients
                all_nutrients.add("Ingredients")
                i += 1
                continue
            # Optional: extract Contains line
            if line.startswith("Contains:"):
                contains = line.split("Contains:", 1)[1].strip()
                row["Contains"] = contains
                all_nutrients.add("Contains")
                i += 1
                continue

            # Case: Calories on one line, number on next
            if line == "Calories" and i+1 < len(lines):
                row["Calories"] = lines[i+1]
                all_nutrients.add("Calories")
                i += 2
                continue

            # Case: Serving Size in its own paragraph
            if line.startswith("Serving Size") and i+1 < len(lines):
                row["Serving Size"] = lines[i+1]
                all_nutrients.add("Serving Size")
                i += 2
                continue

            # Unit-on-same-line nutrients
            m = re.match(r"^(.+?)\s+([\d.]+)\s*([a-zA-Z]+)$", line)
            if m:
                nutrient, val, unit = m.groups()
                row[nutrient] = f"{val}{unit}"
                all_nutrients.add(nutrient)
                i += 1
                continue

            # Name-then-value on next line
            if i+1 < len(lines) and re.match(r"^[\d.]+\w+", lines[i+1]):
                row[line] = lines[i+1]
                all_nutrients.add(line)
                i += 2
                continue

            # otherwise, skip this line
            i += 1

        parsed_rows.append(row)

    for idx, row in enumerate(parsed_rows, start=1):
        row['id'] = idx

    # merge protein columns
    if "Protein <" in all_nutrients:
        for row in parsed_rows:
            if "Protein <" in row:
                row["Protein"] = row.get("Protein") or row.pop("Protein <")
        all_nutrients.discard("Protein <")

    # convert cells to floats
    nutrient_units = {}
    for row in parsed_rows:
        for nutr in list(all_nutrients):
            val = row.get(nutr)
            if not isinstance(val, str):
                continue
            m = re.match(r'^([\d.]+)([a-zA-Z%]+)$', val)
            if m:
                num, unit = m.groups()
                row[nutr] = float(num)
                nutrient_units[nutr] = unit

    new_nutrients = set()
    for nutr in all_nutrients:
        if nutr in nutrient_units:
            new_name = f"{nutr}_{nutrient_units[nutr].lower()}"
            new_nutrients.add(new_name)
            for row in parsed_rows:
                if nutr in row:
                    row[new_name] = row.pop(nutr)
        else:
            new_nutrients.add(nutr)
    all_nutrients = new_nutrients


    # build headers, deduplicated and sorted
    full_path = os.path.join(filepath, filename)

    write_header = (mode == 'w') or (not os.path.exists(full_path))
    headers = ['id', 'Name'] + sorted(all_nutrients)

    with open(full_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerows(parsed_rows)

    print(f"Wrote {len(parsed_rows)} new rows to {filename}")

def export_array(results):
    for result in results:
        export_to_csv(result, mode='a')

def get_date():
    today = datetime.now()
    date_str = f"{today:%A}, {today:%B} {today.day}, {today:%Y}"
    return date_str