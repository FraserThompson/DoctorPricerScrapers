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

			# Completely non standard formatting means we have a different number of cells for a select few
			practice_details = practice_page.find_all('td', {'class': 'table-content'})
			number_of_cells = len(practice_details)

			if name == "Doctors Allen, Adam and Ceveland":
				details_modifier = 1
				fees_modifier = 2
			elif name == "Number 10 Youth Stop Shop":
				details_modifier = 0
				fees_modifier = 1
			elif name == "Vercoe Brown and Associates" or name == "Lumsden Medical Centre":
				details_modifier = 1
				fees_modifier = 1
			elif number_of_cells > 3 and name != "Mornington Health Centre":
				details_modifier = 0
				fees_modifier = details_modifier
			else:
				details_modifier = 1
				fees_modifier = details_modifier

			# The order of address/phone varies too
			if "Phone: " in practice_details[1 - details_modifier].find_all('p')[1].get_text(strip=True):
				scraper.practice['phone'] = practice_details[1 - details_modifier].find_all('p')[1].get_text(strip=True).replace('Phone: ', '')
				scraper.practice['address'] = practice_details[1 - details_modifier].find_all('p')[0].get_text(strip=True)
			else:
				scraper.practice['phone'] = practice_details[1 - details_modifier].find_all('p')[0].get_text(strip=True).replace('Phone: ', '')

			# These guys messed up and put their address instead of their email address lol
			if name == "Gore Medical Centre":
				scraper.practice['address'] = practice_details[1 - details_modifier].find_all('p')[2].get_text(strip=True).replace('Email: ', '')

			fees = practice_details[3 - fees_modifier].find('table').find_all('tr')

			for fee_row in fees:
				cells = fee_row.find_all('td')

				age = scrapers.getFirstNumber(cells[0].get_text(strip=True).replace("Under 6", "0").replace("Under 18", "0"))
				price = scrapers.getFirstNumber(cells[1].get_text(strip=True).replace("Age 10-24", ""))

				if age != 1000 and price != 1000:
					scraper.practice['prices'].append({'age': age, 'price': price})

			scraper.finishPractice()

	return scraper.finish()