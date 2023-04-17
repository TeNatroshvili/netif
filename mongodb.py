# ---------------------------------------------------------
# Code for MongoDB Database Connection and CRUD Operations
# ---------------------------------------------------------
# author:   Stiefsohn Lukas, Baumann Danièl
# created:  2022-12-06
# version:  1.1
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

#### Cryptography

# key is needed for encoding and decoding the passwords which are stored in the database
key = b'Cn_Hngogipr7LZzUDvceg0hBCwJ_bPzKNafW5f-9bHY='
f = Fernet(key)

### Collections

# Collection with all switches including the model info
switches = db.switches

# Collection with all settings data per switch - ip is the key
settings = db.settings

# Collection with the users for the NETIF access - currently only one admin user
users = db.users

# Collection with the encoded login credentials for external data access (switch and fileserver)
credentials = db.credentials

### Functions

# save_settings_to_db()
# Defining a function to save the switch settings to the database
#
# params: switch_object - Json Object witch switch data
def save_settings_to_db(switch_object):
    # Updating the 'settings' collection with the 'switch_object' with the matching 'ip_address'
    # If there is no matching 'ip_address', it creates a new document with the 'switch_object'
    settings.update_one({'ip_address': switch_object["ip_address"]}, {
                        "$set": switch_object}, upsert=True)

# update_switch_ip()
# Define a function to update the switch ip in the database when the ip is changed over the frontend
#
# params: old_ip - old ip adress from the target switch
#         new_ip - new ip from the target switch
def update_switch_ip(old_ip, new_ip):
    switches.update_one({'ip': old_ip}, {
        "$set": {'ip': new_ip}
    }, upsert=True)


# get_switch_credentials()
#
# returns: login dictionary with username and password from the switches
def get_switch_credentials():
    cred = credentials.find_one({"_id": "switch"})
    login = {"username": cred["username"],
             "password": f.decrypt(cred["password"]).decode('ascii')}
    return login


# get_samba_credentials()
#
# returns: login dictionary with username, password and ipadress from the samba file server
def get_samba_credentials():
    cred = credentials.find_one({"_id": "samba"})
    login = {"username": cred["username"],
             "password": f.decrypt(cred["password"]).decode('ascii'),
             "server_ip": cred["server_ip"]}
    return login


# update_switch_credentials()
#
# params: newpass - new password for the switch access
def update_switch_credentials(newpass):
    credentials.update_one({"_id": "switch"}, {
                           "$set": {"password": f.encrypt(newpass.encode('ascii'))}}, upsert=True)


# update_samba_credentials()
#
# params: newpass - new password for the samba file server
def update_samba_credentials(newpass):
    credentials.update_one({"_id": "samba"}, {
                           "$set": {"password": f.encrypt(newpass.encode('ascii'))}}, upsert=True)