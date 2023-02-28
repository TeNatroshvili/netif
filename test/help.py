
import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
#     #'Referer': 'http://10.137.4.35/login.htm',

#     'Content-Type': 'application/x-www-form-urlencoded',
#     'If-Modified-Since': '0'
# }
session = requests.Session()
# session.headers.update(headers)
driver=webdriver.Chrome()
driver.get('http://10.137.4.35/login.htm')
print(driver)
password_input = driver.find_element(By.XPATH,'.//input[@id="passwd"]')
password_input.send_keys('Syp2023hurra')
login_button = driver.find_element(By.XPATH,'.//input[@id="login"]')
login_button.click()
seid_cookie = driver.get_cookies()[1]['value']
print(seid_cookie)

cookies={'seid':seid_cookie, 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
response=session.get('http://10.137.4.35/update/stat/ports?sid=-1', cookies=cookies)
if response.status_code == 200:
    print('Login erfolgreich')
    print(response.content)
    response=session.get('http://10.137.4.35/config/sntp_config', cookies=cookies)
    print(response.content)
else:
    print('Login down')



# session = requests.Session()
# cookies={'seid':'127382843', 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
# session.headers.update(headers)
# response=session.get('http://10.137.4.35/update/stat/ports?sid=-1',headers=headers, cookies=cookies)
# if response.status_code == 200:
#     print('Login erfolgreich')
#     print(response.content)
# else:
#     print('Login down')
