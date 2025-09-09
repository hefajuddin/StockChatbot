# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
# from pydantic import BaseModel
# from typing import List, Dict
# import torch
# import httpx
# import itertools

# from app.model import model, tokenizer
# from app.modelSource import DEVICE, label_maps
# from app.preprocess import convert_sentence, bangla_to_english, suffix_map
# from app.decode import decode_ner_confident, get_label
# from app.config import BASE_OMS_URL, LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT


# # ================== CONFIG ==================
# BASE_OMS_URL = "https://puji.fcslbd.com:20121/api"
# auth_token: str | None = None  # global token storage

# # FastAPI Security
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# bearer_scheme = HTTPBearer()

# app = FastAPI(title="Intent & NER API", version="2.0")


# # ================== MODELS ==================
# class LoginRequest(BaseModel):
#     loginId: str
#     password: str
#     deviceId: str


# class LoginResponse(BaseModel):
#     token: str


# class APIRequestItem(BaseModel):
#     text: str


# class APIRequest(BaseModel):
#     inputs: List[APIRequestItem]


# class Arguments(BaseModel):
#     trading_codes: List[str]
#     marketType: List[str]
#     stockExchange: List[str]


# class Result(BaseModel):
#     intent: str
#     arguments: Arguments
#     sentiment: str
#     language: str
#     status: str
#     context: str


# class APIResponseItem(BaseModel):
#     results: Result
#     market_depths: List[dict]  # OMS থেকে পাওয়া data


# class APIResponse(BaseModel):
#     results: List[APIResponseItem]


# # ================== LOGIN ==================
# @app.post("/login", response_model=LoginResponse, tags=["Authentication"])
# async def login(request: LoginRequest):
#     """
#     OMS সার্ভারে Login করে token রিটার্ন করবে।
#     """
#     global auth_token
#     async with httpx.AsyncClient() as client:
#         # url = f"{BASE_OMS_URL}/Login"
#         url = f"{LOGIN_ENDPOINT}"
#         response = await client.post(url, json=request.dict())

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     data = response.json()
#     print('Print Response Data',data)
#     token = data.get("data", {}).get("accessToken")
#     if not token:
#         raise HTTPException(status_code=500, detail="Token not found in login response")

#     auth_token = token
#     return {"token": token}


# # ================== DEPENDENCY ==================
# def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
#     """
#     Swagger Authorize বাটনে Bearer token verify হবে।
#     """
#     global auth_token

#     if not credentials:
#         raise HTTPException(status_code=401, detail="Not authorized")

#     print("Authorized with credentials:", credentials)

#     token = credentials.credentials
#     if token != auth_token:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return token


# # ================== INFERENCE ==================
# @app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
# async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
#     if not request.inputs:
#         raise HTTPException(status_code=400, detail="Input list is empty")
#     text_list = [item.text for item in request.inputs if item.text.strip()]
#     if not text_list:
#         raise HTTPException(status_code=400, detail="All texts are empty")

#     results = await infer_batch(text_list, token)
#     return {"results": results}


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     # Convert & lowercase safely
#     texts = []
#     for t in text_list:
#         converted = convert_sentence(t, bangla_to_english, suffix_map)
#         if not isinstance(converted, str):
#             converted = str(converted)
#         texts.append(converted.lower())

#     # Tokenize
#     inputs = tokenizer(
#         texts,
#         return_tensors="pt",
#         padding=True,
#         truncation=True,
#         max_length=64
#     )
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits = logits[0][i:i+1]
#         intent_logits = logits[1][i:i+1]
#         sentiment_logits = logits[2][i:i+1]
#         priceStatus_logits = logits[3][i:i+1]
#         language_logits = logits[4][i:i+1]
#         context_logits = logits[5][i:i+1]

#         # Decode NER
#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

#         # Extract arguments
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         # Decode other labels
#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])


#         if intent_label=='sharePrice':
#             requiredEndpoint = SHAREPRICE_ENDPOINT
#             elif intent_label=='portfolio':
#                 requiredEndpoint = PORTFOLIO_ENDPOINT
#             elif intent_label=='balance':
#                 requiredEndpoint = BALANCE_ENDPOINT
#             else:
#                 requiredEndpoint = None

#         # ================== OMS API CALL ==================
#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}

#         stock_exchanges = arguments["stockExchange"] or ["dse"]
#         market_types = arguments["marketType"] or ["public"]
#         trading_codes = arguments["trading_codes"] or []

#         combos = list(itertools.product(stock_exchanges, market_types, trading_codes))

