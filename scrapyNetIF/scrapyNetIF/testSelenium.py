from selenium import  webdriver
from time import sleep
# initialisieren eines Webbrowser Objekt (driver muss angegeben!)
bro = webdriver.Chrome(executable_path='./chromedriver.exe')

bro.get("https://www.youtube.com/")
page_text=bro.page_source
sleep(5)
bro.quit()
