import os
from pymongo import MongoClient
import pandas as pd
# converts mongodb collection to csv


def convert_collection_to_df(mongo_cli, collection, field1, match1,
                             field2, match2):
    dbcli = mongo_cli
    scrader_db = dbcli['scrader']
    cursor = scrader_db[collection].find({'$and': [{field1: {'$in': match1}},
                                         {field2: {'$in': match2}}]},
                                         {'_id': False})

    cursor_list = list(cursor)
    print(cursor_list)
    scrader_db[collection].update({'$and': [{field1: {'$in': match1}},
                                            {field2: {'$in': match2}}]},
                                  {'$set': {'appended': True}},
                                  False, True)
    return pd.DataFrame(cursor_list)


if __name__ == '__main__':
    dataframe = convert_collection_to_df(MongoClient(), 'dev_articles',
                                                        'checked', [True],
                                                        'appended', [False])
    # if file does not exist write header
    if not os.path.isfile('TrainingData.csv'):
        dataframe.to_csv('TrainingData.csv', encoding='utf-8')
    else:  # else it exists so append without writing the header
        dataframe.to_csv('TrainingData.csv', mode='a', header=False,
                         encoding='utf-8')
