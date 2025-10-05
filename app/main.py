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
from app.config import LOGIN_ENDPOINT, REFRESH_ENDPOINT, SHAREPRICE_ENDPOINT, PORTFOLIO_ENDPOINT, BALANCE_ENDPOINT, DEVICE_ID, X_BROKER_ID
from app.utils.response_formatter import build_general_response, filter_responseList
import redis
from app.redis_utils import r, save_to_redis,get_from_redis,delete_from_redis
from datetime import datetime, timedelta


# ================== CONFIG ==================
auth_token: str | None = None  # global token storage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
bearer_scheme = HTTPBearer()

app = FastAPI(title="Intent & NER API", version="2.0")

# ================== MODELS ==================
class LoginRequest(BaseModel):
    deviceId: str
    loginId: str
    password: str

class LoginResponse(BaseModel):
    token: str

class APIRequestItem(BaseModel):
    text: str

class APIRequest(BaseModel):
    inputs: List[APIRequestItem]

class APIResponseItemSimple(BaseModel):
    results: dict  # শুধু generalResponse রাখব
    responseList: List[dict]

class APIResponseSimple(BaseModel):
    results: List[APIResponseItemSimple]


app = FastAPI()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Intent & NER API", version="2.0")

# ================= CORS =================
origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
# r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Pydantic model
class ChatData(BaseModel):
    boCodes: List[str]
    tradingCodes: List[str]
    marketTypes: List[str]
    stockExchanges: List[str]
    intent_label: str
    sentiment_label: str
    language: str
    status_label: str
    context_label: str
    # generalResponse: str = None  # optional

# ----------------- Helper: safe decode -----------------
def _safe_decode(value):
    if isinstance(value, bytes):
        return value.decode()
    return value or ""


from datetime import datetime, timedelta

