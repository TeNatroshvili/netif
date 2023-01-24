import scrapy
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
import requests
import json
from pymongo import MongoClient
import re
import subprocess

def getDatasFromSNMPConfPage(response,switch_json_object):
   # print("SNMPConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    snmpEnabled=scriptText[2].split('"')[1].split('"')[0]
    switch_json_object["snmpEnabled"]=snmpEnabled
    #print(snmpEnabled)

def getDatasFromLLDPConfPage(response,switch_json_object):
   # print("LLDPConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    lldpEnabledList=scriptText[4].split("(")[1].split(")")[0].split(",")
    switch_json_object["lldpEnabledList"]=lldpEnabledList
   # print(lldpEnabledList)

def getDatasFromVlanPortConfPage(response,switch_json_object):
    #print("VlanPortConf-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    vlanEnabled_list=scriptText[5].split("(")[1].split(")")[0].split(",")
    packetTypeList=scriptText[6].split("(")[1].split(")")[0].split(",")
    pvidList=scriptText[7].split("(")[1].split(")")[0].split(",")
    ingressFilteringList=scriptText[9].split("(")[1].split(")")[0].split(",")
    vlanEnabled_list_new= [myL.replace('"', '') for myL in vlanEnabled_list]
    packetTypeList_new= [myL.replace('"', '') for myL in packetTypeList]
    pvidList_new= [myL.replace('"', '') for myL in pvidList]
    ingressFilteringList_new= [myL.replace('"', '') for myL in ingressFilteringList]
    
    switch_json_object["vlanEnabled_list"]=vlanEnabled_list_new
    switch_json_object["packetTypeList"]=packetTypeList_new
    switch_json_object["pvidList"]=pvidList_new
    switch_json_object["ingressFilteringList"]=ingressFilteringList_new
    # print(vlanEnabled)
    # print(packetTypeList)
    # print(pvidList)
    # print(ingressFilteringList)

def getDatasFromLacpSettingPage(response,switch_json_object):
    #print("lacp_setting-script----------------")
    script=response.xpath('//script/text()')[1].extract()
    scriptText= script.split("var")
    lacpEnabledList=scriptText[6].split("(")[1].split(")")[0].split(",")
    lacpEnabledJKeyvalueList=scriptText[7].split("(")[1].split(")")[0].split(",")
    lacpEnabledList_new =  [myL.replace('"', '') for myL in lacpEnabledList]
    lacpEnabledJKeyvalueList_new =  [myL.replace('"', '') for myL in lacpEnabledJKeyvalueList]
    switch_json_object["lacpEnabledList"]=lacpEnabledList_new
    switch_json_object["lacpEnabledJKeyvalueList"]=lacpEnabledJKeyvalueList_new
    #print(lacpEnabledList)
    #print(lacpEnabledJKeyvalueList)


def getDatasFromRateLimitPage(response,switch_json_object):
    #print("rate_limit-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    rateLimitEnabled=scriptText[7].split("(")[1].split(")")[0].split(",")[1]
    limitIndex=scriptText[6].split("(")[1].split(")")[0].split(",")[2]
    limit=scriptText[3].split("(")[1].split(")")[0].split(",")[int(limitIndex)]

    switch_json_object["rateLimitEnabled"]=rateLimitEnabled
    switch_json_object["limit"]=limit.replace('"', '')
    # print(rateLimitEnabled)
    # print(limit)


def getDatasFromPortConfigurationPage(response,switch_json_object):
   # print("port_config-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    jumbo_enabled=scriptText[6].split("(")[1].split(")")[0].split(",")
    if not bool(jumbo_enabled):
        jumbo_enabled="checked"
    else:
        jumbo_enabled="unchecked"
    #print(jumbo_enabled)
    switch_json_object["jumbo_enabled"]=jumbo_enabled

def getDatasFromPortsMirrorPage(response,switch_json_object):
    print("port_mirror-script----------------")
    script=response.xpath('//script/text()')[0].extract()
    scriptText= script.split("var")
    port_to_mirror_to=scriptText[1].split('"')[1].split('"')[0]
    ports_to_mirrorList=scriptText[2].split("(")[1].split(")")[0].split(",")
    port_to_mirror_to_list=[myL.replace('"', 'c') for myL in ports_to_mirrorList]
    switch_json_object["port_to_mirror_to"]=port_to_mirror_to
    print(port_to_mirror_to_list)
    switch_json_object["ports_to_mirrorList"]=port_to_mirror_to_list

    

