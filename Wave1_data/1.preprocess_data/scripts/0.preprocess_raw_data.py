#!/usr/bin/env python
# coding: utf-8

# This notebook pre-processes the data to be available in the repo path.

# In[1]:


import glob
import json
import pathlib
import shutil

import pandas as pd
import tqdm

# In[2]:


# absolute path to the raw data directory (only works on this machine)
path_to_raw_data = pathlib.Path(
    "/home/lippincm/Desktop/18TB/Saguaro_pyroptosis_wave1/"
).resolve(strict=True)

# repository data directory to access the data faster
path_to_repo_data = pathlib.Path("../../../data/raw/").resolve()
path_to_repo_data.mkdir(exist_ok=True, parents=True)

# recurse through the directory and find all the .tif or .tiff files
list_of_files = glob.glob(str(path_to_raw_data / "**/Image/*.tif*"), recursive=True)
print(f"Found {len(list_of_files)} files")


# In[3]:


# copy the files to the repository data directory
for file in tqdm.tqdm(list_of_files):
    file_path = pathlib.Path(file)
    file_parent = file_path.parent
    file_parent_path = path_to_repo_data / pathlib.Path(
        str(file_parent).split("/")[-2]
        / pathlib.Path(str(file_path.stem).split("T")[0].replace("F", "_F"))
    )
    file_parent_path.mkdir(exist_ok=True, parents=True)
    new_file_path = file_parent_path / file_path.name
    if not new_file_path.exists():
        # copy the file to the repository data directory
        shutil.copy(file_path, new_file_path)


# In[4]:


# verify that the number of images in are the same as the number of files copied
list_of_new_files = glob.glob(str(path_to_repo_data / "**/*.tif*"), recursive=True)
print(f"There were {len(list_of_files)} original files")
print(f"We copied {len(list_of_new_files)} files")
assert len(list_of_files) == len(list_of_new_files)


# In[5]:


# make a df out of the file names
df = pd.DataFrame(list_of_new_files, columns=["file_path"])
df.insert(0, "file_name", df["file_path"].apply(lambda x: pathlib.Path(x).name))
df.insert(0, "Plate", df["file_path"].apply(lambda x: x.split("/")[7]))
df.insert(0, "Well", df["file_name"].apply(lambda x: x.split("F")[0].split("W")[-1]))
df.insert(0, "FOV", df["file_name"].apply(lambda x: x.split("T")[0].split("F")[-1]))
df.drop("file_path", axis=1, inplace=True)
df.drop("file_name", axis=1, inplace=True)
# split the plate into time and date
df.insert(2, "Date_Time", df["Plate"].apply(lambda x: x.strip("_").replace("T", "")))
# format the time into YYYY-MM-DD HH:MM:SS
df["Date_Time"] = pd.to_datetime(df["Date_Time"], format="%Y%m%d%H%M%S")

# sort by Date, Time, Plate, Well, FOV
df.sort_values(by=["Date_Time", "Plate", "Well", "FOV"], inplace=True)
df.reset_index(drop=True, inplace=True)
df.head()


# In[6]:


