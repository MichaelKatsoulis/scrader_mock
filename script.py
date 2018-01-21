import os
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
    print(len(cursor_list))
    for article in cursor_list:
        scrader_db[collection].\
            update({"_id": ObjectId(article['_id'])},
                   {'$set': {'appended': True}})
        article.pop('_id', None)

    # scrader_db[collection].update({'$and': [{field1: {'$in': match1}},
    #                                         {field2: {'$in': match2}}]},
    #                               {'$set': {'appended': True}},
    #                               True, True)
    return pd.DataFrame(cursor_list)


def main():
    dataframe = convert_collection_to_df(MongoClient(), 'dev_articles',
                                                        'checked', [True],
                                                        'appended', [False])
    # if file does not exist write header
    if not os.path.isfile('scraderdata.csv'):
        dataframe.to_csv('scraderdata.csv', encoding='utf-8')
    else:  # else it exists so append without writing the header
        dataframe.to_csv('scraderdata.csv', mode='a', header=False,
                         encoding='utf-8')


if __name__ == '__main__':
    main()
