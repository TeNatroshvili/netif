from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

from selenium.webdriver.chrome.service import Service

ser = Service("./chromedriver.exe")

bro = webdriver.Chrome(service=ser)

bro.get("https://www.youtube.com/")

# Koordinieren des Tages
agree_btn=bro.find_element(By.XPATH,'.//div[@class="eom-button-row style-scope ytd-consent-bump-v2-lightbox"][1]/ytd-button-renderer[2]//button')
agree_btn.click()
sleep(5)

search_input = bro.find_element(By.XPATH, './/input[@id="search"]')
search_input.send_keys('Finally you dumb SELENIUM gonna wirte some here')

search_btn = bro.find_element(By.ID,'search-icon-legacy')
search_btn.click()


sleep(5)
bro.quit()
