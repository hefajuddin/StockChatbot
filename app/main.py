from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List
import torch
import httpx
import itertools

from app.model import model, tokenizer
from app.modelSource import DEVICE, label_maps
from app.preprocess import prepare_text_for_infer
from app.decode import decode_ner_confident, get_label
from app.config import LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
from app.utils.response_formatter import build_general_response, filter_priceList

# ================== CONFIG ==================
auth_token: str | None = None  # global token storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
bearer_scheme = HTTPBearer()

app = FastAPI(title="Intent & NER API", version="2.0")

# ================== MODELS ==================
class LoginRequest(BaseModel):
    loginId: str
    password: str
    deviceId: str

class LoginResponse(BaseModel):
    token: str

class APIRequestItem(BaseModel):
    text: str

class APIRequest(BaseModel):
    inputs: List[APIRequestItem]

class APIResponseItemSimple(BaseModel):
    results: dict  # শুধু generalResponse রাখব
    priceList: List[dict]

class APIResponseSimple(BaseModel):
    results: List[APIResponseItemSimple]


# ================== LOGIN ==================
@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    global auth_token
    async with httpx.AsyncClient() as client:
        response = await client.post(LOGIN_ENDPOINT, json=request.dict())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    data = response.json()
    token = data.get("data", {}).get("accessToken")
    if not token:
        raise HTTPException(status_code=500, detail="Token not found")
    auth_token = token
    return {"token": token}


# ================== DEPENDENCY ==================
def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    global auth_token
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authorized")
    token = credentials.credentials
    if token != auth_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token


# ================== INFERENCE ==================
@app.post("/predict_batch", response_model=APIResponseSimple, tags=["Prediction"])
async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
    if not request.inputs:
        raise HTTPException(status_code=400, detail="Input list is empty")
    text_list = [item.text for item in request.inputs if item.text.strip()]
    if not text_list:
        raise HTTPException(status_code=400, detail="All texts are empty")

    results = await infer_batch(text_list, token)
    return {"results": results}


async def infer_batch(text_list: List[str], token: str) -> List[dict]:
    # ---- preprocess + tokenize just like training ----
    texts = [prepare_text_for_infer(t) for t in text_list]
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs)

    results = []
    for i, text in enumerate(texts):
        ner_logits, intent_logits, sentiment_logits, priceStatus_logits, language_logits, context_logits = (
            logits[0][i:i+1], logits[1][i:i+1], logits[2][i:i+1],
            logits[3][i:i+1], logits[4][i:i+1], logits[5][i:i+1]
        )

        ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])
        arguments = {
            "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
            "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
            "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
        }
        
        tradingCodes = arguments["trading_codes"]
        marketTypes = arguments["marketType"]
        stockExchanges = arguments["stockExchange"]
        intent_label = get_label(intent_logits, label_maps["intent_label2id"])
        sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
        priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
        language_label = get_label(language_logits, label_maps["language_label2id"])
        context_label = get_label(context_logits, label_maps["context_label2id"])

        # === Endpoint Mapping ===
        if intent_label == 'sharePrice':
            endpoint = SHAREPRICE_ENDPOINT
        elif intent_label == 'portfolio':
            endpoint = PORTFOLIO_ENDPOINT
        elif intent_label == 'balance':
            endpoint = BALANCE_ENDPOINT
        else:
            endpoint = None

        priceList = []
        headers = {"Authorization": f"Bearer {token}"}
        combos = list(itertools.product(
            arguments["stockExchange"] or ["dse"],
            arguments["marketType"] or ["public"],
            arguments["trading_codes"] or []
        ))

         # === API Call (only if trading_codes exist) ===
        if endpoint and arguments["trading_codes"]:
            async with httpx.AsyncClient() as client:
                for se, mt, tc in combos:
                    url = f"{endpoint}/{se}/{mt}/{tc}"
                    try:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            priceList.append(resp.json())
                        else:
                            priceList.append({
                                "error": f"API returned {resp.status_code}",
                                "details": resp.text,
                                "text": text
                            })
                    except Exception as e:
                        priceList.append({
                            "error": str(e),
                            "text": text
                        })

        # === Always build response ===
        generalResponse = build_general_response(
            language_label, sentiment_label, intent_label, priceStatus_label, arguments, combos
        )

        # # === Special Case: price_status, se, mt আছে কিন্তু trading_code নাই ===
        # if intent_label == "sharePrice" and priceStatus_label and (arguments["marketType"] or arguments["stockExchange"]) and not arguments["trading_codes"]:
        #     generalResponse.append("Please provide the TradingCode/Item properly to get expected response.")

        # # === If nothing found but still a valid follow-up ===
        # if not generalResponse:
        #     generalResponse.append("I need a bit more detail to assist you properly. Could you clarify?")

        # === Filter market depths (if any) ===
        filtered_depths = filter_priceList(priceList, generalResponse, priceStatus_label)

        results.append({
            "results": {
                "tradingCodes": tradingCodes,
                "marketTypes": marketTypes,
                "stockExchanges": stockExchanges,
                "intent": intent_label,
                "sentiment": sentiment_label,
                "language": language_label,
                "status": priceStatus_label,
                "context": context_label,
                "generalResponse": generalResponse,
                "inputText": text
            },
            "priceList": filtered_depths
        })

    return results