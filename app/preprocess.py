import unicodedata
from rapidfuzz import process, fuzz

# ===================== Mappings =====================
trading_codes_mapping_bangla2english = {
"ZAHINTEX": ["যাহিনটেক্স"],
    "ZAHEENSPIN": ["জাহিনস্পিন"],
    "YUSUFLOUR": ["ইউসুফফ্লাওয়ার", "ইউসুফফ্লাওয়ার্স"],
    "GP": ["জিপি", "জীপি"],
    "WONDERTOYS": ["ওন্ডারটয়েস"],
    "WMSHIPYARD": ["ডাব্লিউএমশিপইয়ার্ড"],
    "WEBCOATS": ["ওয়েবকোটস"],
    "WATACHEM": ["ওয়াটাকেম"],
    "WALTONHIL": ["ওয়ালটনহিল"],
    "VFSTDL": ["ভিএফএসটিডিএল"],
    "VAMLRBBF": ["ভিএমএলআরবিবিএফ"],
    "VAMLBDMF1": ["ভিএমএলবিডিএমএফ১"],
    "UTTARAFIN": ["উত্তরাফিন"],
    "UTTARABANK": ["উত্তরাব্যাংক"],
    "USMANIAGL": ["উসমানিআজি এল"],
    "UPGDCL": ["আপিজিডিসিএল"],
    "UNITEDINS": ["ইউনাইটেডইনস"],
    "UNITEDFIN": ["ইউনাইটেডফিন"],
    "UNIQUEHRL": ["ইউনিকএইচআরএল"],
    "UNIONINS": ["ইউনিয়নইনস"],
    "UNIONCAP": ["ইউনিয়নক্যাপ"],
    "UNIONBANK": ["ইউনিয়নব্যাংক"],
    "UNILEVERCL": ["ইউনিলিভারসিএল"],
    "UCB": ["ইউসিবি"],
    "TUNGHAI": ["টাংহাই"],
    "TRUSTBANK": ["ট্রাস্টব্যাংক"],
    "TRUSTB1MF": ["ট্রাস্টবিফার্স্টএমএফ"],
    "TOSRIFA": ["তোসরিফা"],
    "TITASGAS": ["টাইটাসগ্যাস"],
    "TILIL": ["টিলিল"],
    "TECHNODRUG": ["টেকনোড্রাগ"],
    "TB5Y0630": ["টিবি৫ও৬৩০"],
    "TB5Y0529": ["টিবি৫ও৫২৯"],
    "TB2Y0826": ["টিবি২ও৮২৬"],
    "TAMIJTEX": ["তামিজটেক্স"],
    "TALLUSPIN": ["টাল্লাসপিন"],
    "TAKAFULINS": ["তাকাফুলইনস"],
    "SUNLIFEINS": ["সানলাইফইনস"],
    "SUMITPOWER": ["সুমিটপাওয়ার"],
    "STYLECRAFT": ["স্টাইলক্রাফট"],
    "STANDBANKL": ["স্ট্যান্ডব্যাংকলিমিটেড", "স্ট্যান্ডব্যাংকলি"],
    "STANDARINS": ["স্ট্যান্ডারইনস", "স্ট্যান্ডারইন্স্যুরেন্স"],
    "STANCERAM": ["স্ট্যানসেরাম"],
    "SSSTEEL": ["এসএসস্টীল"],
    "SQURPHARMA": ["এসকিউইউআরফার্মা"],
    "SQUARETEXT": ["স্কোয়ারটেক্সট"],
    "SPCL": ["এসপিসিএল"],
    "SPCERAMICS": ["এসপিসিরামিক্স"],
    "SOUTHEASTB": ["সাউথইস্টবি"],
    "SONARGAON": ["সোনারগাঁও"],
    "SONARBAINS": ["সোনারবাংলাইন্স্যুরেন্স"],
    "SONALIPAPR": ["সোনালিপেপার"],
    "SONALILIFE": ["সোনালিলাইফ"],
    "SONALIANSH": ["সোনালিআঁশ", "সোনালিআশ"],
    "SKTRIMS": ["এসকেট্রিমস"],
    "SIPLC": ["এসআইপিএলসি"],
    "SINOBANGLA": ["সিনোবাংলা"],
    "SINGERBD": ["সিঙ্গারবিডি"],
    "SIMTEX": ["সিমটেক্স"],
    "SILVAPHL": ["সিলভাফার্মা", "সিলভাফার্মালিমিটেড"],
    "SILCOPHL": ["সিলকোফার্মা"],
    "SICL": ["এসআইসিএল"],
    "SIBL": ["এসআইবিএল"],
    "SHYAMPSUG": ["শ্যামপসুগ"],
    "SHURWID": ["শুরিদ"],
    "SHEPHERD": ["শেফার্ড"],
    "SHASHADNIM": ["শাশাডেনিম"],
    "SHARPIND": ["শার্পইন্ড"],
    "SHAHJABANK": ["শাহজাব্যাংক", "শাহজালালব্যাংক"],
    "SEMLLECMF": ["এসইমএলএলইসিএমএফ"],
    "SEMLIBBLSF": ["এসইমএলআইবিবিএলএসএফ"],
    "SEMLFBSLGF": ["এসইমএলএফবিএসএলজিএফ"],
    "SEAPEARL": ["সীপার্ল"],
    "SBACBANK": ["এসবিএসিব্যাংক"],
    "SAPORTL": ["সাপোর্টএল"],
    "SANDHANINS": ["সন্ধানীইনস", "সন্ধানী ইন্স্যুরেন্স", "সন্ধানী"],
    "SAMORITA": ["সামোরিতা","সামরিতা"],
    "SAMATALETH": ["সমতালেথ", "সমতালেদার"],
    "SALVOCHEM": ["সালভোকেম","সালভো"],
    "SALAMCRST": ["সালামসিআরএসটি"],
    "SAIHAMTEX": ["সাইহামটেক্স"],
    "SAIHAMCOT": ["সাইহামকট", "সাইহামকটন"],
    "SAIFPOWER": ["সাইফপাওয়ার"],
    "SABKOSPINN": ["সবকোস্পিন"],
    "SADHESIVE": ["সাধেসিভ"],
    "RUPALILIFE": ["রূপালিলাইফ"],
    "RUPALIINS": ["রূপালিইনস", "রূপালিইন্স্যুরেন্স"],
    "RUPALIBANK": ["রূপালিব্যাংক"],
    "RUNNERAUTO": ["রানারঅটো"],
    "RSRMSTEEL": ["আরএসআরএমস্টীল"],
    "ROBI": ["রবি"],
    "RINGSHINE": ["রিংশাইন"],
    "REPUBLIC": ["রিপাবলিক"],
    "RENWICKJA": ["রেনউইকজা"],
    "RENATA": ["রেনাটা","রেনেটা"],
    "RELIANCINS": ["রিলায়েন্সইনস"],
    "RELIANCE1": ["রিলায়েন্স১"],
    "REGENTTEX": ["রিজেন্টটেক্স"],
    "RECKITTBEN": ["রেকিটটবেন"],
    "RDFOOD": ["আরডিফুড"],
    "RANFOUNDRY": ["রানফাউন্ড্রি"],
    "RAKCERAMIC": ["র‌্যাককসিরামিক", "আরএকেসিরামিক"],
    "RAHIMTEXT": ["রাহিমটেক্সট"],
    "RAHIMAFOOD": ["রাহিমাফুড"],
    "QUEENSOUTH": ["কুইনসাউথ"],
    "QUASEMIND": ["কাশেমইন্ড", "কাশেমইন্ডাস্ট্রিজ"],
    "PURABIGEN": ["পুরাবিজেন"],
    "PUBALIBANK": ["পুবালিব্যাংক"],
    "PTL": ["পিটিএল"],
    "PROVATIINS": ["প্রোভাতইনস"],
    "PROGRESLIF": ["প্রগ্রেসলাইফ"],
    "PRIMETEX": ["প্রাইমটেক্স"],
    "PRIMELIFE": ["প্রাইমলাইফ"],
    "PRIMEINSUR": ["প্রাইমইনসুর"],
    "PRIMEFIN": ["প্রাইমফিন"],
    "PRIMEBANK": ["প্রাইমব্যাংক"],
    "PRIME1ICBA": ["প্রাইম১আইসিবিএ"],
    "PREMIERLEA": ["প্রিমিয়ারলী"],
    "PREMIERCEM": ["প্রিমিয়ারসিম"],
    "PREMIERBAN": ["প্রিমিয়ারব্যাংক"],
    "PRAGATILIF": ["প্রগাতিলাইফ"],
    "PRAGATIINS": ["প্রগাতিইনস"],
    "POWERGRID": ["পাওয়ারগ্রিড"],
    "POPULARLIF": ["পপুলারলাইফ"],
    "POPULAR1MF": ["পপুলার১এমএফ"],
    "PLFSL": ["পিএলএফএসএল"],
    "PIONEERINS": ["পায়োনিয়ারইনস"],
    "PHPMF1": ["পিএইচপিএমএফ১"],
    "PHOENIXFIN": ["ফিনিক্সফিন"],
    "PHENIXINS": ["ফেনিক্সইনস"],
    "PHARMAID": ["ফার্মাএইড"],
    "PF1STMF": ["পিএফ১স্টএমএফ"],
    "PEOPLESINS": ["পিপলইনস"],
    "PENINSULA": ["পেনিনসুলা"],
    "PDL": ["পিডিএল"],
    "PARAMOUNT": ["প্যারামাউন্ট"],
    "PADMAOIL": ["পদ্মাঅয়েল"],
    "ORYZAAGRO": ["ওরাইজাএগ্রো"],
    "ORIONPHARM": ["ওরিয়নফার্ম"],
    "ORIONINFU": ["ওরিয়নইনফু"],
    "ONEBANKPLC": ["ওনেব্যাংকপিএলসি"],
    "OLYMPIC": ["ওলিম্পিক"],
    "OIMEX": ["ওআইমেক্স"],
    "OAL": ["ওএএল"],
    "NURANI": ["নুরানী"],
    "NTLTUBES": ["এনটিএলটিউবস"],
    "NTC": ["এনটিসি"],
    "NRBCBANK": ["এনআরবিসিব্যাংক"],
    "NRBBANK": ["এনআরবিব্যাংক"],
    "NPOLYMER": ["এনপলিমার"],
    "NORTHRNINS": ["নর্দার্নইন্স্যুরেন্স"],
    "NORTHERN": ["নর্দার্ন"],
    "NITOLINS": ["নিটলইনস"],
    "NIALCO": ["নিয়ালকো"],
    "NHFIL": ["এনএইচফিল"],
    "NFML": ["এনএফএমএল"],
    "NEWLINE": ["নিউলাইন"],
    "NCCBLMF1": ["এনসিসিবিএলএমএফ১"],
    "NCCBANK": ["এনসিসিব্যাংক"],
    "NBL": ["এনবিএল"],
    "NAVANAPHAR": ["নাভানাফার"],
    "NAVANACNG": ["নাভানাসিএনজি"],
    "NATLIFEINS": ["ন্যাটলাইফইনস"],
    "NAHEEACP": ["নাহীএকেপি"],
    "MTB": ["এমটিবি"],
    "MPETROLEUM": ["এমপেট্রোলিয়াম"],
    "MOSTFAMETL": ["মোস্টফ্যামেটাল"],
    "MONOSPOOL": ["মনোসপুল"],
    "MONNOFABR": ["মননোফ্যাব্র"],
    "MONNOCERA": ["মননোসিরা"],
    "MONNOAGML": ["মননোএজিএমএল"],
    "MLDYEING": ["এমএলডাইয়িং"],
    "MKFOOTWEAR": ["এমকেফুটওয়্যার"],
    "MJLBD": ["এমজেএলবিডি"],
    "MITHUNKNIT": ["মিথুননিট"],
    "MIRAKHTER": ["মিরাখতার","মিরআখতার"],
    "MIRACLEIND": ["মিরাকলইন্ড"],
    "MIDLANDBNK": ["মিডল্যান্ডব্যাংক"],
    "MIDASFIN": ["মিডাসফিন","মিদাসফিন"],
    "MHSML": ["এমএইচএসএমএল"],
    "METROSPIN": ["মেট্রোস্পিন"],
    "MERCINS": ["মারকইনস", "মার্কেন্টাইলইন্স্যুরেন্স"],
    "MERCANBANK": ["মার্কানব্যাংক", "মার্কেন্টাইলব্যাংক"],
    "MEGHNAPET": ["মেঘনাপেট"],
    "MEGHNALIFE": ["মেঘনালাইফ"],
    "MEGHNAINS": ["মেঘনাইনস", "মেঘনাইন্স্যুরেন্স"],
    "MEGHNACEM": ["মেঘনাসিমেন্ট"],
    "MEGCONMILK": ["মেগকনমিল্ক"],
    "MBL1STMF": ["এমবিএল১স্টএমএফ"],
    "MATINSPINN": ["মাতিনস্পিন"],
    "MASTERAGRO": ["মাস্টারঅ্যাগ্রো"],
    "MAMUNAGRO": ["মামুনঅ্যাগ্রো"],
    "MALEKSPIN": ["মালেকস্পিন"],
    "MAKSONSPIN": ["ম্যাকসন্সপিন"],
    "MAGURAPLEX": ["মাগুরাপ্লেক্স"],
    "LRGLOBMF1": ["এলআরজিএলওবিএমএফ১"],
    "LRBDL": ["এলআরবিডিএল"],
    "LOVELLO": ["লাভেল্লো"],
    "LINDEBD": ["লিন্ডাবিডি", "লিনডাবিডি"],
    "LIBRAINFU": ["লাইব্রাইনফু", "লিব্রাইনফু"],
    "LHB": ["এলএইচবি"],
    "LEGACYFOOT": ["লিগ্যাসিফুট"],
    "LANKABAFIN": ["লঙ্কাবাফিন"],
    "KTL": ["কেটিএল"],
    "KPPL": ["কেপিপিএল"],
    "KPCL": ["কেপিসিএল"],
    "KOHINOOR": ["কোহিনূর"],
    "KFL": ["কেএফএল"],
    "KEYACOSMET": ["কেয়াকসমেট"],
    "KDSALTD": ["কেডিএসআল্টডি"],
    "KBSEED": ["কেবিএসইডি"],
    "KBPPWBIL": ["কেবিপিপিডব্লুবিল"],
    "KAY&QUE": ["কেইএন্ডকিউ"],
    "KARNAPHULI": ["কার্ণফুলী"],
    "JUTESPINN": ["জুটস্পিন"],
    "JMISMDL": ["জেমিসিএমডিএল"],
    "JHRML": ["জেএইচআরএমএল"],
    "JANATAINS": ["জনাতাঈনস"],
    "JAMUNAOIL": ["জামুনা অয়েল"],
    "JAMUNABANK": ["জামুনাব্যাংক"],
    "ITC": ["আইটিসি"],
    "ISNLTD": ["আইএসএনলিমিটেড"],
    "ISLAMIINS": ["ইসলামী ইনস"],
    "ISLAMICFIN": ["ইসলামিকফিন"],
    "ISLAMIBANK": ["ইসলামিব্যাংক"],
    "IPDC": ["আইপিডিসি"],
    "INTRACO": ["ইনট্রাকো"],
    "INTECH": ["ইনটেক"],
    "INDEXAGRO": ["ইন্ডেক্সঅ্যাগ্রো"],
    "ILFSL": ["আইএলএফএসএল"],
    "IFILISLMF1": ["আইফিলইসলএমএফ১"],
    "IFIC1STMF": ["আইএফআইসি ১স্টএমএফ"],
    "IFIC": ["আইএফআইসি"],
    "IFADAUTOS": ["আইফাডঅটোস"],
    "IDLC": ["আইডিএলসি"],
    "ICICL": ["আইসিআইসিআইএল"],
    "ICBSONALI1": ["আইসিবিএসোনালী১"],
    "ICBIBANK": ["আইসিবিএ ব্যাংক"],
    "ICBEPMF1S1": ["আইসিবিইপিএমএফ১এস১"],
    "ICBAMCL2ND": ["আইসিবিএমসিএল২এনডি"],
    "ICBAGRANI1": ["আইসিবিএগ্রাণী১"],
    "ICB3RDNRB": ["আইসিবিএ৩আরডিএনআরবি"],
    "ICB": ["আইসিবি"],
    "IBP": ["আইবিআইপি"],
    "IBNSINA": ["আইবিএনসিনা"],
    "HWAWELLTEX": ["এইচডব্লিউএওওয়েলটেক্স"],
    "HRTEX": ["এইচআরটেক্স"],
    "HIMADRI": ["হিমাদ্রি"],
    "HFL": ["এইচএফএল"],
    "HEIDELBCEM": ["হেইডেলবিসিএম"],
    "HAMI": ["হামি"],
    "HAKKANIPUL": ["হাক্কানিপুল"],
    "GSPFINANCE": ["জিএসপিএফিনান্স"],
    "GREENDELT": ["গ্রীনডেল্ট", "গ্রীনডেল্টা"],
    "GREENDELMF": ["গ্রীনডেলএমএফ"],
    "GRAMEENS2": ["গ্রামীন্স২"],
    "GQBALLPEN": ["জিকিউবলপেন"],
    "GPHISPAT": ["জিপিএইচআইএসপিএটি", "জিপিএইচইস্পাত"],
    "GP": ["জিপি", "জীপি"],
    "GOLDENSON": ["গোল্ডেনসন"],
    "GLOBALINS": ["গ্লোবালইনস"],
    "GLDNJMF": ["জিএলডিএনজেএমএফ"],
    "GIB": ["জিআইবি"],
    "GHCL": ["জিএইচসিএল"],
    "GHAIL": ["জিএইচএআইএল"],
    "GENNEXT": ["জেননেক্সট"],
    "GENEXIL": ["জেনএক্সিল"],
    "GEMINISEA": ["জেমিনিসি"],
    "GBBPOWER": ["জিবিবিপাওয়ার"],
    "FUWANGFOOD": ["ফুওয়াংফুড"],
    "FUWANGCER": ["ফুওয়াংসার"],
    "FORTUNE": ["ফরচুন"],
    "FIRSTSBANK": ["ফার্স্টসব্যাংক"],
    "FIRSTFIN": ["ফার্স্টফিন"],
    "FINEFOODS": ["ফাইনফুডস"],
    "FEKDIL": ["ফেকডিল"],
    "FEDERALINS": ["ফেডারেলইনস"],
    "FBFIF": ["এফবিএফআইএফ"],
    "FASFIN": ["ফাসফিন"],
    "FAREASTLIF": ["ফারইস্টলাইফ"],
    "FAREASTFIN": ["ফারইস্টফিন"],
    "FARCHEM": ["ফারচেম"],
    "FAMILYTEX": ["ফ্যামিলিটেক্স"],
    "EXIMBANK": ["এক্সিমব্যাংক"],
    "EXIM1STMF": ["এক্সিম১স্টএমএফ"],
    "ETL": ["ইটিএল"],
    "ESQUIRENIT": ["ইস্কয়ারনিট"],
    "EPGL": ["ইপিজিএল"],
    "ENVOYTEX": ["এনভোয়াইটেক্স"],
    "EMERALDOIL": ["এমেরাল্ডঅয়েল"],
    "EIL": ["ইআইএল"],
    "EHL": ["ইএইচএল"],
    "EGEN": ["ইজেন"],
    "ECABLES": ["ইক্যাবলস"],
    "EBLNRBMF": ["ইবিএলএনআরবিএমএফ"],
    "EBL1STMF": ["ইবিএল১স্টএমএফ"],
    "EBL": ["ইবিএল"],
    "EASTRNLUB": ["ইস্টারনলুব"],
    "EASTLAND": ["ইস্টল্যান্ড"],
    "EASTERNINS": ["ইস্টার্নইনস"],
    "DUTCHBANGL": ["ডাচবাংল"],
    "DULAMIACOT": ["দুলামিয়াকটন"],
    "DSSL": ["ডিএসএসএল"],
    "DSHGARME": ["ডিএসএইচগার্মে"],
    "DOREENPWR": ["ডোরিনপাওয়ার"],
    "DOMINAGE": ["ডোমিনেজ"],
    "DHAKAINS": ["ঢাকাইনস", "ঢাকাইন্স্যুরেন্স"],
    "DHAKABANK": ["ঢাকাব্যাংক"],
    "DGIC": ["ডিজিআইসি"],
    "DESHBANDHU": ["দেশবন্ধু"],
    "DESCO": ["ডেস্কো", "ডেসকো"],
    "DELTASPINN": ["ডেল্টাস্পিন"],
    "DELTALIFE": ["ডেল্টালাইফ"],
    "DBH1STMF": ["ডিবিএইচ১স্টএমএফ", "ডিবিএইচফার্স্টএমএফ"],
    "DBH": ["ডিবিএইচ"],
    "DAFODILCOM": ["ড্যাফোডিলকম"],
    "DACCADYE": ["ঢাকাডাইং", "ঢাকাডায়িং"],
    "CVOPRL": ["সিভিওপিআরএল"],
    "CRYSTALINS": ["ক্রিস্টালইনস", "ক্রিস্টালইন্স্যুরেন্স"],
    "CROWNCEMNT": ["ক্রাউনসিমেন্ট"],
    "CRAFTSMAN": ["ক্রাফটসম্যান"],
    "COPPERTECH": ["কপারটেক"],
    "CONTININS": ["কন্টিনইনস", "কন্টিনেন্টালইন্স্যুরেন্স"],
    "CONFIDCEM": ["কনফিডেন্টসিমেন্ট"],
    "CNATEX": ["সিএনএটেক্স"],
    "CLICL": ["সিএলআইসিএল"],
    "CITYGENINS": ["সিটিজেনইনস", "সিটিজেনইন্স্যুরেন্স"],
    "CITYBANK": ["সিটিব্যাংক"],
    "CENTRALPHL": ["সেন্ট্রালফার্মা", "সেন্ট্রালফার্মালি", "সেন্ট্রালফার্মালিমিটেড"],
    "CENTRALINS": ["সেন্ট্রালইনস", "সেন্ট্রালইন্স্যুুরেন্স"],
    "CAPMIBBLMF": ["ক্যাপএমআইবিবিএলএমএফ"],
    "CAPMBDBLMF": ["ক্যাপএমবিডিবিএলএমএফ"],
    "CAPITECGBF": ["ক্যাপিটেকজিবিএফ"],
    "BXPHARMA": ["বিএক্সফার্মা", "বেক্সিমকোফার্মা"],
    "BSRMSTEEL": ["বিএসআরএমস্টিল"],
    "BSRMLTD": ["বিএসআরএমলিমিটেড"],
    "BSCPLC": ["বিএসসিপিএলসি"],
    "BSC": ["বিএসসি"],
    "BRACBANK": ["ব্র্যাকব্যাংক"],
    "BPPL": ["বিপিপিএল"],
    "BPML": ["বিপিএমএল"],
    "BNICL": ["বিএনআইসিএল"],
    "BIFC": ["বিআইএফসি"],
    "BGIC": ["বিজিআইসি"],
    "BEXIMCO": ["বেক্সিমকো"],
    "BEXGSUKUK": ["বেক্সজুকুক"],
    "BESTHLDNG": ["বেস্টহোল্ডিং"],
    "BERGERPBL": ["বার্জারপিবিএল"],
    "BENGALWTL": ["বেঙ্গলডব্লিউটিএল"],
    "BENGALBISC": ["বেঙ্গালবিস্ক", "বেঙ্গালবিস্কুট"],
    "BEACONPHAR": ["বীকনফার", "বীকনফার্মা"],
    "BEACHHATCH": ["বিচহ্যাচ"],
    "BDWELDING": ["বিডিওয়েল্ডিং"],
    "BDTHAIFOOD": ["বিডিথাইফুড"],
    "BDTHAI": ["বিডিথাই"],
    "BDPAINTS": ["বিডিপেইন্টস"],
    "BDLAMPS": ["বিডিল্যাম্পস"],
    "BDFINANCE": ["বিডিফাইনান্স"],
    "BDCOM": ["বিডিকম"],
    "BDAUTOCA": ["বিডিঅটো", "বিডিঅটোকা"],
    "BBSCABLES": ["বিবিএসকেবলস", "বিবিএসক্যাবলস"],
    "BBS": ["বিবিএস"],
    "BAYLEASING": ["বেলিজিং"],
    "BATBC": ["ব্যাটবিসি", "বিএটিবিসি"],
    "BATASHOE": ["বাটাশো"],
    "BARKAPOWER": ["বারকাপাওয়ার"],
    "BANKASIA": ["ব্যাংকএশিয়া"],
    "BANGAS": ["বংগস", "বাংগ্যাস"],
    "AZIZPIPES": ["আজিজপাইপস", "আজিজপাইপ"],
    "ATLASBANG": ["অ্যাটলাসব্যাংক"],
    "ASIATICLAB": ["এশিয়াটিকল্যাব"],
    "ASIAPACINS": ["এশিয়াপ্যাকইনস", "এশিয়াপ্যাসিফিকইন্স্যুরেন্স"],
    "ASIAINS": ["এশিয়াইনস", "এশিয়াইন্স্যুরেন্স"],
    "ARGONDENIM": ["আরগনডেনিম"],
    "ARAMITCEM": ["আরামিটসিমেন্ট"],
    "ARAMIT": ["আরামিট"],
    "APOLOISPAT": ["অ্যাপলোইস্পাত"],
    "APEXWEAV": ["অ্যাপেক্সওয়েভ"],
    "APEXTANRY": ["অ্যাপেক্সট্যানারি"],
    "APEXSPINN": ["অ্যাপেক্সস্পিন"],
    "APEXFOOT": ["অ্যাপেক্সফুট"],
    "APEXFOODS": ["অ্যাপেক্সফুডস"],
    "AOPLC": ["এওপিএলসি"],
    "AOL": ["এওএল"],
    "ANWARGALV": ["অনোয়ারগ্যালভ", "অনোয়ারগ্যালভানাইজিং"],
    "ANLIMAYARN": ["অ্যানলিমায়ার্ন"],
    "AMPL": ["এএমপিএল"],
    "AMCL(PRAN)": ["এএমসিএল(প্রান)"],
    "AMBEEPHA": ["অ্যাম্বিফার্মা", "এমবিফার্মা"],
    "AMANFEED": ["আমানফিড"],
    "ALLTEX": ["অলটেক্স"],
    "ALIF": ["আলিফ"],
    "ALARABANK": ["আলারাব্যাংক","আলআরাব্যাংক"],
    "AL-HAJTEX": ["আল-হাজটেক্স"],
    "AIL": ["আইএল"],
    "AIBL1STIMF": ["এআইবিএল১স্টআইএমএফ","এআইবিএলফার্স্টআইএমএফ"],
    "AGRANINS": ["অগ্রনীইন্স্যুরেন্স"],
    "AGNISYSL": ["অ্যাগনিসিসএল", "অ্যাগনিসিস্টেম"],
    "AFTABAUTO": ["আফতাবঅটো"],
    "AFCAGRO": ["এএফসিএগ্রো"],
    "ADVENT": ["অ্যাডভেন্ট"],
    "ADNTEL": ["এডিএনটেল"],
    "ACTIVEFINE": ["অ্যাক্টিভফাইন"],
    "ACMEPL": ["একমিপিএল"],
    "ACMELAB": ["একমিল্যাব"],
    "ACIFORMULA": ["এসিআইফর্মুলা"],
    "ACI": ["এসিআই"],
    "ACHIASF": ["আচিয়াসফ"],
    "ACFL": ["এসিএফএল"],
    "ABBANK": ["এবিব্যাংক"],
    "ABB1STMF": ["এবিবি১এসটিএমএফ"],
    "AAMRATECH": ["আমরাটেক"],
    "AAMRANET": ["আমরানেট"],
    "1STPRIMFMF": ["১স্টপ্রাইমএমএফ","ফার্স্টপ্রাইমএমএফ"],
    "1JANATAMF": ["১জনতাএমএফ","ফার্স্টজনতাএমএফ"],
}

