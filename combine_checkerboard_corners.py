# Combines multiple checkerboard corner files for Blaze, IR, and RGB into one file each

def combine_corner_files(input_files, output_file):
    # Open the output file for writing
    with open(output_file, 'w') as fout:
        for file in input_files:
            try:
                # Open each input file and read non-empty lines
                with open(file, 'r') as fin:
                    lines = [line.strip() for line in fin if line.strip()]
                    
                    # Add a comment indicating which file the lines came from
                    fout.write(f"# From file: {file}\n")
                    fout.write('\n'.join(lines) + '\n')
            except Exception as e:
                print(f"Error reading {file}: {e}")
    
    print(f"Combined file saved as: {output_file}")


# Input files for Blaze
blaze_files = ["blaze1.txt", "blaze2.txt", "blaze3.txt", "blaze4.txt", "blaze5.txt"]

# Input files for IR
ir_files = ["ir1.txt", "ir2.txt", "ir3.txt", "ir4.txt", "ir5.txt"]

# Input files for RGB
rgb_files = ["rgb1.txt", "rgb2.txt", "rgb3.txt", "rgb4.txt", "rgb5.txt"]

# Output file paths
combined_blaze = "combined_cornersB.txt"
combined_ir = "combined_cornersI.txt"
combined_rgb = "combined_cornersR.txt"

# Combine and save each set
combine_corner_files(blaze_files, combined_blaze)
combine_corner_files(ir_files, combined_ir)
combine_corner_files(rgb_files, combined_rgb)
