# Layout-generator

## Requirement

Install the required python libraries:
```sh
pip3 install openpyxl
pip3 insatll pyyaml
```

Install commit hooks before updating your changes.
```sh
# Check installed modules in your local environment
pip3 list
# Install pre-commit if not installed
pip3 install pre-commit
# Install commit hooks
cd <layout_generator_repository_path>
pre-commit install
```

⚠ Pip usage depends on your python environment, i.e.:
```sh
# Get python version:
python --version
# python is linked to python3.6+
pip list
pip install
# python is linked to python2+, use:
pip3 list
pip3 install
# or if pip3 doesn't exist:
python3 -m pip list
python3 -m pip install
```

## Feature

### generate_yaml.py

This python script is designed to automate the process of converting memory layout information from Excel files into YAML files and utilizing these YAML files to generate various configuration files for different types of memory layouts（eMMC, NOR, SRAM）.
Following files are generated by script:
-Headers Files(.h)
-Bash Scripts
-Python Scripts(.py)
-JSON Files(.json)
-GNU Linker Script (.ldscript):

### layout_generater.py

This script uses the LayoutXls2yaml class defined in generate_yaml.py. It parses the command line arguments to gain the full file paths and the output directory.

## Usage

The users must provide at least one valid layout file path which contain the directory and full filename, and the required generated_path which determines the location of the generated file.

Run the script from the command line, three examples command is shown below:

### generate  from excel file
```bash
# example generate all the layouts: emmc / nor / sram layout
python layout_generator.py --emmc_file="/path/to/eMMC_layout_1.0.xlsx" --nor_file="/path/to/NOR_Layout_1.0.xlsx" --sram_file="/path/to/SRAM_layout_1.0.xlsx" --generated_path="/path/to/output"
# example generate two layouts 
python layout_generator.py --emmc_file="/path/to/eMMC_layout_1.0.xlsx" --nor_file="/path/to/NOR_Layout_1.0.xlsx" --generated_path="/path/to/output"
# example to generate single layout
python layout_generator.py --emmc_file="/path/to/eMMC_layout_1.0.xlsx" --generated_path="/path/to/output"
```
### generate from yaml file
```bash
python yml_layout_generator.py --output-dir="path/to/output" --layout-dirs="/path/to/yaml"
```
