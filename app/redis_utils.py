# import redis
# from typing import List

# r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# def save_to_redis(
#     user_id: str,
#     tradingCodes: List[str],
#     marketTypes: List[str],
#     stockExchanges: List[str],
#     intent: str,
#     sentiment: str,
#     priceStatus: str,
#     language: str,
#     context: str,
# ):
#     key = f"chat:{user_id}"
#     current = r.hgetall(key)
#     mapping = {}

#     if tradingCodes and any(x.strip() for x in tradingCodes):
#         mapping["tradingCodes"] = "|".join(tradingCodes)
#     if marketTypes and any(x.strip() for x in marketTypes):
#         mapping["marketTypes"] = "|".join(marketTypes)
#     if stockExchanges and any(x.strip() for x in stockExchanges):
#         mapping["stockExchanges"] = "|".join(stockExchanges)
#     if intent and intent != "previous":
#         mapping["intent"] = intent
#     if sentiment:
#         mapping["sentiment"] = sentiment
#     if language:
#         mapping["language"] = language
#     if context:
#         mapping["context"] = context
#     if priceStatus and priceStatus != "No":
#         mapping["priceStatus"] = priceStatus

#     if mapping:
#         r.hset(key, mapping=mapping)
#         r.expire(key, 3600)





# redis_utils.py

import redis
from typing import List

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
KEY_TTL = 3600  # ১ ঘন্টা

def save_to_redis(
    user_id: str,
    tradingCodes: List[str],
    marketTypes: List[str],
    stockExchanges: List[str],
    intent: str,
    sentiment: str,
    priceStatus: str,
    language: str,
    context: str,
):
    key = f"chat:{user_id}"
    mapping = {}

    if tradingCodes and any(x.strip() for x in tradingCodes):
        mapping["tradingCodes"] = "|".join(tradingCodes)
    if marketTypes and any(x.strip() for x in marketTypes):
        mapping["marketTypes"] = "|".join(marketTypes)
    if stockExchanges and any(x.strip() for x in stockExchanges):
        mapping["stockExchanges"] = "|".join(stockExchanges)
    if intent and intent != "previous":
        mapping["intent"] = intent
    if sentiment:
        mapping["sentiment"] = sentiment
    if language:
        mapping["language"] = language
    if context:
        mapping["context"] = context
    if priceStatus and priceStatus != "No":
        mapping["priceStatus"] = priceStatus

    if mapping:
        r.hset(key, mapping=mapping)
        r.expire(key, KEY_TTL)  # TTL set

def get_from_redis(user_id: str) -> dict:
    """
    ডেটা রিড করবে এবং একই সময় TTL রিফ্রেশ করবে (sliding TTL)
    """
    key = f"chat:{user_id}"
    data = r.hgetall(key)
    if data:
        # ডেটা থাকলে TTL রিফ্রেশ
        r.expire(key, KEY_TTL)
    return data

def delete_from_redis(user_id: str):
    """
    লগআউট বা explicit delete
    """
    key = f"chat:{user_id}"
    r.delete(key)
