from database_connection import get_database
import json
dbname = get_database()
 
# Create a new collection
collections = dbname["netif"]
switches = collections["switches"]

#switches.insert_one({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({})

for coll in collections.list_collection_names():
    print(coll)


json_data = collections["chenSwitchInfos"].find_one()
del json_data['_id']
json_formatted_str = json.dumps(json_data, indent=4)

print(json_formatted_str)