from pymongo import MongoClient
import pandas as pd
import os

dbcli = MongoClient()
db = dbcli['scrader']
collection = db['dev_articles']
cursor = list(collection.find({'checked': True}))
dataframe = pd.Dataframe(cursor)
if not os.path.isfile('news.csv'):
    dataframe.to_csv('news.csv', encoding='utf-8')
else:  # else it exists so append without writing the header
    dataframe.to_csv('news.csv', mode='a', header=False, encoding='utf-8')
