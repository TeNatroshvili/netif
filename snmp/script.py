# from pysnmp.hlapi import *

# iterator = getCmd(
#     SnmpEngine(),
#     CommunityData('public', mpModel=0),
#     UdpTransportTarget(('10.128.10.19', 161)),
#     ContextData(),
#     ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
# )

# errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

# if errorIndication:
#     print(errorIndication)

# elif errorStatus:
#     print('%s at %s' % (errorStatus.prettyPrint(),
#                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

# else:
#     for varBind in varBinds:
#         print(' = '.join([x.prettyPrint() for x in varBind]))
# Import the necessary modules
from pysnmp.hlapi import *

# Define the SNMP parameters for the switch
snmp_params = {
    "hostname": "<hostname or IP address of the switch>",
    "community": "<SNMP community string>",
    "port": 161,  # default SNMP port
}

# Define the SNMP Object Identifier (OID) for the switch's system description
oid_sys_descr = ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)

# Create an SNMP get request to retrieve the switch's system description
snmp_request = getCmd(SnmpEngine(),
                      CommunityData(snmp_params["community"]),
                      UdpTransportTarget((snmp_params["hostname"], snmp_params["port"])),
                      ContextData(),
                      ObjectType(oid_sys_descr))

# Send the request and receive the response
snmp_response = next(snmp_request)

# Print the response
print(snmp_response)

# Parse the response to extract the system description from the response
sys_descr = snmp_response[3][0][1].prettyPrint()
print(f"System description: {sys_descr}")

# You can run additional SNMP requests to retrieve other information as needed
# ...
