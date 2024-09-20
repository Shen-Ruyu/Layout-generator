import yaml

HEADER = (
        " *\n"
        " * \\brief ##TYPE## layout addresses definition\n"
        " *\n"
        " * This file contains the implementation of the ##TYPE## addresses \n"
        " * \n"
        " * \\author Continental Automotive , Toulouse \n"
        " * \n"
        " * Copyright 2022 - 2022 Continental \n"
        " * All rights exclusively reserved for Continental, \n"
        " * unless expressly agreed to otherwise. \n"
        " */ \n\n\n"
        "// Attention!\n"
        "// This file is generated!\n"
        "// For changes, do not modify this file but the layout associated\n"
        "// Layout version ##VERSION##\n\n\n"
        "#ifndef ##TYPE##_LAYOUT_ADDRESS_H\n"
        "#define ##TYPE##_LAYOUT_ADDRESS_H\n\n")

FOOTER = "\n#endif // ##TYPE##_LAYOUT_ADDRESS_H\n"

PYTHON_HEADER = (
        "#!/usr/bin/env python\n\n"
        '"""\n'
        "##PYTHON_FILE##\n"
        "Copyright (c) Continental\n\n"
        "##TYPE## address constants\n"
        '"""\n\n'
        "# Attention!\n"
        "# This file is generated!\n"
        "# For changes, do not modify this file but the layout associated\n"
        "# Layout version ##VERSION##\n\n")