#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 url = f"{requiredEndpoint}/{se}/{mt}/{tc}"
#                 try:
#                     resp = await client.get(url, headers=headers)
#                     if resp.status_code == 200:
#                         market_depths.append(resp.json())
#                     else:
#                         market_depths.append({"error": resp.text})
#                 except Exception as e:
#                     market_depths.append({"error": str(e)})

#         result = {
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label
#             },
#             "market_depths": market_depths
#         }
#         results.append(result)

#     return results








# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
# from pydantic import BaseModel
# from typing import List
# import torch
# import httpx
# import itertools

# from app.model import model, tokenizer
# from app.modelSource import DEVICE, label_maps
# from app.preprocess import convert_sentence, bangla_to_english, suffix_map
# from app.decode import decode_ner_confident, get_label
# from app.config import (
#     BASE_OMS_URL, LOGIN_ENDPOINT,
#     SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
# )


# # ================== CONFIG ==================
# auth_token: str | None = None  # global token storage

# # FastAPI Security
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# bearer_scheme = HTTPBearer()

# app = FastAPI(title="Intent & NER API", version="2.0")


# # ================== MODELS ==================
# class LoginRequest(BaseModel):
#     loginId: str
#     password: str
#     deviceId: str


# class LoginResponse(BaseModel):
#     token: str


# class APIRequestItem(BaseModel):
#     text: str


# class APIRequest(BaseModel):
#     inputs: List[APIRequestItem]


# class Arguments(BaseModel):
#     trading_codes: List[str]
#     marketType: List[str]
#     stockExchange: List[str]


# class Result(BaseModel):
#     intent: str
#     arguments: Arguments
#     sentiment: str
#     language: str
#     status: str
#     context: str


# class APIResponseItem(BaseModel):
#     results: Result
#     oms_response: List[dict]  # OMS থেকে পাওয়া data


# class APIResponse(BaseModel):
#     results: List[APIResponseItem]


# # ================== LOGIN ==================
# @app.post("/login", response_model=LoginResponse, tags=["Authentication"])
# async def login(request: LoginRequest):
#     """
#     OMS সার্ভারে Login করে token রিটার্ন করবে।
#     """
#     global auth_token
#     async with httpx.AsyncClient() as client:
#         response = await client.post(LOGIN_ENDPOINT, json=request.dict())

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     data = response.json()
#     token = data.get("data", {}).get("accessToken")
#     if not token:
#         raise HTTPException(status_code=500, detail="Token not found in login response")

#     auth_token = token
#     return {"token": token}


# # ================== DEPENDENCY ==================
# def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
#     """
#     Swagger Authorize বাটনে Bearer token verify হবে।
#     """
#     global auth_token

#     if not credentials:
#         raise HTTPException(status_code=401, detail="Not authorized")

#     token = credentials.credentials
#     if token != auth_token:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return token


# # ================== INTENT HANDLERS ==================
# async def handle_share_price(arguments, token: str):
#     headers = {"Authorization": f"Bearer {token}"}
#     stock_exchanges = arguments["stockExchange"] or ["dse"]
#     market_types = arguments["marketType"] or ["public"]
#     trading_codes = arguments["trading_codes"] or []

#     combos = list(itertools.product(stock_exchanges, market_types, trading_codes))
#     responses = []

#     async with httpx.AsyncClient() as client:
#         for se, mt, tc in combos:
#             url = f"{SHAREPRICE_ENDPOINT}/{se}/{mt}/{tc}"
#             try:
#                 resp = await client.get(url, headers=headers)
#                 if resp.status_code == 200:
#                     responses.append(resp.json())
#                 else:
#                     responses.append({"error": resp.text})
#             except Exception as e:
#                 responses.append({"error": str(e)})
#     return responses


# async def handle_portfolio(arguments, token: str):
#     headers = {"Authorization": f"Bearer {token}"}
#     url = PORTFOLIO_ENDPOINT
#     try:
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(url, headers=headers)
#             return [resp.json()] if resp.status_code == 200 else [{"error": resp.text}]
#     except Exception as e:
#         return [{"error": str(e)}]


# async def handle_balance(arguments, token: str):
#     headers = {"Authorization": f"Bearer {token}"}
#     url = BALANCE_ENDPOINT
#     try:
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(url, headers=headers)
#             return [resp.json()] if resp.status_code == 200 else [{"error": resp.text}]
#     except Exception as e:
#         return [{"error": str(e)}]


