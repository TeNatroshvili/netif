from pysnmp.hlapi import *

# IP-Adresse und SNMP-Community-String des Netzwerkswitches
ip_address = '10.128.10.19'
community_string = 'public'

# OID für das Modell des Netzwerkswitches (1.3.6.1.2.1.1.1.0)
oid = '1.3.6.1.2.1.1.1.0'

# SNMP-Abfrage durchführen
errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData(community_string),
           UdpTransportTarget((ip_address, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(oid)))
)

# Ergebnis auswerten
if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
else:
    for varBind in varBinds:
        oid, value = varBind
        print(value[1])
        print('%s = %s' % (oid.prettyPrint(), value.prettyPrint()))