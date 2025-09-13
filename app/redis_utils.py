import redis
from typing import List

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

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
    current = r.hgetall(key)
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
        r.expire(key, 3600)