# well dictionary for mapping
well_map = {
    "0001": "A01",
    "0002": "A02",
    "0003": "A03",
    "0004": "A04",
    "0005": "A05",
    "0006": "A06",
    "0007": "A07",
    "0008": "A08",
    "0009": "A09",
    "0010": "A10",
    "0011": "A11",
    "0012": "A12",
    "0013": "A13",
    "0014": "A14",
    "0015": "A15",
    "0016": "A16",
    "0017": "A17",
    "0018": "A18",
    "0019": "A19",
    "0020": "A20",
    "0021": "A21",
    "0022": "A22",
    "0023": "A23",
    "0024": "A24",
    "0025": "B01",
    "0026": "B02",
    "0027": "B03",
    "0028": "B04",
    "0029": "B05",
    "0030": "B06",
    "0031": "B07",
    "0032": "B08",
    "0033": "B09",
    "0034": "B10",
    "0035": "B11",
    "0036": "B12",
    "0037": "B13",
    "0038": "B14",
    "0039": "B15",
    "0040": "B16",
    "0041": "B17",
    "0042": "B18",
    "0043": "B19",
    "0044": "B20",
    "0045": "B21",
    "0046": "B22",
    "0047": "B23",
    "0048": "B24",
    "0049": "C01",
    "0050": "C02",
    "0051": "C03",
    "0052": "C04",
    "0053": "C05",
    "0054": "C06",
    "0055": "C07",
    "0056": "C08",
    "0057": "C09",
    "0058": "C10",
    "0059": "C11",
    "0060": "C12",
    "0061": "C13",
    "0062": "C14",
    "0063": "C15",
    "0064": "C16",
    "0065": "C17",
    "0066": "C18",
    "0067": "C19",
    "0068": "C20",
    "0069": "C21",
    "0070": "C22",
    "0071": "C23",
    "0072": "C24",
    "0073": "D01",
    "0074": "D02",
    "0075": "D03",
    "0076": "D04",
    "0077": "D05",
    "0078": "D06",
    "0079": "D07",
    "0080": "D08",
    "0081": "D09",
    "0082": "D10",
    "0083": "D11",
    "0084": "D12",
    "0085": "D13",
    "0086": "D14",
    "0087": "D15",
    "0088": "D16",
    "0089": "D17",
    "0090": "D18",
    "0091": "D19",
    "0092": "D20",
    "0093": "D21",
    "0094": "D22",
    "0095": "D23",
    "0096": "D24",
    "0097": "E01",
    "0098": "E02",
    "0099": "E03",
    "0100": "E04",
    "0101": "E05",
    "0102": "E06",
    "0103": "E07",
    "0104": "E08",
    "0105": "E09",
    "0106": "E10",
    "0107": "E11",
    "0108": "E12",
    "0109": "E13",
    "0110": "E14",
    "0111": "E15",
    "0112": "E16",
    "0113": "E17",
    "0114": "E18",
    "0115": "E19",
    "0116": "E20",
    "0117": "E21",
    "0118": "E22",
    "0119": "E23",
    "0120": "E24",
    "0121": "F01",
    "0122": "F02",
    "0123": "F03",
    "0124": "F04",
    "0125": "F05",
    "0126": "F06",
    "0127": "F07",
    "0128": "F08",
    "0129": "F09",
    "0130": "F10",
    "0131": "F11",
    "0132": "F12",
    "0133": "F13",
    "0134": "F14",
    "0135": "F15",
    "0136": "F16",
    "0137": "F17",
    "0138": "F18",
    "0139": "F19",
    "0140": "F20",
    "0141": "F21",
    "0142": "F22",
    "0143": "F23",
    "0144": "F24",
    "0145": "G01",
    "0146": "G02",
    "0147": "G03",
    "0148": "G04",
    "0149": "G05",
    "0150": "G06",
    "0151": "G07",
    "0152": "G08",
    "0153": "G09",
    "0154": "G10",
    "0155": "G11",
    "0156": "G12",
    "0157": "G13",
    "0158": "G14",
    "0159": "G15",
    "0160": "G16",
    "0161": "G17",
    "0162": "G18",
    "0163": "G19",
    "0164": "G20",
    "0165": "G21",
    "0166": "G22",
    "0167": "G23",
    "0168": "G24",
    "0169": "H01",
    "0170": "H02",
    "0171": "H03",
    "0172": "H04",
    "0173": "H05",
    "0174": "H06",
    "0175": "H07",
    "0176": "H08",
    "0177": "H09",
    "0178": "H10",
    "0179": "H11",
    "0180": "H12",
    "0181": "H13",
    "0182": "H14",
    "0183": "H15",
    "0184": "H16",
    "0185": "H17",
    "0186": "H18",
    "0187": "H19",
    "0188": "H20",
    "0189": "H21",
    "0190": "H22",
    "0191": "H23",
    "0192": "H24",
    "0193": "I01",
    "0194": "I02",
    "0195": "I03",
    "0196": "I04",
    "0197": "I05",
    "0198": "I06",
    "0199": "I07",
    "0200": "I08",
    "0201": "I09",
    "0202": "I10",
    "0203": "I11",
    "0204": "I12",
    "0205": "I13",
    "0206": "I14",
    "0207": "I15",
    "0208": "I16",
    "0209": "I17",
    "0210": "I18",
    "0211": "I19",
    "0212": "I20",
    "0213": "I21",
    "0214": "I22",
    "0215": "I23",
    "0216": "I24",
    "0217": "J01",
    "0218": "J02",
    "0219": "J03",
    "0220": "J04",
    "0221": "J05",
    "0222": "J06",
    "0223": "J07",
    "0224": "J08",
    "0225": "J09",
    "0226": "J10",
    "0227": "J11",
    "0228": "J12",
    "0229": "J13",
    "0230": "J14",
    "0231": "J15",
    "0232": "J16",
    "0233": "J17",
    "0234": "J18",
    "0235": "J19",
    "0236": "J20",
    "0237": "J21",
    "0238": "J22",
    "0239": "J23",
    "0240": "J24",
    "0241": "K01",
    "0242": "K02",
    "0243": "K03",
    "0244": "K04",
    "0245": "K05",
    "0246": "K06",
    "0247": "K07",
    "0248": "K08",
    "0249": "K09",
    "0250": "K10",
    "0251": "K11",
    "0252": "K12",
    "0253": "K13",
    "0254": "K14",
    "0255": "K15",
    "0256": "K16",
    "0257": "K17",
    "0258": "K18",
    "0259": "K19",
    "0260": "K20",
    "0261": "K21",
    "0262": "K22",
    "0263": "K23",
    "0264": "K24",
    "0265": "L01",
    "0266": "L02",
    "0267": "L03",
    "0268": "L04",
    "0269": "L05",
    "0270": "L06",
    "0271": "L07",
    "0272": "L08",
    "0273": "L09",
    "0274": "L10",
    "0275": "L11",
    "0276": "L12",
    "0277": "L13",
    "0278": "L14",
    "0279": "L15",
    "0280": "L16",
    "0281": "L17",
    "0282": "L18",
    "0283": "L19",
    "0284": "L20",
    "0285": "L21",
    "0286": "L22",
    "0287": "L23",
    "0288": "L24",
    "0289": "M01",
    "0290": "M02",
    "0291": "M03",
    "0292": "M04",
    "0293": "M05",
    "0294": "M06",
    "0295": "M07",
    "0296": "M08",
    "0297": "M09",
    "0298": "M10",
    "0299": "M11",
    "0300": "M12",
    "0301": "M13",
    "0302": "M14",
    "0303": "M15",
    "0304": "M16",
    "0305": "M17",
    "0306": "M18",
    "0307": "M19",
    "0308": "M20",
    "0309": "M21",
    "0310": "M22",
    "0311": "M23",
    "0312": "M24",
    "0313": "N01",
    "0314": "N02",
    "0315": "N03",
    "0316": "N04",
    "0317": "N05",
    "0318": "N06",
    "0319": "N07",
    "0320": "N08",
    "0321": "N09",
    "0322": "N10",
    "0323": "N11",
    "0324": "N12",
    "0325": "N13",
    "0326": "N14",
    "0327": "N15",
    "0328": "N16",
    "0329": "N17",
    "0330": "N18",
    "0331": "N19",
    "0332": "N20",
    "0333": "N21",
    "0334": "N22",
    "0335": "N23",
    "0336": "N24",
    "0337": "O01",
    "0338": "O02",
    "0339": "O03",
    "0340": "O04",
    "0341": "O05",
    "0342": "O06",
    "0343": "O07",
    "0344": "O08",
    "0345": "O09",
    "0346": "O10",
    "0347": "O11",
    "0348": "O12",
    "0349": "O13",
    "0350": "O14",
    "0351": "O15",
    "0352": "O16",
    "0353": "O17",
    "0354": "O18",
    "0355": "O19",
    "0356": "O20",
    "0357": "O21",
    "0358": "O22",
    "0359": "O23",
    "0360": "O24",
    "0361": "P01",
    "0362": "P02",
    "0363": "P03",
    "0364": "P04",
    "0365": "P05",
    "0366": "P06",
    "0367": "P07",
    "0368": "P08",
    "0369": "P09",
    "0370": "P10",
    "0371": "P11",
    "0372": "P12",
    "0373": "P13",
    "0374": "P14",
    "0375": "P15",
    "0376": "P16",
    "0377": "P17",
    "0378": "P18",
    "0379": "P19",
    "0380": "P20",
    "0381": "P21",
    "0382": "P22",
    "0383": "P23",
    "0384": "P24",
}
# write the well map to a json file
path_to_repo_data = pathlib.Path("../../../data/processed/").resolve()
path_to_repo_data.mkdir(exist_ok=True, parents=True)
with open(path_to_repo_data / "well_map.json", "w") as f:
    json.dump(well_map, f)
