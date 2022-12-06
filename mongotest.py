from mongodb import get_database
dbname = get_database()
 
# Create a new collection
collection = dbname["netif"]

for x in collection["switches"].find():
  print(x)