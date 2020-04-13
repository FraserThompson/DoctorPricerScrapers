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

			scraper.newPractice(name, url, "Southern PHO")

			practice_page = scrapers.openAndSoup(url)
	
			start_of_details = practice_page.find(text='Contact')
			scraper.practice['address'] = start_of_details.findNext('p').get_text(strip=True)
			scraper.practice['phone'] = start_of_details.findNext('p').findNext('p').get_text(strip=True).split("Phone: ")[1]

			fees = practice_page.find(text='Fees Information').findNext('div').find('table').find_all('tr')

			for fee_row in fees:
				cells = fee_row.find_all('td')

				age = scrapers.getFirstNumber(cells[0].get_text(strip=True).replace("Under 6", "0").replace("Under 18", "0"))
				price = scrapers.getFirstNumber(cells[1].get_text(strip=True).replace("Age 10-24", ""))

				if age != 1000 and price != 1000:
					scraper.practice['prices'].append({'age': age, 'price': price})

			scraper.finishPractice()

	return scraper.finish()