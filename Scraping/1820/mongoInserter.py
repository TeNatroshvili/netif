from pymongo import MongoClient
import pymongo

def save_to_db(switch_object):
        CONNECTION_STRING = "mongodb://admin:admin@10.128.10.7/netif"

        dbname =  MongoClient(CONNECTION_STRING)

        # Create a new collection
        collection = dbname["netif"]
        switches = collection["switch_settings"]
        switches.update_one({'ip_address':switch_object["ip_address"]},{"$set": switch_object}, upsert=True)
        print(switches.find_one(sort=[('ip_address', pymongo.DESCENDING)]))