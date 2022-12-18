import scrapy
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time


def getDatasFromSNMPConfPage(response):
    print("SNMPConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    snmpEnabled=scriptText[2].split('"')[1].split('"')[0]
    print(snmpEnabled)

def getDatasFromLLDPConfPage(response):
    print("LLDPConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    lldpEnabledList=scriptText[4].split("(")[1].split(")")[0].split(",")
    print(lldpEnabledList)

def getDatasFromVlanPortConfPage(response):
    print("VlanPortConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    vlanEnabled=scriptText[5].split("(")[1].split(")")[0].split(",")
    packetTypeList=scriptText[6].split("(")[1].split(")")[0].split(",")
    pvidList=scriptText[7].split("(")[1].split(")")[0].split(",")
    ingressFilteringList=scriptText[9].split("(")[1].split(")")[0].split(",")
    print(vlanEnabled)
    print(packetTypeList)
    print(pvidList)
    print(ingressFilteringList)

def getDatasFromLacpSettingPage(response):
    print("lacp_setting-script----------------")
    script=response.xpath('//script/text()')[1].extract()
    scriptText= script.split("var")
    lacpEnabledList=scriptText[6].split("(")[1].split(")")[0].split(",")
    lacpEnabledJKeyvalueList=scriptText[7].split("(")[1].split(")")[0].split(",")
    print(lacpEnabledList)
    print(lacpEnabledJKeyvalueList)


def getDatasFromRateLimitPage(response):
    print("rate_limit-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    rateLimitEnabled=scriptText[7].split("(")[1].split(")")[0].split(",")[1]
    limitIndex=scriptText[6].split("(")[1].split(")")[0].split(",")[2]
    limit=scriptText[3].split("(")[1].split(")")[0].split(",")[int(limitIndex)]
    print(rateLimitEnabled)
    print(limit)


def getDatasFromPortConfigurationPage(response):
    print("port_config-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    jumbo_enabled=scriptText[6].split("(")[1].split(")")[0].split(",")
    if not bool(jumbo_enabled):
        jumbo_enabled="checked"
    else:
        jumbo_enabled="unchecked"
    print(jumbo_enabled)

def getDatasFromPortsMirrorPage(response):
    print("port_mirror-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    port_to_mirror_to=scriptText[1].split('"')[1].split('"')[0]
    ports_to_mirrorList=scriptText[2].split("(")[1].split(")")[0].split(",")
    print(port_to_mirror_to)
    print(ports_to_mirrorList)

def getDatasFromInformationPage(response):
                print("infomation-script----------------")
                script=response.xpath('//script/text()')[0].extract()
                scriptText= script.split("var")
                 
               # linksStatusList=scriptText[3].split("(").split
                system_name=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[2]/td[2]/text()').extract()
                serial_number=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[8]/td[2]/text()').extract()
                ip_adresse=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[12]/td[2]/text()').extract()
                subnet_mask=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[13]/td[2]/text()').extract()
                gateway_ip=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[14]/td[2]/text()').extract()
                mac_adreese=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[15]/td[2]/text()').extract()
                print(system_name," ", serial_number," ",ip_adresse," ",
                subnet_mask," ",gateway_ip," ",mac_adreese)
               
                linksStatusList=scriptText[4].split("(")[1].split(")")[0].split(",")
                portsSpeedList=scriptText[5].split("(")[1].split(")")[0].split(",")
                flowControlStatusList=scriptText[6].split("(")[1].split(")")[0].split(",")
                autoNegotiationList=scriptText[7].split("(")[1].split(")")[0].split(",")
                frameTypeList=scriptText[8].split("(")[1].split(")")[0].split(",")
                pvidList=scriptText[9].split("(")[1].split(")")[0].split(",")
                trunkNameList=scriptText[10].split("(")[1].split(")")[0].split(",")
                trunkMemberList=scriptText[11].split("(")[1].split(")")[0].split(",")
                
                print(linksStatusList)
                print(portsSpeedList)
                print(flowControlStatusList)
                print(autoNegotiationList)
                print(frameTypeList)
                print(pvidList)
                print(trunkNameList)
                print(trunkMemberList)

class DemoySpider(scrapy.Spider):
    name = 'NetIF'
   # allowed_domains = ['www.youtube.com']
    
 #  start_urls = ['http://10.128.10.19/status/status_ov.html']
    
       

    def start_requests(self):
        urls = ['http://10.128.10.19/status/status_ov.html',
                'http://10.128.10.19/ports/ports_bsc.html',
                'http://10.128.10.19/ports/ports_config.html',
                'http://10.128.10.19/ports/ports_mir.html',
                'http://10.128.10.19/trunks/lacp.html',
                'http://10.128.10.19/vlans/vlan_pconf.html',
                'http://10.128.10.19/vlans/vlan_mconf.html',
                'http://10.128.10.19/lldp/lldpconf.html',
                'http://10.128.10.19/system/system_snmp.html'
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def __init__(self): 
        print("hehrere")
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-authmation'])
        ser = Service("./chromedriver.exe")
        self.bro = webdriver.Chrome(options=option,service=ser)
    
    

    def parse(self, response):
        page_title=response.xpath('//td[@class="page_title"]/text()')[0].extract()
        print(page_title)
        match page_title:
            case "System Information":
                getDatasFromInformationPage(response)
            case "Rate Limits":
                getDatasFromRateLimitPage(response)
            case "Port Configuration":
                getDatasFromPortConfigurationPage(response)
            case "Port Mirroring":
                getDatasFromPortsMirrorPage(response)
            case "LACP Setting":
                getDatasFromLacpSettingPage(response)
            case "802.1Q Per Port Configuration":
                getDatasFromVlanPortConfPage(response)
            case "LLDP Configuration":
                getDatasFromLLDPConfPage(response)
            case "SNMP Configuration":
                getDatasFromSNMPConfPage(response)
                


    


        





        
        # #print(response.xpath('//td'))
        # print("parse")
        # print("menuFrame")
        # print(response.xpath('//html/frameset/frame[@name="menuFrame"]')[0])
        # print("mainFrame")
        # frame_url=response.xpath('//html/frameset/frame[@name="mainFrame"]')
        # print(frame_url)
        # print(frame_url.xpath('//tr'))
        # print(self)
        # yield scrapy.Request(frame_url,callback=self.parse_frame)
    
    # def parse_frame(self,response):

    #     print(response.xpath("//"))
    #     print("ok")
    #     print(response.xpath("//div"))



# Test Version-----------------------------
# import scrapy
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from time import sleep

# from selenium.webdriver.chrome.service import Service


# class DemoySpider(scrapy.Spider):
#     name = 'NetIF'
#     allowed_domains = ['www.youtube.com']
#     start_urls = ['https://www.youtube.com/']

#     def __init__(self):  # Initialisieren eines Browsers

#         option = webdriver.ChromeOptions()
#         option.add_experimental_option('excludeSwitches', ['enable-authmation'])
#         ser = Service("./chromedriver.exe")

#         self.bro = webdriver.Chrome(options=option,service=ser)

#     def parse(self, response):
#         sleep(1)
#        # print(response.xpath('./'))
#         print("jjojo")
#         found_videos = response.xpath('//div[@class="text-wrapper style-scope ytd-video-renderer"]')
#         for found_vid in found_videos:
#             title = found_vid.xpath('./div[@id="meta"]//h3/a/@title')[0].extract()
#             watched_times = found_vid.xpath('./div[@id="meta"]//div[@id="metadata-line"]//span[1]/text()')[0].extract()
#             upload_time = found_vid.xpath('./div[@id="meta"]//div[@id="metadata-line"]//span[2]/text()')[0].extract()
#             producer = found_vid.xpath('./div[@id="channel-info"]//div[@id="text-container"]//a/text()')[0].extract()

#             print("Found a vid -------------------------------------")
#             print("Title: ", title, " -", watched_times, " Views", upload_time, " ")
#             print("producer: ", producer,"\n")


    # old version -----
        # recommend_list = response.xpath('//div[@id="contents"]//div[@id="content"]//div[@class="style-scope ytd-rich-grid-media"]//div[@id="details"]')

        # for div in recommend_list:
        # print(div)
        # print("ok - content")
        # print()
        # author = div.xpath('./div[@id="meta"]/h3/a/@title')[0].extract()
        # print(author)
