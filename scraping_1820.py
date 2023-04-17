# ------------------------------------------
# interface to the Scraping for 1810 Switch
# ------------------------------------------
# author:   Chen Junbo
# created:  2023-02-7   
# version:  1.2
# ------------------------------------------

from lxml import html
import requests

from mongodb import save_settings_to_db
from mongodb import get_switch_credentials


def scrap_switch_1820(swtich_ip_adresse):
    # all urls, that will be scrapped
    urls = ['http://'+swtich_ip_adresse+'/htdocs/pages/base/dashboard.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/network_ipv4_cfg.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/lua/deviceviewer/deviceviewer_status.lua?unit=1&ports%5B%5D=1&ports%5B%5D=2&ports%5B%5D=3&ports%5B%5D=4&ports%5B%5D=5&ports%5B%5D=6&ports%5B%5D=7&ports%5B%5D=8&ports%5B%5D=9&ports%5B%5D=10&ports%5B%5D=11&ports%5B%5D=12&ports%5B%5D=13&ports%5B%5D=14&ports%5B%5D=15&ports%5B%5D=16&ports%5B%5D=17&ports%5B%5D=18&ports%5B%5D=19&ports%5B%5D=20&ports%5B%5D=21&ports%5B%5D=22&ports%5B%5D=23&ports%5B%5D=24&ports%5B%5D=25&ports%5B%5D=26&leds%5B%5D=power&leds%5B%5D=locator&leds%5B%5D=fault&_=1677577757505',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/port_mirror.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/jumbo_frames.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/switch_config.lsp',
            # 'http://10.137.4.41/htdocs/pages/switching/vlan_status.lsp',
            # 'http://10.137.4.41/htdocs/pages/switching/vlan_port.lsp',
            # 'http://10.137.4.41/htdocs/pages/switching/port_channel_summary.lsp',
            # 'http://10.137.4.41/htdocs/pages/switching/lldp_stats.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/switching/lldp_med_local.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/switching/lldp_remote.lsp'
            ]
    
    #first a session is created for all the scraping
    session = requests.Session()

    # login to destination website
    response = session.post('http://'+swtich_ip_adresse+'/htdocs/login/login.lua',
                            data=get_switch_credentials())
    cookie = session.cookies.get_dict()

    # test If login works
    if response.status_code == 200:
        # print('Login erfolgreich')
        # final switch setting object, which will inserted into mongDB
        switch_json_object = {}

        for url in urls:

            # scrape every single url in urls
            response = session.get(url, cookies=cookie)
            if (cookie != {} and response.status_code == 200):
                # print('Scraping für:', url)
                # print('-------------------------------------------')

                # because the response of deviceveiwer_status ......(the url which returns the port status)
                # isnt a html page like other urls, so if the deviceviewer_status is in url
                # the page_title is automaticaly the ports_vlan_status
                #
                # For all other urls, the page_title will scraped from the response html
                if ("deviceviewer_status.lua" in url):
                    page_title = "ports_vlan_status"
                else:
                    root = html.fromstring(response.content)
                    page_title = root.xpath('//title/text()')[0]

                # according the page_title, the different function will be used to scrape the data
                match page_title:
                    case "Get Connected":
                        getDatasFromGetConnected(root, switch_json_object)
                    case "Dashboard":
                        getDatasFromDashboard(root, switch_json_object)
                    case "ports_vlan_status":
                        getDatasFromPortsVlan(response.content.decode(
                            "utf-8"), switch_json_object)
                    case "Port Mirroring":
                        getDatasFromPortMirror(root, switch_json_object)
                    case "Jumbo Frames Configuration":
                        getDatasFromJumbpFrame(root, switch_json_object)
                    case "Flow Control Configuration":
                        getDatasFromFlowControl(root, switch_json_object)
                    case "LLDP-MED Local Device Summary":
                        getDatasFromLocalDevice(root, switch_json_object)
                    case "LLDP Remote Device Summary":
                        getDatasFromRemoteDevice(root, switch_json_object)


            elif (cookie == {}):
                print("Fehler beim Scrapen der Daten von ", url)
                print(
                    "Möglicher Grund: Session key ist abgelaufen, neues Key erfoderlich")
            elif (cookie == 503):
                print('Überlastung des Servers, bitte warten! Status Code 503')
            else:
                print("Fehler beim Scrapen der Daten von ", url)
                print("Statuscode: ", response)

        # Logout of the destination website and close the session
        session.get("http://"+swtich_ip_adresse +
                    "/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
        session.close()

        # Save the Setting into Database
        save_settings_to_db(switch_json_object)
    else:
        if (response == 401):
            print(
                'Login nicht erfolgreich. Status Code 401. Möglicher Grund: falsche Login Daten')
        elif (response == 503):
            print('Überlastung des Servers, bitte warten! Status Code 503: the maximum number of web sessions are active.')
        else:
            print('Login nicht erfolgreich. Fehlermeldung: ', response)


def getDatasFromDashboard(response,switch_json_object):
    # get the values via xpath
    system_model=response.xpath('//td[@id="sys_descr"]/text()')[0].split(",")[0]
    system_name=response.xpath('//input[@id="sys_name"]/@value')
    # insert the data into switch setting object
    switch_json_object['system_model']=system_model
    switch_json_object['system_name']=system_name


def getDatasFromGetConnected(response,switch_json_object):
    # get the values via xpath
    protocol_type=response.xpath('//input[@id="protocol_type_sel_static"]/@checked')
    ip_address=response.xpath('//input[@id="ip_addr"]/@value')
    subnet_mask=response.xpath('//input[@id="subnet_mask"]/@value')
    gateway_address=response.xpath('//input[@id="gateway_address"]/@value')
    mac_address=response.xpath('//td[@id="mac_address"]/text()')
    snmp_enalbed=response.xpath('//input[@id="snmp_sel_enabled"]/@checked')

    # insert the data into switch setting object
    switch_json_object['ip_address']=ip_address[0]
    switch_json_object['subnet_mask']=subnet_mask[0]
    switch_json_object['gateway_address']=gateway_address[0]
    switch_json_object['mac_address']=mac_address[0]
    switch_json_object['snmp_enalbed']=True if len(snmp_enalbed) > 0 and snmp_enalbed[0] in 'checked' else False
    switch_json_object['protocol_type']='Staic' if  len(protocol_type) > 0 and protocol_type[0] in 'checked' else 'DHCP'
    

def getDatasFromPortsVlan(response,switch_json_object):
    response= response.replace('"',"")
    portsresponse= response.split("Port: ")
    i = 1
    formatieret_ports=[]
    # according the response, there are 26 ports
    # insert the data into switch setting object
    while i<=26:
        # split the data string
        einzelPort = portsresponse[i].split("<br>")
        port = {
            "port": einzelPort[0],
            "status": einzelPort[1],
            "autoNeg":  einzelPort[2],
            "link_Speed": einzelPort[3],
            "MTU": einzelPort[4]
        }    
        # every second line is a usefull port line (not a line of usefull information like ",,,") 
        i += 2     
        # append the single port to ports
        formatieret_ports.append(port)

    # insert the data into switch setting object
    switch_json_object['ports']=formatieret_ports


def getDatasFromPortMirror(response,switch_json_object):
    # get the script text, because the values and data are in the script text
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')
    port_mirrors=[]
    # print(dataLines)
    # if there is a mirror port, tehre will be more than 2 lines
    if len(dataLines)>2:
        i = 1
        while i < len(dataLines):
            values={}
            values.update({dataLines[i].split(">")[1].split(",")[1].replace("'",""):dataLines[i].split(">")[1].split(",")[2].split("]")[0].replace("'","")})
            port_mirrors.append(values)
            i+=2
       
        destination_port={
            # get the destination_port with xpath
            "destination_port":response.xpath('//option[@selected="selected"]/text()')[0],
            # insert the mirorred ports which i got from script text
            "mirorred_port":port_mirrors
        }
         
        # insert the data into switch setting object
        switch_json_object['port_mirrors']=destination_port


def getDatasFromJumbpFrame(response,switch_json_object):
    # get the values via xpath
    # insert the data into switch setting object
    jumbo_frames_enabled=response.xpath('//input[@id="jumbo_frames_mode_sel_enabled"]/@checked')
    switch_json_object['jumbo_frames']='enabled' if len(jumbo_frames_enabled) > 0 and jumbo_frames_enabled in 'checked' else 'disabled'


def getDatasFromFlowControl(response,switch_json_object):
    # get the values via xpath
    # insert the data into switch setting object
    flow_control_enabled=response.xpath('//input[@id="flow_control_mode_sel_enabled"]/@checked')
    switch_json_object['flow_control']='enabled' if len(flow_control_enabled) > 0 and flow_control_enabled in 'checked' else 'disabled'


def getDatasFromRemoteDevice(response,switch_json_object):
    # get the script text, because the values and data are in the script text
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')

    remote_devices=[]
    # if there is a remote device, tehre will be more than 2 lines
    if len(dataLines)>2:
        i = 1
        # get the values from script text
        while i < len(dataLines):
            values={}
            datas=dataLines[i].split("[")[1].split("]")[0].replace("'","").split(",")
            values.update({
                    "interface":datas[0],
                    "remoteID":datas[1],
                    "systemID":datas[2],
                    "mac_address":datas[3]
                })
            i+=2
            remote_devices.append(values)

    # insert the data into switch setting object
    switch_json_object['remote_devices']=remote_devices


def getDatasFromLocalDevice(response,switch_json_object):
    # get the script text, because the values and data are in the script text
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')
    local_devices=[]
    # if there is a local device, tehre will be more than 2 lines
    if len(dataLines)>2:
        i = 1
        # get the values from script text
        while i < len(dataLines):
            values={}
            datas=dataLines[i].split("[")[2].split("]")[1].replace("'","").split(",")
            values.update({
                    "Interface":datas[1],
                    "PortID":datas[2],
                })
            i+=2
            local_devices.append(values)

        # insert the data into switch setting object
        switch_json_object['local_devices']=local_devices