import torch
import torch.nn.functional as F
from .config import label_maps
from .model import tokenizer

def decode_ner_confident(text, ner_logits, label_map):
    id2label = {v: k for k, v in label_map.items()}
    encoding = tokenizer(text, return_tensors="pt", return_offsets_mapping=True, truncation=True, max_length=64)
    tokens = tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])
    word_ids = encoding.word_ids()
    probs = F.softmax(ner_logits[0], dim=-1)

    results = []
    current_word_idx = None
    current_word_tokens = []
    current_probs = []

    for idx, word_idx in enumerate(word_ids):
        if word_idx is None:
            continue
        token = tokens[idx]
        token_prob = probs[idx]
        if word_idx != current_word_idx:
            if current_word_tokens:
                avg_probs = torch.stack(current_probs).mean(dim=0)
                label_id = torch.argmax(avg_probs).item()
                label = id2label[label_id]
                word_text = tokenizer.convert_tokens_to_string(current_word_tokens).replace(" ", "")
                results.append({"text": word_text, "tag": label})
            current_word_idx = word_idx
            current_word_tokens = [token]
            current_probs = [token_prob]
        else:
            current_word_tokens.append(token)
            current_probs.append(token_prob)

    if current_word_tokens:
        avg_probs = torch.stack(current_probs).mean(dim=0)
        label_id = torch.argmax(avg_probs).item()
        label = id2label[label_id]
        word_text = tokenizer.convert_tokens_to_string(current_word_tokens).replace(" ", "")
        results.append({"text": word_text, "tag": label})

    return results

def get_label(logits, label_map):
    pred = torch.argmax(logits, dim=1).item()
    return list(label_map.keys())[pred]
