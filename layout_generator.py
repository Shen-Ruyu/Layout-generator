import argparse
import os
from generate_yaml import LayoutXls2Yaml

if ( __name__ == "__main__" ):
    parser = argparse.ArgumentParser(description='python generate_yaml.py --emmc_file "/path/to/emmc_layout.xlsx" --nor_file "/path/to/nor_layout.xlsx" --sram_file "/path/to/sram_layout.xlsx" --generated_path /path/to/output')
    parser.add_argument('--emmc_file', type=str, help='File path for eMMC layout')
    parser.add_argument('--nor_file', type=str, help='File path for NOR layout')
    parser.add_argument('--sram_file', type=str, help='File path for SRAM layout')
    parser.add_argument('--generated_path', type=str, required=True)
    args=parser.parse_args()
   
    layout_path = next((arg for arg in [args.emmc_file, args.nor_file, args.sram_file] if arg), None)
    if layout_path:
        layout_path = os.path.dirname(layout_path)
    else:
        print("Error: No valid layout file provided.")
        
    layout_converter = LayoutXls2Yaml(layout_path, generate_path = args.generated_path )
    layout_converter.build_yaml(args.emmc_file, args.nor_file, args.sram_file)
    layout_converter.build_files(args.emmc_file, args.nor_file, args.sram_file, args.generated_path)
