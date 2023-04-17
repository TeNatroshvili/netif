# ---------------------------------------------------------
# Code for MongoDB Database Connection and CRUD Operations
# ---------------------------------------------------------
# author:   Stiefsohn Lukas
# created:  2023-12-06
# version:  1.0
# ---------------------------------------------------------

from pymongo import MongoClient
from cryptography.fernet import Fernet

# Creating the connection string with the login credentials
CONNECTION_STRING = "mongodb://{username}:{password}@10.128.10.7/netif".format(
    username="admin",
    password="admin"
)

# Creating a client instance and connecting it to the database
client = MongoClient(CONNECTION_STRING)

# Getting the 'netif' database
db = client.get_database('netif')

# cryptography
key = b'Cn_Hngogipr7LZzUDvceg0hBCwJ_bPzKNafW5f-9bHY='
f = Fernet(key)

# Collections
switches = db.switches
settings = db.settings
users = db.users
credentials = db.credentials

for user in users.find():
        print(user)

# Defining a function to save the switch settings to the database
def save_settings_to_db(switch_object):
    # Updating the 'settings' collection with the 'switch_object' with the matching 'ip_address'
    # If there is no matching 'ip_address', it creates a new document with the 'switch_object'
    settings.update_one({'ip_address': switch_object["ip_address"]}, {
                        "$set": switch_object}, upsert=True)


def update_switch_ip(old_ip, new_ip):
    switches.update_one({'ip': old_ip}, {
        "$set": {'ip': new_ip}
    }, upsert=True)


def get_switch_credentials():
    cred = credentials.find_one({"_id": "switch"})
    login = {"username": cred["username"],
             "password": f.decrypt(cred["password"]).decode('ascii')}
    return login


def get_samba_credentials():
    cred = credentials.find_one({"_id": "samba"})
    login = {"username": cred["username"],
             "password": f.decrypt(cred["password"]).decode('ascii'),
             "server_ip": cred["server_ip"]}
    return login


def update_switch_credentials(newpass):
    credentials.update_one({"_id": "switch"}, {
                           "$set": {"password": f.encrypt(newpass.encode('ascii'))}}, upsert=True)
    print(credentials.find_one({"_id":"switch"}))

def update_samba_credentials(newpass):
    credentials.update_one({"_id": "samba"}, {
                           "$set": {"password": f.encrypt(newpass.encode('ascii'))}}, upsert=True)