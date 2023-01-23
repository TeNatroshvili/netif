from reportlab.lib.pagesizes import A4
from mongodb import switches

from pysnmp.hlapi import *
from reportlab.pdfgen import canvas
from datetime import datetime

def gen_report():
  errorIndication, errorStatus, errorIndex, varBinds = next(
      getCmd(SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget(('10.128.10.19', 161)),
            ContextData(),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysObjectID', 0)),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysServices', 0))
            )
  )

  if errorIndication:
      print("error")
      print(errorIndication)
  elif errorStatus:
      print('%s at %s' % (errorStatus.prettyPrint(),
                          errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
  else:
      c = canvas.Canvas("reports/daily_report.pdf", pagesize=A4)

      c.drawString(100, 750, "Daily Report")

      now = datetime.now()
      current_time = now.strftime("%H:%M:%S")
      current_date = now.strftime("%m/%d/%Y")

      c.drawString(300, 750, "Current Date:")
      c.drawString(400, 750, current_date)
      c.drawString(300, 730, "Current Time:")
      c.drawString(400, 730, current_time)

      c.drawString(100, 630, "System Description:")
      c.drawString(260, 630, varBinds[0][1].prettyPrint())
      c.drawString(100, 610, "System Object ID:")
      c.drawString(260, 610, varBinds[1][1].prettyPrint())
      c.drawString(100, 590, "Number of System Services:")
      c.drawString(260, 590, varBinds[2][1].prettyPrint())

      c.save()