def getDatasFromInformationPage(response,switch_json_object):
                # print("infomation-script----------------")
                script=response.xpath('//script/text()')[0].extract()
                scriptText= script.split("var")
                 
               # linksStatusList=scriptText[3].split("(").split
                system_name=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[2]/td[2]/text()').extract()
                serial_number=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[8]/td[2]/text()').extract()
                ip_adresse=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[12]/td[2]/text()').extract()
                subnet_mask=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[13]/td[2]/text()').extract()
                gateway_ip=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[14]/td[2]/text()').extract()
                mac_adreese=response.xpath('/html/body/form/table//tr[1]/td/table//tr[3]/td/table[1]//tr[15]/td[2]/text()').extract()
                # print(system_name," ", serial_number," ",ip_adresse," ",
                # subnet_mask," ",gateway_ip," ",mac_adreese)
                switch_json_object["system_name"]=system_name
                switch_json_object["serial_number"]=serial_number
                switch_json_object["ip_adresse"]=ip_adresse
                switch_json_object["subnet_mask"]=subnet_mask
                switch_json_object["gateway_ip"]=gateway_ip
                switch_json_object["mac_adreese"]=mac_adreese


                linksStatusList=scriptText[4].split("(")[1].split(")")[0].split(",")
                portsSpeedList=scriptText[5].split("(")[1].split(")")[0].split(",")
                flowControlStatusList=scriptText[6].split("(")[1].split(")")[0].split(",")
                autoNegotiationList=scriptText[7].split("(")[1].split(")")[0].split(",")
                frameTypeList=scriptText[8].split("(")[1].split(")")[0].split(",")
                pvidList=scriptText[9].split("(")[1].split(")")[0].split(",")
                trunkNameList=scriptText[10].split("(")[1].split(")")[0].split(",")
                trunkMemberList=scriptText[11].split("(")[1].split(")")[0].split(",")

                linksStatusList_new= [myL.replace('"', '') for myL in linksStatusList]
                portsSpeedList_new= [myL.replace('"', '') for myL in portsSpeedList]
                flowControlStatusList_new= [myL.replace('"', '') for myL in flowControlStatusList]
                autoNegotiationList_new= [myL.replace('"', '') for myL in autoNegotiationList]
                pvidList_new= [myL.replace('"', '') for myL in pvidList]
                frameTypeList_new= [myL.replace('"', '') for myL in frameTypeList]
                trunkNameList_new= [myL.replace('"', '') for myL in trunkNameList]
                trunkMemberList_new= [myL.replace('"', '') for myL in trunkMemberList]


                switch_json_object["linksStatusList"]=linksStatusList_new
                switch_json_object["portsSpeedList"]=portsSpeedList_new
                switch_json_object["flowControlStatusList"]=flowControlStatusList_new
                switch_json_object["autoNegotiationList"]=autoNegotiationList_new
                switch_json_object["frameTypeList"]=frameTypeList_new
                switch_json_object["pvidList"]=pvidList_new
                switch_json_object["trunkNameList"]=trunkNameList_new
                switch_json_object["trunkMemberList"]=trunkMemberList_new

                # print(linksStatusList)
                # print(portsSpeedList)
                # print(flowControlStatusList)
                # print(autoNegotiationList)
                # print(frameTypeList)
                # print(pvidList)
                # print(trunkNameList)
                # print(trunkMemberList)
def login():
        login_data={"password":"Syp2223"}
        login_url='http://10.128.10.19/login.html'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        requests.post(login_url, data=login_data, headers=headers)
        print("gelogged")
        
def postsomeThing(url,form_data):
    # url='http://10.128.10.19/ports/ports_bsc.html'
        login()
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=form_data, headers=headers)
        print(response)




