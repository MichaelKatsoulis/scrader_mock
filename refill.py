import os
import copy
from pymongo import MongoClient
import pandas as pd
from bson.objectid import ObjectId
# converts mongodb collection to csv


def convert_collection_to_df(mongo_cli, collection, field1, match1,
                             field2, match2):
    dbcli = mongo_cli
    scrader_db = dbcli['scrader']
    cursor = scrader_db[collection].find({'$and': [{field1: {'$in': match1}},
                                         {field2: {'$in': match2}}]})
    cursor_list = list(cursor)
    copied_list = copy.deepcopy(cursor_list)
    
    for d in cursor_list:
    	title = d['title']
        times = 0
    	for dic in copied_list:
	    if dic['title']==title:
                times += 1
                if times==2:
                    print(title)
	            copied_list.remove(dic)
                    break	
    
    print(len(copied_list))
    somelist = []
    somedict = {'direction':'', 'title':''}
    for article in copied_list:
	newart = copy.deepcopy(somedict)
        #scrader_db[collection].\
         #   update({"_id": ObjectId(article['_id'])},
          #        {'$set': {'appended': True}})
        #article.pop('_id', None)
	newart['direction'] = article.get('direction')
	newart['title'] = article.get('title')
	somelist.append(newart)

    # scrader_db[collection].update({'$and': [{field1: {'$in': match1}},
    #                                         {field2: {'$in': match2}}]},
    #                               {'$set': {'appended': True}},
    #                               True, True)
    return pd.DataFrame(somelist)


def main():
    dataframe = convert_collection_to_df(MongoClient(), 'dev_articles',
                                                        'checked', [True],
                                                        'User', ['Ptrs'])
    # if file does not exist write header
    if not os.path.isfile('newdata.csv'):
        #pass
        dataframe.to_csv('newdata.csv', encoding='utf-8', index=False)
    else:  # else it exists so append without writing the header
        #pass
        dataframe.to_csv('newdata.csv', mode='a', header=False, index=False,
                         encoding='utf-8')


if __name__ == '__main__':
    main()
