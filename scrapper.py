from bs4 import BeautifulSoup
import urllib2
import pandas as pd
import httplib
import socket
import unicodedata
import ssl
import os
import datetime
import scraper_constants
import algorithm


def convert_to_df(url_list, image_list, title_list, date_list, companies_list,
                  website_url_list, websites_list):

    data = pd.DataFrame({"Article": url_list, "Title": title_list,
                         "Image": image_list, "Date": date_list,
                         "Company": companies_list, "Website": websites_list,
                         "Website url": website_url_list})
    print(len(data))
    abs_filename = "./Scraderlatestnews.csv"
    try:
        os.remove(abs_filename)
    except OSError:
        pass
    data.to_csv(abs_filename, encoding='utf-8')
    algorithm.run_algorithm(abs_filename)


def main():
    company_list = scraper_constants.company_list
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
        website = website_list[index]
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
        soup = BeautifulSoup(content, "html.parser")

        # vriskei ola ta links
        links = soup.find_all("a")
        for company in company_list:
            for link in links:
                h_link = link.get("href", False)
                if not h_link:
                    continue
                if company in h_link:
                    h_link = h_link.encode('utf-8')
                    if not (h_link.startswith("http") or h_link.startswith("https")):
                        if h_link.startswith("//"):
                            h_link = url_slice_no_http + h_link
                        elif h_link.startswith("/"):
                            h_link = url_slice_no_link + h_link

                    h_link_req = urllib2.Request(
                        h_link, headers={'User-Agent': user_agent}
                    )
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
                        image = url_image['content']
                        if not (image.startswith("http") or image.startswith("https")):
                            image = 'https:' + image
                        # print image
                        url_title = h_link_soup.title.string
                        url_title = unicodedata.normalize('NFKD', url_title).\
                            encode('ascii', 'ignore')
                        # print url_title
                        if h_link not in url_list:
                            url_list.append(h_link)
                            image_list.append(image)
                            title_list.append(url_title)
                            date_list.append(date)
                            companies_list.append(company)
                            website_url_list.append(url)
                            websites_list.append(website)
                    else:
                        # print "No image in " + url
                        pass

    print(len(url_list))
    print(len(image_list))
    print(len(title_list))
    print(len(date_list))
    print(len(companies_list))
    print(len(website_url_list))
    print(len(websites_list))
    convert_to_df(url_list, image_list, title_list, date_list, companies_list,
                  website_url_list, websites_list)


if __name__ == '__main__':
    timeout = 10
    socket.setdefaulttimeout(timeout)
    main()