trading_market_types_bangla2english={
    "BLOCK": ["ব্লক"],
    "PUBLIC": ["পাবলিক"],
}

trading_stock_exchanges_bangla2english={
    "DSE": ["ডিএসই"],
    "CSE": ["সিএসই"]    
}



suffix_map = {
    "ের": " এর", "ে": " এ", "র": " এর", "টি": " টি",
    "টা": " টা", "গুলো": " গুলো", "তে": " তে", "রা": "রা",
    "’র": " এর", "”র": " এর"
}

phonetic_map = {
    "ী": ["ি", "ী"],
    "ূ": ["ু", "ূ"],
    "ৈ": ["ে", "ৈ"],
    "ৌ": ["উ", "ৌ"],
    "ো": ["ো", "ো"],
    "ু": ["ো", "ু"],
    "(": [""],
    ")": [""],
    "ে": ["্যা", "ে"],
    "্যা": ["ে", "্যা"],
    "ঁ": [""],
    "ঃ": [""],
    "্": [""],
    "প": ["ফ", "প"],
    "স": ["শ", "স"],
    "ন": ["ণ", "ন"],
    "য": ["জ", "য"],
    "জ": ["য", "জ"],
    "ই": ["এ", "ই"],
    "এ": ["এ", "ই"],
}

