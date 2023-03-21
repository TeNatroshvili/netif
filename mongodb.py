# ---------------------------------------------------------
# Code for MongoDB Database Connection and CRUD Operations
# ---------------------------------------------------------
# author:   Stiefsohn Lukas
# created:  2023-12-06
# version:  1.0
# ---------------------------------------------------------

from pymongo import MongoClient

from login_credentials import mongodb_login_credentials

# Creating the connection string with the login credentials
CONNECTION_STRING = "mongodb://{username}:{password}@10.128.10.7/netif".format(
    username=mongodb_login_credentials["username"],
    password=mongodb_login_credentials["password"]
)

# Creating a client instance and connecting it to the database
client = MongoClient(CONNECTION_STRING)

# Getting the 'netif' database
db = client.get_database('netif')

# Getting the 'switches', 'settings', and 'users' collections from the 'netif' database
switches = db.switches
settings = db.settings
users = db.users

# Defining a function to save the switch settings to the database
def save_settings_to_db(switch_object):
    # Updating the 'settings' collection with the 'switch_object' with the matching 'ip_address'
    # If there is no matching 'ip_address', it creates a new document with the 'switch_object'
    settings.update_one({'ip_address': switch_object["ip_address"]}, {
                        "$set": switch_object}, upsert=True)


# Defining a function to update the IP address of a switch
def update_switch_ip(old_ip, new_ip):
    # Updating the 'switches' collection with the new IP address of the switch with the matching 'ip'
    # If there is no matching 'ip', it creates a new document with the 'ip'
    switches.update_one({'ip':old_ip},{
        "$set": {'ip' : new_ip}
    }, upsert=True)