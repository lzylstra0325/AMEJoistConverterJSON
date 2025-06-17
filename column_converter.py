import json
import hashlib

def to_xyz_dict(point: dict) -> dict:
    """
    Converts a Tekla-style XYZ point (with capitalized keys) to lowercase.
    """
    return {
        "x": point.get("X", 0),
        "y": point.get("Y", 0),
        "z": point.get("Z", 0)
    }

def hash_line(start: dict, end: dict) -> str:
    """
    Generates a unique hash based on the line geometry to remove duplicates.
    """
    return hashlib.md5(
        f"{start['X']},{start['Y']},{start['Z']}|{end['X']},{end['Y']},{end['Z']}".encode()
    ).hexdigest()

def convert_columns_to_grasshopper(input_path: str, output_path: str):
    with open(input_path, "r") as f:
        model = json.load(f)

    column_types = []
    start_pts = []
    end_pts = []
    seen_hashes = set()

    for element in model.get("Elements", {}).values():
        if element.get("discriminator") != "Elements.AMEColumn":
            continue

        column_name = element.get("ColumnName", "")
        center_line = element.get("CenterLine", {})
        start = center_line.get("Start")
        end = center_line.get("End")

        if not (column_name and start and end):
            continue

        line_hash = hash_line(start, end)
        if line_hash in seen_hashes:
            continue
        seen_hashes.add(line_hash)

        column_types.append(column_name)
        start_pts.append(to_xyz_dict(start))
        end_pts.append(to_xyz_dict(end))

    output_data = {
        "column_types": column_types,
        "start_pts": start_pts,
        "end_pts": end_pts
    }

    with open(output_path, "w") as f_out:
        json.dump(output_data, f_out, indent=2)

    print(f"✅ Exported {len(column_types)} columns to {output_path}")

convert_columns_to_grasshopper("model.json", "columns_for_grasshopper.json")
