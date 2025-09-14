# app/responses.py

RESPONSES = {
    "bn": {
        "sentiment": {
            "positive": "নিশ্চই স্যার...",
            "angry": "আপনার কষ্টের কারণ হয়ে থাকলে দুঃখিত; দয়াকরে শান্ত হোন। উত্তেজিত অবস্থায় সঠিক সিদ্ধান্ত নেওয়া কঠিন।",
            "bye": "আপনাকে ধন্যবাদ। কোনো প্রশ্ন থাকলে পরবর্তীতে জানাবেন।",
            "appreciate": "আপনাকে অনেক অনেক ধন্যবাদ। আমি ভবিষ্যতে আরো ইমপ্রুভ করার চেষ্টা করব।",
            "introduction": "আমি একজন স্টক মার্কেট এসিস্ট্যান্ট। আমি আপনাকে বাংলাদেশ স্টক মার্কেটের তথ্য দিয়ে সহায়তা করতে পারি বিশেষ করে শেয়ার প্রাইস।",
            "irrelevant": "দয়াকরে বাংলাদেশ স্টক মার্কেট সম্পর্কে প্রশ্ন করুন বিশেষ করে শেয়ার প্রাইস।",
            "greetAsk": "হ্যা, সবকিছুই ভাল যাচ্ছে, ধন্যবাদ আপনাকে...",
            "fun": "হুম.. আমি বুঝতে পেরেছি তুমি আমার সাথে মজা করছ। এসব বাদ দিয়ে শেয়ার মার্কেটে মনোযোগ দাও, প্রয়োজনে আমার সহযোগিতা নাও।",
            "greet": "হ্যালো বন্ধু, আমি আপনাকে সাহায্য করতে সর্বদা প্রস্তুত-",
            "nudity": "নগ্নতা এখানে অনুমোদিত নয়, দয়াকরে সংযত হোন।",
            # "shortcut": "আচ্চা...",
            "neutral": "",
        },
        "intent": {
            "analysis": "আপাতত শেয়ার এনালাইসিস বিষয়ে আমার যথেষ্ট জ্ঞান নেই। এ বিষয়ে আমি শিখছি...",
            "trade": "আপাতত শেয়ার বাই/সেল বিষয়ে আমার যথেষ্ট জ্ঞান নেই। এ বিষয়ে আমি শিখছি...",
            "portfolio": "আপাতত এই বিষয়ে আমার যথেষ্ট জ্ঞান নেই। এ বিষয়ে আমি শিখছি...",
            "balance": "আপাতত এই বিষয়ে আমার যথেষ্ট জ্ঞান নেই। এ বিষয়ে আমি শিখছি...",
            "other": "আপাতত এই বিষয়ে আমার যথেষ্ট জ্ঞান নেই। দয়াকরে বাংলাদেশ স্টক মার্কেট সম্পর্কে স্পষ্ট প্রশ্ন করুন।",
            "dialogue": "দয়াকরে বাংলাদেশ স্টক মার্কেট সম্পর্কে স্পষ্ট প্রশ্ন করুন।",
            "comment": "ধন্যবাদ। বুঝতে পেরেছি...,",
            None : "প্রত্যাশিত উত্তর পাওয়ার জন্য স্পষ্ট প্রশ্ন করুন।",
        },
        "sharePrice": {
            "volume": "{se} তে {mt} মার্কেটে {tc} এর volume হল-",
            "ltp": "{se} তে {mt} মার্কেটে {tc} এর ltp হল-",
            "value": "{se} তে {mt} মার্কেটে {tc} এর value হল-",
            "ycp": "{se} তে {mt} মার্কেটে {tc} এর  ycp হল-",
            "maketDepth": "{se} তে {mt} মার্কেটে {tc} এর market depth হল-",
            "all": "{se} তে {mt} মার্কেটে {tc} এর price সম্পর্কে বিস্তারিত হল-",
            "marketDepth": "{se} তে {mt} মার্কেটে {tc} এর market depth হল-",
            "price": "{se} তে {mt} মার্কেটে {tc} এর price সম্পর্কে তথ্য হল-",
            "No": "{tc} এর সম্পর্কে আপনি কী জানতে চান, দয়াকরে স্পষ্টভাবে বলুন-",
        },

    },

    "bn-latn": {
        "sentiment": {
            "positive": "nischoi sir...",
            "angry": "apnake sontushto korte na parar jonno dukhito; doyakore shanto hon. uttejito obosthay sothik siddhanto neoa kothin.",
            "bye": "apnake dhonnobad. kono proshno thakle porobortite janaben.",
            "appreciate": "apnake onek onek dhonnobad. ami vobisshote aro improv korar cheshta korbo.",
            "introduction": "ami ekjon stock market assistant. ami apnake bangladesh stock market-er tottho diye sohayota korte pari bishesh kore share price.",
            "irrelevant": "doyakore bangladesh stock market somporke proshno korun bishesh kore share price.",
            "greetAsk": "ha, sobkichu-i bhalo jacche, dhonnobad apnake...",
            "fun": "hum.. ami bujhte perechi tumi amar sathe moja korcho. eshob bad diye share market-e monojog dao, proyojone amar sohojogita nao.",
            "greet": "hello bondhu, ami apnake sahajjo korte shorboda prostut-",
            "nudity": "nognota ekhane onumodito noy, doyakore songjoto hon.",
            # "shortcut": "accha...",
            "neutral": "",
        },
        "intent": {
            "analysis": "apatoto ei bisoye amar jothesto gyan nei. ei bisoye ami shikhchi...",
            "trade": "apatoto ei bisoye amar jothesto gyan nei. ei bisoye ami shikhchi...",
            "portfolio": "apatoto ei bisoye amar jothesto gyan nei. ei bisoye ami shikhchi...",
            "balance": "apatoto ei bisoye amar jothesto gyan nei. ei bisoye ami shikhchi...",
            "other": "apatoto ei bisoye amar jothesto gyan nei. doyakore bangladesh stock market somporke spostho proshno korun.",
            "dialogue": "doyakore bangladesh stock market somporke spostho proshno korun.",
            "comment": "dhonnobad. bujhte perechi...,",
            None : "protyashito uttor pawar jonno spostho proshno korun।",
        },
        "sharePrice": {
            "volume": "{se} te {mt} market e {tc} er volume holo-",
            "ltp": "{se} te {mt} market e {tc} er ltp holo-",
            "value": "{se} te {mt} market e {tc} er value holo-",
            "ycp": "{se} te {mt} market e {tc} er ycp holo-",
            "maketDepth": "{se} te {mt} market e {tc} er market depth holo-",
            "all": "{se} te {mt} market e {tc} er price somporke bistariito holo-",
            "marketDepth": "{se} te {mt} market e {tc} er market depth holo-",
            "price": "{se} te {mt} market e {tc} er price somporke tottho holo-",
            "No": "{tc} er somporke apni ki jante chan, doyakore spostho bhabe bolun-"
        }
    },

    "en": {
        "sentiment": {
            "positive": "Sure sir...",
            "angry": "Sorry for not being able to satisfy you; please stay calm. It's hard to make the right decision when you're upset.",
            "bye": "Thank you. If you have any questions, feel free to ask later.",
            "appreciate": "Thank you very much. I will try to improve even more in the future.",
            "introduction": "I am a stock market assistant. I can help you with Bangladesh stock market information, especially share prices.",
            "irrelevant": "Please ask questions about the Bangladesh stock market, especially share prices.",
            "greetAsk": "Yes, everything is going well, thank you...",
            "fun": "Haha.. I see you are joking with me. Let's focus on the stock market, and feel free to ask for my help if needed.",
            "greet": "Hello friend, I am always ready to help you-",
            "nudity": "Nudity is not allowed here, please be cautious.",
            # "shortcut": "absolutely...",
            "neutral": "",
        },
        "intent": {
            "analysis": "I don't have enough knowledge on this topic yet. I'm still learning...",
            "trade": "I don't have enough knowledge on this topic yet. I'm still learning...",
            "portfolio": "I don't have enough knowledge on this topic yet. I'm still learning...",
            "balance": "I don't have enough knowledge on this topic yet. I'm still learning...",
            "other": "I don't have enough knowledge on this topic yet. Please ask a clear question about the Bangladesh stock market.",
            "dialogue": "Please ask a clear question about the Bangladesh stock market.",
            "comment": "Thank you. I understand...,",
            None : "Please ask a clear question to get the expected answer.",
        },
        "sharePrice": {
            "volume": "At {se} in {mt} market {tc}'s volume is-",
            "ltp": "At {se} in {mt} market {tc}'s LTP is-",
            "value": "At {se} in {mt} market {tc}'s value is-",
            "ycp": "At {se} in {mt} market {tc}'s YCP is-",
            "maketDepth": "At {se} in {mt} market {tc}'s market depth is-",
            "all": "At {se} in {mt} market detailed price information for {tc} is-",
            "marketDepth": "At {se} in {mt} market {tc}'s market depth is-",
            "price": "At {se} in {mt} market price information for {tc} is-",
            "No": "What do you want to know about {tc}? Please specify clearly-"
        }
    }    
}
