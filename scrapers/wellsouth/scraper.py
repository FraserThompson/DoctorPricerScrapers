import sys, codecs, os
import json
import re
import requests
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	regions = scrapers.openAndSoup('https://wellsouth.nz/community/find-a-general-practice/').find_all('a', {'class': 'button location'})

	for region in regions:
		region_url = "https://wellsouth.nz" + region.attrs['href']

		practices = scrapers.openAndSoup(region_url).find_all('a', {'class': 'button location'})

		for practice in practices:
			name = practice.get_text(strip=True)
			url = "https://wellsouth.nz" + practice.attrs['href']

			if name == "Junction Doctors":
				# This practice is literally at north end so we don't need it
				continue

			scraper.newPractice(name, url, "WellSouth PHO")

			practice_page = scrapers.openAndSoup(url)
	
			start_of_details = practice_page.find(text='Contact')
			scraper.practice['address'] = start_of_details.findNext('p').get_text(strip=True)
			scraper.practice['phone'] = start_of_details.findNext('p').findNext('p').get_text(strip=True).split("Phone: ")[1]

			fees = practice_page.find(text='Fees Information').findNext('div').find('table').find_all('tr')

			price_col = 0
			price_csc_col = None

			for fee_row in fees:
				cells = fee_row.find_all('td')
	
				# Checking if this is a CSC table
				if cells[0].get_text(strip=True) == "Age":
					for i, cell in enumerate(cells):
						text = cell.get_text(strip=True)
						if "Non" in text:
							price_col = i
						elif "CSC" in text:
							price_csc_col = i

				age = scrapers.getFirstNumber(cells[0].get_text(strip=True).replace("Under 6", "0").replace("Under 18", "0"))

				scraper.practice['prices_csc'] = []
				scraper.practice['prices'] = []

				if (price_csc_col):
					price_csc = scrapers.getFirstNumber(cells[price_csc_col].get_text(strip=True).replace("Age 10-24", ""))
					scraper.practice['prices_csc'].append({'age': age, 'price': price_csc})
		
				price = scrapers.getFirstNumber(cells[price_col].get_text(strip=True).replace("Age 10-24", ""))
				scraper.practice['prices'].append({'age': age, 'price': price})

			scraper.finishPractice()

	return scraper.finish()