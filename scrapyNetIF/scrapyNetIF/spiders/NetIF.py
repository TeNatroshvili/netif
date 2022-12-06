import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

from selenium.webdriver.chrome.service import Service


class DemoySpider(scrapy.Spider):
    name = 'NetIF'
    allowed_domains = ['www.youtube.com']
    start_urls = ['https://www.youtube.com/']

    def __init__(self):  # Initialisieren eines Browsers

        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-authmation'])
        ser = Service("./chromedriver.exe")

        self.bro = webdriver.Chrome(options=option,service=ser)

    def parse(self, response):
        sleep(1)
       # print(response.xpath('./'))
        print("jjojo")
        found_videos = response.xpath('//div[@class="text-wrapper style-scope ytd-video-renderer"]')
        for found_vid in found_videos:
            title = found_vid.xpath('./div[@id="meta"]//h3/a/@title')[0].extract()
            watched_times = found_vid.xpath('./div[@id="meta"]//div[@id="metadata-line"]//span[1]/text()')[0].extract()
            upload_time = found_vid.xpath('./div[@id="meta"]//div[@id="metadata-line"]//span[2]/text()')[0].extract()
            producer = found_vid.xpath('./div[@id="channel-info"]//div[@id="text-container"]//a/text()')[0].extract()

            print("Found a vid -------------------------------------")
            print("Title: ", title, " -", watched_times, " Views", upload_time, " ")
            print("producer: ", producer,"\n")
        # recommend_list = response.xpath('//div[@id="contents"]//div[@id="content"]//div[@class="style-scope ytd-rich-grid-media"]//div[@id="details"]')

        # for div in recommend_list:
        # print(div)
        # print("ok - content")
        # print()
        # author = div.xpath('./div[@id="meta"]/h3/a/@title')[0].extract()
        # print(author)
