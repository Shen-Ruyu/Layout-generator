from .yaml_parser_common import YamlParserBase

import json

class YamlParserEMMC(YamlParserBase):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.ltype="EMMC"

        self.state = {
            "BOOT_0_A_BOOT_1_B" : "_BOOT0_",
            "USER_AREA" : "_USER_AREA_"
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
                k = key.replace("HPCGEN2_", "").replace("BOOT0_", "").replace("BOOT1_", "").replace("USER_AREA_", "")
                bank = ""
                if "_A" == k[-2:]:
                    bank = 'a'
                    k = k[:-2]
                elif "_B" == k[-2:]:
                    bank = 'b'
                    k = k[:-2]
                if k in files:
                    if bank == 'a':
                        values_a[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "EMMC", "erase": True}
                    elif bank == 'b':
                        values_b[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "EMMC", "erase": True}
                    else:
                        values_a[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "EMMC", "erase": True}
                        values_b[k] = {"name": files[k], "address": self.yaml[key]['start_address'], "memory": "EMMC", "erase": True}

            return values_a, values_b
    
    def generate_bash(self, bash_file_banka, bash_file_bankb):
        """
        Generate a bash file which contains the list of address with the partition of each part of the layout
        """
        values_a = list()
        values_b = list()
        for key in self.yaml:
            bank = ""
            if "_A" == key[-2:]:
                bank = 'a'
            elif "_B" in key:
                bank = 'b'

            if "_BOOT0_" in key:
                values_a.append(key)
            elif "_BOOT1_" in key:
                values_b.append(key)
            elif bank == 'a':
                values_a.append(key)
            elif bank == 'b':
                values_b.append(key)
            else:
                values_a.append(key)
                values_b.append(key)

        with open(bash_file_banka, 'w') as f:
            f.write("# Attention!\n")
            f.write("# This file is generated!\n")
            f.write("# For changes, do not modify this file but the layout associated\n")
            f.write(f"# Layout version {self.version}\n\n")
            for val in values_a:
                partition = "mmcblk0p"
                if "BOOT0_" in val:
                    partition = "mmcblk0boot0p"
                elif "BOOT1_" in val:
                    partition = "mmcblk0boot1p"
                k = val.replace("HPCGEN2_", "").replace("BOOT0_", "").replace("BOOT1_", "").replace("USER_AREA_", "")
                k = k.lower()
                if k[0].isdigit():
                    k = f"_{k}"
                f.write(f"{k}={self.yaml[val]['start_address'].lower()}\n")
                if self.yaml[val]['partition']:
                    f.write(f"{k}_partition={partition}{self.yaml[val]['partition']}\n")
                f.write("\n")

        with open(bash_file_bankb, 'w') as f:
            f.write("# Attention!\n")
            f.write("# This file is generated!\n")
            f.write("# For changes, do not modify this file but the layout associated\n")
            f.write(f"# Layout version {self.version}\n\n")
            for val in values_b:
                partition = "mmcblk0p"
                if "BOOT0_" in val:
                    partition = "mmcblk0boot0p"
                elif "BOOT1_" in val:
                    partition = "mmcblk0boot1p"
                k = val.replace("HPCGEN2_", "").replace("BOOT0_", "").replace("BOOT1_", "").replace("USER_AREA_", "")
                k = k.lower()
                if k[0].isdigit():
                    k = f"_{k}"
                f.write(f"{k}={self.yaml[val]['start_address'].lower()}\n")
                if self.yaml[val]['partition']:
                    f.write(f"{k}_partition={partition}{self.yaml[val]['partition']}\n")
                f.write("\n")

    def generate_gtp_files(self, generate_path=None):
        """
        Generate the gtp files to create and format if needed the partitions
        """
        first_boot0_lba = None
        last_boot0_lba = None
        boot0_part = list()
        ext4_boot0_area_partitions = ['ext4_boot0_area_partitions=""']

        first_boot1_lba = None
        last_boot1_lba = None
        boot1_part = list()
        ext4_boot1_area_partitions = ['ext4_boot1_area_partitions=""']

        first_user_area_lba = None
        last_user_area_lba = None
        user_area_part = list()
        ext4_user_area_partitions = ['ext4_user_area_partitions=""']
        for key in self.yaml:
            name = key.lower().replace("hpcgen2_", "")
            if "BOOT0_" in key:
                if first_boot0_lba is None and self.yaml[key]["lba"]:
                    first_boot0_lba = self.yaml[key]["lba"]
                if self.yaml[key]["lba"] is not None:
                    last_boot0_lba = self.yaml[key]["lba"]
                if self.yaml[key]['partition'] and self.yaml[key]['partition'] != "-":
                    boot0_part.append(f'/dev/mmcblk0boot0p{self.yaml[key]["partition"]} : start={self.yaml[key]["lba"]},     size={int(self.yaml[key]["size"]/512)},     name="{name}"')
                if self.yaml[key]['fs']:
                    ext4_boot0_area_partitions.append(f'ext4_boot0_area_partitions="${{ext4_boot0_area_partitions}}  mmcblk0boot0p{self.yaml[key]["partition"]}"')
            elif "BOOT1_" in key:
                if first_boot1_lba is None and self.yaml[key]["lba"]:
                    first_boot1_lba = self.yaml[key]["lba"]
                if self.yaml[key]["lba"] is not None:
                    last_boot1_lba = self.yaml[key]["lba"]
                if self.yaml[key]['partition'] and self.yaml[key]['partition'] != "-":
                    boot1_part.append(f'/dev/mmcblk0boot1p{self.yaml[key]["partition"]} : start={self.yaml[key]["lba"]},     size={int(self.yaml[key]["size"]/512)},     name="{name}"')
                if self.yaml[key]['fs']:
                    ext4_boot1_area_partitions.append(f'ext4_boot1_area_partitions="${{ext4_boot1_area_partitions}}  mmcblk0boot1p{self.yaml[key]["partition"]}"')
            else:
                name = name.replace("user_area_", "")
                if first_user_area_lba is None and self.yaml[key]["lba"]:
                    first_user_area_lba = self.yaml[key]["lba"]
                if self.yaml[key]["lba"] is not None:
                    last_user_area_lba = self.yaml[key]["lba"]
                if self.yaml[key]['partition'] and self.yaml[key]['partition'] != "-":
                    user_area_part.append(f'/dev/mmcblk0p{self.yaml[key]["partition"]} : start={self.yaml[key]["lba"]},     size={int(self.yaml[key]["size"]/512)},     name="{name}"')
                if self.yaml[key]['fs']:
                    ext4_user_area_partitions.append(f'ext4_user_area_partitions="${{ext4_user_area_partitions}}  mmcblk0p{self.yaml[key]["partition"]}"')

        
        with open(f"{generate_path}/mmcblk0boot0-layout.txt", 'w') as f:
            f.write("label: gpt\n")
            f.write("device: /dev/mmcblk0boot0\n")
            f.write("unit: sectors\n")
            f.write(f"first-lba: {first_boot0_lba}\n")
            f.write(f"last-lba: {last_boot0_lba}\n\n")

            f.writelines("%s\n" % p for p in boot0_part)

        with open(f"{generate_path}/mmcblk0boot1-layout.txt", 'w') as f:
            f.write("label: gpt\n")
            f.write("device: /dev/mmcblk0boot1\n")
            f.write("unit: sectors\n")
            f.write(f"first-lba: {first_boot1_lba}\n")
            f.write(f"last-lba: {last_boot1_lba}\n\n")

            f.writelines("%s\n" % p for p in boot1_part)

        with open(f"{generate_path}/mmcblk0-layout.txt", 'w') as f:
            f.write("label: gpt\n")
            f.write("device: /dev/mmcblk0\n")
            f.write("unit: sectors\n")
            f.write(f"first-lba: {first_user_area_lba}\n")
            f.write(f"last-lba: {int(last_user_area_lba)}\n\n")

            f.writelines("%s\n" % p for p in user_area_part)

        with open(f"{generate_path}/ext4-partition", 'w') as f:
            f.writelines("%s\n" % p for p in ext4_boot0_area_partitions)
            f.writelines("%s\n" % p for p in ext4_boot1_area_partitions)
            f.writelines("%s\n" % p for p in ext4_user_area_partitions)

