

import redis.asyncio as aioredis
from typing import List, Dict

# Redis async client
r = aioredis.Redis(host="localhost", port=6379, db=0)  # decode_responses=True প্রয়োজন নেই, bytes handle করা হয়েছে

# TTL: ১ সপ্তাহ
KEY_TTL = 7 * 24 * 60 * 60  # seconds


async def save_to_redis(
    user_id: str,
    boCodes: List[str] = None,
    tradingCodes: List[str] = None,
    marketTypes: List[str] = None,
    stockExchanges: List[str] = None,
    intent: str = None,
    sentiment: str = None,
    priceStatus: str = None,
    language: str = None,
    context: str = None,
):
    """Save session data to Redis with TTL."""
    key = f"chat:{user_id}"
    mapping = {}

    if boCodes and any(x.strip() for x in boCodes):
        mapping["boCodes"] = "|".join(boCodes)
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
        await r.hset(key, mapping=mapping)
        await r.expire(key, KEY_TTL)


async def get_from_redis(user_id: str) -> Dict[str, str]:
    """Read session data and refresh TTL (sliding TTL)."""
    key = f"chat:{user_id}"
    data = await r.hgetall(key)
    if data:
        # bytes → string conversion
        data = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
        # TTL refresh
        await r.expire(key, KEY_TTL)
    return data


async def delete_from_redis(user_id: str):
    """Delete all keys in Redis that contain the given user_id."""
    cursor = 0
    user_keys = []

    while True:
        cursor, keys = await r.scan(cursor=cursor, match=f"*{user_id}*", count=100)
        for k in keys:
            if isinstance(k, bytes):
                k = k.decode()
            user_keys.append(k)
        if cursor == 0:
            break

    if user_keys:
        await r.delete(*user_keys)
        print(f"[Redis] Deleted keys: {user_keys}")
    else:
        print(f"[Redis] No keys found for user_id={user_id}")
