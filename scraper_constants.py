company_list = [
    "aig-", "amazon", "uber-", "netflix-", "google-", "boeing-", "ibm-",
    "apple-", "ryanair", "motorolla", "equifax", "microsoft", "spotify",
    "exxon", "wells-fargo", "toyota", "hsbc-", "bp-", "volkswagen",
    "bnp-paribas", "daimler", "samsung", "axa-", "vodafone", "nestle",
    "ford", "metlife", "general-motors", "intel-", "oracle", "unilever",
    "morgan-stanley", "barclays", "christian-dior", "3m-", "target-", "canon",
    "nintendo", "tesla", "panasonic", "ebay", "kia-", "renault", "apache",
    "philips", "monsanto", "accenture", "toshiba", "baidu", "sky-news",
    "jpmorgan", "jp-morgan", "p&g-", "vw-", "bmw-", "benz-", "mercedes",
    "at&t-", "renault", "alibaba", "citi-", "chevron", "wal-mart", "gazprom",
    "verizon", "santander", "siemens", "novartis", "goldman", "metlife",
    "hyundai", "disney", "prudencial", "qualcomm", "honeywell", "abb-",
    "astrazeneca", "carrefour", "aetna", "edf", "pfizer", "statoil",
    "facebook", "twitter", "general-motors", "gm-", "honda", "cisco",
    "hyundai", "cnooc-", "unilever", "eon-", "bayer", "hitachi", "lockheed",
    "deloitte"
]

company_names_list = [
    "aig", "amazon", "uber", "netflix", "google", "boeing", "ibm",
    "apple", "ryanair", "motorolla", "equifax", "microsoft", "spotify",
    "exxon", "wells-fargo", "toyota", "hsbc", "bp", "volkswagen",
    "bnp-paribas", "daimler", "samsung", "axa", "vodafone", "nestle",
    "ford", "metlife", "general-motors", "intel", "oracle", "unilever",
    "morgan-stanley", "barclays", "christian-dior", "3m", "target", "canon",
    "nintendo", "tesla", "panasonic", "ebay", "kia", "renault", "apache",
    "philips", "monsanto", "accenture", "toshiba", "baidu", "sky-news",
    "jpmorgan", "jp-morgan", "p&g", "vw", "bmw", "benz", "mercedes",
    "at&t", "renault", "alibaba", "citi", "chevron", "wal-mart", "gazprom",
    "verizon", "santander", "siemens", "novartis", "goldman", "metlife",
    "hyundai", "disney", "prudencial", "qualcomm", "honeywell", "abb-",
    "astrazeneca", "carrefour", "aetna", "edf", "pfizer", "statoil",
    "facebook", "twitter", "general-motors",  "general motors", "gm", "honda",
    "cisco", "hyundai", "cnooc", "unilever", "eon", "bayer", "hitachi",
    "lockheed", "deloitte"
]

scraping_list = [
    "https://www.nytimes.com/section/business?action=click&pgtype=Homepage&region=TopBar&module=HPMiniNav&contentCollection=Business&WT.nav=page",
    "http://www.businessinsider.com/enterprise",
    "http://money.cnn.com/technology",
    "http://www.reuters.com/news/archive/businessNews?view=page",
    "https://www.forbes.com/home_usa/#62fa69d6324b",
    "http://www.bbc.com/news/business",
    "http://abcnews.go.com/Technology",
    "http://nypost.com/business/",
    "http://www.chicagotribune.com/business/",
    "http://www.foxbusiness.com/",
    "https://finance.yahoo.com/tech/",
    "https://www.nbcnews.com/business",
    "https://www.huffingtonpost.com/section/business/",
    "http://www.newser.com",
    "http://www.newsweek.com/business",
    "https://www.usatoday.com/money/business/",
    "https://www.washingtonpost.com/business/",
    "https://www.wsj.com/news/business/",
    "https://www.usatoday.com",
    "http://www.telegraph.co.uk/business/companies",
    "https://www.bloomberg.com/europe",
    "https://www.theguardian.com/uk/business",
    "https://www.npr.org/sections/business/",
    "https://www.nbcnews.com/business",
    "https://www.cnbc.com/technology/",
    "https://www.cnbc.com/finance/",
    "https://www.cnbc.com/investing/",
    "https://www.cnbc.com/markets/",
    "https://www.cnbc.com/autos/",
    "https://news.sky.com/business",
    "https://www.fin24.com/Companies/",
    "https://www.wsj.com/news/technology",
    "https://www.wsj.com/news/markets",
    "https://www.ft.com/companies",
    "https://www.marketwatch.com/",
    "https://www.usatoday.com/money/markets/",
    "http://www.londonstockexchange.com/exchange/news/alliance-news/archive.html?nameCode=&type=collapsed&tagCode=ALLCOS",
    "https://www.forbes.com/business/#19a2399c535f",
    "https://www.forbes.com/technology/#10c33c0b4bad",
    "https://www.fnlondon.com/",
    "http://money.cnn.com/news/",
    "http://www.morningstar.co.uk/uk/equities/default.aspx"
]

website_list = [
    "nytimes.com",
    "businessinsider.com",
    "cnn.com",
    "reuters.com",
    "forbes.com",
    "bbc.com",
    "abcnews.go.com",
    "nypost.com",
    "chicagotribune.com",
    "foxbusiness.com",
    "finance.yahoo.com",
    "nbcnews.com",
    "huffingtonpost.com",
    "newser.com",
    "newsweek.com",
    "www.usatoday.com/money",
    "washingtonpost.com",
    "wsj.com",
    "usatoday.com",
    "telegraph.co.uk",
    "bloomberg.com",
    "theguardian.com",
    "npr.org",
    "nbcnews.com",
    "cnbc.com",
    "cnbc.com",
    "cnbc.com",
    "cnbc.com",
    "cnbc.com",
    "news.sky.com",
    "fin24.com",
    "wsj.com",
    "wsj.com",
    "ft.com",
    "marketwatch.com",
    "usatoday.com",
    "londonstockexchange.com",
    "forbes.com",
    "forbes.com",
    "fnlondon.com",
    "cnn.com",
    "morningstar.co.uk"
]
