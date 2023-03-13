from pymongo import MongoClient
 
 # MongoDB Client
CONNECTION_STRING = "mongodb://admin:admin@10.128.10.7/netif"
client = MongoClient(CONNECTION_STRING)
db = client.get_database('netif')

# Collections
switches = db.switches
settings = db.settings
users = db.users