# # ================== INFERENCE ==================
# @app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
# async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
#     if not request.inputs:
#         raise HTTPException(status_code=400, detail="Input list is empty")
#     text_list = [item.text for item in request.inputs if item.text.strip()]
#     if not text_list:
#         raise HTTPException(status_code=400, detail="All texts are empty")

#     results = await infer_batch(text_list, token)
#     return {"results": results}


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     texts = []
#     for t in text_list:
#         converted = convert_sentence(t, bangla_to_english, suffix_map)
#         texts.append(converted.lower())

#     # Tokenize
#     inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits = logits[0][i:i+1]
#         intent_logits = logits[1][i:i+1]
#         sentiment_logits = logits[2][i:i+1]
#         priceStatus_logits = logits[3][i:i+1]
#         language_logits = logits[4][i:i+1]
#         context_logits = logits[5][i:i+1]

#         # Decode NER
#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

#         # Extract arguments
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         # Decode other labels
#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         # ================== Intent based routing ==================
#         if intent_label == "sharePrice":
#             oms_response = await handle_share_price(arguments, token)
#         elif intent_label == "portfolio":
#             oms_response = await handle_portfolio(arguments, token)
#         elif intent_label == "balance":
#             oms_response = await handle_balance(arguments, token)
#         else:
#             oms_response = [{"info": "No OMS call for this intent"}]

#         result = {
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label,
#             },
#             "oms_response": oms_response,
#         }
#         results.append(result)

#     return results










# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
# from pydantic import BaseModel
# from typing import List, Dict
# import torch
# import httpx
# import itertools

# from app.model import model, tokenizer
# from app.modelSource import DEVICE, label_maps
# from app.preprocess import convert_sentence, bangla_to_english, suffix_map
# from app.decode import decode_ner_confident, get_label
# from app.config import LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
# from app.responses import RESPONSES


# # ================== CONFIG ==================
# auth_token: str | None = None  # global token storage

# # FastAPI Security
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# bearer_scheme = HTTPBearer()

# app = FastAPI(title="Intent & NER API", version="2.0")


# # ================== MODELS ==================
# class LoginRequest(BaseModel):
#     loginId: str
#     password: str
#     deviceId: str


# class LoginResponse(BaseModel):
#     token: str


# class APIRequestItem(BaseModel):
#     text: str


# class APIRequest(BaseModel):
#     inputs: List[APIRequestItem]


# class Arguments(BaseModel):
#     trading_codes: List[str]
#     marketType: List[str]
#     stockExchange: List[str]


# class Result(BaseModel):
#     intent: str
#     arguments: Arguments
#     sentiment: str
#     language: str
#     status: str
#     context: str
#     generalResponse: List[str]


# class APIResponseItem(BaseModel):
#     results: Result
#     market_depths: List[dict]  # OMS থেকে পাওয়া data


# class APIResponse(BaseModel):
#     results: List[APIResponseItem]


# # ================== LOGIN ==================
# @app.post("/login", response_model=LoginResponse, tags=["Authentication"])
# async def login(request: LoginRequest):
#     """
#     OMS সার্ভারে Login করে token রিটার্ন করবে।
#     """
#     global auth_token
#     async with httpx.AsyncClient() as client:
#         url = f"{LOGIN_ENDPOINT}"
#         response = await client.post(url, json=request.dict())

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     data = response.json()
#     token = data.get("data", {}).get("accessToken")
#     if not token:
#         raise HTTPException(status_code=500, detail="Token not found in login response")

#     auth_token = token
#     return {"token": token}


# # ================== DEPENDENCY ==================
# def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
#     """
#     Swagger Authorize বাটনে Bearer token verify হবে।
#     """
#     global auth_token
#     if not credentials:
#         raise HTTPException(status_code=401, detail="Not authorized")

#     token = credentials.credentials
#     if token != auth_token:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return token


# # ================== RESPONSE BUILDER ==================
# def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments):
#     print("xyzzzzzzzzzzzzzzzzzzzzzzzzz",language_label, sentiment_label, intent_label, priceStatus_label, arguments)
#     generalResponse = []

#     if language_label == "bn":
#         # === Sentiment ===
#         sentiment_text = RESPONSES["bn"]["sentiment"].get(sentiment_label)
#         if sentiment_text:
#             generalResponse.append(sentiment_text)

