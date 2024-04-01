import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

details_dict = {}

# Access the URLs
def scrape(name):
	scraper = scrapers.Scraper(name)

	root_url = 'https://www.pinnacle.co.nz'

	listUrlSouped = scrapers.openAndSoup(root_url + "/practices")

	practice_items = listUrlSouped.find_all('div', {'class': 'practice-block'})

	for practice in practice_items:

		name = practice.find('a').get_text(strip=True)
		url = root_url + practice.find('a').get('href')

		scraper.newPractice(name, url, 'Pinnacle PHO', "")

		scraper.practice['phone'] = practice.find('div', {'class': 'deets'}).find('div', {'class': 'd-flex'}).find_all('div')[1].get_text(strip=True)

		deets_text = practice.find('div', {'class': 'deets'}).get_text(strip=True)
		if "we are accepting new patients" not in deets_text:
			scraper.notEnrolling()

		practiceInfoSouped = scrapers.openAndSoup(url)

		# The address is a link to google maps so we can get it like this
		regex = re.compile('maps.google.com')
		scraper.practice['address'] = practiceInfoSouped.find("a", {"href" : regex}).get_text(strip=True).replace('\n', ' ')

		all_text = practiceInfoSouped.find('section').get_text(strip=True).lower()

		if 'enrolled patient fees' not in all_text:
			scraper.addError("No prices found")
		elif name == "Wintec Health Services":
			scraper.practice['prices'] = [
				{
					'age': 0,
					'price': 12.00
				}
			]
			scraper.practice['restriction'] = "Student"
		else:
			fees_table = practiceInfoSouped.find('table')
		
			scraper.practice['prices'] = []
			scraper.practice['prices_csc'] = []

			fees_rows = fees_table.find_all('tr')

			for i, row in enumerate(fees_rows):
				cells = row.find_all('td')

				# Skip empty rows
				if not cells[0].get_text(strip=True):
					continue

				# Some of them have a third column for CSC
				if len(cells) > 2:

					# CSC is first col, non-CSC is second col
					# This hopefully won't change
					csc_index = 1
					non_csc_index = 2

					# Skip header row
					if i == 0 and cells[1].find('strong'):
						continue
	
					price = {
						'age': scrapers.getFirstNumber(cells[0].get_text(strip=True)),
						'price': scrapers.getFirstNumber(cells[non_csc_index].get_text(strip=True))
					}
					scraper.practice['prices'].append(price)

					price_csc = {
						'age': scrapers.getFirstNumber(cells[0].get_text(strip=True)),
						'price': scrapers.getFirstNumber(cells[csc_index].get_text(strip=True))
					}
					scraper.practice['prices_csc'].append(price_csc)
	
				else:
					price = {
						'age': scrapers.getFirstNumber(cells[0].get_text(strip=True)),
						'price': scrapers.getFirstNumber(cells[1].get_text(strip=True))
					}
					scraper.practice['prices'].append(price)

		scraper.finishPractice()

	return scraper.finish()