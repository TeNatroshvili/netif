from pymongo import MongoClient

from login_credentials import mongodb_login_credentials


# MongoDB Client
CONNECTION_STRING = "mongodb://{username}:{password}@10.128.10.7/netif".format(
    username=mongodb_login_credentials["username"],
    password=mongodb_login_credentials["password"]
)
client = MongoClient(CONNECTION_STRING)
db = client.get_database('netif')

# Collections
switches = db.switches
settings = db.settings
users = db.users

# Save Settings to MongoDB

def save_settings_to_db(switch_object):
    settings.update_one({'ip_address': switch_object["ip_address"]}, {
                        "$set": switch_object}, upsert=True)
