from pysnmp.hlapi import *
import socket
from mongodb import get_database
dbname = get_database()

# Create a new collection
collection = dbname["netif"]
switches = collection["switches"]

switch_id = 1

devices = []
for j in range(255):
    ip = "10.128.4." + str(j)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.01)
    if s.connect_ex((ip, 161)) == 0:
      devices.append(ip)
    s.close()

for i in range(255):
# Replace with the IP address of the switch
    switch_ip = devices[i]
    #switch_ip = "10.128.10.19"
    #print(i+1)
# Replace with the SNMP community string
    community = "public"

# Replace with the OID for the CPU speed
    name_oid = "1.3.6.1.2.1.1.5.0"

    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((switch_ip, 161), timeout=0, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity(name_oid)))
    )

    if error_indication:
     #print(error_indication)
     #exit
     print("10.128.4." + str(i) + " -->                                                            nicht vorhanden")
    elif error_status:
    # print('%s at %s' % (error_status.prettyPrint(),
     #                     error_index and var_binds[str(error_index) - 1][0] or '?'))
      #exit
      print("10.128.4." + str(i) + " -->                                                            nicht vorhanden")
    else:
        for var_bind in var_binds:
        # The CPU speed will be in the first variable binding
            #switch_oid, switch_value = var_bind
            #print(switch_value[1])
            #print('%s = %s' % (switch_oid.prettyPrint(), switch_value.prettyPrint()))
            switch_name = str(var_bind[1])
            switch_ip = "10.128.4." + str(i)
            print("10.128.4." + str(i) + " --> " + switch_name)
            switches.insert_one({ "_id": switch_id, "name": switch_name, "ip": switch_ip })
            switch_id = switch_id + 1