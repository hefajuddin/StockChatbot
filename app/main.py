from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch

from app.model import model, tokenizer
from app.config import DEVICE, label_maps
from app.preprocess import convert_sentence
from app.decode import decode_ner_confident, get_label

app = FastAPI(title="Stock Chatbot Intent & NER API", version="2.0")


# ===================== Request / Response Models =====================
class APIRequestItem(BaseModel):
    text: str

class APIRequest(BaseModel):
    inputs: List[APIRequestItem]

class Arguments(BaseModel):
    trading_codes: List[str]
    marketType: List[str]
    stockExchange: List[str]

class Result(BaseModel):
    intent: str
    arguments: Arguments
    sentiment: str
    language: str
    status: str
    context: str

class APIResponseItem(BaseModel):
    results: Result

class APIResponse(BaseModel):
    results: List[APIResponseItem]


# ===================== Inference Function =====================
async def infer_batch(text_list: List[str]) -> List[dict]:
    # Convert & lowercase safely
    texts = [convert_sentence(t).lower() for t in text_list]

    # Tokenize
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=64
    )
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs)

    results = []
    for i, text in enumerate(texts):
        ner_logits = logits[0][i:i+1]
        intent_logits = logits[1][i:i+1]
        sentiment_logits = logits[2][i:i+1]
        priceStatus_logits = logits[3][i:i+1]
        language_logits = logits[4][i:i+1]
        context_logits = logits[5][i:i+1]

        ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

        arguments = {
            "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
            "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
            "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
        }

        intent_label = get_label(intent_logits, label_maps["intent_label2id"])
        sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
        priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
        language_label = get_label(language_logits, label_maps["language_label2id"])
        context_label = get_label(context_logits, label_maps["context_label2id"])

        result = {
            "results": {
                "intent": intent_label,
                "arguments": arguments,
                "sentiment": sentiment_label,
                "language": language_label,
                "status": priceStatus_label,
                "context": context_label
            }
        }
        results.append(result)

    return results


# ===================== API Endpoint =====================
@app.post("/predict_price", response_model=APIResponse)
async def predict_price(request: APIRequest):
    if not request.inputs:
        raise HTTPException(status_code=400, detail="Input list is empty")

    text_list = [item.text for item in request.inputs if item.text.strip()]
    if not text_list:
        raise HTTPException(status_code=400, detail="All texts are empty")

    results = await infer_batch(text_list)
    return {"results": results}
