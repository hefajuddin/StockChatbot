# utils/response_formatter.py
from typing import List, Dict
from app.responses import RESPONSES

def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments):
    """
    language_label, sentiment_label, intent_label, priceStatus_label অনুযায়ী
    generalResponse তৈরী করবে। 
    """
    generalResponse = []

    if language_label == "bn":
        # === Sentiment ===
        sentiment_text = RESPONSES["bn"]["sentiment"].get(sentiment_label)
        if sentiment_text:
            generalResponse.append(sentiment_text)

        # === Intent ===
        if intent_label == "sharePrice":
            trading_codes = arguments.get("trading_codes", [])
            template = RESPONSES["bn"]["sharePrice"].get(priceStatus_label)
            if template and trading_codes:
                for tc in trading_codes:
                    generalResponse.append(template.format(tc))
        else:
            intent_text = RESPONSES["bn"]["intent"].get(intent_label)
            if intent_text:
                generalResponse.append(intent_text)

    return generalResponse

def filter_market_depths(market_depths: List[dict], generalResponse: List[str], status=None) -> List[dict]:
    if not market_depths:
        return []   # follow-up case → just return empty list

    if not generalResponse:
        return ["Please input more specific..."]

    keyword_map = {
        "volume": ["volume"],
        "ltp": ["ltp"],
        "value": ["value"],
        "ycp": ["ycp"],
        "maketDepth": ["buySellDetails"],
        "marketDepth": ["buySellDetails"],
        "all": ["open", "ltp", "ycp", "close", "high", "low", "trade", "volume", "value", "change"],
        "price": ["open", "ltp", "ycp", "close", "high", "low"],
        "No": []
    }

    filtered = []
    for depth in market_depths:
        data = depth.get("data", {})
        selected = {}

        keys_to_check = [status] if status else keyword_map.keys()

        for key in keys_to_check:
            fields = keyword_map.get(key, [])
            for f in fields:
                if f in data:
                    selected[f] = data[f]

        if selected:
            filtered.append(selected)
        else:
            filtered.append(data)

    return filtered