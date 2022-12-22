# # # from pysnmp.hlapi import *

# # # iterator = getCmd(
# # #     SnmpEngine(),
# # #     CommunityData('public', mpModel=0),
# # #     UdpTransportTarget(('10.128.10.19', 161)),
# # #     ContextData(),
# # #     ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
# # # )

# # # errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

# # # if errorIndication:
# # #     print(errorIndication)

# # # elif errorStatus:
# # #     print('%s at %s' % (errorStatus.prettyPrint(),
# # #                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

# # # else:
# # #     for varBind in varBinds:
# # #         print(' = '.join([x.prettyPrint() for x in varBind]))
# # # Import the necessary modules
# # from pysnmp.hlapi import *

# # # Define the SNMP parameters for the switch
# # # Import the necessary libraries
# # from pysnmp.hlapi import *

# # # Define the SNMP community and host
# # community = ('public')
# # host = '10.128.10.19'

# # # Define the OID for the data flowing through the switch
# # oid = '1.3.6.1.2.1.2.2.1.10'

# # # Create an SNMP engine instance
# # snmp_engine = SnmpEngine()

# # # Set up the SNMP transport
# # snmp_transport = UdpTransportTarget((host, 161))

# # # Create a GET request PDU
# # snmp_request_pdu = CommunityData(community, mpModel = 0)

# # # Define the variable binding for the GET request
# # snmp_var_bind = ObjectType(ObjectIdentity(oid))

# # # Send the GET request and retrieve the response
# # snmp_response = getCmd(snmp_engine, snmp_request_pdu, snmp_transport, snmp_var_bind)

# # # Parse the response and print the value of the variable binding

# # snmp_response_value = next(snmp_response)[3]
# # def is_generator_empty(gen):
# #   try:
# #     next(gen)
# #     return False
# #   except StopIteration:
# #     return True
# # print(is_generator_empty(snmp_response))

# # iterator = iter(snmp_response_value)
# # while True:
# #     try:
# #         element = next(iterator)
# #         print(element.prettyPrint())
# #     except StopIteration:
# #         break
# from pysnmp.hlapi import *
# from reportlab.pdfgen import canvas


# switch_ip = "10.128.4.102"

# community = "public"

# name_oid = "1.3.6.1.2.1.1.5.0"
# cpu_oid= "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.5"

# error_indication, error_status, error_index, var_binds = next(
#     getCmd(SnmpEngine(),
#            CommunityData(community),
#            UdpTransportTarget((switch_ip, 161)),
#            ContextData(),
#            ObjectType(ObjectIdentity(name_oid)))
# )

# if error_indication:
#     print(error_indication)
# elif error_status:
#     print('%s at %s' % (error_status.prettyPrint(),
#                         error_index and var_binds[str(error_index) - 1][0] or '?'))
# else:
#     for var_bind in var_binds:
#         name = str(var_bind[1])
#         print("The name is " + name)

# error_indication, error_status, error_index, cpu_usage = next(
#     getCmd(SnmpEngine(),
#            CommunityData(community),
#            UdpTransportTarget((switch_ip, 161)),
#            ContextData(),
#            ObjectType(ObjectIdentity(name_oid)))
# )

# if error_indication:
#     print(error_indication)
# elif error_status:
#     print('%s at %s' % (error_status.prettyPrint(),
#                         error_index and cpu_usage[str(error_index) - 1][0] or '?'))
# else:
#     for var_bind in cpu_usage:
#         cpu = str(var_bind[1])
#         print("The cpu is " + cpu)

# c = canvas.Canvas("mypdf.pdf")

# c.drawString(100, 750, "name is: " + name +"\n"+"cpu usage is: " + cpu)

# c.save()

from pysnmp.hlapi import *
from reportlab.pdfgen import canvas

# Set up SNMP credentials
community_string = 'public'
ip_address = '10.128.10.19'

# Set up SNMP request to retrieve CPU usage
error_indication, error_status, error_index, var_binds = next(
    getCmd(SnmpEngine(),
           CommunityData(community_string),
           UdpTransportTarget((ip_address, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('HOST-RESOURCES-MIB', 'hrProcessorLoad', 1)))
)

# Check for errors
if error_indication:
    print(error_indication)
elif error_status:
    print('%s at %s' % (error_status.prettyPrint(),
                        error_index and var_binds[int(error_index) - 1][0] or '?'))
else:
    # Create a PDF file and write the CPU usage to it
    pdf_filename = 'cpu_usage.pdf'
    c = canvas.Canvas(pdf_filename)
    c.drawString(100, 750, 'CPU Usage: {}%'.format(int(var_bind[1])))
    c.showPage()
    c.save()
