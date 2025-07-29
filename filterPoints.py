import os

def filter_point_files(directory):
    for filename in os.listdir(directory):
        if not filename.endswith('.txt'):
            continue
        if filename.endswith('_filtered.txt'):
            continue
            
        input_path = os.path.join(directory, filename)
        if not os.path.isfile(input_path):
            continue
            
        base_name = filename[:-4]  # Remove the .txt extension
        output_filename = base_name + '_filtered.txt'
        output_path = os.path.join(directory, output_filename)
        
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
                tokens = line.split()
                if len(tokens) != 3:
                    continue
                try:
                    z_val = float(tokens[2])
                    if z_val < 2:
                        continue
                    # Convert the first two tokens to float to ensure they are numbers
                    float(tokens[0])
                    float(tokens[1])
                    outfile.write(line)
                except (ValueError, IndexError):
                    continue

# usage
filter_point_files('pcd')