def postsomeThing(form_data):
    print("ido post") 
    login_data={"password":"Syp2223"}
    url='http://10.128.10.19/ports/ports_bsc.html'
    login_url='http://10.128.10.19/login.html'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(login_url, data=login_data, headers=headers)
#    print(response)
    response = requests.post(url, data=form_data, headers=headers)
#    print(response)
    




class DemoySpider(scrapy.Spider):
    name = 'NetIF'
    start_urls = [
        'http://10.128.10.19/status/status_ov.html',
                'http://10.128.10.19/ports/ports_bsc.html',
                'http://10.128.10.19/ports/ports_config.html',
                'http://10.128.10.19/ports/ports_mir.html',
                'http://10.128.10.19/trunks/lacp.html',
                'http://10.128.10.19/vlans/vlan_pconf.html',
                'http://10.128.10.19/vlans/vlan_mconf.html',
                'http://10.128.10.19/lldp/lldpconf.html',
                'http://10.128.10.19/system/system_snmp.html',
    ]

    # def start_requests(self):
    #     urls = ['http://10.128.10.19/status/status_ov.html',
    #             'http://10.128.10.19/ports/ports_bsc.html',
    #             'http://10.128.10.19/ports/ports_config.html',
    #             'http://10.128.10.19/ports/ports_mir.html',
    #             'http://10.128.10.19/trunks/lacp.html',
    #             'http://10.128.10.19/vlans/vlan_pconf.html',
    #             'http://10.128.10.19/vlans/vlan_mconf.html',
    #             'http://10.128.10.19/lldp/lldpconf.html',
    #             'http://10.128.10.19/system/system_snmp.html'
    #             ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    # def __init__(self):
    #     login() 
        # option = webdriver.ChromeOptions()
        # option.add_experimental_option('excludeSwitches', ['enable-authmation'])
        # ser = Service("./chromedriver.exe")
        # self.bro = webdriver.Chrome(options=option,service=ser)

    # def login_ok(login_data,arg3):
    #     print("hereeeeeeee")
    #     print("gelogged")
    #     print(login_data)
    #     print(arg3)
    #     yield scrapy.FormRequest(url='http://10.128.10.19/login.html',formdata=login_data) 
    #     form_data={"_submit":"Apply","R11":"2","R52":"on","R12":"2","R51":"1"}
    #     yield scrapy.FormRequest(url='http://10.128.10.19/ports/ports_bsc.html',formdata=form_data,callback=login_data.help)

    def help(self,response):
        print(response)

    def parse(self, response):
    
        switch_json_object=self.settings["SWTICH_JSON_OBJECT"]

        page_title=response.xpath('//td[@class="page_title"]/text()')[0].extract()
        print(page_title)
        match page_title:
            case "System Information":

                getDatasFromInformationPage(response,switch_json_object)
            case "Rate Limits":
                getDatasFromRateLimitPage(response,switch_json_object)
            case "Port Configuration":
                getDatasFromPortConfigurationPage(response,switch_json_object)
            case "Port Mirroring":
                getDatasFromPortsMirrorPage(response,switch_json_object)
            case "LACP Setting":
                getDatasFromLacpSettingPage(response,switch_json_object)
            case "802.1Q Per Port Configuration":
                getDatasFromVlanPortConfPage(response,switch_json_object)
            case "LLDP Configuration":
                getDatasFromLLDPConfPage(response,switch_json_object)
            case "SNMP Configuration":
                getDatasFromSNMPConfPage(response,switch_json_object)

                


    def closed(self, reason):
        switch_json_object=self.settings.get("SWTICH_JSON_OBJECT")
        print(switch_json_object)
        CONNECTION_STRING = "mongodb://admin:admin@10.128.10.7/netif"

        dbname =  MongoClient(CONNECTION_STRING)

        # Create a new collection
        collection = dbname["netif"]
        switches = collection["settings"]
     #   switches.update_one({'_id': switch_id}, {"$set": {"ip": switch_ip, "name": switch_name, "model": switch_model}}, upsert=True)

        switches.update_one({'ip_adresse':switch_json_object["ip_adresse"]},{"$set": switch_json_object}, upsert=True)
        print("json object done insert")
        for x in switches.find():
          print("Switch -----",x)
          print(x)




        





        
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