def subtract_two_minutes(expiry_str: str) -> str:
    """
    expiry_str: যেমন "2025-09-18T16:43:30Z"
    ২ মিনিট বিয়োগ করে একই ফরম্যাটে স্ট্রিং রিটার্ন করবে
    """
    # Z → UTC বুঝানোর জন্য আগে Z কে +0000 হিসেবে ধরা হয়
    dt = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%SZ")
    new_dt = dt - timedelta(minutes=2)
    return new_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Login → refresh → save session → return final access token.
    """
    payload = {
        "loginId": request.loginId,
        "password": request.password,
        "deviceId": request.deviceId or DEVICE_ID,
    }

    async with httpx.AsyncClient() as client:
        # ---- login ----
        try:
            resp = await client.post(LOGIN_ENDPOINT, json=payload, timeout=15.0)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Login request failed: {e}")

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)

        resp_data = resp.json().get("data") or {}
        access = resp_data.get("accessToken")
        refresh = resp_data.get("refreshToken")
        expiry = resp_data.get("accessTokenExpiryDateTimeUtc")
        user_id = resp_data.get("userId") or resp_data.get("userID")
        device_id = resp_data.get("deviceId") or payload["deviceId"]

        if not access or not user_id:
            raise HTTPException(status_code=500, detail="Missing accessToken or userId")

        # ---- refresh ----
        try:
            refresh_resp = await client.post(
                REFRESH_ENDPOINT,
                json={
                    "accessToken": access,
                    "refreshToken": refresh,
                    "deviceId": device_id,
                },
                timeout=15.0,
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Refresh request failed: {e}")

        if refresh_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Refresh failed; please login again")

        data = refresh_resp.json().get("data") or {}
        new_access = data.get("accessToken") or access
        new_refresh = data.get("refreshToken") or refresh
        new_expiry = data.get("accessTokenExpiryDateTimeUtc") or expiry
        print('xxxxa',new_access)
        print('xxxxxr',new_refresh)
        print('xxxxxxe',new_expiry)
        print('xxxxxxxd',device_id)

    # ---- save to Redis ----
    
    await _save_session_to_redis(user_id, new_access, new_refresh, new_expiry, device_id)

    asyncio.create_task(periodic_refresh(user_id))

    return {"token": new_access}


#     # -------- call refresh API --------
# async def login(accessToken, deviceId, refreshToken):
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.post(
#                 REFRESH_ENDPOINT,
#                 json={"accessToken": clean_token,
#                         "deviceId": device_id},
#                         "refreshToken": refresh_token,                    
#                 timeout=15.0,
#             )
#         except httpx.RequestError as e:
#             raise HTTPException(status_code=503, detail=f"Refresh request failed: {e}")

#     if resp.status_code != 200:
#         await r.delete(session_key)
#         await r.delete(token_map_key)
#         raise HTTPException(status_code=401, detail="Refresh failed; please login again")

#     data = resp.json().get("data") or {}
#     new_access = data.get("accessToken") or data.get("token")
#     new_refresh = data.get("refreshToken") or refresh_token
#     new_expiry = data.get("accessTokenExpiryDateTimeUtc") or expiry_iso


# Helper function
from datetime import datetime

# ----------------- Redis session save -----------------
from datetime import datetime, timedelta

# ---- helper ----
def _make_token_key(token: str) -> str:
    """Always build redis key the same way."""
    return f"token_to_user:{token.strip()}"


# ----------------- Redis session save -----------------
async def _save_session_to_redis(
    user_id: str,
    access_token: str,
    refresh_token: str,
    expiry_iso: str | None,
    device_id: str,
):
    """
    Saves the user session keyed by user_id and token_to_user mapping.
    """
    clean_token = access_token.strip()
    session_key = f"session:{user_id}"


    # print("xxx_expiry_iso", expiry_iso)

    # Save session as hash
    await r.hset(session_key, mapping={
        "accessToken": clean_token,
        # "refreshToken": refresh_token or "",
        "deviceId": device_id or "",
        "expiry": expiry_iso or ""
    })
    await r.expire(session_key, 18*60*60)

    refresh_key = f"refresh:{user_id.strip()}"
    await r.set(refresh_key, refresh_token, ex=18*60*60)
    # print("set_refresh_token", refresh_token)

    # user_key = f"user:{refresh_token}"
    # await r.set(user_key, user_id, ex=11*60*60)

    # TTL for token
    if expiry_iso:
        try:
            expiry_dt = datetime.fromisoformat(expiry_iso.replace("Z", "")) - timedelta(seconds=590)
            ttl_token = max(int((expiry_dt - datetime.utcnow()).total_seconds()), 1)
            print("========================== expiry time", expiry_dt)
            print("========================== ttl duration", ttl_token)
        except Exception:
            ttl_token = 20
    else:
        ttl_token = 20

    print("[DEBUG] PING:", await r.ping())
    # print("Saved mapping:", clean_token, "->", user_id)
    # print("Check in redis:", await r.get(clean_token))
    # print("[DEBUG] Going to save token", access_token[:20], "...")


    await r.expire(session_key, ttl_token + 3600)

    # print(f"[SAVE] {clean_token} -> {user_id} (TTL {ttl_token}s)")


ACCESS_TOKEN_BUFFER = 120  # মেয়াদ শেষের আগে যত সেকেন্ডে রিফ্রেশ শুরু হবে

async def refresh_if_needed(clean_token: str,
                            refresh_token: str,
                            device_id: str,
                            expiry_iso: str) -> str:
    """expiry দেখে প্রয়োজন হলে REFRESH_ENDPOINT-এ কল করে নতুন access token ফেরত দেয়"""
    try:
        expiry_dt = datetime.fromisoformat(expiry_iso.replace("Z", "")) if expiry_iso else None
    except Exception:
        expiry_dt = None

    now = datetime.utcnow()
    need_refresh = (not expiry_dt) or (expiry_dt - now <= timedelta(seconds=ACCESS_TOKEN_BUFFER))

    if not need_refresh:
        return clean_token

    async with httpx.AsyncClient() as client:
        payload = {
            "accessToken": clean_token.strip(),
            "refreshToken": refresh_token.strip(),
            "deviceId": device_id,
        }
        print("[REFRESH] Sending request", payload)

        try:
            resp = await client.post(REFRESH_ENDPOINT, json=payload, timeout=15.0)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"[REFRESH] Network error: {e}")

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code,
                                detail=f"[REFRESH] HTTP {resp.status_code}: {resp.text}")

        try:
            body = resp.json()
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"[REFRESH] JSON parse error: {e}")

        data = body.get("data") or {}
        if data.get("success") is False:
            raise HTTPException(status_code=401,
                                detail=f"[REFRESH] {data.get('errorMessage', 'Unknown')}")

        new_access = data.get("accessToken") or data.get("token")
        new_refresh = data.get("refreshToken") or refresh_token
        new_expiry = data.get("accessTokenExpiryDateTimeUtc") or expiry_iso
        if not new_access:
            raise HTTPException(status_code=500,
                                detail=f"[REFRESH] No access token returned. Raw: {data}")

        return new_access, new_refresh, new_expiry





async def read_session(user_id: str):
    session_key = f"session:{user_id}"
    raw_data = await r.hgetall(session_key)

    decoded = {
        k.decode() if isinstance(k, bytes) else k:
        v.decode() if isinstance(v, bytes) else v
        for k, v in raw_data.items()
    }
    return decoded



# ----------------- Validate / refresh token -----------------
async def get_valid_token(current_access_token: str, user_id: str) -> str:
    """Redis থেকে token লোড করে expiry চেক করে, দরকার হলে রিফ্রেশ করে"""

    if not user_id:
        raise HTTPException(status_code=401, detail="Unknown token / session not found")
 

    clean_token = (current_access_token or "").strip()


    # session_key = f"session:{user_id}"
    # session = await r.hgetall(session_key) or {}
    # stored_access = (session.get("accessToken") or "").strip()
    # expiry_iso = session.get("expiry") or ""
    # device_id = session.get("deviceId") or "DEVICE_ID"


    data = await read_session(user_id)
    stored_access = (data.get("accessToken") or "").strip()
    expiry_iso = data.get("expiry") or ""    
    device_id = data.get("deviceId") or DEVICE_ID





    if stored_access and stored_access != clean_token:
        clean_token = stored_access

    refresh_key = f"refresh:{user_id.strip()}"
    # refresh_token = await r.get(refresh_key)

    val = await r.get(refresh_key)
    refresh_token = val.decode() if isinstance(val, bytes) else val


    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not available; please login again")



    if expiry_iso:
        try:
            expiry_dt = datetime.fromisoformat(expiry_iso.replace("Z", ""))
            expiry_dt= expiry_dt - timedelta(seconds=60)
            if datetime.utcnow() < expiry_dt:
                return clean_token
        except Exception:
            return clean_token
    else:
        return clean_token

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not available; please login again")


    # মেয়াদ দেখে দরকার হলে রিফ্রেশ
    result = await refresh_if_needed(clean_token, refresh_token, device_id, expiry_iso)
    if isinstance(result, tuple):
        new_access, new_refresh, new_expiry = result
    else:
        # refresh দরকার হয়নি
        return result

    # পুরনো সেশন ডিলিট
    # before = await r.hgetall(session_key)
    # print("[DEBUG] Before delete:", before)
    # deleted = await r.delete(session_key)
    # print(f"[DEBUG] Deleted {deleted} key(s): {session_key}")
    # print("[DEBUG] After delete:", await r.hgetall(session_key))

    # নতুন সেশন সেভ করো
    await _save_session_to_redis(user_id, new_access, new_refresh, new_expiry, device_id)
    return new_access


from datetime import datetime, timedelta, timezone

# @app.on_event("startup")
# async def start_background_tasks():
#     print("[Startup] Scheduling periodic_refreshবববববববববববববববববববববববব")
#     user_id = "65ca1cdea37a8fd05090dc46"  # এখানে প্রপার user_id ব্যবহার করতে হবে
#     asyncio.create_task(periodic_refresh(user_id))



from datetime import datetime, timedelta, timezone
import asyncio
import httpx
from fastapi import HTTPException

ACCESS_TOKEN_BUFFER = 120  # মেয়াদ শেষের আগে রিফ্রেশ শুরু হবে (সেকেন্ডে)

async def periodic_refresh(user_id: str):
    print(f"[Periodic] Starting periodic_refresh for user_id={user_id}")
    
    while True:
        try:
            session_key = f"session:{user_id}"
            # session = await r.hgetall(session_key) or {}

            # access_token = (session.get("accessToken") or "").strip()
            # expiry_iso = session.get("expiry") or ""
            # device_id = session.get("deviceId") or "DEVICE_ID"
            # refresh_key = f"refresh:{user_id.strip()}"
            # refresh_token = await r.get(refresh_key)


            data = await read_session(user_id)
            access_token = (data.get("accessToken") or "").strip()
            expiry_iso = data.get("expiry") or ""    
            device_id = data.get("deviceId") or DEVICE_ID

            refresh_key = f"refresh:{user_id.strip()}"
            val = await r.get(refresh_key)
            refresh_token = val.decode() if isinstance(val, bytes) else val

            # print("--------==============----------")
            # print("access::", access_token)
            # print("refresh::", refresh_token)
            # print("expiry::", expiry_iso)
            now = datetime.now()
            # print("Local Time::", now)




            if not access_token or not expiry_iso or not refresh_token:
                print(f"[Periodic] Missing tokens/session for user_id={user_id}. Sleeping 60s.")
                await asyncio.sleep(60)
                continue

            # aware datetime
            now = datetime.now(timezone.utc)
            try:
                expiry = datetime.fromisoformat(expiry_iso.replace("Z", "+00:00"))
            except Exception:
                expiry = None

            need_refresh = (not expiry) or (expiry - now <= timedelta(seconds=ACCESS_TOKEN_BUFFER))
            print(f"[Periodic] Checking refresh for user_id={user_id}, now= {now}, need_refresh={need_refresh}")

            if need_refresh:
                print(f"[Periodic] Calling refresh_if_needed for user_id={user_id}")
                try:
                    result = await refresh_if_needed(access_token, refresh_token, device_id, expiry_iso)
                except HTTPException as e:
                    print(f"[Periodic Refresh Error] {e.status_code}: {e.detail}")
                    if e.status_code == 401:
                        # Invalid refresh, delete session and refresh token
                        print(f"[Periodic] Deleting invalid session/refresh token for user_id={user_id}")
                        await r.delete(session_key)
                        await r.delete(refresh_key)
                        break  # stop periodic_refresh
                    else:
                        # অন্য কোনো error হলে পরের iteration এ আবার চেষ্টা হবে
                        await asyncio.sleep(60)
                        continue

                # update Redis session
                if isinstance(result, tuple):
                    new_access, new_refresh, new_expiry = result
                    await _save_session_to_redis(user_id, new_access, new_refresh, new_expiry, device_id)
                    print(f"[Periodic] Session updated for user_id={user_id}")
                else:
                    print(f"[Periodic] No refresh needed, token valid for user_id={user_id}")

        except Exception as e:
            print(f"[Periodic Refresh Unexpected Error] {e}")

        # পরবর্তী চেকের জন্য sleep
        await asyncio.sleep(60)




# ----------------- Get current token -----------------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Dependency for endpoints: validates Authorization header
    Returns a valid access token string.
    """
    # print("Credentials:", credentials)


    if not credentials:
        raise HTTPException(status_code=401, detail="Not authorized")

    token = credentials.credentials 
    user_id = await get_user_id_from_jwt(token)

    return user_id



