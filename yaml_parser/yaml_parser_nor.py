from .yaml_parser_common import YamlParserBase

import json

class YamlParserNOR(YamlParserBase):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.ltype="NOR"
        self.state = {
            "BANKA" : "_A_",
            "BANKB" : "_B_",
            "DATA" : "_"
        }

    def generate_json(self, mapping):
        """
        Generate a json file which contains the list of images (address, size, type and if we must erase the area or not) we want use to flash using pmic
        """
        with open(mapping) as map_file:
            files = json.load(map_file)

        values_a = dict()
        values_b = dict()
        for key in self.yaml:
            k = key.replace("HPCGEN2_", "")
            bank = ""
            if "_A_" in k :
                bank = 'a'
                k = k.replace("_A_", "")
            elif "_B_" in k:
                bank = 'b'
                k = k.replace("_B_", "")
            if k[-1] == '_':
                k = k[:-1]
            if k in files:
                erase_v = True
                if k in ["DCD", "DCDBACKUP", "DCDBIST", "DCDBISTBACKUP", "QSPI"]:
                    erase_v = False
                if bank == 'a':
                    values_a[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "QSPI", "erase": erase_v}
                elif bank == 'b':
                    values_b[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "QSPI", "erase": erase_v}
                else:
                    values_a[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "QSPI", "erase": erase_v}
                    values_b[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "QSPI", "erase": erase_v}

        return values_a, values_b

    def generate_bash(self, bash_file_banka, bash_file_bankb):
        """
        Generate a bash file which contains the list of address of each part of the layout
        """
        values_a = list()
        values_b = list()
        for key in self.yaml:
            bank = ""
            if "_A_" in key:
                bank = 'a'
            elif "_B_" in key:
                bank = 'b'

            if bank == 'a':
                values_a.append(key)
            elif bank == 'b':
                values_b.append(key)
            else:
                values_a.append(key)
                values_b.append(key)

        with open(bash_file_banka, 'w') as f:
            f.write("# Attention!\n")
            f.write("# This file is generated!\n")
            f.write("# For changes, do not modify this file but the layout associated\n\n")
            f.write(f"# Layout version {self.version}\n\n")
            for val in values_a:
                k = val.lower()
                k = k.replace("hpcgen2_", "")
                if k[-1] == '_':
                    k = k[:-1]
                f.write(f"{k}={self.yaml[val]['start_address'].lower()}\n")

        with open(bash_file_bankb, 'w') as f:
            f.write("# Attention!\n")
            f.write("# This file is generated!\n")
            f.write("# For changes, do not modify this file but the layout associated\n\n")
            f.write(f"# Layout version {self.version}\n\n")
            for val in values_b:
                k = val.lower()
                k = k.replace("hpcgen2_", "")
                if k[-1] == '_':
                    k = k[:-1]
                f.write(f"{k}={self.yaml[val]['start_address'].lower()}\n")

    def generate_fls_scriptor(self, python_file):
        """
        Generate a script for scriptor to adapt the NOR adress in FLS module
        """
        key = "HPCGEN2_NVMDATA_OPERATIONALDATABLOCKMETHA_"
        # size is the number of blocks * size of block
        sector_size = 64 * 4096
        start_address = self.yaml[key]['start_address']
        nvm_size = self.yaml[key]['size']
        num_sectors = int(nvm_size/sector_size)
        nvm_size_sector = int(nvm_size / num_sectors)

        with open(python_file, 'w') as f:
            f.write("<Script xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation='Scriptor.xsd'>\n")
            f.write("\t<Name>Fls_PostImport</Name>\n")
            f.write(f"\t<Decription>FLS NOR layout version {self.version}</Decription>\n")
            f.write("\t<Expression>as:modconf('Fls')[1]</Expression>\n")
            f.write("\t<Operations>\n\n")

            for i in range(num_sectors):
                start_address = hex(int(start_address, 16) + nvm_size_sector)
                sector_address = nvm_size_sector * i
                f.write('\t\t<Operation Type= "ForEach">\n')
                f.write(f"\t\t\t<Expression>as:modconf('Fls')[1]/FlsConfigSet/FlsSectorList/FlsSector/FlsSector_{i}/FlsSectorHwAddress</Expression>\n")
                f.write("\t\t\t<Operations>\n")
                f.write('\t\t\t\t<Operation Type="SetValue">\n')
                f.write(f"\t\t\t\t\t<Expression>'{start_address}'</Expression>\n")
                f.write("\t\t\t\t</Operation>\n")
                f.write("\t\t\t</Operations>\n")
                f.write("\t\t</Operation>\n\n")
                f.write('\t\t<Operation Type= "ForEach">\n')
                f.write(f"\t\t\t<Expression>as:modconf('Fls')[1]/FlsConfigSet/FlsSectorList/FlsSector/FlsSector_{i}/FlsSectorStartaddress</Expression>\n")
                f.write("\t\t\t<Operations>\n")
                f.write('\t\t\t\t<Operation Type="SetValue">\n')
                f.write(f"\t\t\t\t\t<Expression>'{sector_address}'</Expression>\n")
                f.write("\t\t\t\t</Operation>\n")
                f.write("\t\t\t</Operations>\n")
                f.write("\t\t</Operation>\n\n")

            f.write("\t</Operations>\n\n")
            f.write("</Script>\n")
