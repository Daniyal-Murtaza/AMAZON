# -*- coding: utf-8 -*-
import scrapy
import os
import csv
from datetime import datetime

class AmazonSpider(scrapy.Spider):
	name = 'amazon'
	CSV_TITLE = [
				"isbn", "Price", "shipping", "Price + Shipping", "Sold by", "Shipped by", "Position", "Buybox",
				"Date", "Time"
			]
			
	download_delay = 2.0

	def __init__(self):
		# Read your API key from proxy.txt
		with open(os.path.join(os.path.dirname(__file__), "proxy.txt"), 'r') as file:
			self.api_key = file.read().strip()
		# Read ASINs
		with open(os.path.join(os.path.dirname(__file__), "Input_ASIN.txt"), 'r') as f:
			self.lines = f.readlines()

	def start_requests(self):
		if not os.path.exists('Results_CSV_Files'):
			os.makedirs('Results_CSV_Files')
				
		Date_Time = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
		csv_file = open('./Results_CSV_Files/' + Date_Time + '.csv', "a+", newline='', encoding='utf-8')
		csv_wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		csv_wr.writerow(self.CSV_TITLE)
		
		for asin_num in self.lines:
			asin_num = asin_num.strip()
			url = f"https://www.amazon.com/dp/{asin_num}"
			scraperapi_url = f"http://api.scraperapi.com/?api_key={self.api_key}&url={url}&render=true"
			yield scrapy.Request(scraperapi_url, callback=self.parse, meta={'asin_num': asin_num, 'csv_wr': csv_wr, 'Date_Time': Date_Time})
				
	def parse(self, response):
		# open_in_browser(response)
		Date_Time = response.meta['Date_Time']
		csv_wr = response.meta['csv_wr']
		asin_num = response.meta['asin_num']
		# content = "".join(response.xpath('//div[@class="a-box-inner a-accordion-row-container"] | //div[@class="a-box a-last"]').extract()).strip()
		# buynew_price = response.xpath('//span[@id="newBuyBoxPrice"]/text() | //*[@id="price"]/text()').extract_first()
		# buynew_shipping = response.xpath('//*[@id="price"]/following::div[1]/div/div[@id="deliveryBlockContainer"]//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]//text()[normalize-space()][1] | //span[@id="newBuyBoxPrice"]/following::div[@class="a-accordion-inner accordion-row-content"][1]//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]//text()[normalize-space()][1] | //*[@id="price"]/following::div[1]/div/div[@id="deliveryBlockContainer"]//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]/span/a/text()[1]').extract_first()
		# if buynew_shipping:
			# buynew_shipping = "".join(buynew_shipping).strip()
			# buynew_shipping = buynew_shipping.replace('FREE delivery:','$0.00').replace('Arrives:','').replace(' delivery:','')
		# else:
			# buynew_shipping = ''
		# buynew_sold_by = response.xpath('//div[@id="merchant-info"]/a/text()').extract_first()
		# if buynew_sold_by:
			# buynew_sold_by = buynew_sold_by
		# else:
			# buynew_sold_by = 'Amazon.com'
		seller_url = "https://www.amazon.com/gp/aod/ajax?filters=%257B%2522all%2522%253Atrue%252C%2522new%2522%253Atrue%257D&asin={}&m=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp".format(str(asin_num))
		rq = scrapy.Request(seller_url, callback=self.parse_seller)
		# rq = scrapy.Request(seller_url, callback=self.parse_seller)
		# rq.meta['content'] = content
		rq.meta['asin_num'] = asin_num
		rq.meta['csv_wr'] = csv_wr
		rq.meta['Date_Time'] = Date_Time
		# rq.meta['buynew_price'] = buynew_price
		# rq.meta['buynew_shipping'] = buynew_shipping
		# rq.meta['buynew_sold_by'] = buynew_sold_by
		yield rq
		
	def parse_seller(self, response):
		# open_in_browser(response)
		# price_shipping = ''
		Date_Time = response.meta['Date_Time']
		csv_wr = response.meta['csv_wr']
		asin_num = '['+response.meta['asin_num']
		# buynew_price = response.meta['buynew_price']
		# buynew_shipping = response.meta['buynew_shipping']
		# buynew_sold_by = response.meta['buynew_sold_by']
		# content = response.meta['content']
		Date = datetime.now().strftime("%Y_%m_%d")
		Time = datetime.now().strftime("%H_%M_%S")
		for sel in response.xpath('//div[@id="aod-offer"] | //div[@id="aod-sticky-pinned-container"]'):
			price = "".join(sel.xpath('.//div[contains(@id,"aod-price-")]/span/span/text()').extract()).strip()
			if price:
				price = price
			else:
				price = '$0.00'
			shipping = "".join(sel.xpath('.//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]/b/preceding-sibling::text()[1][normalize-space()] | .//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]/b/preceding-sibling::a[1]/text() | .//div[@id="mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"]/span/a[1]/text()').extract()).strip()
			shipping = shipping.replace('FREE delivery:','$0.00').replace(' delivery:','').replace('Arrives:','')
			if shipping:
				shipping = shipping
			else:
				shipping = '$0.00'
			sold = "".join(sel.xpath('.//span[contains(.,"Sold by")]/following::div[1]/a/text() | .//span[contains(.,"Sold by")]/following::div[1]/span/text()').extract()).strip()
			shipped_by = "".join(sel.xpath('.//span[contains(.,"Ships from")]/following::div[1]/a/text() | .//span[contains(.,"Ships from")]/following::div[1]/span/text()').extract()).strip()
			position = "".join(sel.xpath('.//div[contains(@id,"aod-price-")]/@id').re('aod-price-(\d+)')).strip()
			if position == '0':
				buybox = 'Yes'
			else:
				buybox = 'No'
			price_shipping = float(price.strip('$')) + float(shipping.strip('$'))
			dat =[
				asin_num,
				price,
				shipping,
				price_shipping,
				sold,
				shipped_by,
				position,
				buybox,
				Date,
				Time,
				]
			print ('Output Results are saved into Results file =>', dat)
			csv_wr.writerow(dat)
			
# pyinstaller -F amazon.py --hidden-import AMAZON.spiders
if __name__ == '__main__':
	process = CrawlerProcess(settings=get_project_settings())
	process.crawl(AmazonSpider)
	process.start()