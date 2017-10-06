from gevent import monkey

import time
import gevent

import new_companies
import new_articles


monkey.patch_all()


def get_all_companies():
    # returns a list of all companies
    return list(new_companies.all_companies.keys())


def company_typed_search(company):

    company_found = None
    for company_name in new_companies.all_companies.keys():
        company_name_net = company_name.split()[0]
        if company in company_name_net.lower():
            return company_name

    return company_found


def company_news_type(company_given):
    #list of news type a company has
    company_news = new_companies.all_companies.get(company_given).get('company_news_ids')
    type_of_news = []
    for new_id in company_news:
        if 'POS' in new_articles.articles[new_id]['direction']:
            type_of_news.append('good_companies')
        elif 'NEG' in new_articles.articles[new_id]['direction']:
            type_of_news.append('bad_companies')
    return list(set(type_of_news))


def total_articles():
    return len(new_articles.articles.keys())


def companies_by_type(news_type):
    # list of companies names , type can be good_companies bad_companies

    companies_list = []
    if news_type == 'good_companies':
        news_type = 'POS'
    elif news_type == 'bad_companies':
        news_type = 'NEG'

    for company_name, company_dict in new_companies.all_companies.items():
        updated_company_dict = {}
        for new_id in company_dict['company_news_ids']:
            if news_type in new_articles.articles[new_id]['direction']:
                updated_company_dict['company_name'] = company_name
                updated_company_dict.update(company_dict)
                companies_list.append(updated_company_dict)
                break

    return companies_list


def get_news_by_direction(direction):
    #list of news by their direction good bad

    news = []
    for new_id, new_dict in new_articles.articles.items():
        if new_dict.get('direction') == direction:
            news.append(new_dict)
    return news

def get_news_by_direction_and_company(direction, company):
    #list of news by their direction good bad

    news = []
    for new_id, new_dict in new_articles.articles.items():
        if direction in new_dict.get('direction'):
            if new_dict.get('company') == company:
                news.append(new_dict)
    return news

def update_companies_news(time_interval):

    while True:
        all_news = new_articles.articles
        all_companies = new_companies.all_companies
        for new_id, new_dict in all_news.items():
            company = new_dict.get('company')
            if new_id not in all_companies[company]['company_news_ids']:
                all_companies[company]['company_news_ids'].append(new_id)
        gevent.sleep(time_interval)


def news_poll(poll_time):

    gevent.spawn(update_companies_news, poll_time)

def add_article(article):
    import hashlib
    id = int(hashlib.md5(article.get('image_url')).hexdigest(), 16)
    new_articles.articles[id] = article


def get_article_by_id(article_id):

    return new_articles.articles.get(article_id, None)

def article_from_excel():

    from xlrd import open_workbook
    import copy
    book = open_workbook('Scrader-Sample_1-10.xlsx')
    sheet = book.sheet_by_index(0)
    keys = dict((i, sheet.cell_value(0, i)) for i in range(sheet.ncols))
    articles = (dict((keys[j], sheet.cell_value(i, j)) for j in keys) for i in range(1, sheet.nrows))

    for article in articles:
        new_article = {}
        new_article['title'] = article.get('Title')
        new_article['image_url'] = article.get('image url')
        new_article['subtitle'] = '10/5/2017'
        new_article['item_url'] = article.get('URL')
        new_article['direction'] = article.get('Sentiment')
        new_article['company'] = article.get('Company')
        new_article['website'] = 'cnn.com'
        new_article['website_url'] = 'http://edition.cnn.com/'
        add_article(new_article)