# ===================== Utilities =====================
def normalize_unicode(text):
    return unicodedata.normalize("NFC", text)

def phonetic_variants(word, phonetic_map):
    variants = {word}
    for k, vals in phonetic_map.items():
        new_variants = set()
        for w in variants:
            if k in w:
                for v in vals:
                    new_variants.add(w.replace(k, v))
        variants |= new_variants
    return variants

def convert_word(word, mapping, suffix_map, cutoff=80):
    word = normalize_unicode(word)

    # ---------------- Suffix Handling ----------------
    for suf in sorted(suffix_map.keys(), key=len, reverse=True):
        if word.endswith(suf):
            core = word[:-len(suf)]
            variants = phonetic_variants(core, phonetic_map)
            # Check exact mapping
            for eng, bn_list in mapping.items():
                if any(v in bn_list for v in variants):
                    return eng + suffix_map[suf]
            # Fuzzy match
            all_bangla = [b for bl in mapping.values() for b in bl]
            match_score = process.extractOne(core, all_bangla, scorer=fuzz.ratio)
            if match_score:
                match, score = match_score[0], match_score[1]
                if score >= cutoff:
                    for eng, bn_list in mapping.items():
                        if match in bn_list:
                            return eng + suffix_map[suf]
            break  # Only apply one suffix

    # ---------------- Direct Match ----------------
    variants = phonetic_variants(word, phonetic_map)
    for eng, bn_list in mapping.items():
        if any(v in bn_list for v in variants):
            return eng

    # ---------------- Fuzzy Full Word ----------------
    all_bangla = [b for bl in mapping.values() for b in bl]
    match_score = process.extractOne(word, all_bangla, scorer=fuzz.ratio)
    if match_score:
        match, score = match_score[0], match_score[1]
        if score >= cutoff:
            for eng, bn_list in mapping.items():
                if match in bn_list:
                    return eng

    # No match, return original word
    return word

