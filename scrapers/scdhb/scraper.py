import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)

	practice_list = scrapers.openAndSoup('https://www.scdhb.health.nz/info-for-you/gps').find('div', {'id': 'gpList'}).find_all('li') #this won't work because it's populated via javascript! need phantomjs or something
	fees_list = scrapers.openAndSoup('https://www.scdhb.health.nz/info-for-you/gps/fees').find('table').find_all('tr')

	ages = []
	practice_prices = {}

	for index, row in enumerate(fees_list):

		header_cells = row.find_all('th')
		cells = row.find_all('td')

		# Get ages
		if index == 0:

			for cell in header_cells[1:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True).replace("Under 13", "0"))

				if age != 1000:
					ages.append(age)
			
			continue

		name = header_cells[0].get_text(strip=True)

		prices = []

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index].get_text(strip=True))

			prices.append({'age': age, 'price': price })

		practice_prices[name] = prices

	for practice in practice_list:

		name = practice.find('h3').get_text(strip=True)
		url = practice.find('a').attrs['href']

		scraper.newPractice(name, url, "SCDHB")

		deets = practice.find_all('p')

		scraper.practice['address'] = deets[0].get_text(strip=True)
		scraper.practice['phone'] = deets[1].get_text(strip=True).replace('Phone: ', '')
		scraper.practice['prices'] = practice_prices[name]

		print(scraper.practice)

		#scraper.finishPractice()

	return scraper.finish()