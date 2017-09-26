import gevent
import time
from gevent import monkey
from random import randint
import mongo

# Monkey patch python runtime
monkey.patch_all()
GREENLETS = {}


def scrader_poll(companies, sources):
    print companies, sources
    print 'Heslloo'
    global GREENLETS

    GREENLETS = gevent. \
        spawn(get_news, companies, sources, 3)


def get_news(companies, sources, sleep_time):
    count = 0
    while True:
        count += 1
        print count
        mongo.delete_many('companies')
        for company in companies:
            news = get_company_news(company, sources)
            # update db ("companies", company, news)
            mongo.insert_one("companies", news)
            # print(news)
        print "number is " + str(mongo.count("companies"))
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

    ran_gen_good = randint(0, 60)
    ran_gen_bad = randint(0, 60)

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


def fetch_news_from_db():

    result = {}
    news = mongo.fetch_collection('companies')
    for new in news:
        # print new
        result.update(new)

    return result
