from lxml import html
import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
import time 
from mongoInserter import *



def scrap_switch1810(switch_url):
    driver=webdriver.Chrome()
    driver.get('http://'+switch_url+'/login.htm')
    print(driver)
    password_input = driver.find_element(By.XPATH,'.//input[@id="passwd"]')
    password_input.send_keys('Syp2023hurra')
    login_button = driver.find_element(By.XPATH,'.//input[@id="login"]')
    login_button.click()


    switch_json_object={}

    frame_address="home_sysinfo_config.htm"
    elements_name=["system_model","system_name"]
    elements_type=[By.CLASS_NAME,By.ID]
    elements_find=['cl','sys_name']
    elements_value=["text","value"]
    get_data(driver,frame_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,1)

    frame_address="basic_switch_setup_ip_config.htm"
    elements_name=["ip_address","subnet_mask","gateway_address","mac_address"]
    elements_type=[By.ID,By.ID,By.ID,By.CLASS_NAME]
    elements_find=['ip_addr','ip_mask','gateway_addr','cl']
    elements_value=["value","value","value","text"]
    get_data(driver,frame_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,2)

    # frame_address="flow_control_flow_ctrl.htm"
    # elements_name=["flow_control"]
    # elements_type=[By.ID]
    # elements_find=['flow_ctrl_mode']
    # elements_value=["check"]
    #get_data(driver,frame_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,0)

    seid_cookie = driver.get_cookies()[1]['value']
    cookies={'seid':seid_cookie, 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
    session = requests.Session()
    getDataFromPorts(session,"http://"+switch_url+"/update/stat/ports?sid=-1",cookies,switch_json_object)
    #getDataFromTrunks(session,"http://10.137.4.45/stat/trunk_status?sid=-1",cookies,switch_json_object)
    #getDataFromPortMirrors(session,"http://10.137.4.45/update/config/mirroring?sid=-1",cookies,switch_json_object)
    save_to_db(switch_json_object)



def get_data(driver,frame_html_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,help):
    
    driver.switch_to.frame('contents') 

    switch_site_button = driver.find_element(By.ID,frame_html_address)
    switch_site_button.click()
    driver.switch_to.parent_frame()

    driver.switch_to.frame("main") 
    for element,type,find,value in zip(elements_name,elements_type,elements_find,elements_value):
        name=element
        element=driver.find_element(type,find)
        match value:
            case "text":switch_json_object[name]=element.text
            case "value":switch_json_object[name]=element.get_attribute("value")
        
              #  switch_json_object[name]=element.get_attribute("checked")
    
    driver.switch_to.parent_frame()
    
def getDataFromPorts(session,url,cookies,switch_json_object):
    response=session.get(url, cookies=cookies)
    if response.status_code == 200:
        print('Login erfolgreich')
        content=response.content.decode("utf-8")
        content=content.split(",")[0].split("|")
        ports=[]
        for line in content:
            if(len(line)>2):
                data=line.split("/")
                port={
                    "port":data[0],
                    "status":data[1],
                    "autoNeg":data[2],
                    "link_Speed":data[3],
                    "MTU":data[4]
                }
                ports.append(port)
        switch_json_object['ports']=ports

scrap_switch1810("10.137.4.45")
# def getDataFromTrunks(session,url,cookies,switch_json_object):
#     response=session.get(url, cookies=cookies)
#     if response.status_code == 200:
#         print('Login erfolgreich')
#         content=response.content.decode("utf-8")
#         content=content.split(",")[0].split("|")
#         print(content)
#         ports=[]
#         for line in content:
#             if(len(line)>2):
#                 print(line)
#                 data=line.split("/")
#                 port={
#                     "unit":data[0],
#                     "name":data[2],
#                     # "mode":data[3],
#                     "ports":data[4]
#                 }
#                 ports.append(port)
#         switch_json_object['trunks']=ports

# def getDataFromPortMirrors(session,url,cookies,switch_json_object):
#     response=session.get(url, cookies=cookies)
#     if response.status_code == 200:
#         print('Login erfolgreich')
#         content=response.content.decode("utf-8")
#         content=content.split(",")[0].split("|")
#         print(content)
#         ports=[]
#         for line in content:
#             data=line.split("/")
#             if(len(line)==3 and (data[1]==1 or data[2]==1)):
#                 port={
#                     data[0]:"Rx" if data[1] ==1 and data[2]==0 else ("Tx" if data[1] ==1 and data[2]==0 else " ")
#                     +" "+"Rx" if data[1] ==1 and data[2]==0 else ("Tx" if data[1] ==1 and data[2]==0 else " ")
#                 }
#                 ports.append(port)
#         switch_json_object['port_mirrors']=ports





    # seid_cookie = driver.get_cookies()[1]['value']
    # print(seid_cookie)

    # cookies={'seid':seid_cookie, 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
    # cookie1={'name': 'seid', 'value': seid_cookie, 'path': '/', 'domain': '10.137.4.45'}
    # cookie2={'name': 'deviceid', 'value': 'YWRtaW46U3lwMjAyM2h1cnJh', 'path': '/', 'domain': '10.137.4.45'}
    # driver.add_cookie(cookie1)
    # driver.add_cookie(cookie2)
    # driver.get('http://10.137.4.45/sysinfo_config.htm')
    # time.sleep(3)
    # ele = driver.find_element(By.ID,'sys_name')
    # print(ele.text)
    # #response=session.get('http://10.137.4.35/update/stat/ports?sid=-1', cookies=cookies)
    # #response=session.get('http://10.137.4.45/update/config/sysinfo', cookies=cookies)
    #if response.status_code == 200:
    #     print('Login erfolgreich')
    #     #print(response.content)
        
    #     print(response.content)
    #    # root = html.fromstring(response.content)
    #    # print(root.xpath('//input[@id="sys_name"]/@value'))

    # else:
    #     print('Login down')

    # response=session.get('http://10.137.4.35/update/stat/ports?sid=-1', cookies=cookies)



    # session = requests.Session()
    # cookies={'seid':'127382843', 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
    # session.headers.update(headers)
    # response=session.get('http://10.137.4.35/update/stat/ports?sid=-1',headers=headers, cookies=cookies)
    # if response.status_code == 200:
    #     print('Login erfolgreich')
    #     print(response.content)
    # else:
    #     print('Login down')