#         # === Intent ===
#         if intent_label == "sharePrice":
#             trading_codes = arguments.get("trading_codes", [])
#             template = RESPONSES["bn"]["sharePrice"].get(priceStatus_label)
#             if template and trading_codes:
#                 for tc in trading_codes:
#                     generalResponse.append(template.format(tc))
#         else:
#             intent_text = RESPONSES["bn"]["intent"].get(intent_label)
#             if intent_text:
#                 generalResponse.append(intent_text)
#     print('General Responseeeeeeeeeeeeeeeeeeeee:',generalResponse)

#     return generalResponse


# # ================== INFERENCE ==================
# @app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
# async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
#     if not request.inputs:
#         raise HTTPException(status_code=400, detail="Input list is empty")
#     text_list = [item.text for item in request.inputs if item.text.strip()]
#     if not text_list:
#         raise HTTPException(status_code=400, detail="All texts are empty")

#     results = await infer_batch(text_list, token)
#     return {"results": results}


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     # Convert & lowercase safely
#     texts = []
#     for t in text_list:
#         converted = convert_sentence(t, bangla_to_english, suffix_map)
#         if not isinstance(converted, str):
#             converted = str(converted)
#         texts.append(converted.lower())

#     # Tokenize
#     inputs = tokenizer(
#         texts,
#         return_tensors="pt",
#         padding=True,
#         truncation=True,
#         max_length=64
#     )
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits = logits[0][i:i+1]
#         intent_logits = logits[1][i:i+1]
#         sentiment_logits = logits[2][i:i+1]
#         priceStatus_logits = logits[3][i:i+1]
#         language_logits = logits[4][i:i+1]
#         context_logits = logits[5][i:i+1]

#         # Decode NER
#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

#         # Extract arguments
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         # Decode other labels
#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         # Intent অনুযায়ী Endpoint ঠিক করা
#         if intent_label == 'sharePrice':
#             requiredEndpoint = SHAREPRICE_ENDPOINT
#         elif intent_label == 'portfolio':
#             requiredEndpoint = PORTFOLIO_ENDPOINT
#         elif intent_label == 'balance':
#             requiredEndpoint = BALANCE_ENDPOINT
#         else:
#             requiredEndpoint = None

#         # OMS API Call
#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}

#         stock_exchanges = arguments["stockExchange"] or ["dse"]
#         market_types = arguments["marketType"] or ["public"]
#         trading_codes = arguments["trading_codes"] or []

#         combos = list(itertools.product(stock_exchanges, market_types, trading_codes))

#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 if requiredEndpoint:
#                     url = f"{requiredEndpoint}/{se}/{mt}/{tc}"
#                     try:
#                         resp = await client.get(url, headers=headers)
#                         if resp.status_code == 200:
#                             market_depths.append(resp.json())
#                         else:
#                             market_depths.append({"error": resp.text})
#                     except Exception as e:
#                         market_depths.append({"error": str(e)})

#         # Build General Response
#         generalResponse = build_general_response(
#             language_label,
#             sentiment_label,
#             intent_label,
#             priceStatus_label,
#             arguments
#         )

#         result = {
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label,
#                 "generalResponse": generalResponse
#             },
#             "market_depths": market_depths
#         }
#         results.append(result)

#     return results







# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
# from pydantic import BaseModel
# from typing import List, Dict
# import torch
# import httpx
# import itertools

# from app.model import model, tokenizer
# from app.modelSource import DEVICE, label_maps
# from app.preprocess import convert_sentence, bangla_to_english, suffix_map
# from app.decode import decode_ner_confident, get_label
# from app.config import LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
# from app.responses import RESPONSES


# # ================== CONFIG ==================
# auth_token: str | None = None  # global token storage

# # FastAPI Security
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# bearer_scheme = HTTPBearer()

# app = FastAPI(title="Intent & NER API", version="2.0")


# # ================== MODELS ==================
# class LoginRequest(BaseModel):
#     loginId: str
#     password: str
#     deviceId: str


# class LoginResponse(BaseModel):
#     token: str


# class APIRequestItem(BaseModel):
#     text: str


# class APIRequest(BaseModel):
#     inputs: List[APIRequestItem]


# class Arguments(BaseModel):
#     trading_codes: List[str]
#     marketType: List[str]
#     stockExchange: List[str]


# class Result(BaseModel):
#     intent: str
#     arguments: Arguments
#     sentiment: str
#     language: str
#     status: str
#     context: str
#     generalResponse: List[str]


# class APIResponseItem(BaseModel):
#     results: Result
#     market_depths: List[dict]  # OMS থেকে পাওয়া data


# class APIResponse(BaseModel):
#     results: List[APIResponseItem]


