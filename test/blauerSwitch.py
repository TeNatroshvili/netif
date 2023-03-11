import requests

urls=['http://10.137.4.41/htdocs/pages/base/dashboard.lsp',
      'http://10.137.4.41/htdocs/pages/base/network_ipv4_cfg.lsp',
      'http://10.137.4.41/htdocs/lua/deviceviewer/deviceviewer_status.lua?unit=1&ports%5B%5D=1&ports%5B%5D=2&ports%5B%5D=3&ports%5B%5D=4&ports%5B%5D=5&ports%5B%5D=6&ports%5B%5D=7&ports%5B%5D=8&ports%5B%5D=9&ports%5B%5D=10&ports%5B%5D=11&ports%5B%5D=12&ports%5B%5D=13&ports%5B%5D=14&ports%5B%5D=15&ports%5B%5D=16&ports%5B%5D=17&ports%5B%5D=18&ports%5B%5D=19&ports%5B%5D=20&ports%5B%5D=21&ports%5B%5D=22&ports%5B%5D=23&ports%5B%5D=24&ports%5B%5D=25&ports%5B%5D=26&leds%5B%5D=power&leds%5B%5D=locator&leds%5B%5D=fault&_=1677577757505',
      'http://10.137.4.41/htdocs/pages/base/port_mirror.lsp',
      'http://10.137.4.41/htdocs/pages/base/jumbo_frames.lsp',
      'http://10.137.4.41/htdocs/pages/base/switch_config.lsp',
      'http://10.137.4.41/htdocs/pages/switching/vlan_status.lsp',
      'http://10.137.4.41/htdocs/pages/switching/vlan_port.lsp',
      #'http://10.137.4.41/htdocs/pages/switching/port_channel_summary.lsp',
      'http://10.137.4.41/htdocs/pages/switching/lldp_local.lsp',
      'http://10.137.4.41/htdocs/pages/switching/lldp_remote.lsp',
      'http://10.137.4.41/htdocs/pages/switching/lldp_stats.lsp'
      ]
session = requests.Session()

response = session.post('http://10.137.4.41/htdocs/login/login.lua', data={"username":"admin","password":"Syp2023hurra"})
cookie=session.cookies.get_dict()
response=session.get('http://10.137.4.41/htdocs /lua/deviceviewer/deviceviewer_status.lua?unit=1&ports%5B%5D=1&ports%5B%5D=2&ports%5B%5D=3&ports%5B%5D=4&ports%5B%5D=5&ports%5B%5D=6&ports%5B%5D=7&ports%5B%5D=8&ports%5B%5D=9&ports%5B%5D=10&ports%5B%5D=11&ports%5B%5D=12&ports%5B%5D=13&ports%5B%5D=14&ports%5B%5D=15&ports%5B%5D=16&ports%5B%5D=17&ports%5B%5D=18&ports%5B%5D=19&ports%5B%5D=20&ports%5B%5D=21&ports%5B%5D=22&ports%5B%5D=23&ports%5B%5D=24&ports%5B%5D=25&ports%5B%5D=26&leds%5B%5D=power&leds%5B%5D=locator&leds%5B%5D=fault&_=1677577757505',cookies=cookie)
print(response.content)

print(cookie)
# if response.status_code == 200:
#     print('Login erfolgreich')
#     for url in urls:
        
#         # response = session.post('http://10.137.4.41/htdocs/login/login.lua', data={"username":"admin","password":"Syp2023hurra"})
#         # cookie=session.cookies.get_dict()
#         print('Url: ',url)
#         response=session.get(url,cookies=cookie)
#         print(response)
#     session.close()
# else:
#     print('Login down')
