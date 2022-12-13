# Finde IP-Adressen

import socket

def get_network_devices():
  devices = []
  for i in range(255):
    ip = "10.128.4." + str(i)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.01)
    if s.connect_ex((ip, 161)) == 0:
      devices.append(ip)
    s.close()
  return devices
#print(get_network_devices())

# Finde Switches

from pysnmp.hlapi import *

def get_ip_addresses(community, host):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)))
    )

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            oid, value = varBind
            print('%s = %s' % (oid.prettyPrint(), value.prettyPrint()))

# Beispielaufruf der Funktion
devices = get_network_devices()
print(devices)
#for j in range(255):
  #  miin = devices[j]
   # print(miin)
get_ip_addresses('public', '10.128.10.19')







# Suche alle offenen Ports
"""  
import socket

def scan_ports(host, start, end):
  for port in range(start, end+1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.01)
    if s.connect_ex((host, port)) == 0:
      print(f"Port {port} is open on {host}")
    s.close()

# Scan all ports from 1 to 65535 on the host 192.168.1.5
scan_ports("10.128.10.19", 1, 65535)
"""