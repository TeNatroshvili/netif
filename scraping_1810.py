import requests

from mongodb import save_settings_to_db, get_switch_credentials

# ------------------------------------
# interface to the Scraping for 1810 Switch
# ------------------------------------
# author:   Chen Junbo
# created:  2023-02-14
# version:  1.0
# ------------------------------------
def scrap_switch_1810(switch_url):
    #first a session is created for all the scraping
    session = requests.Session()
    response = session.post('http://'+switch_url+'/config/login', data=get_switch_credentials()["password"])
    seid_cookie = session.cookies.get_dict()
    seid_cookie_str = '; '.join([f'{key}={value}' for key, value in seid_cookie.items()])
    cookies = {'seid': seid_cookie_str, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

    # final switch setting object, which will inserted into mongDB
    switch_json_object = {}

    # -------------------------------------------------------
    # Scrape the datas from website ip/config
    response=session.get("http://"+switch_url+"/update/config/ip_config",cookies=cookies)
    datas = response.content.decode("utf-8").split("/")
    # insert the data into switch setting object
    switch_json_object['ip_address']=datas[1]
    switch_json_object['subnet_mask']=datas[2]
    switch_json_object['gateway_address']=datas[3]
    switch_json_object['mac_address']=datas[4].split(",")[0]
    switch_json_object['snmp_enalbed'] = datas[6].split(",")[1] == '1' if len(datas) == 8 else datas[7].split(",")[1] == '1' 


    # -------------------------------------------------------
    # Scrape the datas from website config/sysinfo 
    response=session.get("http://"+switch_url+"/update/config/sysinfo",cookies=cookies)
    datas = response.content.decode("utf-8").split("/")
    # insert the data into switch setting object
    switch_json_object['system_model']=datas[0].split(",")[0]
    switch_json_object['system_name']=datas[1]
    
    # -------------------------------------------------------
    # Scrape the datas from website config/mirroring
    response=session.get("http://"+switch_url+"/update/config/mirroring?sid=-1",cookies=cookies)
    datas = response.content.decode("utf-8").split("|")
    datas=response.content.decode("utf-8").split("|")
    port_mirrors=[]
    # get the destination port for mirroring
    destinationport={
        "destination_port":datas[0].split(",")[1]
    }
    # get another port and their directions for mirroring
    for data in datas[1].split(",CPU")[0].split(","):
        data=data.split("/")
        if(data[1] == '1' and data[2] =='1'):
             mirror_status="TX/RX"
        elif data[1]=='1':
            mirror_status="RX"
        elif data[2]=='1':
            mirror_status="TX"
        else:
            continue
        port_mirror={
            data[0]:mirror_status
        }
        port_mirrors.append(port_mirror)

    # append the ports and their directions to destination_port
    destinationport={
        "destination_port":datas[0].split(",")[1],
        "mirorred_port":port_mirrors
    }

    # insert the data into switch setting object
    switch_json_object['port_mirrors']=destinationport
    switch_json_object["port_mirroring"]="enabled" if datas[0].split(",")[3]==1 else "disabled"

    # -------------------------------------------------------
    # Scrape the datas from website /config/jumbo
    response=session.get("http://"+switch_url+"/config/jumbo?sid=-1",cookies=cookies)
    data = response.content.decode("utf-8")
    switch_json_object['jumbo_frames']='enabled' if len(data) == 1 else 'disabled'

    # -------------------------------------------------------
    # Scrape the flow_control datas from website lldp_neighbors
    response=session.get("http://"+switch_url+"/config/lldp_neighbors?sid=-1",cookies=cookies)
    data = response.content.decode("utf-8")
    switch_json_object['flow_control']='enabled' if len(data) == 1 else 'disabled'

    # -------------------------------------------------------
    # Scrape the port datas from website lldp_neighbors
    getDataFromPorts(session,"http://"+switch_url+"/update/stat/ports?sid=-1",cookies,switch_json_object)
    
    # -------------------------------------------------------
    # Save the Setting into Database
    save_settings_to_db(switch_json_object)
    print(switch_json_object)

def getDataFromPorts(session ,url, cookies,switch_json_object):
    response = session.get(url,cookies=cookies)
    if response.status_code == 200:
        content = response.content.decode("utf-8")
        content = content.split(",")[0].split("|")
        ports = []
        for line in content:
            if (len(line) > 2):
                data = line.split("/")
                port = {
                    "port": data[0],
                    "status": data[1],
                    "autoNeg": data[2],
                    "link_Speed": data[3],
                    "MTU": data[4]
                }
                ports.append(port)
        switch_json_object['ports'] = ports

    save_settings_to_db(switch_json_object)
scrap_switch_1810("10.137.4.45")