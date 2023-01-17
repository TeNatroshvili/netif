from selenium import  webdriver
from time import sleep
from scrapy.utils.project import get_project_settings

# initialisieren eines Webbrowser Objekt (driver muss angegeben!)
bro = webdriver.Chrome(executable_path='./chromedriver.exe')

bro.get("https://www.youtube.com/")
page_text=bro.page_source
sleep(5)
bro.quit()
