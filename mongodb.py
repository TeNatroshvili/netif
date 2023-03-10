from pymongo import MongoClient
 
CONNECTION_STRING = "mongodb://admin:admin@10.128.10.7/netif"
client = MongoClient(CONNECTION_STRING)
db = client.get_database('netif')


# Create a new collection
switches = db.switches
settings = db.settings
users = db.users
#switches.insert_one({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({})

# for name in db.list_collection_names():
#     print(name)

from flask_bcrypt import bcrypt
for elem in users.find():
    print(elem)

# users.update_one({'_id': '95f31207e0a84b45906d30a1b4730259'}, 
#                                 {"$set": {"password": bcrypt.hashpw(("ja").encode('utf-8'), bcrypt.gensalt())}},
#                                  upsert=True)

# for elem in users.find():
#     print(elem)

# db.create_collection("users")
# db.drop_collection("users")
