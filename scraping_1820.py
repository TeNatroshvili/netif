from lxml import html
import requests
import threading
import multiprocessing
import time

from mongodb import save_settings_to_db
from login_credentials import switch_login_credentials


def scrap_switch_1820(swtich_ip_adresse):
        print("inseide")
        st = time.time()
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
        session = requests.Session()

        response = session.post('http://'+swtich_ip_adresse+'/htdocs/login/login.lua',
                                data=switch_login_credentials)
        cookie = session.cookies.get_dict()

        # If login works
        if response.status_code == 200:
            print('Login erfolgreich')
            switch_json_object = {}
            pool = multiprocessing.Pool(8)
            results = []

            for url in urls:
            #if (url == urls[0] or url == urls[2]):
                response = session.get(url, cookies=cookie)
                print("sad")
                print(response)
                if (cookie != {} and response.status_code == 200):
                    print('Scraping für:', url)
                    print('-------------------------------------------')

                    
                    if ("deviceviewer_status.lua" in url):
                        page_title = "ports_vlan_status"
                    else:
                        root = response.content
                        page_title = response = html.fromstring(root).xpath('//title/text()')[0]

                    match page_title:
                        case "Get Connected":
                            results.append(pool.apply_async(getDatasFromGetConnected,(root,)))
                            
                        case "Dashboard":
                            results.append(pool.apply_async(getDatasFromDashboard,(root,)))
                            
                        case "ports_vlan_status":
                            results.append(pool.apply_async(getDatasFromPortsVlan,(response.content.decode("utf-8"),)))
                            
                        case "Port Mirroring":
                            results.append(pool.apply_async(getDatasFromPortMirror,(root,)))
                            
                        case "Jumbo Frames Configuration":
                            results.append(pool.apply_async(getDatasFromJumbpFrame,(root,)))
                            
                        case "Flow Control Configuration":
                            results.append(pool.apply_async(getDatasFromFlowControl,(root,)))
                            
                        case "LLDP-MED Local Device Summary":
                            results.append(pool.apply_async(getDatasFromLocalDevice,(root,)))
                            
                        case "LLDP Remote Device Summary":
                            results.append(pool.apply_async(getDatasFromRemoteDevice,(root,)))
                            
                elif (cookie == {}):
                    print("Fehler beim Scrapen der Daten von ", url)
                    print(
                        "Möglicher Grund: Session key ist abgelaufen, neues Key erfoderlich")
                elif (cookie == 503):
                    print('Überlastung des Servers, bitte warten! Status Code 503')
                else:
                    print("Fehler beim Scrapen der Daten von ", url)
                    print("Statuscode: ", response)

            
            pool.close()
            # Logout
            session.get("http://"+swtich_ip_adresse +
                        "/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
            session.close()
            
            pool.join()
            et = time.time()
            print('Execution time:', et-st, 'seconds')
            for result in results:
                switch_json_object.update(result.get())
            save_settings_to_db(switch_json_object)

        else:
            if (response == 401):
                print(
                    'Login nicht erfolgreich. Status Code 401. Möglicher Grund: falsche Login Daten')
            elif (response == 503):
                print('Überlastung des Servers, bitte warten! Status Code 503: the maximum number of web sessions are active.')
            else:
                print('Login nicht erfolgreich. Fehlermeldung: ', response)




def getDatasFromDashboard(response):
    switch_json_object = {}
    response = html.fromstring(response)
    system_model=response.xpath('//td[@id="sys_descr"]/text()')[0].split(",")[0]
    system_name=response.xpath('//input[@id="sys_name"]/@value')

    switch_json_object['system_model']=system_model
    switch_json_object['system_name']=system_name
    return switch_json_object


def getDatasFromGetConnected(response):
    switch_json_object = {}
    response = html.fromstring(response)
    protocol_type=response.xpath('//input[@id="protocol_type_sel_static"]/@checked')
    ip_address=response.xpath('//input[@id="ip_addr"]/@value')
    subnet_mask=response.xpath('//input[@id="subnet_mask"]/@value')
    gateway_address=response.xpath('//input[@id="gateway_address"]/@value')
    mac_address=response.xpath('//td[@id="mac_address"]/text()')
    snmp_enalbed=response.xpath('//input[@id="snmp_sel_enabled"]/@checked')

    switch_json_object['ip_address']=ip_address[0]
    switch_json_object['subnet_mask']=subnet_mask[0]
    switch_json_object['gateway_address']=gateway_address[0]
    switch_json_object['mac_address']=mac_address[0]
    switch_json_object['snmp_enalbed']=True if len(snmp_enalbed) > 0 and snmp_enalbed[0] in 'checked' else False
    switch_json_object['protocol_type']='Staic' if  len(protocol_type) > 0 and protocol_type[0] in 'checked' else 'DHCP'
    return switch_json_object
    

def getDatasFromPortsVlan(response):
    switch_json_object = {}
    response= response.replace('"',"")
    portsresponse= response.split("Port: ")
    i = 1
    formatieret_ports=[]
    while i<=26:
        einzelPort = portsresponse[i].split("<br>")
        port = {
            "port": einzelPort[0],
            "status": einzelPort[1],
            "autoNeg":  einzelPort[2],
            "link_Speed": einzelPort[3],
            "MTU": einzelPort[4]
        }    
        i += 2     
        formatieret_ports.append(port)

    
    switch_json_object['ports']=formatieret_ports
    return switch_json_object


def getDatasFromPortMirror(response):
    switch_json_object = {}
    response = html.fromstring(response)
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')
    port_mirrors=[]
    if len(dataLines)>2:
        i = 1
        while i < len(dataLines):
            values={}
            values.update({dataLines[i].split(">")[1].split(",")[1].replace("'",""):dataLines[i].split(">")[1].split(",")[2].split("]")[0].replace("'","")})
            port_mirrors.append(values)
            i+=2

        switch_json_object['port_mirrors']=port_mirrors
    return switch_json_object


def getDatasFromJumbpFrame(response):
    switch_json_object = {}
    response = html.fromstring(response)
    jumbo_frames_enabled=response.xpath('//input[@id="jumbo_frames_mode_sel_enabled"]/@checked')
    switch_json_object['jumbo_frames']='enabled' if len(jumbo_frames_enabled) > 0 and jumbo_frames_enabled in 'checked' else 'disabled'
    return switch_json_object


def getDatasFromFlowControl(response):
    switch_json_object = {}
    response = html.fromstring(response)
    flow_control_enabled=response.xpath('//input[@id="flow_control_mode_sel_enabled"]/@checked')
    switch_json_object['flow_control']='enabled' if len(flow_control_enabled) > 0 and flow_control_enabled in 'checked' else 'disabled'
    return switch_json_object


def getDatasFromRemoteDevice(response):
    switch_json_object = {}
    response = html.fromstring(response)
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')

    remote_devices=[]
    if len(dataLines)>2:
        i = 1
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
    switch_json_object['remote_devices']=remote_devices
    return switch_json_object


def getDatasFromLocalDevice(response):
    switch_json_object = {}
    response = html.fromstring(response)
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')
    local_devices=[]
    if len(dataLines)>2:
        i = 1
        while i < len(dataLines):
            values={}
            datas=dataLines[i].split("[")[2].split("]")[1].replace("'","").split(",")
            values.update({
                    "Interface":datas[1],
                    "PortID":datas[2],
                })
            i+=2
            local_devices.append(values)
        switch_json_object['local_devices']=local_devices
    return switch_json_object