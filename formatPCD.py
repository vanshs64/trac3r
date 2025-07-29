import numpy as np
import os
def pack_rgb_float(r, g, b):
    """Pack R, G, B into a single float32 as required by the PCD 'rgb' field."""
    rgb_int = (int(r) << 16) | (int(g) << 8) | int(b)
    return np.frombuffer(np.array([rgb_int], dtype=np.uint32).tobytes(), dtype=np.float32)[0]

def convert_to_pcd(input_file_path, output_file_path, color=(0, 255, 0)):
    """Convert XYZ raw point data into a properly formatted PCD file with color."""
    
    packed_rgb = pack_rgb_float(*color)

    points = []
    with open(input_file_path, 'r') as f_in:
        for line in f_in:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                    points.append((x, y, z, packed_rgb))
                except ValueError:
                    continue  # skip invalid lines

    num_points = len(points)
    if num_points == 0:
        print("❌ No valid points found in input file.")
        return

    header = f"""# .PCD v.7 - Point Cloud Data file format
VERSION .7
FIELDS x y z rgb
SIZE 4 4 4 4
TYPE F F F F
COUNT 1 1 1 1
WIDTH {num_points}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {num_points}
DATA ascii
"""

    with open(output_file_path, 'w') as f_out:
        f_out.write(header)
        for x, y, z, rgb in points:
            f_out.write(f"{x} {y} {z} {rgb}\n")

    print(f"✅ Formatted PCD file written to: {output_file_path}")

def batch_convert_filtered_txt_to_pcd(directory="./pcd"):
    """Convert all *_filtered.txt files in a directory to numbered PCD files."""
    files = sorted(f for f in os.listdir(directory) if f.endswith("_filtered.txt"))

    if not files:
        print("❌ No '_filtered.txt' files found in directory.")
        return

    for idx, filename in enumerate(files):
        input_path = os.path.join(directory, filename)
        output_path = os.path.join(directory, f"{idx}.pcd")
        print(f"🔄 Converting {filename} → {idx}.pcd")
        convert_to_pcd(input_path, output_path)

    print(f"✅ Done! {len(files)} PCD files generated in: {directory}")

# Usage

# directory with all pcd files
pcd_path = "pcd"
batch_convert_filtered_txt_to_pcd(pcd_path)