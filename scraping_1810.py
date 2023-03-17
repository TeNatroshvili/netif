from selenium.webdriver.common.by import By
from selenium import webdriver
from lxml import html
import requests
import time
from mongodb import save_settings_to_db
from login_credentials import switch_login_credentials

def getDataFromPorts(session, url, cookies, switch_json_object):
    response = session.get(url, cookies=cookies)
    if response.status_code == 200:
        print('Login erfolgreich')
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

def scrap_switch_1810(switch_url):
    session = requests.Session()
    response = session.post('http://'+switch_url+'/config/login', data=switch_login_credentials["password"])
    seid_cookie = session.cookies.get_dict()
    switch_json_object = {}
    seid_cookie_str = '; '.join([f'{key}={value}' for key, value in seid_cookie.items()])
    cookies = {'seid': seid_cookie_str, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}

    
    response=session.get("http://"+switch_url+"/update/config/ip_config",cookies=cookies)
    print(response.content)
    datas = response.content.decode("utf-8").split("/")
    switch_json_object['ip_address']=datas[1]
    switch_json_object['subnet_mask']=datas[2]
    switch_json_object['gateway_address']=datas[3]
    switch_json_object['mac_address']=datas[4].split(",")[0]



    response=session.get("http://"+switch_url+"/update/config/sysinfo",cookies=cookies)
    print(response.content)
    datas = response.content.decode("utf-8").split("/")
    switch_json_object['system_model']=datas[0].split(",")[0]
   

    response=session.get("http://"+switch_url+"/stat/trunk_status?sid=-1",cookies=cookies)
    print(response.content)



    response=session.get("http://"+switch_url+"/update/config/mirroring?sid=-1",cookies=cookies)
    print(response.content)
    datas = response.content.decode("utf-8").split(",")["|"][1].split(",")
    # for data in datas:
    #     port_mirror={

    #     }

    # response=session.get("http://"+switch_url+"/config/flow_ctrl?sid=-1",cookies=cookies)
    # print(response.content)

    response=session.get("http://"+switch_url+"/config/jumbo?sid=-1",cookies=cookies)
    print(response.content)
    data = response.content.decode("utf-8").split(",")["|"][0]
    switch_json_object['jumbo_frames']='enabled' if len(data) == 1 else 'disabled'

    response=session.get("http://"+switch_url+"/config/lldp_neighbors?sid=-1",cookies=cookies)
    print(response.content)
    datas = response.content.decode("utf-8").split(",")["|"][0]

scrap_switch_1810("10.137.4.42")

 # driver = webdriver.Chrome()
    # driver.get('http://'+switch_url+'/login.htm')
    # print(driver)
    # password_input = driver.find_element(By.XPATH, './/input[@id="passwd"]')
    # password_input.send_keys(switch_login_credentials["password"])
    # login_button = driver.find_element(By.XPATH, './/input[@id="login"]')
    # login_button.click()

    # switch_json_object = {}
    # time.sleep(3)
    # frame_address = "home_sysinfo_config.htm"
    # elements_name = ["system_model", "system_name"]
    # elements_type = [By.CLASS_NAME, By.ID]
    # elements_find = ['cl', 'sys_name']
    # elements_value = ["text", "value"]
    # get_data(driver, frame_address, elements_name, elements_type,
    #          elements_find, elements_value, switch_json_object, 1)

    # frame_address = "basic_switch_setup_ip_config.htm"
    # elements_name = ["ip_address", "subnet_mask",
    #                  "gateway_address", "mac_address"]
    # elements_type = [By.ID, By.ID, By.ID, By.CLASS_NAME]
    # elements_find = ['ip_addr', 'ip_mask', 'gateway_addr', 'cl']
    # elements_value = ["value", "value", "value", "text"]
    # get_data(driver, frame_address, elements_name, elements_type,
    #          elements_find, elements_value, switch_json_object, 2)

    # # frame_address="flow_control_flow_ctrl.htm"
    # # elements_name=["flow_control"]
    # # elements_type=[By.ID]
    # # elements_find=['flow_ctrl_mode']
    # # elements_value=["check"]
    # # get_data(driver,frame_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,0)

    # seid_cookie = driver.get_cookies()[1]['value']
    # cookies = {'seid': seid_cookie, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}
    # session = requests.Session()
    # print(switch_json_object)
    # getDataFromPorts(session, "http://"+switch_url +
    #                  "/update/stat/ports?sid=-1", cookies, switch_json_object)
    # getDataFromTrunks(session,"http://10.137.4.45/stat/trunk_status?sid=-1",cookies,switch_json_object)
    # getDataFromPortMirrors(session,"http://10.137.4.45/update/config/mirroring?sid=-1",cookies,switch_json_object)
    # driver.switch_to.frame("links")
    # logout_button= driver.find_elements(By.XPATH, './/a[@class="links_style"]')[2]
    # logout_button.click()
    # print(switch_json_object)
    #save_settings_to_db(switch_json_object)

# def get_data(driver, frame_html_address, elements_name, elements_type, elements_find, elements_value, switch_json_object, help):
#   #  time.sleep(0.001)
#     frameset = driver.find_element(By.ID, "contents")
#     driver.switch_to.frame(frameset)

#     switch_site_button = driver.find_element(By.ID, frame_html_address)
#     switch_site_button.click()
#     driver.switch_to.default_content()
#     time.sleep(0.1)

#     driver.switch_to.parent_frame()
#     driver.switch_to.frame("main")
#     for element, type, find, value in zip(elements_name, elements_type, elements_find, elements_value):
#         name = element
#         element = driver.find_element(type, find)
#         match value:
#             case "text": switch_json_object[name] = element.text
#             case "value": switch_json_object[name] = element.get_attribute("value")

#             #  switch_json_object[name]=element.get_attribute("checked")

#     #driver.switch_to.default_content()
#     driver.switch_to.parent_frame()



