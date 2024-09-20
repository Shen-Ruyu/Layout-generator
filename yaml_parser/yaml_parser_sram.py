from .yaml_parser_common import YamlParserBase

import json

class YamlParserSRAM(YamlParserBase):
    def __init__(self, yaml_file):
        super().__init__(yaml_file)
        self.ltype="SRAM"

    def generate_ldscript(self, ldscript_file):
        """
        Generate a ldscript use for all classic memory definition
        """
        with open(ldscript_file, 'w') as f:
            f.write("/* Attention!\n")
            f.write(" * This file is generated!\n")
            f.write(" * For changes, do not modify this file but the layout associated\n")
            f.write(f" * SRAM Layout version {self.version}\n\n")
            f.write(" */\n\n")
            f.write("MEMORY\n")
            f.write("{\n")
            # f.write("\treset           (RX)  : org = 0x00000800, len = 0x200\n")
            # f.write("\t/* Note:\n")
            # f.write("\t * We only create one memory\n")
            # f.write("\t * and alias every other region to this one (c.f. below REGION_ALIAS\n")
            # f.write("\t * directives).\n")
            # f.write("\t */\n\n")

            for key in self.yaml:
                if self.yaml[key]["rights"] == "Ignored":
                    continue

                k = key.replace("HPCGEN2_SRAM_", "")
                start = self.yaml[key]["start_address"]
                end = self.yaml[key]["end_address"]
                len_k = hex(self.yaml[key]['size']).upper().replace("0X", "0x")
                rights = self.yaml[key]['rights']
                if rights:
                    rights = f"\t({rights})"
                else:
                    rights = ""
                if k in ("IPL", "METHAIMAGE", "PROPAIMAGE"):
                    start = hex(int(start, 16) + 0xC00).upper().replace("0X", "0x")
                    len_k = hex(int(end, 16) - int(start, 16)).upper().replace("0X", "0x")
                if k.startswith('RAM') or "DTCM" in k or "RESET" in k:
                    k=k
                elif "LLCE" not in k:
                    k = k.lower()
                if "LLCE_SYNC_AREA" in k:
                    k = k.lower()
                f.write(f"\t{k.ljust(36)}\t: org = {start}, len = {len_k.ljust(10)}\t /* {start} - {end} */\n")
            f.write("}\n")
