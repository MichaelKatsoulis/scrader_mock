import gevent
import mongo
import schedule
import time
import pickle

from gevent import monkey

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
    # list of news type a company has
    news_cursor = mongo.find_matches('articles', {'company': company_given})
    comp_type_of_news = []
    for new in news_cursor:
        if 'POS' in new['direction']:
            comp_type_of_news.append('good_companies')
        elif 'NEG' in new['direction']:
            comp_type_of_news.append('bad_companies')

    return list(set(comp_type_of_news))


def total_articles():

    total_cursor = mongo.find_matches_not_containing('articles', 'direction', ['NEU', 'NEUTRAL'])
    return total_cursor.count()


def companies_by_type(news_type):
    # list of companies names , type can be good_companies bad_companies

    if news_type == 'good_companies':
        match = ['POS', 'POSITIVE']
    elif news_type == 'bad_companies':
        match = ['NEG', 'NEGATIVE']

    articles_cursor = list(mongo.find_matches_containing_many('articles', 'direction', match))
    companies_new_list = []
    for article in articles_cursor:
        comp_dict= mongo.find_one_match('companies', {'name': article.get('company')})
        if comp_dict not in companies_new_list:
            comp_dict['company_name'] = comp_dict.pop('name')
            companies_new_list.append(comp_dict)

    return companies_new_list


def get_news_by_direction_and_company(company, direction_list):
    # list of news by their direction good bad

    news_list = list(mongo.find_matches_two_fields('articles', 'company', [company], 'direction', direction_list))
    return news_list


def get_companies_articles(company):
    return list(mongo.find_matches('articles', {'company': company}))


def article_from_excel():

    from xlrd import open_workbook
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
        mongo.insert_one('articles', new_article)


def article_from_csv():

    import csv
    articles = []
    with open('Scrader4.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for article in reader:
            new_article = {}
            new_article['title'] = article.get('Title')
            new_article['image_url'] = article.get('Image')
            new_article['subtitle'] = article.get('Date')
            new_article['item_url'] = article.get('Article')
            articles.append(new_article)
    return articles


def send_user_news(user_id):
    user = mongo.find_one_match('users', {"user_id": user_id})
    print("sending staff for user" + user.get('name'))


def start_scheduler(datetime, user_id):
    schedule.every().day.at(datetime).do(send_user_news, user_id)
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler_task(user):
    datetime = user.get('datetime')
    user_id = user.get('user_id')
    if user.get('task_id') is not None:
        task_ob = pickle.loads(user.get('task_id'))
        print(task_ob)
        gevent.kill(task_ob)

    task_ob = gevent.spawn(start_scheduler, datetime, user_id)
    task_id = pickle.dumps(task_ob)
    mongo.insert_one_in('users', {"user_id": user_id}, {'task_id': task_id})

