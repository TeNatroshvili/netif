import scrapy


class NetifSpider(scrapy.Spider):
    name = 'NetIF'
  #  #allowed_domains = ['10.128.10.19']
  #  start_urls = ['http://10.128.10.19/']
#
  #  def parse(self, response):
  #      print("ok")
  #      print(response)
  #      pass

   # name = 'bilibili'
    allowed_domains = ['bilibili.com']
    start_urls = ['https://www.bilibili.com/']

    def parse(self, response):
        print(response.xpath('//div'))
#        div_list = response.xpath('//div[@class="container"]/div[@class="recommended-card"]')
        div_list = response.xpath('//div[@class="feed-card"]')
        for div in div_list:
            print("scrapped vids:")
            author = div.xpath('./div[1]/div[2]/div[1]/div[1]/div[1]/a/span/text()')[0].extract()
            content = div.xpath('./div[1]/div[2]/div[1]/div[1]/h3/a/text()')[0].extract()

            print("Author:" , author , "Vid_Title:", content, "\n")