# # ================== LOGIN ==================
# @app.post("/login", response_model=LoginResponse, tags=["Authentication"])
# async def login(request: LoginRequest):
#     """
#     OMS সার্ভারে Login করে token রিটার্ন করবে।
#     """
#     global auth_token
#     async with httpx.AsyncClient() as client:
#         url = f"{LOGIN_ENDPOINT}"
#         response = await client.post(url, json=request.dict())

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

#     data = response.json()
#     token = data.get("data", {}).get("accessToken")
#     if not token:
#         raise HTTPException(status_code=500, detail="Token not found in login response")

#     auth_token = token
#     return {"token": token}


# # ================== DEPENDENCY ==================
# def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
#     """
#     Swagger Authorize বাটনে Bearer token verify হবে।
#     """
#     global auth_token
#     if not credentials:
#         raise HTTPException(status_code=401, detail="Not authorized")

#     token = credentials.credentials
#     if token != auth_token:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return token


# # ================== RESPONSE BUILDER ==================
# def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments):
#     generalResponse = []

#     if language_label == "bn":
#         # === Sentiment ===
#         sentiment_text = RESPONSES["bn"]["sentiment"].get(sentiment_label)
#         if sentiment_text:
#             generalResponse.append(sentiment_text)

#         # === Intent ===
#         if intent_label == "sharePrice":
#             trading_codes = arguments.get("trading_codes", [])
#             template = RESPONSES["bn"]["sharePrice"].get(priceStatus_label)
#             if template and trading_codes:
#                 for tc in trading_codes:
#                     generalResponse.append(template.format(tc))
#         else:
#             intent_text = RESPONSES["bn"]["intent"].get(intent_label)
#             if intent_text:
#                 generalResponse.append(intent_text)

#     return generalResponse


# # ================== MARKET DEPTH FILTER ==================
# def filter_market_depths(market_depths: List[dict], generalResponse: List[str]) -> List[dict]:
#     """
#     generalResponse অনুযায়ী শুধু দরকারি ফিল্ডগুলো market_depths থেকে রিটার্ন করবে।
#     """
#     if not market_depths or not generalResponse:
#         return market_depths

#     keyword_map = {
#         "volume": ["volume"],
#         "ltp": ["ltp"],
#         "value": ["value"],
#         "ycp": ["ycp"],
#         "maketDepth": ["buySellDetails"],
#         "marketDepth": ["buySellDetails"],
#         "all": ["open", "ltp", "ycp", "close", "high", "low", "trade", "volume", "value", "priceTick", "quantityTick", "change"],
#         "price": ["open", "ltp", "ycp", "close", "high", "low"]
#     }

#     filtered = []
#     for depth in market_depths:
#         data = depth.get("data", {})
#         selected = {}
#         for key, fields in keyword_map.items():
#             if any(key in resp for resp in generalResponse):
#                 for f in fields:
#                     if f in data:
#                         selected[f] = data[f]
#         if selected:
#             filtered.append(selected)
#         else:
#             filtered.append(data)  # fallback: full data

#     return filtered


# # ================== INFERENCE ==================
# @app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
# async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
#     if not request.inputs:
#         raise HTTPException(status_code=400, detail="Input list is empty")
#     text_list = [item.text for item in request.inputs if item.text.strip()]
#     if not text_list:
#         raise HTTPException(status_code=400, detail="All texts are empty")

#     results = await infer_batch(text_list, token)
#     return {"results": results}


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     # Convert & lowercase safely
#     texts = []
#     for t in text_list:
#         converted = convert_sentence(t, bangla_to_english, suffix_map)
#         if not isinstance(converted, str):
#             converted = str(converted)
#         texts.append(converted.lower())

#     # Tokenize
#     inputs = tokenizer(
#         texts,
#         return_tensors="pt",
#         padding=True,
#         truncation=True,
#         max_length=64
#     )
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits = logits[0][i:i+1]
#         intent_logits = logits[1][i:i+1]
#         sentiment_logits = logits[2][i:i+1]
#         priceStatus_logits = logits[3][i:i+1]
#         language_logits = logits[4][i:i+1]
#         context_logits = logits[5][i:i+1]

#         # Decode NER
#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])

#         # Extract arguments
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         # Decode other labels
#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         # Intent অনুযায়ী Endpoint ঠিক করা
#         if intent_label == 'sharePrice':
#             requiredEndpoint = SHAREPRICE_ENDPOINT
#         elif intent_label == 'portfolio':
#             requiredEndpoint = PORTFOLIO_ENDPOINT
#         elif intent_label == 'balance':
#             requiredEndpoint = BALANCE_ENDPOINT
#         else:
#             requiredEndpoint = None

