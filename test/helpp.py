
import requests


session = requests.Session()
cookies={'SID':'ysgbmWQGQYaJKsBRtxUVswCblHjqzchXuQYHMrnepQOBipsdomBjkdMvmVLLXvIsljBzAOErgUS'}
response=session.get('http://10.137.4.33/htdocs/lua/deviceviewer/deviceviewer_status.lua?unit=1&ports%5B%5D=1&ports%5B%5D=2&ports%5B%5D=3&ports%5B%5D=4&ports%5B%5D=5&ports%5B%5D=6&ports%5B%5D=7&ports%5B%5D=8&ports%5B%5D=9&ports%5B%5D=10&ports%5B%5D=11&ports%5B%5D=12&ports%5B%5D=13&ports%5B%5D=14&ports%5B%5D=15&ports%5B%5D=16&ports%5B%5D=17&ports%5B%5D=18&ports%5B%5D=19&ports%5B%5D=20&ports%5B%5D=21&ports%5B%5D=22&ports%5B%5D=23&ports%5B%5D=24&ports%5B%5D=25&ports%5B%5D=26&leds%5B%5D=power&leds%5B%5D=locator&leds%5B%5D=fault&_=1677508306011',cookies=cookies)
if response.status_code == 200:
    print('Login erfolgreich')
    print(response.content)
else:
    print('Login down')

    #response=session.get('http://10.137.4.35/config/sntp_config', cookies=cookies)





# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
#     #'Referer': 'http://10.137.4.35/login.htm',
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'If-Modified-Since': '0'
# }
# session = requests.Session()
# cookies={'seid':'127382843', 'deviceid':'YWRtaW46U3lwMjAyM2h1cnJh'}
# session.headers.update(headers)
# response=session.get('http://10.137.4.35/update/stat/ports?sid=-1',headers=headers, cookies=cookies)
# if response.status_code == 200:
#     print('Login erfolgreich')
#     print(response.content)
# else:
#     print('Login down')
