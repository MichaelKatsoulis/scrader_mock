import csv
from pymongo import MongoClient
import copy
dbcli = MongoClient('127.0.0.1', 8080)
db = dbcli['scrader']
db.authenticate('scrader', 'scr@d3r')

collection = db['url_terms']
with open('LIST_OF_URLS.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	url_terms = []
	for url_term in reader:
	    term = url_term.get('URL TERMS')
            print term
            url_terms.append(term)
url_dict = {'url_terms': url_terms}
collection.insert_one(url_dict)
#url_list = list(collection.find({}, {'_id': False}))
#urls = url_list[0].get('url_terms')
#print(len(urls))
#print urls[0]
#print urls[-1]
collection = db['scraper_companies']
companies = []
company_dict = {}
synonims_keys = ['SYNOMYM 1', 'SYNOMYM 2', 'SYNOMYM 3', 'SYNOMYM 4']
with open('COMPANY_NAMES.csv') as csvfile:
       reader = csv.DictReader(csvfile)
       for company in reader:
           if company.get('COMPANY NAMES') != '':
                #print company.get('COMPANY NAMES')
           	term = company.get('COMPANY NAMES')
                new_comp_dict = copy.deepcopy(company_dict)
                new_comp_dict['company_name'] = term
                new_comp_dict['synonims'] = []
                new_comp_dict['url_terms'] = []
                new_comp_dict['url_terms'].append(company.get('URL TERMS'))
                for syn in synonims_keys:
                        #print syn
                        #print(company.get(syn))
                	if company.get(syn) != "":
                          if  company.get(syn) is not None:
                                #print company.get(syn)
                        	new_comp_dict['synonims'].append(company.get(syn))
                new_comp_dict['synonims'].append(term)
                companies.append(new_comp_dict)
           else:
                #print(company.get('URL TERMS'))
           	new_comp_dict['url_terms'].append(company.get('URL TERMS'))

#collection.insert_many(companies)
#print(len(companies))
#print companies[76]
#print companies[32]
#print companies[900]
#print companies[1876]
#print companies[632]
#print companies[1899]

#scraper_companies = list(collection.find({}, {'_id': False}))
#print len(scraper_companies)
#print scraper_companies[0]
#print scraper_companies[-1]

#for comp in companies:
#	if comp.get('company_name') == 'Citigroup':
#        	print comp.get('synonims')
#        if comp.get('company_name') == 'Royal Dutch Shell':
#               print comp.get('synonims')               
