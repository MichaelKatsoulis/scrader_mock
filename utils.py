from gevent import monkey

import time
import gevent

import new_articles
import mongo


monkey.patch_all()


def get_all_companies():
    # returns a list of all companies
    companies = mongo.fetch_collection('companies')
    return [comp['name'] for comp in companies]


def company_typed_search(company):

    company_found = None
    companies = mongo.fetch_collection('companies')
    all_companies = [comp['name'] for comp in companies]
    for company_name in all_companies:
        company_name_net = company_name.split()[0]
        if company in company_name_net.lower():
            return company_name

    return company_found


def company_news_type(company_given):
    #list of news type a company has
    news_cursor = mongo.find_matches('articles', {'company': company_given})
    comp_type_of_news = []
    for new in news_cursor:
        if 'POS' in new['direction']:
            comp_type_of_news.append('good_companies')
        elif 'NEG' in new['direction']:
            comp_type_of_news.append('bad_companies')

    company_dict = mongo.find_one_match('companies', {"name": company_given})
    company_news = company_dict.get('company_news_ids')
    type_of_news = []
    for new_id in company_news:
        if 'POS' in new_articles.articles[new_id]['direction']:
            type_of_news.append('good_companies')
        elif 'NEG' in new_articles.articles[new_id]['direction']:
            type_of_news.append('bad_companies')
    return list(set(type_of_news))


def total_articles():
    total_number = 0
    total_cursor = mongo.find_matches_not_containing('articles', 'direction', ['NEU', 'NEUTRAL'])
    # print(total_cursor.count())
    for article in new_articles.articles.values():
        if 'NEU' not in article.get('direction'):
            total_number += 1
    return total_number


def companies_by_type(news_type):
    # list of companies names , type can be good_companies bad_companies

    companies_list = []
    if news_type == 'good_companies':
        news_type = 'POS'
        match = ['POS', 'POSITIVE']
    elif news_type == 'bad_companies':
        news_type = 'NEG'
        match = ['NEG', 'NEGATIVE']

    articles_cursor = list(mongo.find_matches_containing_many('articles', 'direction', match))
    companies_new_list = []
    for article in articles_cursor:
        comp_dict= mongo.find_one_match('companies', {'name': article.get('company')})
        if comp_dict not in companies_new_list:
            comp_dict['company_name'] = comp_dict.pop('name')
            companies_new_list.append(comp_dict)

    companies = mongo.fetch_collection('companies')
    for company_dict in companies:
        for new_id in company_dict['company_news_ids']:
            if news_type in new_articles.articles[new_id]['direction']:
                company_dict['company_name'] = company_dict.pop('name')
                companies_list.append(company_dict)
                break
    return companies_list


def get_news_by_direction(direction):
    #list of news by their direction good bad

    news = []
    for new_id, new_dict in new_articles.articles.items():
        if new_dict.get('direction') == direction:
            news.append(new_dict)
    return news

def get_news_by_direction_and_company(direction, company, direction_list):
    #list of news by their direction good bad

    news_list = list(mongo.find_matches_two_fields('articles', 'company', [company], 'direction', direction_list))
    news = []
    for new_id, new_dict in new_articles.articles.items():
        if direction in new_dict.get('direction'):
            if 'NEU' not in new_dict.get('direction'):
                if new_dict.get('company') == company:
                    news.append(new_dict)
    return news

def update_companies_news(time_interval):

    while True:
        all_news = new_articles.articles
        for new_id, new_dict in all_news.items():
            if 'NEU' in new_dict.get('direction'):
                continue
            company = new_dict.get('company')
            company_dict = mongo.find_one_match('companies', {"name": company})
            if new_id not in company_dict['company_news_ids']:
                company_dict['company_news_ids'].append(new_id)
                mongo.insert_one_in('companies', {"name": company},
                                    {'company_news_ids': company_dict['company_news_ids']})
        gevent.sleep(time_interval)


def update_companies_news_once():

    all_news = new_articles.articles
    for new_id, new_dict in all_news.items():
        if 'NEU' in new_dict.get('direction'):
            continue
        company = new_dict.get('company')
        company_dict = mongo.find_one_match('companies', {"name": company})
        if new_id not in company_dict['company_news_ids']:
            company_dict['company_news_ids'].append(new_id)
            mongo.insert_one_in('companies', {"name": company},
                                {'company_news_ids': company_dict['company_news_ids']})


def news_poll(poll_time):

    gevent.spawn(update_companies_news, poll_time)


def add_article(article):
    import hashlib
    title = article.get('title').encode('utf-8')
    id = str(hashlib.md5(title).hexdigest())
    new_articles.articles[id] = article


def get_article_by_id(article_id):

    return new_articles.articles.get(article_id, None)

def get_companies_articles(company):
    return list(mongo.find_matches('articles', {'company': company}))


def article_from_excel():

    from xlrd import open_workbook
    import copy
    book = open_workbook('Scrader-Sample_1-12.xlsx')
    sheet = book.sheet_by_index(0)
    keys = dict((i, sheet.cell_value(0, i)) for i in range(sheet.ncols))
    articles = (dict((keys[j], sheet.cell_value(i, j)) for j in keys) for i in range(1, sheet.nrows))
    mongo.delete_many('articles')
    for article in articles:
        new_article = {}
        new_article['title'] = article.get('Title')
        new_article['image_url'] = article.get('image url')
        new_article['subtitle'] = '10/5/2017'
        new_article['item_url'] = article.get('URL')
        new_article['direction'] = article.get('Sentiment')
        new_article['company'] = article.get('Company')
        new_article['website'] = article.get('Website')
        new_article['website_url'] = article.get('Website url')
        add_article(new_article)
        mongo.insert_one('articles', new_article)
