import new_companies
import new_articles

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
    company_news = new_companies.all_companies.get(company_given)
    type_of_news = []
    for new_id in company_news:
        if new_articles.articles[new_id]['direction'] == 'good':
            type_of_news.append('good_companies')
        else:
            type_of_news.append('bad_companies')

    return list(set(type_of_news))

def total_articles():
    return len(new_articles.articles.keys())

def companies_by_type(news_type):
    # list of companies names , type can be good_companies bad_companies

    companies_list = []
    if news_type == 'good_companies':
        news_type = 'good'
    else:
        news_type = 'bad'

    for company_name, company_dict in new_companies.all_companies.items():
        for new_id in companies_dict['company_news_ids']:
            if new_articles.articles[new_id]['direction'] == news_type:
                updated_company_dict['company_name'] = company_name
                updated_company_dict.update(company_dict)
                companies_list.append(updated_company_dict)

    return companies_list

def get_news_by_direction(direction):
    #list of news by their direction good bad

    news = []
    for new_id, new_dict in new_articles.articles.items():
        if new_dict.get('direction') == direction:
            news.append(new_dict)
    return news
