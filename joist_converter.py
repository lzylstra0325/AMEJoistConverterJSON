import json
import hashlib
import re

def get_joist_type(name):
    match = re.match(r"([0-9]+K)", name)
    return match.group(1) if match else "UNKNOWN"

def hash_line(line):
    """Generate a hash from line geometry to prevent duplicates."""
    s, e = line.get("Start", {}), line.get("End", {})
    return hashlib.md5(f"{s.get('x')},{s.get('y')},{s.get('z')}|{e.get('x')},{e.get('y')},{e.get('z')}".encode()).hexdigest()

def convert_amejoists_to_grasshopper(input_path, output_path):
    with open(input_path, 'r') as f:
        model = json.load(f)

    joist_types = []
    start_pts = []
    end_pts = []
    seen_hashes = set()

    for element in model.get("Elements", {}).values():
        if element.get("discriminator") != "Elements.AMEJoist":
            continue

        name = element.get("Name", "")
        line = element.get("TopOfSteelSlopeLine", {})
        start = line.get("Start")
        end = line.get("End")

        if not (name and start and end):
            continue

        line_hash = hash_line(line)
        if line_hash in seen_hashes:
            continue  # skip duplicates
        seen_hashes.add(line_hash)

        joist_types.append(get_joist_type(name))
        start_pts.append(start)
        end_pts.append(end)

    gh_data = {
        "joist_types": joist_types,
        "start_pts": start_pts,
        "end_pts": end_pts
    }

    with open(output_path, 'w') as f_out:
        json.dump(gh_data, f_out, indent=2)

convert_amejoists_to_grasshopper(
    input_path="model_chatgpt_minified.json",
    output_path="joists_for_grasshopper.json"
)
