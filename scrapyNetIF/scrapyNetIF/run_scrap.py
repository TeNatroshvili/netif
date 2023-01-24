import subprocess
def run_spider():
    subprocess.run(["cd", "netif\scrapyNetIF\scrapyNetIF"])
    process = subprocess.Popen(["scrapy", "crawl", "NetIF"])

run_spider()