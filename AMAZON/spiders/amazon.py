# -*- coding: utf-8 -*-
import scrapy
import os
import csv
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    CSV_TITLE = [
        "isbn", "Price", "Sold by", "Shipped by", "Date", "Time"
    ]
    
    download_delay = 2.0

    def __init__(self):
        # Read API key
        with open(os.path.join(os.path.dirname(__file__), "proxy.txt"), 'r') as file:
            self.api_key = file.read().strip()
        # Read ASINs
        with open(os.path.join(os.path.dirname(__file__), "Input_ASIN.txt"), 'r') as f:
            self.lines = f.readlines()

    def start_requests(self):
        if not os.path.exists('Results_CSV_Files'):
            os.makedirs('Results_CSV_Files')
            
        Date_Time = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        self.csv_file = open('./Results_CSV_Files/' + Date_Time + '.csv', "a+", newline='', encoding='utf-8')
        self.csv_wr = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)
        self.csv_wr.writerow(self.CSV_TITLE)
        
        for asin_num in self.lines:
            asin_num = asin_num.strip()
            url = f"https://www.amazon.com/dp/{asin_num}"
            scraperapi_url = f"http://api.scraperapi.com/?api_key={self.api_key}&url={url}&render=true"
            yield scrapy.Request(scraperapi_url, callback=self.parse, meta={'asin_num': asin_num, 'Date_Time': Date_Time})

    def parse(self, response):
        Date_Time = response.meta['Date_Time']
        asin_num = response.meta['asin_num']
        pageno = 1  # Start from page 1
        seller_url = f"https://www.amazon.com/gp/aod/ajax?filters=%257B%2522all%2522%253Atrue%252C%2522new%2522%253Atrue%257D&asin={asin_num}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&pageno={pageno}"
        rq = scrapy.Request(seller_url, callback=self.parse_seller)
        rq.meta['asin_num'] = asin_num
        rq.meta['Date_Time'] = Date_Time
        rq.meta['pageno'] = pageno
        yield rq
        
    def parse_seller(self, response):
        Date_Time = response.meta['Date_Time']
        asin_num = response.meta['asin_num']
        pageno = response.meta.get('pageno', 1)
        Date = datetime.now().strftime("%Y_%m_%d")
        Time = datetime.now().strftime("%H_%M_%S")

        for sel in response.xpath('//div[@id="aod-offer"] | //div[@id="aod-sticky-pinned-container"]'):
            price_whole = sel.xpath('.//span[contains(@id,"aod-price-")]//span[contains(@class,"a-price-whole")]/text()').get()
            price_fraction = sel.xpath('.//span[contains(@id,"aod-price-")]//span[contains(@class,"a-price-fraction")]/text()').get()

            if price_whole and price_fraction:
                price = f"${price_whole.strip()}.{price_fraction.strip()}"
            else:
                price = sel.xpath('.//span[contains(@id,"aod-price-")]//span[@class="aok-offscreen"]/text()').get(default='$0.00').strip()

            sold = "".join(sel.xpath('.//span[contains(.,"Sold by")]/following::div[1]/a/text() | .//span[contains(.,"Sold by")]/following::div[1]/span/text()').extract()).strip()
            shipped_by = "".join(sel.xpath('.//span[contains(.,"Ships from")]/following::div[1]/a/text() | .//span[contains(.,"Ships from")]/following::div[1]/span/text()').extract()).strip()
            position = "".join(sel.xpath('.//div[contains(@id,"aod-price-")]/@id').re('aod-price-(\d+)')).strip()
            buybox = 'Yes' if position == '0' else 'No'

            dat = [
                asin_num,
                price,
                sold,
                shipped_by,
                Date,
                Time,
            ]

            print('Output Results are saved into Results file =>', dat)
            self.csv_wr.writerow(dat)

        # Get total number of offers from the element
        total_offers_text = response.xpath('//*[@id="aod-filter-offer-count-string"]/text()').get()
        if total_offers_text:
            try:
                total_offers = int("".join(filter(str.isdigit, total_offers_text)))
                max_pages = (total_offers + 9) // 10  # Round up to get total pages
            except:
                max_pages = 1  # default fallback if parsing fails
        else:
            max_pages = 1  # default if element not found

        # Check for next page
        if pageno < max_pages:
            next_pageno = pageno + 1
            asin_num_clean = response.meta['asin_num']
            seller_url = f"https://www.amazon.com/gp/aod/ajax?filters=%257B%2522all%2522%253Atrue%252C%2522new%2522%253Atrue%257D&asin={asin_num_clean}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&pageno={next_pageno}"
            rq = scrapy.Request(seller_url, callback=self.parse_seller)
            rq.meta['asin_num'] = asin_num_clean
            rq.meta['Date_Time'] = Date_Time
            rq.meta['pageno'] = next_pageno
            yield rq
        else:
            print(f"Reached max page: {max_pages}, stopping.")


    def closed(self, reason):
        self.csv_file.close()

# Run the spider if executed directly
if __name__ == '__main__':
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AmazonSpider)
    process.start()
