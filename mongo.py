from pymongo import MongoClient


def init_database():

    global client
    client = MongoClient()
    global db
    db = client['scrader']
    return db


def insert_one(collection_name, document):
    collection = db[collection_name]
    return collection.insert_one(document)


def delete_many(collection_name):
    collection = db[collection_name]
    return collection.delete_many({})


def count(collection_name):
    return db[collection_name].count()


def fetch_collection(collection_name):
    collection = db[collection_name]
    return collection.find({}, {'_id': False})


def find_one(collection_name, to_match):
    collection = db[collection_name]
    return collection.find(to_match)


def insert_one_in(collection_name, to_match, new_data):
    collection = db[collection_name]
    return collection.update(to_match, {'$set': new_data})
