import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from safetensors.torch import load_file
from .modelSource import DEVICE, MODEL_PATH, label_maps

class MultiTaskXLMRModel(nn.Module):
    def __init__(self, model_checkpoint, num_ner_labels, num_intent_labels,
                 num_sentiment_labels, num_priceStatus_labels,
                 num_language_labels, num_context_labels):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_checkpoint)
        hidden_size = self.backbone.config.hidden_size

        self.ner_classifier       = nn.Linear(hidden_size, num_ner_labels)
        self.intent_classifier    = nn.Linear(hidden_size, num_intent_labels)
        self.sentiment_classifier = nn.Linear(hidden_size, num_sentiment_labels)
        self.price_classifier     = nn.Linear(hidden_size, num_priceStatus_labels)
        self.language_classifier  = nn.Linear(hidden_size, num_language_labels)
        self.context_classifier   = nn.Linear(hidden_size, num_context_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        seq_out = outputs.last_hidden_state
        pooled_out = seq_out[:,0,:]

        ner_logits       = self.ner_classifier(seq_out)
        intent_logits    = self.intent_classifier(pooled_out)
        sentiment_logits = self.sentiment_classifier(pooled_out)
        price_logits     = self.price_classifier(pooled_out)
        language_logits  = self.language_classifier(pooled_out)
        context_logits   = self.context_classifier(pooled_out)

        return ner_logits, intent_logits, sentiment_logits, price_logits, language_logits, context_logits

# Load model & tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
model = MultiTaskXLMRModel(
    model_checkpoint=label_maps["model_checkpoint"],
    num_ner_labels=len(label_maps["ner_label2id"]),
    num_intent_labels=len(label_maps["intent_label2id"]),
    num_sentiment_labels=len(label_maps["sentiment_label2id"]),
    num_priceStatus_labels=len(label_maps["priceStatus_label2id"]),
    num_language_labels=len(label_maps["language_label2id"]),
    num_context_labels=len(label_maps["context_label2id"])
)

state_dict = load_file(f"{MODEL_PATH}/model.safetensors")
model.load_state_dict(state_dict)
model.to(DEVICE)
model.eval()
