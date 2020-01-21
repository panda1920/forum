import time
import json
from pathlib import Path

from pymongo import MongoClient

# multiple client works
client = MongoClient(host='localhost', port=3000)
client2 = MongoClient(host='localhost', port=3000)

# get db reference
db = client['forum-webapp']
# get collection reference
users = db['users']

# one thing to note here is that these reference involves no operation on the 
# mongoDB side
# actual creation of database/collection is triggered when
# the first document is written

sampleuser = {
    'userId': '222222',
    'displayName': 'John Doe',
    'password': '11111111',
    'createdAt': time.time(),
}
result = users.insert_one(sampleuser)
print(result)
print(db.list_collection_names())
print(client2['forum-webapp']['users'].find_one())

client.drop_database('forum-webapp')

# - break test up into different files
# - Start implementing CRUD in mongoDB
# - rewrite test with more abstraction
# - put dbname, mongoserver hostname, portnum on enviornment variable
# - figure out how configure this test on circleci