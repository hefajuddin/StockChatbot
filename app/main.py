from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List, Dict
import torch
import httpx
import itertools

from app.model import model, tokenizer
from app.modelSource import DEVICE, label_maps
from app.preprocess import convert_sentence, bangla_to_english, suffix_map
from app.decode import decode_ner_confident, get_label
from app.config import BASE_OMS_URL, LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT


# ================== CONFIG ==================
BASE_OMS_URL = "https://puji.fcslbd.com:20121/api"
auth_token: str | None = None  # global token storage

# FastAPI Security
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
    market_depths: List[dict]  # OMS থেকে পাওয়া data


class APIResponse(BaseModel):
    results: List[APIResponseItem]


# ================== LOGIN ==================
@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    OMS সার্ভারে Login করে token রিটার্ন করবে।
    """
    global auth_token
    async with httpx.AsyncClient() as client:
        # url = f"{BASE_OMS_URL}/Login"
        url = f"{LOGIN_ENDPOINT}"
        response = await client.post(url, json=request.dict())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    print('Print Response Data',data)
    token = data.get("data", {}).get("accessToken")
    if not token:
        raise HTTPException(status_code=500, detail="Token not found in login response")

    auth_token = token
    return {"token": token}


# ================== DEPENDENCY ==================
def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Swagger Authorize বাটনে Bearer token verify হবে।
    """
    global auth_token

    if not credentials:
        raise HTTPException(status_code=401, detail="Not authorized")

    print("Authorized with credentials:", credentials)

    token = credentials.credentials
    if token != auth_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token


# ================== INFERENCE ==================
@app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
    if not request.inputs:
        raise HTTPException(status_code=400, detail="Input list is empty")
    text_list = [item.text for item in request.inputs if item.text.strip()]
    if not text_list:
        raise HTTPException(status_code=400, detail="All texts are empty")

    results = await infer_batch(text_list, token)
    return {"results": results}


async def infer_batch(text_list: List[str], token: str) -> List[dict]:
    # Convert & lowercase safely
    texts = []
    for t in text_list:
        converted = convert_sentence(t, bangla_to_english, suffix_map)
        if not isinstance(converted, str):
            converted = str(converted)
        texts.append(converted.lower())

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

        # Decode NER
        ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

        # Extract arguments
        arguments = {
            "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
            "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
            "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
        }

        # Decode other labels
        intent_label = get_label(intent_logits, label_maps["intent_label2id"])
        sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
        priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
        language_label = get_label(language_logits, label_maps["language_label2id"])
        context_label = get_label(context_logits, label_maps["context_label2id"])


        if intent_label=='sharePrice':
            requiredEndpoint = SHAREPRICE_ENDPOINT
            elif intent_label=='portfolio':
                requiredEndpoint = PORTFOLIO_ENDPOINT
            elif intent_label=='balance':
                requiredEndpoint = BALANCE_ENDPOINT
            else:
                requiredEndpoint = None

        # ================== OMS API CALL ==================
        market_depths = []
        headers = {"Authorization": f"Bearer {token}"}

        stock_exchanges = arguments["stockExchange"] or ["dse"]
        market_types = arguments["marketType"] or ["public"]
        trading_codes = arguments["trading_codes"] or []

        combos = list(itertools.product(stock_exchanges, market_types, trading_codes))

        async with httpx.AsyncClient() as client:
            for se, mt, tc in combos:
                url = f"{requiredEndpoint}/{se}/{mt}/{tc}"
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        market_depths.append(resp.json())
                    else:
                        market_depths.append({"error": resp.text})
                except Exception as e:
                    market_depths.append({"error": str(e)})

        result = {
            "results": {
                "intent": intent_label,
                "arguments": arguments,
                "sentiment": sentiment_label,
                "language": language_label,
                "status": priceStatus_label,
                "context": context_label
            },
            "market_depths": market_depths
        }
        results.append(result)

    return results
