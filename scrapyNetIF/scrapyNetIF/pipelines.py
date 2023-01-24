# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import time
from selenium.webdriver.common.by import By
from netif.scrapyNetIF.scrapyNetIF.spiders.NetIF import login

class ScrapynetifPipeline:

    def open_spider(self, spider):
        login()
        # print("ok")
        # bro = spider.bro
        # # # requst.url -> die url die das Programm schickt
        # request='http://10.128.10.19/index.html'
        # bro.get(request)
        # frame = bro.find_element(By.XPATH,'//html/frameset/frame')
        # bro.switch_to.frame(frame)
        # time.sleep(3)
        # login_input=bro.find_element(By.XPATH,'.//input[@id="password"]')
        # login_input.send_keys('Syp2223')
        
        # login_button=bro.find_element(By.XPATH,'//input[@class="button"]')
        # login_button.click()
        # time.sleep(2)

    def process_item(self, item, spider):
        return item
