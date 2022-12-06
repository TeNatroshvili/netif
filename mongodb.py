from pymongo import MongoClient
def get_database():
    CONNECTION_STRING = "mongodb://admin:admin@10.128.10.7/netif"
    client = MongoClient(CONNECTION_STRING)
    return client
  
if __name__ == "__main__":   
    dbname = get_database()

dbname = get_database()
 
# Create a new collection
collection_name = dbname["switches"]
 
print(collection_name.get_collection("switches").find())