# map the well to the well_map
df["Well"] = df["Well"].map(well_map)
df.head()


# In[7]:


print(f"There are {len(df['Well'].unique())} wells.")
print(f"There are {len(df['FOV'].unique())} fields of view.")
print(f"There are {len(df['Plate'].unique())} plates.")
print(f"There are {len(df['Date_Time'].unique())} unique time points.")
print("The times are:\n")
print(df["Date_Time"].unique())


# In[8]:


# check that there are
# 5 fovs * 5 channels * 96 wells = 2400 images per plate
# get the dirs in the data directory
dirs = glob.glob(str(pathlib.Path("../../../data/raw") / "*"))
dirs = [x for x in dirs if pathlib.Path(x).is_dir()]
plate_dict = {
    "plate_name": [],
    "num_files": [],
}
for dir in dirs:
    # get the files in the dir
    files = glob.glob(str(pathlib.Path(dir) / "*"))
    files = [x for x in files if pathlib.Path(x).is_file()]
    plate_dict["plate_name"].append(pathlib.Path(dir).name)
    plate_dict["num_files"].append(len(files))
plate_df = pd.DataFrame(plate_dict)
plate_df["correct_num_files"] = plate_df["num_files"] == 2400
# sort by correct_num_files
plate_df.sort_values(by="correct_num_files", inplace=True)
plate_df.reset_index(drop=True, inplace=True)
plate_df


