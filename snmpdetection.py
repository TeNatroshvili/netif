from pysnmp.hlapi import *

# Replace with the IP address of the switch
switch_ip = "10.128.4.20"

# Replace with the SNMP community string
community = "public"

# Replace with the OID for the CPU speed
name_oid = "1.3.6.1.2.1.1.5.0"

error_indication, error_status, error_index, var_binds = next(
    getCmd(SnmpEngine(),
           CommunityData(community),
           UdpTransportTarget((switch_ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(name_oid)))
)

if error_indication:
    print(error_indication)
elif error_status:
    print('%s at %s' % (error_status.prettyPrint(),
                        error_index and var_binds[str(error_index) - 1][0] or '?'))
else:
    for var_bind in var_binds:
        # The CPU speed will be in the first variable binding
        name = str(var_bind[1])
        print("the name is " + name)