class YamlParserBase:

    def __init__(self, yaml_file):
        self.yaml_file=yaml_file
        self.ltype=""
        self.version=""
        self.state={}
        self.yaml=dict()

    def clean_name(self, name):
        """
        Clean name from yaml
        Return the cleaned name in upper case and the name before the upper case
        """
        name_ref = name
        n = name.upper()

        if len(n) > 80:
            return None, None

        return n, name_ref
    
    def MBKB2B(self,size:str):
        # size=size.upper()
        if "MB" in size:
            result=int(size.replace("MB",""))
            result=int(result*1024*1024)
        elif "KB" in size:
            result=int(size.replace("KB",""))
            result=int(result*1024)
        elif "B" in size:
            result=int(size.replace("B",""))
        return result

    def parser_yaml(self):
        with open(self.yaml_file,"r") as ym:
            bank="_"
            ym=yaml.load(ym,Loader=yaml.FullLoader)
            self.ltype=ym["name"].upper()
            self.version=str(ym["version"])
            self.yaml={}
            for block in ym["blocks"]:
                name,name_ref=self.clean_name(block["name"])
                size=self.MBKB2B(block["size"])
                start_address=block['start_address']
                end_address=block['end_address']
                if "bank" in block and block["bank"] in self.state:
                    bank=self.state[block["bank"]]   
                if self.ltype=="SRAM":
                    name="HPCGEN2_SRAM_"+name
                elif self.ltype=="NOR":
                    name="HPCGEN2_"+name+bank
                elif self.ltype=="EMMC":
                    if bank == "_BOOT0_":
                        other_name="HPCGEN2"+"_BOOT1_"+name
                        self.yaml[other_name]=block
                        self.yaml[other_name]['start_address']=hex(start_address)
                        self.yaml[other_name]['end_address']=hex(end_address)
                        self.yaml[other_name]["name"]=name_ref
                        self.yaml[other_name]["size"]=size
                    else:
                        pass
                    name="HPCGEN2"+bank+name
                self.yaml[name]=block
                self.yaml[name]["name"]=name_ref
                self.yaml[name]['start_address']=hex(start_address)
                self.yaml[name]['end_address']=hex(end_address)
                self.yaml[name]["size"]=size
                
    def generate_header(self, header_file):
        """
        Generate a header file usable in C/C++ which contains the list of address (start, end) and the size of each element of layout
        """
        with open(header_file, 'w') as f:
            f.write("/**\n"
                    f" * \\file {header_file}\n")
            f.write(HEADER.replace("##TYPE##", self.ltype).replace("##VERSION##", self.version))

            for key in self.yaml:
                # Add '_' at the end of the name
                k = key
                if k[-1] != '_':
                    k += '_'

                start=self.yaml[key]['start_address']
                end=self.yaml[key]['end_address']
                size=self.yaml[key]['size']
                

                f.write(f"/*****   {self.yaml[key]['name']}   ****/\n")
                f.write(f"#define {k}START_ADDRESS  {start}u\n")
                f.write(f"#define {k}END_ADDRESS    {end}u\n")
                f.write(f"#define {k}SIZE          {size}u\n")
                if 'partition' in self.yaml[key] and self.yaml[key]['partition'] and self.yaml[key]['partition'] != "-":
                    partition = "mmcblk0p"
                    if "BOOT0_" in k:
                        partition = "mmcblk0boot0p"
                    elif "BOOT1_" in k:
                        partition = "mmcblk0boot1p"
                    f.write(f"#define {k}PARTITION \"/dev/{partition}{self.yaml[key]['partition']}\"\n")
                f.write("\n")

            f.write(FOOTER.replace("##TYPE##", self.ltype))

    def generate_python(self, python_file):
        """
        Generate a file usable in python which contains the list of address (start, end) and the size of each element of layout
        """
        with open(python_file, 'w') as f:
            f.write(PYTHON_HEADER.replace("##TYPE##", self.ltype).replace("##PYTHON_FILE##", python_file).replace("##VERSION##", self.version))

            for key in self.yaml:
                # Remove '_' at the end of the name
                k = key
                if k[-1] == '_':
                    k = k[:-1]
                              
                # Write the start address of the element
                f.write(f"{k}={self.yaml[key]['start_address'].lower()}\n")
                # Add the number of the partition if exists
                if 'partition' in self.yaml[key] and self.yaml[key]['partition'] and self.yaml[key]['partition'] != "-":
                    f.write(f"{k}_partition={self.yaml[key]['partition']}\n")
                    f.write("\n")
                # Add the size of the element if related to the NVM or the DA4C
                if ('NVM' in k) or ('DA4C' in k):
                    f.write(f"{k}_SIZE={self.yaml[key]['size']}\n")

    def generate_logical_block(self):
        """
        Generate the logical block with address and partition
        """
        values_a = list()
        values_b = list()
        for key in self.yaml:
            bank = ""
            if "_A" == key[-2:] or "_A_" == key[-3:]:
                bank = 'a'
            elif "_B" in key[-2:] or "_B_" == key[-3:]:
                bank = 'b'

            if bank == 'a':
                values_a.append(key)
            elif bank == 'b':
                values_b.append(key)
            else:
                values_a.append(key)
                values_b.append(key)

        lb_bank = list()
        for val in values_a:
            lb_key = ""
            val_b = val
            if self.ltype == "EMMC":
                if "BOOT0_" in val:
                    continue
                elif "BOOT1_" in val:
                    continue
                partition = "/dev/mmcblk0p"
                lb_key = val.replace("HPCGEN2_", "").replace("BOOT0_", "").replace("BOOT1_", "").replace("USER_AREA_", "")
                if "_A" == lb_key[-2:]:
                    lb_key = lb_key[:-2]
                    val_b = val[:-2] + "_B"
                if self.yaml[val]['partition']:
                    partition_a = f"{partition}{self.yaml[val]['partition']}"
                    partition_b = f"{partition}{self.yaml[val_b]['partition']}"
                    offset_a = 0
                    offset_b = 0
                else:
                    offset_a = int(self.yaml[val]['start_address'],16)
                    offset_b = int(self.yaml[val_b]['start_address'],16)
            else:
                partition_a = "/dev/mtd0"
                partition_b = "/dev/mtd0"
                lb_key = val.replace("HPCGEN2_", "")
                if "_A_" == lb_key[-3:]:
                    lb_key = lb_key[:-3]
                    val_b = val[:-3] + "_B_"
                if "_" == lb_key[-1:]:
                    lb_key = lb_key[:-1]
                offset_a = int(self.yaml[val]['start_address'],16)
                offset_b = int(self.yaml[val_b]['start_address'],16)

            if self.yaml[val]["lb_id"] and self.yaml[val]["lb_id"] != None:
                if self.ltype == "EMMC":
                    if "USER_AREA" in val:
                        ltype = "eMMC_user"
                    else:
                        ltype = "eMMC_boot"
                else:
                    ltype = self.ltype
                lb_bank.append({
                                "logicalBlockId": self.yaml[val]["lb_id"],
                                 "name": lb_key,
                                 "packageType": "image",
                                 "mandatoryInOdx": self.yaml[val]["update"] == True,
                                 "banks": [
                                     {
                                         "bank": "A",
                                         "segments": [
                                             {
                                                "blockDeviceType": ltype,
                                                "blockDevicePath": partition_a,
                                                "offset": offset_a,
                                                "size": self.yaml[val]['size']
                                             }
                                         ]
                                     },
                                     {
                                         "bank": "B",
                                         "segments": [
                                             {
                                                "blockDeviceType": ltype,
                                                "blockDevicePath": partition_b,
                                                "offset": offset_b,
                                                "size": self.yaml[val_b]['size']
                                             }
                                         ]
                                     }
                                 ]})

        return lb_bank



