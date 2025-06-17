import json
import hashlib
import re

def get_joist_type(designation):
    """
    Extract joist type prefix (e.g., '30K', '40LH', '44DLH').
    Only allows K, LH, and DLH series.
    """
    match = re.match(r"([0-9]+(?:K|LH|DLH))", designation)
    return match.group(1) if match else "UNKNOWN"

def to_xyz_dict(point):
    """
    Convert capitalized X/Y/Z dict to lowercase x/y/z.
    """
    return {
        "x": point.get("X", 0),
        "y": point.get("Y", 0),
        "z": point.get("Z", 0)
    }

def hash_line(start, end):
    """
    Generate a hash from start and end points to avoid duplicates.
    """
    return hashlib.md5(
        f"{start['X']},{start['Y']},{start['Z']}|{end['X']},{end['Y']},{end['Z']}".encode()
    ).hexdigest()

def convert_amejoists_to_grasshopper(input_path, output_path):
    """
    Converts a Hypar-style model JSON to Grasshopper-friendly joist data.
    """
    with open(input_path, 'r') as f:
        model = json.load(f)

    joist_types = []
    start_pts = []
    end_pts = []
    seen_hashes = set()

    for element in model.get("Elements", {}).values():
        if element.get("discriminator") != "Elements.AMEJoist":
            continue

        designation = element.get("JoistDesignation", "")
        top_line = element.get("TopOfSteelSlopeLine", {})
        start = top_line.get("Start")
        end = top_line.get("End")

        if not (designation and start and end):
            continue

        jt = get_joist_type(designation)
        if jt == "UNKNOWN":
            continue

        line_hash = hash_line(start, end)
        if line_hash in seen_hashes:
            continue
        seen_hashes.add(line_hash)

        joist_types.append(jt)
        start_pts.append(to_xyz_dict(start))
        end_pts.append(to_xyz_dict(end))

    # Final Grasshopper-friendly format
    gh_data = {
        "joist_types": joist_types,
        "start_pts": start_pts,
        "end_pts": end_pts
    }

    with open(output_path, 'w') as f_out:
        json.dump(gh_data, f_out, indent=2)

    print(f"✅ Wrote {len(joist_types)} joists to {output_path}")

convert_amejoists_to_grasshopper(
    input_path="model.json",
    output_path="joists_for_grasshopper.json"
)
