from bs4 import BeautifulSoup
import urllib2
import requests
import pandas as pd
import httplib
import socket
import unicodedata
import ssl

timeout = 10
socket.setdefaulttimeout(timeout)
company_list = ["aig-",
             "amazon", "uber-", "netflix-", "google-", "boeing-","ibm-","apple-","ryanair","motorolla",
             "equifax", "microsoft","spotify", "exxon", "wells-fargo", "toyota", "hsbc-", "bp-", "volkswagen",
             "bnp-paribas", "daimler", "samsung", "axa-", "vodafone", "nestle", "ford", "metlife", "general-motors",
             "intel-", "oracle", "unilever", "morgan-stanley", "barclays", "christian-dior", "3m-", "target-", "canon", "nintendo",
             "tesla", "panasonic", "ebay", "kia-", "renault", "apache", "philips", "monsanto", "accenture", "toshiba", "baidu",
              "sky-news", "jpmorgan", "jp-morgan", "p&g-", "vw-", "bmw-", "benz-", "mercedes", "at&t-","renault", "alibaba",
             "citi-","chevron","wal-mart","gazprom","verizon", "santander","siemens","novartis","goldman","metlife","hyundai",
            "disney","prudencial","qualcomm","honeywell","abb-","astrazeneca","carrefour","aetna",
              "edf","pfizer","statoil","facebook","twitter","general-motors","gm-","honda","cisco",
               "hyundai", "cnooc-","unilever","eon-","bayer","hitachi","lockheed","deloitte"
]


scraping_list = ["https://www.nytimes.com/section/business?action=click&pgtype=Homepage&region=TopBar&module=HPMiniNav&contentCollection=Business&WT.nav=page",
               "http://www.businessinsider.com/enterprise",
               "http://money.cnn.com/technology",
               "http://www.reuters.com/news/archive/businessNews?view=page"
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
               "https://www.nbcnews.com/business"
]

title_list = []
url_list = []
image_list = []
date_list = []
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
for url in scraping_list:
    url_slice_no_http = url[:(url.find(":") + 1)]
    if url.find(".com") == -1:
        url_slice_no_link = url[:(url.find("co.uk") + 5)]
    else:
        url_slice_no_link = url[:(url.find(".com") + 4)]
    req = urllib2.Request(url, headers={'User-Agent': user_agent})
    try:
        content = urllib2.urlopen(req).read()
    except urllib2.URLError:
        print "Bad URL or timeout"
        print url
        continue
    soup = BeautifulSoup(content, "html5lib")
    # print soup.prettify()

    # vriskei ola ta links
    links = soup.find_all("a")
    for company in company_list:
        for link in links:
            h_link = link.get("href", False)
            if not h_link: continue
            if company in h_link:
                h_link = h_link.encode('utf-8')
                if not (h_link.startswith("http") or h_link.startswith("https")):
                    if h_link.startswith("//"):
                        h_link = url_slice_no_http + h_link
                    elif h_link.startswith("/"):
                        h_link = url_slice_no_link + h_link

                h_link_req = urllib2.Request(h_link, headers={'User-Agent': user_agent})
                try:
                    h_link_content = urllib2.urlopen(h_link_req).read()
                except urllib2.HTTPError, e:
                    print h_link
                    print e
                    continue
                except urllib2.URLError, e:
                    print h_link
                    print e
                    continue
                except httplib.HTTPException, e:
                    print h_link
                    print e
                    continue
                except ssl.SSLError, e:
                    print h_link
                    print e
                    continue
                except Exception:
                    print h_link
                    continue

                h_link_soup = BeautifulSoup(h_link_content, "html5lib")
                url_image = h_link_soup.find("meta", property="og:image")
                time = [meta.get('content') for meta in h_link_soup.find_all('meta', itemprop='datePublished')]
                if time:
                    date = time[0][:time[0].find("T")]
                else:
                    date = ''
                # date= time[(time.find("-")+1):time.find("T")]
                #                     print date
                if url_image is not None:
                    image = url_image['content']
                    if not (image.startswith("http") or image.startswith("https")):
                        image = 'https:' + image
                    # print image
                    url_title = h_link_soup.title.string
                    url_title = unicodedata.normalize('NFKD', url_title).encode('ascii', 'ignore')
                    # print url_title
                    if h_link not in url_list:
                        url_list.append(h_link)
                        image_list.append(image)
                        title_list.append(url_title)
                        date_list.append(date)
                else:
                    # print "No image in " + url
                    pass

print(len(url_list))
print(len(image_list))
print(len(title_list))
print(len(date_list))

data = pd.DataFrame({"Article": url_list, "Title": title_list, "Image": image_list, "Date": date_list})
print(len(data))
data.to_csv("./Scraderlatestnews.csv", encoding='utf-8')