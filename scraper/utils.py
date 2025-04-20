import csv
import re
from datetime import datetime
import os

# export function from chatgpt. formats it very nicely to put in sql database
def export_to_csv(results, mode='w', filename="nutrition_breakdown.csv"):
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

    # build headers, deduplicated and sorted
    write_header = (mode == 'w') or (not os.path.exists(filename))
    headers = ["Name"] + sorted(all_nutrients)

    with open(filename, mode, newline='', encoding='utf-8') as f:
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