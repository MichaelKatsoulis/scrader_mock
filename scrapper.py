from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib2
import pandas as pd
import httplib
import socket
import unicodedata
import ssl
import os
import re
import datetime
import scraper_constants
import algorithm
import script
import csv
import copy
import logging

dbcli = MongoClient()
db = dbcli['scrader']
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('scraper_logs.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def convert_to_df(url_list, image_list, title_list, date_list, companies_list,
                  website_url_list, websites_list):

    data = pd.DataFrame({"Article": url_list, "Title": title_list,
                         "Image": image_list, "Date": date_list,
                         "Company": companies_list, "Website": websites_list,
                         "Website url": website_url_list})
    logger.info('found {} new articles'.format(len(data)))
    abs_filename = "./Scraderlatestnews.csv"
    try:
        os.remove(abs_filename)
    except OSError:
        pass
    data.to_csv(abs_filename, encoding='utf-8')
    script.main()
    algorithm.run_algorithm(abs_filename)


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def skip_unwanted(h_link):
    unwanted_list = ["://itunes.apple.com/", "//www.facebook.com/",
                     "//facebook.com/", "//apps.microsoft.com", "yahoo.com",
                     "//yahoofinance.tumblr.com", "//play.google.com"]
    for item in unwanted_list:
        if item in h_link:
            return True
    return False


def companies_in_title(url_title, scraper_companies, url_term):
    if url_title == '':
        return None

    if 'CBS New York' in url_title:
        return None

    collection = db['scraper_companies']
    company_dict = list(collection.find({'url_terms': url_term}, {'_id': False}))[0]
    company_synonims = company_dict.get('synonims')
    res = None
    for synonim in company_synonims:
        res = findWholeWord(synonim)(url_title)
        if res is not None:
            res = company_dict.get('company_name')
            break
    if res is None:
        return None
    
    num_of_comps = 1
    for company in scraper_companies:
        if company.get('company_name') != res:
            for synonim in company.get('synonims'):
                result = findWholeWord(synonim)(url_title)
                if result is not None:
                    num_of_comps += 1
                    break
            if num_of_comps >= 2:
                return None
 
    return res


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def main():

    collection = db['url_terms']
    url_collection = list(collection.find({}, {'_id': False}))
    urls_list = url_collection[0].get('url_terms')

    collection = db['scraper_companies']
    scraper_companies = list(collection.find({}, {'_id': False}))

    scraping_list = scraper_constants.scraping_list
    website_list = scraper_constants.website_list

    title_list = []
    url_list = []
    image_list = []
    date_list = []
    companies_list = []
    website_url_list = []
    websites_list = []
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'

    for index, url in enumerate(scraping_list):
        logger.info('Opening URL: {}'.format(url))
        website = website_list[index]
        url_slice_no_http = url[:(url.find(":") + 1)]
        if url.find(".com") == -1:
            url_slice_no_link = url[:(url.find("co.uk") + 5)]
            logger.info('url_slice_no_link is: {}'.format(url_slice_no_link))
        else:
            url_slice_no_link = url[:(url.find(".com") + 4)]
            logger.info('url_slice_no_link is: {}'.format(url_slice_no_link))
        req = urllib2.Request(url, headers={'User-Agent': user_agent})
        try:
            content = urllib2.urlopen(req).read()
        except ssl.SSLError:
            logger.error('Bad URL given: {}'.format(url))
            continue     
        except urllib2.URLError:
            logger.error('Bad URL given: {}'.format(url))
            continue
        except Exception:
            logger.error('Bad URL given: {}'.format(url))
            continue
        soup = BeautifulSoup(content, "html.parser")

        # vriskei ola ta links
        links = soup.find_all("a")
        for url_term in urls_list:
            for link in links:
                h_link = link.get("href", False)
                if not h_link:
                    continue
                if skip_unwanted(h_link):
                    # logger.error('skiping unwanted {}'.format(h_link))
                    continue

                if url_term in h_link:
                    h_link = h_link.encode('utf-8')
                    if not (h_link.startswith("http") or h_link.startswith("https")):
                        # logger.warning('url before: {}'.format(h_link))
                        if h_link.startswith("//"):
                            h_link = url_slice_no_http + h_link
                            # logger.warning('url after: {}'.format(h_link))
                        elif h_link.startswith("/"):
                            h_link = url_slice_no_link + h_link
                            # logger.warning('url after: {}'.format(h_link))

                    h_link_req = urllib2.Request(
                        h_link, headers={'User-Agent': user_agent}
                    )
                    try:
                        h_link_content = urllib2.urlopen(h_link_req).read()
                    except urllib2.HTTPError, e:
                        logger.warning('Bad hyperlink: {}: {}'.format(h_link, url))
                        continue
                    except urllib2.URLError, e:
                        logger.warning('Bad hyperlink: {}: {}'.format(h_link, url))
                        continue
                    except httplib.HTTPException, e:
                        logger.warning('Bad hyperlink: {}: {}'.format(h_link, url))
                        continue
                    except ssl.SSLError, e:
                        logger.warning('Bad hyperlink: {}: {}'.format(h_link, url))
                        continue
                    except Exception:
                        logger.warning('Bad hyperlink: {}: {}'.format(h_link, url))
                        continue

                    h_link_soup = BeautifulSoup(h_link_content, "html.parser")
                    url_image = h_link_soup.find("meta", property="og:image")
                    time = [meta.get('content') for meta in h_link_soup.find_all('meta', itemprop='datePublished')]
                    if time:
                        date = time[0][:time[0].find("T")]
                    else:
                        today = datetime.date.today()
                        date = '{}/{}/{}'.format(today.month, today.day, today.year)
                    # date= time[(time.find("-")+1):time.find("T")]
                    #                     print date
                    if url_image is not None:
                        image = url_image.get('content')
                        if image is None or image == '':
                            continue
                        if not (image.startswith("http") or image.startswith("https")):
                            img_before = image
                            image = 'https:' + image
                            if not (image.startswith("https://")):
                                image = "https://" + img_before
                        # print image
                        url_title = h_link_soup.title.string
                        if url_title is None:
                            continue
                        url_title = unicodedata.normalize('NFKD', url_title).\
                            encode('ascii', 'ignore')
                        url_title = url_title.replace("&apos;","'")
                        
                        company_name = companies_in_title(url_title, scraper_companies, url_term)
                        if company_name is None:
                            continue
                        # print url_title
                        if h_link not in url_list:
                            url_list.append(h_link)
                            image_list.append(image)
                            title_list.append(url_title)
                            date_list.append(date)
                            companies_list.append(company_name)
                            website_url_list.append(url)
                            websites_list.append(website)
                    else:
                        # print "No image in " + url
                        pass

    # print(len(url_list))
    # print(len(image_list))
    # print(len(title_list))
    # print(len(date_list))
    # print(len(companies_list))
    # print(len(website_url_list))
    # print(len(websites_list))
    convert_to_df(url_list, image_list, title_list, date_list, companies_list,
                  website_url_list, websites_list)


if __name__ == '__main__':
    timeout = 10
    socket.setdefaulttimeout(timeout)
    logger.info('new scraping started')
    main()
