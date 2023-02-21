from database_connection import get_database
from bson.json_util import dumps
from bson.json_util import loads
dbname = get_database()
 
# Create a new collection
collection = dbname["netif"]
switches = collection["switches"]
settings = collection["settings"]
#switches.insert_one({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({})

# for name in collection.list_collection_names():
#     print(name)

# for switch in switches.find():
#     print(switch)
# collection.create_collection("switches")
# collection.drop_collection("switches")
