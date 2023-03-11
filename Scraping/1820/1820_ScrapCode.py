import requests
from extractMethods import *
from lxml import html

from mongoInserter import *



def scrap_switch(swtich_ip_adresse):
      urls=['http://'+swtich_ip_adresse+'/htdocs/pages/base/dashboard.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/network_ipv4_cfg.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/lua/deviceviewer/deviceviewer_status.lua?unit=1&ports%5B%5D=1&ports%5B%5D=2&ports%5B%5D=3&ports%5B%5D=4&ports%5B%5D=5&ports%5B%5D=6&ports%5B%5D=7&ports%5B%5D=8&ports%5B%5D=9&ports%5B%5D=10&ports%5B%5D=11&ports%5B%5D=12&ports%5B%5D=13&ports%5B%5D=14&ports%5B%5D=15&ports%5B%5D=16&ports%5B%5D=17&ports%5B%5D=18&ports%5B%5D=19&ports%5B%5D=20&ports%5B%5D=21&ports%5B%5D=22&ports%5B%5D=23&ports%5B%5D=24&ports%5B%5D=25&ports%5B%5D=26&leds%5B%5D=power&leds%5B%5D=locator&leds%5B%5D=fault&_=1677577757505',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/port_mirror.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/jumbo_frames.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/base/switch_config.lsp',
      #  'http://10.137.4.41/htdocs/pages/switching/vlan_status.lsp',
      #  'http://10.137.4.41/htdocs/pages/switching/vlan_port.lsp',
            #'http://10.137.4.41/htdocs/pages/switching/port_channel_summary.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/switching/lldp_med_local.lsp',
            'http://'+swtich_ip_adresse+'/htdocs/pages/switching/lldp_remote.lsp'
      # 'http://10.137.4.41/htdocs/pages/switching/lldp_stats.lsp'
            ]
      session = requests.Session()

      response = session.post('http://'+swtich_ip_adresse+'/htdocs/login/login.lua', data={"username":"admin","password":"Syp2023hurra"})
      cookie=session.cookies.get_dict()

      #If login works 
      if response.status_code == 200:
            print('Login erfolgreich')
            switch_json_object={}
            for url in urls:
            #  if (url == urls[0] or url == urls[6]):
                  response=session.get(url,cookies=cookie)
                  if (cookie != {} and response.status_code ==200):
                        print('Scraping für:', url)
                        print('-------------------------------------------')

                        if("deviceviewer_status.lua" in url):
                              page_title="ports_vlan_status"
                        else:
                              root = html.fromstring(response.content)
                              page_title=root.xpath('//title/text()')[0]

                        match page_title:
                              case "Get Connected":
                                    getDatasFromGetConnected(root,switch_json_object)
                              case "Dashboard":
                                    getDatasFromDashboard(root,switch_json_object)
                              case "ports_vlan_status":
                                    getDatasFromPortsVlan(response.content.decode("utf-8"),switch_json_object)
                              case "Port Mirroring":
                                    getDatasFromPortMirror(root,switch_json_object)
                              case "Jumbo Frames Configuration":
                                    getDatasFromJumbpFrame(root,switch_json_object)
                              case "Flow Control Configuration":
                                    getDatasFromFlowControl(root,switch_json_object)
                              case "LLDP-MED Local Device Summary":
                                    getDatasFromLocalDevice(root,switch_json_object)
                              case "LLDP Remote Device Summary":
                                    getDatasFromRemoteDevice(root,switch_json_object)
                        
                  elif (cookie == {}):
                        print("Fehler beim Scrapen der Daten von ",url)
                        print("Möglicher Grund: Session key ist abgelaufen, neues Key erfoderlich")
                  elif (cookie == 503):
                        print('Überlastung des Servers, bitte warten! Status Code 503')
                  else:
                        print("Fehler beim Scrapen der Daten von ",url)
                        print("Statuscode: ", response)

            # Logout
            session.get("http://"+swtich_ip_adresse+"/htdocs/pages/main/logout.lsp", cookies=session.cookies.get_dict())
            session.close()
            save_to_db(switch_json_object)
      else:
            if(response == 401):
                  print('Login nicht erfolgreich. Status Code 401. Möglicher Grund: falsche Login Daten')
            elif(response == 503):
                  print('Überlastung des Servers, bitte warten! Status Code 503: the maximum number of web sessions are active.')
            else:
                  print('Login nicht erfolgreich. Fehlermeldung: ',response)


# scrap_switch("10.137.4.33")

