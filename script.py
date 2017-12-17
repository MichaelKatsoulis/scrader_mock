from pymongo import MongoClient
import pandas as pd
# converts mongodb collection to csv


def convert_collection_to_df(mongo_cli, collection, match):
    dbcli = mongo_cli
    scrader_db = dbcli['scrader']
    cursor = scrader_db[collection].find(match, {'_id': False})
    return pd.DataFrame(list(cursor))


if __name__ == '__main__':
    dataframe = convert_collection_to_df(MongoClient(), 'dev_articles',
                                                        {'checked': True})
    dataframe.to_csv("./TrainingData.csv", encoding='utf-8')
