import json
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = r"D:\Hefaj\DL\LatestChatbot\4\FinalSave" #140000 datapoints
# MODEL_PATH = r"D:\Hefaj\DL\LatestChatbot\4\Final_Save_4700_200000_Datapoints"

with open(f"{MODEL_PATH}/label_maps.json", "r", encoding="utf-8") as f:
    label_maps = json.load(f)



# import torch

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# MODEL_PATH = r"D:\Hefaj\DL\LatestChatbot\4\FinalSave"  # নতুন মডেল
# LABEL_MAPS_PATH = f"{MODEL_PATH}/label_maps.json"