# ----------------- Get current token -----------------
async def get_current_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Dependency for endpoints: validates Authorization headeawait r.
    Returns a valid access token string.
    """
    # print("Credentials:", credentials)


    if not credentials:
        raise HTTPException(status_code=401, detail="Not authorized")

    token = credentials.credentials 
    user_id = await get_user_id_from_jwt(token)
    # print("tttttttttttttttttttttttttttttttt", token)
    # print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu", user_id)

    try:
        valid_token = await get_valid_token(token, user_id)
        return valid_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation error: {e}")


import base64
import json
from fastapi import FastAPI, Header, HTTPException

async def get_user_id_from_jwt(token: str) -> str | None:
    """
    Decode a JWT (without verifying signature) and return the `name` claim.
    """
    try:
        header_b64, payload_b64, _ = token.split(".")
        payload_b64 += "=" * (-len(payload_b64) % 4)      # padding ঠিক করা
        payload_json = base64.urlsafe_b64decode(payload_b64).decode()
        payload = json.loads(payload_json)                # এখানে await লাগবে না
        return payload.get("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name")
    except Exception as e:
        print("JWT decode error:", e)
        return None


import asyncio
from datetime import datetime, timedelta


# ================== INFERENCE ==================
@app.post("/predict_batch", response_model=APIResponseSimple, tags=["Prediction"])
async def predict_batch(request: APIRequest, token: str = Depends(get_current_token)):
    if not request.inputs:
        raise HTTPException(status_code=400, detail="Input list is empty")
    text_list = [item.text for item in request.inputs if item.text.strip()]
    if not text_list:
        raise HTTPException(status_code=400, detail="All texts are empty")

    results = await infer_batch(text_list, token)




    # print("Redis Keys print")
    # for key in await r.scan_iter("*"):             # সব key ধাপে ধাপে আনে
    #     key_type = await r.type(key)
    #     print(f"\nKey: {key}  (type: {key_type})")

    #     if key_type == "string":
    #         print("Value:", await r.get(key))
    #     elif key_type == "hash":
    #         print("Value:", await r.hgetall(key))
    #     elif key_type == "list":
    #         print("Value:", await r.lrange(key, 0, -1))
    #     elif key_type == "set":
    #         print("Value:", await r.smembers(key))
    #     elif key_type == "zset":
    #         print("Value:", await r.zrange(key, 0, -1, withscores=True))

    return {"results": results}



from app.redis_utils import save_to_redis, get_from_redis, delete_from_redis
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool

@app.post("/logout")
async def logout(authorization: str | None = Header(default=None)):
    """
    JWT Authorization header থেকে user_id বের করে Redis থেকে সব ডিলিট করবে
    """
    if not authorization:
        raise HTTPException(status_code=400, detail="Missing Authorization header")

    # Authorization: Bearer <token>
    token = authorization.replace("Bearer ", "")
    user_id = await get_user_id_from_jwt(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token or user_id not found")

    # delete_from_redis synchronous, তাই threadpool এ রান করি
    # await run_in_threadpool(delete_from_redis, user_id)
    await delete_from_redis(user_id)

    return {"message": f"{user_id} logged out and cache cleared"}





async def infer_batch(text_list: list[str], token: str) -> list[dict]:
    results = []
    texts = [prepare_text_for_infer(t) for t in text_list]
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=64)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    # print("Tokenized inputs:", inputs)

    with torch.no_grad():
        logits = model(**inputs)

    for i, text in enumerate(texts):
        # logits থেকে লেবেল বের করা
        ner_logits, intent_logits, sentiment_logits, priceStatus_logits, language_logits, context_logits = (
            logits[0][i:i+1], logits[1][i:i+1], logits[2][i:i+1],
            logits[3][i:i+1], logits[4][i:i+1], logits[5][i:i+1]
        )
        ner_result = decode_ner_confident(text, ner_logits, label_maps["ner_label2id"])
        # print("NER Result:", ner_result)

        from collections import OrderedDict 

        boCodes = list(OrderedDict.fromkeys(x["text"] for x in ner_result if "boCode" in x["tag"]))
        tradingCodes = list(OrderedDict.fromkeys(x["text"] for x in ner_result if "tradingCode" in x["tag"]))
        # tradingCodes = [x["text"] for x in ner_result if "tradingCode" in x["tag"]]
        marketTypes = list(OrderedDict.fromkeys(x["text"] for x in ner_result if "marketType" in x["tag"]))
        stockExchanges = list(OrderedDict.fromkeys(x["text"] for x in ner_result if "stockExchange" in x["tag"]))
        intent_label = get_label(intent_logits, label_maps["intent_label2id"])
        sentiment_label = get_label(sentiment_logits, label_maps["sentiment_label2id"])
        status_label = get_label(priceStatus_logits, label_maps["priceStatus_label2id"])
        language_label = get_label(language_logits, label_maps["language_label2id"])
        context_label = get_label(context_logits, label_maps["context_label2id"])

        # print('aaaaaaaaaaaaaaaaaa',tradingCodes, marketTypes, stockExchanges, intent_label, sentiment_label, status_label, language_label, context_label)

     # ➡️ Redis-এ সেভ (শর্ত সহ)
        # fix user_id for development; will be dynamic in production

        try:
            user_id = await get_user_id_from_jwt(token.strip())
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

        await save_to_redis(
            user_id,
            boCodes,
            tradingCodes,
            marketTypes,
            stockExchanges,
            intent_label,
            sentiment_label,
            status_label,
            language_label,
            context_label,
        )

        # --- Redis থেকে সব ডেটা পড়া ---
        # user_id = "ai_hefaj"
        decoded = await get_from_redis(user_id)  # hgetall + TTL রিফ্রেশ

        # hgetall সাধারণত {b'key': b'value'} রিটার্ন করে, তাই decode দরকার হতে পারে
        # decoded = {k.decode() if isinstance(k, bytes) else k:
        #         v.decode() if isinstance(v, bytes) else v
        #         for k, v in stored.items()}

        # যেসব ফিল্ড '|' দিয়ে সেভ করা, সেগুলো split করে নাও
        bo_codes   = decoded.get("boCodes", "").split("|")   if decoded.get("boCodes")   else []
        trading_codes   = decoded.get("tradingCodes", "").split("|")   if decoded.get("tradingCodes")   else []
        market_types    = decoded.get("marketTypes", "").split("|")    if decoded.get("marketTypes")    else []
        stock_exchanges = decoded.get("stockExchanges", "").split("|") if decoded.get("stockExchanges") else []
        intent_label      = decoded.get("intent")
        sentiment_label   = decoded.get("sentiment")
        language_label    = decoded.get("language")
        status_label = decoded.get("priceStatus")
        context_label     = decoded.get("context")

        # print("Decoded redis data:", decoded)

            # === Endpoint Mapping ===
        if intent_label == 'sharePrice':
            endpoint = SHAREPRICE_ENDPOINT
        elif intent_label == 'portfolio':
            endpoint = PORTFOLIO_ENDPOINT
        elif intent_label == 'balance':
            endpoint = BALANCE_ENDPOINT
        else:
            endpoint = None
        print("5555555555555555555:", language_label, sentiment_label, intent_label, status_label)


        responseList= []
        if intent_label=='balance':

            headers = {
                "Authorization": f"Bearer {token}",
                "X-Brokerid": X_BROKER_ID
            }

            bo_codes = [str(x) for x in bo_codes if x] or []
            combos = list(itertools.product(bo_codes))

            if endpoint  and intent_label=='balance' and combos:
                async with httpx.AsyncClient() as client:
                    for bo in combos:
                        url = f"{endpoint}/{X_BROKER_ID}|{bo[0]}"# 64915efea94c25659a7d360d puji broker id
                        try:
                            resp = await client.get(url, headers=headers)
                            if resp.status_code == 200:
                                responseList.append(resp.json())
                            else:
                                responseList.append({
                                    "error": f"API returned {resp.status_code}",
                                    "details": resp.text,
                                    "text": text
                                })
                        except Exception as e:
                            responseList.append({
                                "error": str(e),
                                "text": text
                            })

                status_label="balance"

            # === Always build response ===
                
                generalResponse = build_general_response(
                    language_label, sentiment_label, intent_label, status_label, combos, responseList
                )
                print("gggggggggggggggggggggggggggggggggggggggggggggggggggggb", generalResponse)

                
                    # === Special Case: price_status, se, mt আছে কিন্তু trading_code নাই ===# generalResponse যদি ডিকশনারি হয় তাহলে এটা
                if intent_label=="balance" and not boCodes:
                    generalResponse["recommendResponse"].append(
                        "Please input your Bo Code-"
                    )


                # # if not generalResponse["recommendResponse"] and not generalResponse["specificResponse"]:
                if not generalResponse:
                    generalResponse["recommendResponse"].append(
                        "I need a bit more specific to assist you properly. Could you clarify?"
                    )

                # === Filter market depths (if any) ===
                filtered_response = filter_responseList(responseList, generalResponse, status_label, intent_label)


                results.append({
                    "results": {
                        "tradingCodes": trading_codes,
                        "marketTypes": market_types,
                        "stockExchanges": stock_exchanges,
                        "intent": intent_label,
                        "sentiment": sentiment_label,
                        "language": language_label,
                        "priceStatus": status_label,
                        "context": context_label,
                        "generalResponse": generalResponse,
                        "inputText": text
                    },
                    "responseList": filtered_response            
                })
            print("filtered_responsesssssss:", filtered_response)    
            print("Final Resultssssssss:", results)
            return results






        if intent_label=='sharePrice' and endpoint and trading_codes:

            # responseList = []
            headers = {"Authorization": f"Bearer {token}"}
            stock_exchanges = [x for x in stock_exchanges if x] or ["dse"]
            market_types = [x for x in market_types if x] or ["public"]
            trading_codes = [x for x in trading_codes if x] or []
            bo_codes = [x for x in bo_codes if x] or []


            combos = list(itertools.product(
                stock_exchanges,
                market_types,
                trading_codes
            ))
            # print("Combos:", combos)

            # এখন combos থেকে API কল
            # === API Call (only if trading_codes exist) ===
            # print("Endpoint:", endpoint, "Trading Codes:", trading_codes)
        
            async with httpx.AsyncClient() as client:
                for se, mt, tc in combos:
                    url = f"{endpoint}/{se}/{mt}/{tc}"
                    try:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            responseList.append(resp.json())
                        else:
                            responseList.append({
                                "error": f"API returned {resp.status_code}",
                                "details": resp.text,
                                "text": text
                            })
                    except Exception as e:
                        responseList.append({
                            "error": str(e),
                            "text": text
                        })
        # print("Price List:", responseList)

        # === Always build response ===
                
                generalResponse = build_general_response(
                    language_label, sentiment_label, intent_label, status_label, combos, responseList
                )
                print("ggggggggggggggggggggggggggggggggggggggggggggggggggggg", generalResponse)
                
                
                if intent_label and status_label and not trading_codes:
                    generalResponse["recommendResponse"].append(
                        "Please provide the TradingCode/Item properly to get expected response."
                    )

                if not generalResponse:
                    generalResponse["recommendResponse"].append(
                        "I need a bit more specific to assist you properly. Could you clarify?"
                    )

        if intent_label!='sharePrice' and intent_label!='balance':
            generalResponse = build_general_response(
                language_label, sentiment_label, intent_label
            )            

            if not generalResponse:
                generalResponse["recommendResponse"].append(
                    "I need a bit more specific to assist you properly. Could you clarify?"
                )
        
     

        # === Filter market depths (if any) ===
        filtered_response = filter_responseList(responseList, generalResponse, status_label, intent_label)
        print("filteredddddddddddddddddd_response:", filtered_response)


        results.append({
            "results": {
                "tradingCodes": trading_codes,
                "marketTypes": market_types,
                "stockExchanges": stock_exchanges,
                "intent": intent_label,
                "sentiment": sentiment_label,
                "language": language_label,
                "priceStatus": status_label,
                "context": context_label,
                "generalResponse": generalResponse,
                "inputText": text
            },
            "responseList": filtered_response
        })
    print("General Responseeeeeeeeee111111111111111:", generalResponse)
    print("filtered_responsesssssss1111111111111111:", filtered_response)
    print("Final Resultssssssss11111111111111111111:", results)
    return results