#         # OMS API Call
#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}

#         stock_exchanges = arguments["stockExchange"] or ["dse"]
#         market_types = arguments["marketType"] or ["public"]
#         trading_codes = arguments["trading_codes"] or []

#         combos = list(itertools.product(stock_exchanges, market_types, trading_codes))

#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 if requiredEndpoint:
#                     url = f"{requiredEndpoint}/{se}/{mt}/{tc}"
#                     try:
#                         resp = await client.get(url, headers=headers)
#                         if resp.status_code == 200:
#                             market_depths.append(resp.json())
#                         else:
#                             market_depths.append({"error": resp.text})
#                     except Exception as e:
#                         market_depths.append({"error": str(e)})

#         # Build General Response
#         generalResponse = build_general_response(
#             language_label,
#             sentiment_label,
#             intent_label,
#             priceStatus_label,
#             arguments
#         )

#         # === এখানে ফিল্টার প্রয়োগ ===
#         filtered_depths = filter_market_depths(market_depths, generalResponse)

#         result = {
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label,
#                 "generalResponse": generalResponse
#             },
#             "market_depths": filtered_depths
#         }
#         results.append(result)

#     return results




# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
# from pydantic import BaseModel
# from typing import List
# import torch
# import httpx
# import itertools

# from app.model import model, tokenizer
# from app.modelSource import DEVICE, label_maps
# from app.preprocess import convert_sentence, bangla_to_english, suffix_map
# from app.decode import decode_ner_confident, get_label
# from app.config import LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
# from app.utils.response_formatter import build_general_response, filter_market_depths

# # ================== CONFIG ==================
# auth_token: str | None = None  # global token storage

# # FastAPI Security
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# bearer_scheme = HTTPBearer()

# app = FastAPI(title="Intent & NER API", version="2.0")

# # ================== MODELS ==================
# class LoginRequest(BaseModel):
#     loginId: str
#     password: str
#     deviceId: str

# class LoginResponse(BaseModel):
#     token: str

# class APIRequestItem(BaseModel):
#     text: str

# class APIRequest(BaseModel):
#     inputs: List[APIRequestItem]

# class Arguments(BaseModel):
#     trading_codes: List[str]
#     marketType: List[str]
#     stockExchange: List[str]

# class Result(BaseModel):
#     intent: str
#     arguments: Arguments
#     sentiment: str
#     language: str
#     status: str
#     context: str
#     generalResponse: List[str]

# class APIResponseItem(BaseModel):
#     results: Result
#     market_depths: List[dict]

# class APIResponse(BaseModel):
#     results: List[APIResponseItem]

# # ================== LOGIN ==================
# @app.post("/login", response_model=LoginResponse, tags=["Authentication"])
# async def login(request: LoginRequest):
#     global auth_token
#     async with httpx.AsyncClient() as client:
#         response = await client.post(LOGIN_ENDPOINT, json=request.dict())
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
#     data = response.json()
#     token = data.get("data", {}).get("accessToken")
#     if not token:
#         raise HTTPException(status_code=500, detail="Token not found")
#     auth_token = token
#     return {"token": token}

# # ================== DEPENDENCY ==================
# def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
#     global auth_token
#     if not credentials:
#         raise HTTPException(status_code=401, detail="Not authorized")
#     token = credentials.credentials
#     if token != auth_token:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return token

# # ================== INFERENCE ==================
# @app.post("/predict_batch", response_model=APIResponse, tags=["Prediction"])
# async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
#     if not request.inputs:
#         raise HTTPException(status_code=400, detail="Input list is empty")
#     text_list = [item.text for item in request.inputs if item.text.strip()]
#     if not text_list:
#         raise HTTPException(status_code=400, detail="All texts are empty")

#     results = await infer_batch(text_list, token)
#     return {"results": results}


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     texts = [str(convert_sentence(t, bangla_to_english, suffix_map)).lower() for t in text_list]
#     inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits, intent_logits, sentiment_logits, priceStatus_logits, language_logits, context_logits = (
#             logits[0][i:i+1], logits[1][i:i+1], logits[2][i:i+1], logits[3][i:i+1], logits[4][i:i+1], logits[5][i:i+1]
#         )

