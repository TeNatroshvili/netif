from pysnmp.hlapi import *
from reportlab.pdfgen import canvas

errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData('public'),
           UdpTransportTarget(('10.128.10.19', 161)),
           ContextData(),
           ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
           ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysObjectID', 0)),
           ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)),
           ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysServices', 0))
           )
)

# Check for errors
if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
else:
    c = canvas.Canvas("daily_report.pdf")
    
    c.drawString(100, 750, "Daily Report")
    
    c.drawString(100, 730, "System Description:")
    c.drawString(250, 730, varBinds[0][1].prettyPrint())
    c.drawString(100, 710, "System Object ID:")
    c.drawString(250, 710, varBinds[1][1].prettyPrint())
    c.drawString(100, 690, "System Location:")
    c.drawString(250, 690, varBinds[2][1].prettyPrint())
    c.drawString(100, 670, "Number of System Services: ")
    c.drawString(250, 670, varBinds[3][1].prettyPrint())

    c.save()

