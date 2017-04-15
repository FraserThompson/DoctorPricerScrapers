import sys, codecs, os
import json, io
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)

	url = 'http://www.westcoastpho.org.nz/General-Practices-Fees'
	listUrlSouped = scrapers.openAndSoup(url)
	prac_links = listUrlSouped.find('table', {'id': 'dnn_ctr9792_Latest_ctl00'}).find_all('a', href=True)

	for link in prac_links:
		prices = []
		scraper.newPractice(link.get_text(strip=True), link['href'], "West Coast PHO", "")
		prac_page = scraper.openAndSoup()

		print(name)
		info = prac_page.find('table', {'cellpadding': '3px'}).find_all('tr')
		contact_info = info[len(info) - 2].get_text().strip().splitlines()
		scraper.practice['address'] = contact_info[1]
		scraper.practice['phone'] = contact_info[2].split(": ")[1]

		if len(info) > 2:
			fee_info = info[0].find('td').contents
			fee_rows = [x for x in fee_info if not hasattr(x, "name") or not x.name == "br"][1:]
			prices = []
			if len(fee_rows) > 1:
				for fee in fee_rows[1:]:
					fee = fee.replace("Zero", "$0")
					try:
						price = {
							'age': scrapers.getFirstNumber(fee.split(' $')[0]),
							'price': scrapers.getFirstNumber(fee.split(' $')[1].replace("Free", "0"))
						}

						if price['age'] == -1:
							price['age'] = prices[len(prices) - 1]['age'] + 1

						prices.append(price);
					except IndexError:
						print("index error: " + fee)
						continue

		if len(prices) == 0:
			scraper.addWarning("No prices.")

		scraper.practice['prices'] = prices
		scraper.postPractice()
		time.sleep(1.5)

	scraper.finish()