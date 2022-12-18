import scrapy
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time


class DemoySpider(scrapy.Spider):
    name = 'NetIF'
   # allowed_domains = ['www.youtube.com']
    
 #  start_urls = ['http://10.128.10.19/status/status_ov.html']
    
       

    def start_requests(self):
        urls = ['http://10.128.10.19/status/status_ov.html',
                'http://10.128.10.19/ports/ports_config.html',
                'http://10.128.10.19/ports/ports_mir.html',
                'http://10.128.10.19/trunks/trunks_mem.html',
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
        print(response.xpath('//td[@class="page_title"]/text()')[0].extract())

        





        
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
