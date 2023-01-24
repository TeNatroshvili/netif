import subprocess
import os
 
def run_spider():
    os.chdir("C:/_Schule/_5.Jahrgang/Projekt/Projekt/netif/scrapyNetIF/scrapyNetIF")
    process = subprocess.Popen(["scrapy", "crawl", "NetIF"])
 
run_spider()