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

	practice_items = listUrlSouped.find_all('div', {'class': 'practice-item'})

	for practice in practice_items:

		name = practice.find('h4').get_text(strip=True)
		url = root_url + practice.find('h4').find('a').get('href').split("..")[1]

		scraper.newPractice(name, url, 'Pinnacle PHO', "")

		scraper.practice['address'] = practice.find('div', {'class': 'address'}).get_text(strip=True).split("Address:")[1].split("\n")[0]
		scraper.practice['phone'] = practice.find('div', {'class': 'info'}).find('p').get_text(strip=True).split("P:")[1]

		enrolling = practice.find("i", {"class": "fa-check-circle"})
		if not enrolling:
			scraper.notEnrolling()

		practiceInfoSouped = scrapers.openAndSoup(url)
		fees_table = practiceInfoSouped.find('table', {'class': 'fees'})

		if fees_table:
			scraper.practice['prices'] = []
			scraper.practice['prices_csc'] = []

			age_row = fees_table.find_all('th')
			all_rows = fees_table.find_all('tr')

			# This means no CSC/Non-CSC split
			print(age_row[0].get_text(strip=True))
			if age_row[0].get_text(strip=True):
				prices_row = fees_table.find_all('td')

				for i, cell in enumerate(age_row):
					price = {
						'age': scrapers.getFirstNumber(cell.get_text(strip=True)),
						'price': scrapers.getFirstNumber(prices_row[i].get_text(strip=True)),
					}
					scraper.practice['prices'].append(price)
			else:
				prices_row = all_rows[1].find_all('td')
				prices_csc_row = all_rows[2].find_all('td')

				for i, cell in enumerate(age_row[1:]):
					price = {
						'age': scrapers.getFirstNumber(cell.get_text(strip=True)),
						'price': scrapers.getFirstNumber(prices_row[i + 1].get_text(strip=True)),
					}
					scraper.practice['prices'].append(price)

					price_csc = {
						'age': scrapers.getFirstNumber(cell.get_text(strip=True)),
						'price': scrapers.getFirstNumber(prices_csc_row[i + 1].get_text(strip=True)),
					}
					scraper.practice['prices_csc'].append(price_csc)
		else:
			scraper.addError("No prices found")

		scraper.finishPractice()

	return scraper.finish()