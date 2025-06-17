import json
import re
import hashlib

def extract_girder_profile(name_field: str) -> str:
    """
    Extracts any girder profile matching the pattern '###G' from the Name field.
    """
    match = re.match(r"(\d+G)", name_field)
    return match.group(1) if match else "UNKNOWN"

def to_xyz_dict(point: dict) -> dict:
    """
    Converts Tekla-style XYZ dict with capital keys to lowercase.
    """
    return {
        "x": point.get("X", 0),
        "y": point.get("Y", 0),
        "z": point.get("Z", 0)
    }

def hash_line(start: dict, end: dict) -> str:
    """
    Creates a hash of the line's start and end coordinates for deduplication.
    """
    return hashlib.md5(
        f"{start['X']},{start['Y']},{start['Z']}|{end['X']},{end['Y']},{end['Z']}".encode()
    ).hexdigest()

def convert_girders_to_grasshopper(input_path: str, output_path: str):
    with open(input_path, "r") as f:
        model = json.load(f)

    girder_types = []
    start_pts = []
    end_pts = []
    seen_hashes = set()

    for element in model.get("Elements", {}).values():
        if element.get("discriminator") != "Elements.AMEJoistGirder":
            continue

        name_field = element.get("Name", "")
        top_line = element.get("TopOfSteelLine", {})
        start = top_line.get("Start")
        end = top_line.get("End")

        if not (name_field and start and end):
            continue

        profile = extract_girder_profile(name_field)
        if profile == "UNKNOWN":
            continue

        line_hash = hash_line(start, end)
        if line_hash in seen_hashes:
            continue
        seen_hashes.add(line_hash)

        girder_types.append(profile)
        start_pts.append(to_xyz_dict(start))
        end_pts.append(to_xyz_dict(end))

    output_data = {
        "girder_types": girder_types,
        "start_pts": start_pts,
        "end_pts": end_pts
    }

    with open(output_path, "w") as f_out:
        json.dump(output_data, f_out, indent=2)

    print(f"✅ Exported {len(girder_types)} girders to {output_path}")

convert_girders_to_grasshopper("model.json", "girders_for_grasshopper.json")
