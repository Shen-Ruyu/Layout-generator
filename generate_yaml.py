import os
import argparse
import pathlib
import sys
import json

sys.path.append("layout_generator/src")

import xls2yaml

# from xls2yaml.xl2ml_common import yamlData
from xls2yaml.xl2ml_emmc import xlData_emmc
from xls2yaml.xl2ml_nor import xlData_nor
from xls2yaml.xl2ml_sram import xlData_sram
from xls2yaml.xl2ml_common import yamlData


DEFAULT_LAYOUT_DIR = "layouts"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOGLEVEL = "INFO"
        

class LayoutXls2Yaml :

    LAYOUT_SOURCE_PATH="default"
    LAYOUT_YAML_PATH="./yaml"
    LAYOUT_GEN_PATH="./generated"    

    NAME2FILE="./default/name_mapping_to_file.json"
    DATAID="./default/dataidentifiers.json"   

    def __init__(self, layout_path= None, generate_path = None):

        if layout_path != None :
            self.LAYOUT_SOURCE_PATH = layout_path
            self.NAME2FILE=f"{self.LAYOUT_SOURCE_PATH}/name_mapping_to_file.json"
            self.DATAID=f"{self.LAYOUT_SOURCE_PATH}/dataidentifiers.json"

        if generate_path != None :
            self.LAYOUT_YAML_PATH = f"{generate_path}/{self.LAYOUT_YAML_PATH}"

        if not os.path.exists(f"{self.LAYOUT_YAML_PATH}") :
            os.makedirs(self.LAYOUT_YAML_PATH)               

        self.EMMC_YAML=f"{self.LAYOUT_YAML_PATH}/EMMC.yaml"
        self.NOR_YAML=f"{self.LAYOUT_YAML_PATH}/NOR.yaml"
        self.SRAM_YAML=f"{self.LAYOUT_YAML_PATH}/SRAM.yaml"              

    def build_yaml(self, emmc_file=None, nor_file=None, sram_file=None):
        sys.path.append("layout_generator/src")

        from xls2yaml.xl2ml_emmc import xlData_emmc
        from xls2yaml.xl2ml_nor import xlData_nor
        from xls2yaml.xl2ml_sram import xlData_sram
        from xls2yaml.xl2ml_common import yamlData

        if emmc_file:
            emmc_layout_name = os.path.splitext(os.path.basename(emmc_file))[0].rsplit('_', 1)[0]
            self.emmc_version = os.path.splitext(os.path.basename(emmc_file))[0].rsplit('_', 1)[1]
            EMMC_LAYOUT_FILE_NAME = f"{emmc_layout_name}_{self.emmc_version}.xlsx"
            EMMC = xlData_emmc(name="EMMC", version=self.emmc_version, project="HPCGEN2", start_address="0x_0000_0000", size="28736MB")
            EMMC.Readxl(f"{self.LAYOUT_SOURCE_PATH}/{EMMC_LAYOUT_FILE_NAME}","eMMC layout")
            EMMC.xl_datas["blocks"].sort(key=lambda element: int(element["start_address"],16))
            data=EMMC.xl_datas
            yamlData.data2ml(data,self.EMMC_YAML)
        else:
            print("No eMMC layout file provided for building EMMC_YAML")

        if nor_file:
            nor_layout_name = os.path.splitext(os.path.basename(nor_file))[0].rsplit('_', 1)[0]
            self.nor_version = os.path.splitext(os.path.basename(nor_file))[0].rsplit('_', 1)[1]
            NOR_LAYOUT_FILE_NAME = f"{nor_layout_name}_{self.nor_version}.xlsx"
            NOR = xlData_nor(name="NOR", version=self.nor_version, project="HPCGEN2", start_address="0x_0000_0000", size="32MB")
            NOR.Readxl(f"{self.LAYOUT_SOURCE_PATH}/{NOR_LAYOUT_FILE_NAME}","Partitioning")
            NOR.xl_datas["blocks"].sort(key=lambda element: int(element["start_address"],16))
            data=NOR.xl_datas
            yamlData.data2ml(data,self.NOR_YAML)
        else:
            print("No NOR layout file provided for building NOR_YAML")

        if sram_file:
            sram_layout_name = os.path.splitext(os.path.basename(sram_file))[0].rsplit('_', 1)[0]
            self.sram_version = os.path.splitext(os.path.basename(sram_file))[0].rsplit('_', 1)[1]
            SRAM_LAYOUT_FILE_NAME = f"{sram_layout_name}_{self.sram_version}.xlsx"
            SRAM = xlData_sram(name="SRAM", version=self.sram_version, project="HPCGEN2", start_address="0x2000_0000", size="569MB")
            SRAM.Readxl(f"{self.LAYOUT_SOURCE_PATH}/{SRAM_LAYOUT_FILE_NAME}","SRAM Layout")
            SRAM.xl_datas["blocks"].sort(key=lambda element: int(element["start_address"],16))
            data=SRAM.xl_datas
            yamlData.data2ml(data,self.SRAM_YAML)
        else:
            print("No SRAM layout file provided for building SRAM_YAML")

    def build_files(self, emmc_file=None, nor_file=None, sram_file=None, generate_path=None):
        sys.path.append("../layout_generator/src")

        from yaml_parser.yaml_parser_emmc import YamlParserEMMC
        from yaml_parser.yaml_parser_nor import YamlParserNOR
        from yaml_parser.yaml_parser_sram import YamlParserSRAM

        lb_nor = []
        lb_emmc = []

        if nor_file:      
            parserNOR = YamlParserNOR(yaml_file=self.NOR_YAML)
            parserNOR.parser_yaml()
            parserNOR.generate_header(f"{generate_path}/NOR_address.h")
            parserNOR.generate_bash(f"{generate_path}/nor_banka", f"{generate_path}/nor_bankb")
            parserNOR.generate_python(f"{generate_path}/pylayout_nor_data.py")
            # parserNOR.generate_fls_scriptor("Fls_PostImport.xml")
            val_nor_a, val_nor_b = parserNOR.generate_json(self.NAME2FILE)
            lb_nor = parserNOR.generate_logical_block()
        else:
            print("No NOR layout file provided for building files")

        if emmc_file:
            parserEMMC = YamlParserEMMC(yaml_file=self.EMMC_YAML)
            parserEMMC.parser_yaml()
            parserEMMC.generate_header(f"{generate_path}/EMMC_address.h")
            parserEMMC.generate_bash(f"{generate_path}/emmc_banka", f"{generate_path}/emmc_bankb")
            parserEMMC.generate_python(f"{generate_path}/pylayout_emmc_data.py")
            parserEMMC.generate_gtp_files(f"{generate_path}")
            val_emmc_a, val_emmc_b = parserEMMC.generate_json(self.NAME2FILE)
            lb_emmc = parserEMMC.generate_logical_block()
        else:
            print("No eMMC layout file provided for building files")

        if sram_file:
            parserSRAM = YamlParserSRAM(yaml_file=self.SRAM_YAML)
            parserSRAM.parser_yaml()
            parserSRAM.generate_header(f"{generate_path}/SRAM_address.h")
            parserSRAM.generate_python(f"{generate_path}/pylayout_sram_data.py")
            parserSRAM.generate_ldscript(f"{generate_path}/memory_area.ldscript")
        else:
            print("No SRAM layout file provided for building files")

        if nor_file and emmc_file:
            values_a = val_nor_a
            values_a.update(val_emmc_a)
            values_b = val_nor_b
            values_b.update(val_emmc_b)
            with open(f"{generate_path}/images_banka.json", 'w') as f:
                 json.dump(values_a, f, indent=4)
            with open(f"{generate_path}/images_bankb.json", 'w') as f:
                 json.dump(values_b, f, indent=4)
        else:
            print("No NOR and eMMC layout file provided for generating images json")

        lb_config = {
            "status": "ok",
            "eMMCLayoutVersion": f"v{self.emmc_version}"if emmc_file else "",
            "NORLayoutVersion": f"v{self.nor_version}"if nor_file else "",
            "LogicalBlockVersion": "v1.0",
            "logicalBlocks": lb_emmc + lb_nor
        }

        dataidentifiers = dict()
        with open(self.DATAID, "r") as f:
            dataidentifiers = json.load(f)

        lb_config.update(dataidentifiers)
        with open(f"{generate_path}/dps_lb_config.json", "w") as f:
             json.dump(lb_config, f, indent=4)    


