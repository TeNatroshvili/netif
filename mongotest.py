from mongodb import get_database
dbname = get_database()
 
# Create a new collection
collection = dbname["netif"]
switches = collection["switches"]

#switches.insert_one({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({ "name": "test 3", "address": "Highway 37" })
#switches.delete_many({})

for x in switches.find():
  print(x)