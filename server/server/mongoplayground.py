import time
import json
from pathlib import Path

from pymongo import MongoClient

# client = MongoClient(host='localhost', port=3000)

# # get db reference
# db = client['forum-webapp']
# # get collection reference
# users = db['users']

# # one thing to note here is that these reference involves no operation on the 
# # mongoDB side
# # actual creation of database/collection is triggered when
# # the first document is written

# sampleuser = {
#     'userId': '222222',
#     'displayName': 'John Doe',
#     'password': '11111111',
#     'createdAt': time.time(),
# }
# result = users.insert_one(sampleuser)
# print(result)
# print(db.list_collection_names())

# setting up test environment
# create database
# create collection
# create records
# drop collection
# drop database

# - break test up into different files
# - Start implementing CRUD in mongoDB
# - rewrite test with more abstraction