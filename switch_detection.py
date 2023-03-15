from pysnmp.hlapi import *
import socket
import re

from mongodb import switches

def search_switches():

    switch_id = 0
    ip_range = "10.137.4."
    devices = []

    for j in range(255):
        ip = ip_range + str(j)
        print(ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.01)
        if s.connect_ex((ip, 161)) == 0:
            devices.append(ip)
        s.close()

    for i in range(255):
        switch_ip = devices[i]
        print(switch_ip)
        community = "public"
        name_oid = "1.3.6.1.2.1.1.5.0"
        name_oid2 = "1.3.6.1.2.1.1.1.0"

        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((switch_ip, 161), timeout=0, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(name_oid)))
        )

        error_indication, error_status, error_index, var_binds2 = next(
            getCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((switch_ip, 161), timeout=0, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(name_oid2)))
        )

        if error_indication:
            print(error_indication)
        elif error_status:
            print('%s at %s' % (error_status.prettyPrint(),
                            error_index and var_binds[str(error_index) - 1][0] or '?'))
        else:
            for var_bind in var_binds:
                switch_oid, switch_value = var_bind
                switch_value2 = var_binds2
                switch_data = re.split(r' = |, | - ', str(switch_value2[0])) 
                switch_name = str(var_bind[1])
                switch_ip = ip_range + str(i)
                switch_model = str(switch_data[1])
                print(ip_range + str(i) + " --> " + switch_name +  " --> " + switch_model)
                switches.update_one({'_id': switch_id}, 
                                {"$set": {"ip": switch_ip, "name": switch_name, "model": switch_model}},
                                 upsert=True)
                switch_id = switch_id + 1
    return "switches loaded"
search_switches()