#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         if intent_label == 'sharePrice':
#             endpoint = SHAREPRICE_ENDPOINT
#         elif intent_label == 'portfolio':
#             endpoint = PORTFOLIO_ENDPOINT
#         elif intent_label == 'balance':
#             endpoint = BALANCE_ENDPOINT
#         else:
#             endpoint = None

#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}
#         combos = list(itertools.product(
#             arguments["stockExchange"] or ["dse"],
#             arguments["marketType"] or ["public"],
#             arguments["trading_codes"] or []
#         ))

#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 if endpoint:
#                     url = f"{endpoint}/{se}/{mt}/{tc}"
#                     try:
#                         resp = await client.get(url, headers=headers)
#                         if resp.status_code == 200:
#                             market_depths.append(resp.json())
#                         else:
#                             market_depths.append({"error": resp.text})
#                     except Exception as e:
#                         market_depths.append({"error": str(e)})

#         generalResponse = build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments)
#         filtered_depths = filter_market_depths(market_depths, generalResponse)

#         # ✅ শুধুমাত্র generalResponse + filtered_depths
#         results.append({
#             "results": {
#                 "generalResponse": generalResponse
#             },
#             "market_depths": filtered_depths
#         })

#     return results


  
# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     texts = [str(convert_sentence(t, bangla_to_english, suffix_map)).lower() for t in text_list]
#     inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits, intent_logits, sentiment_logits, priceStatus_logits, language_logits, context_logits = (
#             logits[0][i:i+1], logits[1][i:i+1], logits[2][i:i+1], logits[3][i:i+1], logits[4][i:i+1], logits[5][i:i+1]
#         )

#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         if intent_label == 'sharePrice':
#             endpoint = SHAREPRICE_ENDPOINT
#         elif intent_label == 'portfolio':
#             endpoint = PORTFOLIO_ENDPOINT
#         elif intent_label == 'balance':
#             endpoint = BALANCE_ENDPOINT
#         else:
#             endpoint = None

#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}
#         combos = list(itertools.product(
#             arguments["stockExchange"] or ["dse"],
#             arguments["marketType"] or ["public"],
#             arguments["trading_codes"] or []
#         ))

#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 if endpoint:
#                     url = f"{endpoint}/{se}/{mt}/{tc}"
#                     try:
#                         resp = await client.get(url, headers=headers)
#                         if resp.status_code == 200:
#                             market_depths.append(resp.json())
#                         else:
#                             market_depths.append({"error": resp.text})
#                     except Exception as e:
#                         market_depths.append({"error": str(e)})

#         generalResponse = build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments)
#         filtered_depths = filter_market_depths(market_depths, generalResponse)

#         results.append({
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label,
#                 "generalResponse": generalResponse
#             },
#             "market_depths": filtered_depths
#         })


#     return results





from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List
import torch
import httpx
import itertools

from app.model import model, tokenizer
from app.modelSource import DEVICE, label_maps
from app.preprocess import convert_sentence, bangla_to_english, suffix_map
from app.decode import decode_ner_confident, get_label
from app.config import LOGIN_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT
from app.utils.response_formatter import build_general_response, filter_market_depths

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
    market_depths: List[dict]

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


# async def infer_batch(text_list: List[str], token: str) -> List[dict]:
#     texts = [str(convert_sentence(t, bangla_to_english, suffix_map)).lower() for t in text_list]
#     inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
#     inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

#     with torch.no_grad():
#         logits = model(**inputs)

#     results = []
#     for i, text in enumerate(texts):
#         ner_logits, intent_logits, sentiment_logits, priceStatus_logits, language_logits, context_logits = (
#             logits[0][i:i+1], logits[1][i:i+1], logits[2][i:i+1],
#             logits[3][i:i+1], logits[4][i:i+1], logits[5][i:i+1]
#         )

#         ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])
#         arguments = {
#             "trading_codes": [item["text"] for item in ner_result if "tradingCode" in item["tag"]],
#             "marketType": [item["text"] for item in ner_result if "marketType" in item["tag"]],
#             "stockExchange": [item["text"] for item in ner_result if "stockExchange" in item["tag"]],
#         }

#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzz",ner_result)

#         intent_label = get_label(intent_logits, label_maps["intent_label2id"])
#         sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
#         priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
#         language_label = get_label(language_logits, label_maps["language_label2id"])
#         context_label = get_label(context_logits, label_maps["context_label2id"])

#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzzi",intent_label)
#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzzs",sentiment_label)
#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzzp",priceStatus_label)
#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzzl",language_label)
#         print("xyzzzzzzzzzzzzzzzzzzzzzzzzzc",context_label)

