import yaml

class Size:
    def B2KB2MB(size):
        if size>=1024 and size%1024==0:
            result=size/1024
            if result>=1024 and result%1024==0: 
                result=f"{int(result/1024)}MB"
            else:
                result=f"{int(result)}KB"
        else:
            result=f"{int(size)}B"  
        return result
    
class str2hex:
    def FormatAddr(address):
        faddress=hex(int(address,16))
        add=10-len(faddress)
        if add>0:
            faddress=faddress.replace("0x","0x"+"0"*add)
        faddress=faddress[:-8]+"_"+faddress[-8:-4]+"_"+faddress[-4:]
        return faddress

class yamlData :
    def data2ml(Data,mlFile):
        ml_data=yaml.dump(Data,sort_keys=False)
        with open (mlFile,"w") as f:
            f.write(ml_data.replace("'",""))


class layoutData:
    file_version=""
    sheet_name=""
    project_name=""
    start_address=""
    file_path=""

