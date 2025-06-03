import sys

def parse_pocket_pdb(pocket_pdb_path):
    x_coords, y_coords, z_coords = [], [], []

    with open(pocket_pdb_path, 'r') as f:
        for line in f:
            if line.startswith("HETATM") or line.startswith("ATOM  "):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    x_coords.append(x)
                    y_coords.append(y)
                    z_coords.append(z)
                except ValueError:
                    continue

    if not x_coords:
        raise ValueError("No coordinates found in pocket file.")

    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    center_z = sum(z_coords) / len(z_coords)

    size_x = max(x_coords) - min(x_coords) + 5  # Add buffer
    size_y = max(y_coords) - min(y_coords) + 5
    size_z = max(z_coords) - min(z_coords) + 5

    return (center_x, center_y, center_z), (size_x, size_y, size_z)

def write_vina_config(center, size, output_file="config.txt"):
    config_text = f"""# Auto-generated Vina config file

center_x = {center[0]:.3f}
center_y = {center[1]:.3f}
center_z = {center[2]:.3f}

size_x = {size[0]:.1f}
size_y = {size[1]:.1f}
size_z = {size[2]:.1f}

"""
    with open(output_file, 'w') as f:
        f.write(config_text)
    print(f"Vina config written to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_vina_grid.py pocketX_atm.pdb")
        sys.exit(1)

    pocket_file = sys.argv[1]
    center, size = parse_pocket_pdb(pocket_file)
    write_vina_config(center, size)

