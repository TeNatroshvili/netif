
import json

def getDatasFromDashboard(response,switch_json_object):
    system_model=response.xpath('//td[@id="sys_descr"]/text()')[0].split(",")[0]
    system_name=response.xpath('//input[@id="sys_name"]/text()')

    switch_json_object['system_model']=system_model
    switch_json_object['system_name']=system_model

def getDatasFromGetConnected(response,switch_json_object):
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
    
def getDatasFromPortsVlan(response,switch_json_object):
    data = json.loads(response)
    switch_json_object['ports']=data['ports']
    switch_json_object['trunks']=data['trunk']

def getDatasFromPortMirror(response,switch_json_object):
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


        

def getDatasFromJumbpFrame(response,switch_json_object):
    jumbo_frames_enabled=response.xpath('//input[@id="jumbo_frames_mode_sel_enabled"]/@checked')
    switch_json_object['jumbo_frames']='enabled' if len(jumbo_frames_enabled) > 0 and jumbo_frames_enabled in 'checked' else 'disabled'


def getDatasFromFlowControl(response,switch_json_object):
    flow_control_enabled=response.xpath('//input[@id="flow_control_mode_sel_enabled"]/@checked')
    switch_json_object['flow_control']='enabled' if len(flow_control_enabled) > 0 and flow_control_enabled in 'checked' else 'disabled'


def getDatasFromRemoteDevice(response,switch_json_object):
    script= response.xpath('//script/text()')
    dataLines=script[1].split(";")[0].split("aDataSet ")[1].split('\n')
    remote_devices=[]
    if len(dataLines)>2:
        i = 1
        while i < len(dataLines):
            values={}
            datas=dataLines[i].split("[")[1].split("]")[0].replace("'","").split(",")

            values.update({
                    "Interface":datas[0],
                    "RemoteID":datas[1],
                    "SystemID":datas[2]
                })
            i+=2
        remote_devices.append(values)
        switch_json_object['remote_devices']=remote_devices



def getDatasFromLocalDevice(response,switch_json_object):
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