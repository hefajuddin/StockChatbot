# # utils/response_formatter.py
# from typing import List, Dict
# from app.responses import RESPONSES

# def build_general_response(language_label, sentiment_label, intent_label, status_label, combos):
#     """
#     language_label, sentiment_label, intent_label, status_label অনুযায়ী
#     generalResponse তৈরী করবে। RESPONSES থেকে টেমপ্লেট নিয়ে।
#     """
#     generalResponse = []

#     # language_label সাপোর্ট না করলে default 'bn'
#     lang_responses = RESPONSES.get(language_label, RESPONSES.get("bn", {}))

#     # === Sentiment ===
#     sentiment_text = lang_responses.get("sentiment", {}).get(sentiment_label)
#     if sentiment_text:
#         generalResponse.append(sentiment_text)

#     # === Intent ===
#     if intent_label == "sharePrice":
#         template = lang_responses.get("sharePrice", {}).get(status_label)
#         if template and combos:
#             for se, mt, tc in combos:
#                 values = {
#                     "se": se or "dse",
#                     "mt": mt or "public",
#                     "tc": tc.lower() if tc else ""
#                 }
#                 generalResponse.append(template.format(**values))
#     else:
#         intent_text = lang_responses.get("intent", {}).get(intent_label)
#         if intent_text:
#             generalResponse.append(intent_text)

#     return generalResponse





from typing import List, Dict
from app.responses import RESPONSES


def build_general_response(
    language_label: str,
    sentiment_label: str,
    intent_label: str,
    status_label: str=None,
    combos: List[tuple]=None,
    responseList: List[dict] = None
) -> Dict[str, List[str]]:
    """
    language_label, sentiment_label, intent_label, status_label অনুযায়ী
    recommendResponse এবং specificResponse আলাদা আকারে বানিয়ে রিটার্ন করবে।
    """
    recommendResponse: List[str] = []
    specificResponse: List[str] = []

    # language_label সাপোর্ট না করলে default 'bn'
    lang_responses = RESPONSES.get(language_label, RESPONSES.get("bn", {}))

    # === Sentiment অংশ recommendResponse-এ ===
    sentiment_text = lang_responses.get("sentiment", {}).get(sentiment_label)
    
    if sentiment_text:
        recommendResponse.append(sentiment_text)

    # === Intent ===
    if intent_label == "sharePrice":
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', combos, status_label)
        template = lang_responses.get("sharePrice", {}).get(status_label)
        print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", template)
        if template and combos:
            for se, mt, tc in combos:
                print("zzzz", (se, mt, tc))
                values = {
                    "se": se or "dse",
                    "mt": mt or "public",
                    "tc": tc.lower() if tc else ""
                }
                print('sssssssssssssssssssssssssssssss', values)
 
                specificResponse.append(template.format(**values))
    
    
    elif intent_label == "balance":
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', combos, status_label)
        template = lang_responses.get("balance", {}).get(status_label)
        print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", template)
        if template and combos:
            for code in combos:
                print("zzzz", code)
                values = {
                    "code": code.lower() if isinstance(code, str) else code[0]
                }
                print('sssssssssssssssssssssssssssssss', values)
                
                specificResponse.append(template.format(**values))
        
                
    else:
        
        # অন্য intent হলে সরাসরি recommendResponse-এ
        intent_text = lang_responses.get("intent", {}).get(intent_label)
        if intent_text:
            recommendResponse.append(intent_text)
        print("kkkkkkkkkkkkkkkkkkkkkkkkkk", intent_label, language_label, sentiment_label, status_label, intent_text, recommendResponse)

    return {
        "recommendResponse": recommendResponse,
        "specificResponse": specificResponse
    }



def filter_responseList(responseList: List[dict], generalResponse: List[str], status=None, intent_label=None) -> List[dict]:
    if not responseList:
        return []   # follow-up case → just return empty list

    if not generalResponse:
        return ["Please input more specific..."]
    
    keyword_map = {}
    if intent_label == "sharePrice":
        keyword_map = {
            "volume": ["volume"],
            "ltp": ["ltp"],
            "value": ["value"],
            "ycp": ["ycp"],
            "marketDepth": ["buySellDetails"],
            "all": ["open", "ltp", "ycp", "close", "high", "low", "trade", "volume", "value", "change"],
            "price": ["open", "ltp", "ycp", "close", "high", "low"],
            "No": [],
            None: [],
        }
    if intent_label == "balance":
        status="balance"
        keyword_map = {
            "balance": ["cashBalance", "maturedBalance"],
            "No": [],
            None: [],
        }

    filtered = []
    for depth in responseList:
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