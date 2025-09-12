# utils/response_formatter.py
from typing import List, Dict
from app.responses import RESPONSES

# def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments):
#     """
#     language_label, sentiment_label, intent_label, priceStatus_label অনুযায়ী
#     generalResponse তৈরী করবে। 
#     """
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



# def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments, combos):
#     """
#     language_label, sentiment_label, intent_label, priceStatus_label অনুযায়ী
#     generalResponse তৈরী করবে। 
#     """
#     generalResponse = []

#     print("mmmmmmmmmmmmmmmmmmmmmmmmmm", arguments)

#     # language_label সাপোর্ট না করলে default 'bn'
#     lang_responses = RESPONSES.get(language_label, RESPONSES.get("bn", {}))

#     # === Sentiment ===
#     sentiment_text = lang_responses.get("sentiment", {}).get(sentiment_label)
#     if sentiment_text:
#         generalResponse.append(sentiment_text)

#     # === Intent ===
#     if intent_label == "sharePrice":
#         trading_codes = arguments.get("trading_codes", [])

#         template = lang_responses.get("sharePrice", {}).get(priceStatus_label)
#         if template and trading_codes:

#             # helper ফাংশন: যদি ভ্যালু লিস্ট হয় তাহলে প্রথম এলিমেন্ট নেবে
#             def normalize(value, default):
#                 if isinstance(value, list) and value:
#                     return value[0]
#                 return value if value else default

#             for tc in trading_codes:
#                 values = {
#                     "se": normalize(arguments.get("stock_exchange"), "dse"),
#                     "mt": normalize(arguments.get("market_type"), "public"),
#                     "tc": tc.lower()  # trading_code lowercase করলে সুন্দর দেখাবে
#                 }
#                 generalResponse.append(template.format(**values))

#     else:
#         intent_text = lang_responses.get("intent", {}).get(intent_label)
#         if intent_text:
#             generalResponse.append(intent_text)

#     return generalResponse




def build_general_response(language_label, sentiment_label, intent_label, priceStatus_label, arguments, combos):
    """
    language_label, sentiment_label, intent_label, priceStatus_label অনুযায়ী
    generalResponse তৈরী করবে। RESPONSES থেকে টেমপ্লেট নিয়ে।
    """
    generalResponse = []

    # language_label সাপোর্ট না করলে default 'bn'
    lang_responses = RESPONSES.get(language_label, RESPONSES.get("bn", {}))

    # === Sentiment ===
    sentiment_text = lang_responses.get("sentiment", {}).get(sentiment_label)
    if sentiment_text:
        generalResponse.append(sentiment_text)

    # === Intent ===
    if intent_label == "sharePrice":
        template = lang_responses.get("sharePrice", {}).get(priceStatus_label)
        if template and combos:
            for se, mt, tc in combos:
                values = {
                    "se": se or "dse",
                    "mt": mt or "public",
                    "tc": tc.lower() if tc else ""
                }
                generalResponse.append(template.format(**values))
    else:
        intent_text = lang_responses.get("intent", {}).get(intent_label)
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
        print("a", keys_to_check)

        if keys_to_check == ["No"]:
            return []


        for key in keys_to_check:
            fields = keyword_map.get(key, [])
            for f in fields:
                if f in data:
                    selected[f] = data[f]
                    print("b", f, data[f])

        if selected:
            filtered.append(selected)
        else:
            filtered.append(data)

    print("c", filtered)
    return filtered