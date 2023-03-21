# -------------------------------------------------------------------
# Function to search for switches and extract information using SNMP
# -------------------------------------------------------------------
# author:   Stiefsohn Lukas
# created:  2023-01-23
# version:  1.0
# -------------------------------------------------------------------
from pysnmp.hlapi import *
import socket
import re

from mongodb import switches

def search_switches():

    # set switch_id and the ip_range
    switch_id = 0
    ip_range = "10.137.4." # IP range to scan for switches
    devices = [] # List to store IPs of discovered switches

    # Loop through all possible IP addresses in the range
    for j in range(255):
        ip = ip_range + str(j) # IP address to be checked
        print(ip)

        # Use UDP socket to attempt connection to SNMP port
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
        s.settimeout(0.01) # set a timeout for the socket
        if s.connect_ex((ip, 161)) == 0: # If connection is successful, add IP to devices list
            devices.append(ip)
        s.close() # close the socket

    # Loop through all discovered switch IPs and extract information using SNMP
    for i in range(len(devices)):
        switch_ip = devices[i] # IP address of the switch to be queried
        print(switch_ip)
        community = "public" # SNMP community string
        name_oid = "1.3.6.1.2.1.1.5.0" # OID for switch name
        name_oid2 = "1.3.6.1.2.1.1.1.0" # OID for switch model

        # Get switch name using SNMP protocol
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((switch_ip, 161), timeout=0, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(name_oid)))
        )

        # Get switch model using SNMP protocol
        error_indication, error_status, error_index, var_binds2 = next(
            getCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((switch_ip, 161), timeout=0, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(name_oid2)))
        )

        # Check for SNMP errors
        if error_indication:
            print(error_indication)
        elif error_status:
            print('%s at %s' % (error_status.prettyPrint(),
                            error_index and var_binds[str(error_index) - 1][0] or '?'))
        else:
            # Parse switch model from SNMP response
            for var_bind in var_binds:
                switch_oid, switch_value = var_bind
                switch_value2 = var_binds2
                switch_data = re.split(r' = |, | - ', str(switch_value2[0])) 
                switch_name = str(var_bind[1])
                switch_ip = ip_range + str(i)
                switch_model = str(switch_data[1])
                print(ip_range + str(i) + " --> " + switch_name +  " --> " + switch_model)
                
                 # Save switch details to database
                switches.update_one({'_id': switch_id}, 
                                {"$set": {"ip": switch_ip, "name": switch_name, "model": switch_model}},
                                 upsert=True)
                switch_id = switch_id + 1 # increment switch ID
    return "switches loaded" # return a message indicating that switches have been found and loaded into the database