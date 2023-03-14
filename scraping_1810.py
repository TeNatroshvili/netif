from selenium.webdriver.common.by import By
from selenium import webdriver
from lxml import html
import requests

from mongodb import save_settings_to_db
from login_credentials import switch_login_credentials


def scrap_switch_1810(switch_url):
    driver = webdriver.Chrome()
    driver.get('http://'+switch_url+'/login.htm')
    print(driver)
    password_input = driver.find_element(By.XPATH, './/input[@id="passwd"]')
    password_input.send_keys(switch_login_credentials["password"])
    login_button = driver.find_element(By.XPATH, './/input[@id="login"]')
    login_button.click()

    switch_json_object = {}

    frame_address = "home_sysinfo_config.htm"
    elements_name = ["system_model", "system_name"]
    elements_type = [By.CLASS_NAME, By.ID]
    elements_find = ['cl', 'sys_name']
    elements_value = ["text", "value"]
    get_data(driver, frame_address, elements_name, elements_type,
             elements_find, elements_value, switch_json_object, 1)

    frame_address = "basic_switch_setup_ip_config.htm"
    elements_name = ["ip_address", "subnet_mask",
                     "gateway_address", "mac_address"]
    elements_type = [By.ID, By.ID, By.ID, By.CLASS_NAME]
    elements_find = ['ip_addr', 'ip_mask', 'gateway_addr', 'cl']
    elements_value = ["value", "value", "value", "text"]
    get_data(driver, frame_address, elements_name, elements_type,
             elements_find, elements_value, switch_json_object, 2)

    # frame_address="flow_control_flow_ctrl.htm"
    # elements_name=["flow_control"]
    # elements_type=[By.ID]
    # elements_find=['flow_ctrl_mode']
    # elements_value=["check"]
    # get_data(driver,frame_address,elements_name,elements_type,elements_find,elements_value,switch_json_object,0)

    seid_cookie = driver.get_cookies()[1]['value']
    cookies = {'seid': seid_cookie, 'deviceid': 'YWRtaW46U3lwMjAyM2h1cnJh'}
    session = requests.Session()
    getDataFromPorts(session, "http://"+switch_url +
                     "/update/stat/ports?sid=-1", cookies, switch_json_object)
    # getDataFromTrunks(session,"http://10.137.4.45/stat/trunk_status?sid=-1",cookies,switch_json_object)
    # getDataFromPortMirrors(session,"http://10.137.4.45/update/config/mirroring?sid=-1",cookies,switch_json_object)
    save_settings_to_db(switch_json_object)


def get_data(driver, frame_html_address, elements_name, elements_type, elements_find, elements_value, switch_json_object, help):

    driver.switch_to.frame('contents')

    switch_site_button = driver.find_element(By.ID, frame_html_address)
    switch_site_button.click()
    driver.switch_to.parent_frame()

    driver.switch_to.frame("main")
    for element, type, find, value in zip(elements_name, elements_type, elements_find, elements_value):
        name = element
        element = driver.find_element(type, find)
        match value:
            case "text": switch_json_object[name] = element.text
            case "value": switch_json_object[name] = element.get_attribute("value")

            #  switch_json_object[name]=element.get_attribute("checked")

    driver.switch_to.parent_frame()


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