# In[9]:


# get all files in the 20241026T164425_ dir
files = glob.glob(str(pathlib.Path("../../../data/raw/20241026T164425_") / "*"))
files = [pathlib.Path(x).stem for x in files if pathlib.Path(x).is_file()]
df = pd.DataFrame(files, columns=["file_name"])
df["well"] = df["file_name"].str.split("F").str[0]
df["FOV"] = df["file_name"].str.split("F").str[1].str.split("T").str[0]
df["channel"] = df["file_name"].str.split("F").str[1].str.split("Z001").str[1]
# sort by well, FOV, channel
df.sort_values(by=["well", "FOV", "channel"], inplace=True)

# get the value counts for well, FOV
df[["well", "FOV"]].value_counts().sort_values()


# In[10]:


# get FOV 4 and well 0318 in the df
df[(df["well"] == "W0321")]


# In[11]:


# get FOV 4 and well 0318 in the df
df[(df["well"] == "W0322")]


# In[12]:


# get all files in the 20241025T045229_ dir
files = glob.glob(str(pathlib.Path("../../../data/raw/20241025T045229_") / "*"))
files = [pathlib.Path(x).stem for x in files if pathlib.Path(x).is_file()]
df = pd.DataFrame(files, columns=["file_name"])
df["well"] = df["file_name"].str.split("F").str[0]
df["FOV"] = df["file_name"].str.split("F").str[1].str.split("T").str[0]
df["channel"] = df["file_name"].str.split("F").str[1].str.split("Z001").str[1]
# sort by well, FOV, channel
df.sort_values(by=["well", "FOV", "channel"], inplace=True)

# get the value counts for well, FOV
df[["well", "FOV"]].value_counts().reset_index().sort_values(by=["count"])


# In[13]:


# get FOV 4 and well 0318 in the df
df[(df["well"] == "W0318")]


# In[14]:


# get FOV 4 and well 0318 in the df
df[(df["well"] == "W0319")]
