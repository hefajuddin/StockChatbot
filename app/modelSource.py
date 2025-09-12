import json
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = r"D:\Hefaj\DL\LatestChatbot\3\FinalSave"

with open(f"{MODEL_PATH}/label_maps.json", "r", encoding="utf-8") as f:
    label_maps = json.load(f)