#         if intent_label == 'sharePrice':
#             endpoint = SHAREPRICE_ENDPOINT
#         elif intent_label == 'portfolio':
#             endpoint = PORTFOLIO_ENDPOINT
#         elif intent_label == 'balance':
#             endpoint = BALANCE_ENDPOINT
#         else:
#             endpoint = None

#         market_depths = []
#         headers = {"Authorization": f"Bearer {token}"}
#         combos = list(itertools.product(
#             arguments["stockExchange"] or ["dse"],
#             arguments["marketType"] or ["public"],
#             arguments["trading_codes"] or []
#         ))

#         print('texttttttttttttttttttttttttttttttt', texts)
#         print('inputttttttttttttttttttttttttttttt', inputs)
#         print('nerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', ner_result)
#         async with httpx.AsyncClient() as client:
#             for se, mt, tc in combos:
#                 if endpoint:
#                     url = f"{endpoint}/{se}/{mt}/{tc}"
#                     try:
#                         resp = await client.get(url, headers=headers)
#                         if resp.status_code == 200:
#                             market_depths.append(resp.json())
#                         else:
#                             market_depths.append({"error": resp.text})
#                     except Exception as e:
#                         market_depths.append({"error": str(e)})

#         generalResponse = build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments)
#         print('aaaaaaaaaaaa', generalResponse)
#         filtered_depths = filter_market_depths(market_depths, generalResponse, priceStatus_label)
#         print('bbbbbbbbbbb', filtered_depths)
#         print('ccccccccccc', market_depths)

#         results.append({
#             "results": {
#                 "intent": intent_label,
#                 "arguments": arguments,
#                 "sentiment": sentiment_label,
#                 "language": language_label,
#                 "status": priceStatus_label,
#                 "context": context_label,
#                 "generalResponse": generalResponse
#             },
#             "market_depths": filtered_depths
#         })


#     return results



async def infer_batch(text_list: List[str], token: str) -> List[dict]:
    texts = [str(convert_sentence(t, bangla_to_english, suffix_map)).lower() for t in text_list]
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

        intent_label = get_label(intent_logits, label_maps["intent_label2id"])
        sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
        priceStatus_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
        language_label = get_label(language_logits, label_maps["language_label2id"])
        context_label = get_label(context_logits, label_maps["context_label2id"])


        print("nerrrrrrrrrrrrrrrrr", intent_label)
        print("nerrrrrrrrrrrrrrrrr", sentiment_label)
        print("nerrrrrrrrrrrrrrrrr", priceStatus_label)
        print("nerrrrrrrrrrrrrrrrr", language_label)
        print("nerrrrrrrrrrrrrrrrr", context_label)
        print("nerrrrrrrrrrrrrrrrr", context_label)



        # === Endpoint Mapping ===
        if intent_label == 'sharePrice':
            endpoint = SHAREPRICE_ENDPOINT
        elif intent_label == 'portfolio':
            endpoint = PORTFOLIO_ENDPOINT
        elif intent_label == 'balance':
            endpoint = BALANCE_ENDPOINT
        else:
            endpoint = None

        market_depths = []
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
                            market_depths.append(resp.json())
                        else:
                            market_depths.append({
                                "error": f"API returned {resp.status_code}",
                                "details": resp.text,
                                "text": text
                            })
                    except Exception as e:
                        market_depths.append({
                            "error": str(e),
                            "text": text
                        })

        # === Always build response ===
        generalResponse = build_general_response(
            language_label, sentiment_label, intent_label, priceStatus_label, arguments
        )

        # === Special Case: price_status, se, mt আছে কিন্তু trading_code নাই ===
        if intent_label == "sharePrice" and priceStatus_label and (arguments["marketType"] or arguments["stockExchange"]) and not arguments["trading_codes"]:
            generalResponse.append("Please provide the trading code to fetch share price details.")

        # === If nothing found but still a valid follow-up ===
        if not generalResponse:
            generalResponse.append("I need a bit more detail to assist you properly. Could you clarify?")

        # === Filter market depths (if any) ===
        filtered_depths = filter_market_depths(market_depths, generalResponse, priceStatus_label)

        results.append({
            "results": {
                "intent": intent_label,
                "arguments": arguments,
                "sentiment": sentiment_label,
                "language": language_label,
                "status": priceStatus_label,
                "context": context_label,
                "generalResponse": generalResponse,
                "inputText": text
            },
            "market_depths": filtered_depths
        })

    return results