bangla2english_mapping = {
    **trading_codes_mapping_bangla2english,
    **trading_market_types_bangla2english,
    **trading_stock_exchanges_bangla2english
}

def convert_sentence(text):
    words = text.split()
    return " ".join(convert_word(w, bangla2english_mapping , suffix_map) for w in words)


import re
import random
import unicodedata
from html import unescape
# ---- Preprocess text ----
def preprocess(text, remove_repetition=True):

    text = convert_sentence(text)

    text = text.lower()  # lowercase all English
    text = unicodedata.normalize("NFC", text)
    text = unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove commas inside numbers
    text = re.sub(r'(?<=\d),(?=\d)', '', text)  # English numbers
    text = re.sub(r'(?<=\u09E6|\d),(?=\u09E6|\d)', '', text)  # Bengali numbers
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    if remove_repetition:
        # Reduce repeated letters/punctuations to a single occurrence
        text = re.sub(r'(.)\1+', r'\1', text)
    
    print("processsssssss", text)
    return text


trading_codes = list(trading_codes_mapping_bangla2english.keys())
market_types = list(trading_market_types_bangla2english.keys())
stock_exchanges = list(trading_stock_exchanges_bangla2english.keys())

# ---- Tokenize while preserving multi-word / special char entities ----
def tokenize_protect_entities(text, trading_codes, market_types, stock_exchanges):
    """
    Tokenize text while preserving multi-word / special-character entities.
    Assumes text is already preprocessed and lowercase.
    """
    # Protect all entities with placeholders
    entity_map = {}
    all_entities = trading_codes + market_types + stock_exchanges
    for i, ent in enumerate(all_entities):
        placeholder = f"__ENTITY_{i}__"
        # replace all case-insensitive occurrences
        text = re.sub(re.escape(ent), placeholder, text, flags=re.IGNORECASE)
        entity_map[placeholder] = ent.lower()  # store lowercase entity

    # Tokenize including placeholders
    pattern = r'[০-৯0-9]+|[\u0980-\u09FF]+|[A-Za-z]+|[^\s\w\u0980-\u09FF]|__ENTITY_\d+__'
    tokens = re.findall(pattern, text)

    # Replace placeholders back with original entity
    tokens = [entity_map.get(t, t) for t in tokens]
    print("tokenizeeeeeeeeeee", tokens)

    return tokens


    # === inference utility ===
def prepare_text_for_infer(raw_text: str) -> str:
    """
    Training এর মতোই preprocess + tokenize_protect_entities চালিয়ে
    space-separated string ফেরত দেবে।
    """
    # preprocess (HTML, comma inside number, lower, ইত্যাদি)
    clean = preprocess(raw_text)

    # entity-safe tokenization (কমা, স্টককোড, এক্সচেঞ্জ, সব ঠিক মতো ভাঙবে)
    tokens = tokenize_protect_entities(
        clean,
        trading_codes,
        market_types,
        stock_exchanges
    )

    # HF tokenizer এর আগে train এর মত space-separated string বানাও
    return " ".join(tokens).lower()