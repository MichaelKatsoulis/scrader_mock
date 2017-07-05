import gevent
import time
from gevent import monkey
from random import randint
# Monkey patch python runtime
monkey.patch_all()
GREENLETS = {}


def scrader_poll(companies, sources):
    print companies, sources
    print 'Hello'
    global GREENLETS

    GREENLETS = gevent. \
        spawn(get_news, companies, sources, 5)


def get_news(companies, sources, sleep_time):
    count = 0
    while True:
        count += 1
        print count
        for company in companies:
            news = get_company_news(company, sources)
            # update db ("companies", company, news)
            print(news)
        gevent.sleep(sleep_time)


def get_company_news(company, sources):

    news = {
            company:
                {
                "Good_news" : [],
                "Bad_news" : []
                }
           }

    # generate random number between 1 and 20 for good news
    # generate random number between 1 and 20 for bad news

    ran_gen_good = randint(0, 20)
    ran_gen_bad = randint(0, 20)

    for num in range(ran_gen_good):
        new = {
                "id": num,
                "time": int(time.time())
              }
        news[company]["Good_news"].append(new)

    # generate random number between 1 and 20 for bad news
    for num in range(ran_gen_bad):
        new = {
                "id": num,
                "time": int(time.time())
              }
        news.get(company).get("Bad_news").append(new)

    return news
