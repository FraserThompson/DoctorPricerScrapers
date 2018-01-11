import sys, codecs, os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	options = scrapers.openAndSoup('http://www.tttpho.co.nz/find-nearest-doctor/').find_all('select', {'name': 'city'})

	for select in options:
		city_slugs = select.find_all('option')[1:]

		for slug in city_slugs:
			city_page_url = "http://www.tttpho.co.nz/practitioners/" + slug.attrs['data-slug']
			practice_list = scrapers.openAndSoup(city_page_url).find('div', {'class': 'practitionerlist'}).find_all('h2')

			for practice_link in practice_list:

				name = practice_link.get_text(strip=True)
				url = practice_link.find('a').attrs['href']

				scraper.newPractice(name, url, "Te Tai Tokerau", "")

				practice_page = scrapers.openAndSoup(url).find('div', {'class': 'maincol'})

				scraper.practice['phone'] = list(practice_page.find(text='Contact us').findNext('p').stripped_strings)[1]
				scraper.practice['address'] = scrapers.better_strip(practice_page.find(text='Find us').findNext('p').stripped_strings)

				fees_list = list(practice_page.find(text='Clinic Fees').findNext('p').stripped_strings)

				if len(fees_list) == 1:
					if fees_list[0] == "$0.00":
						scraper.practice['prices'].append({'age': 0, 'price': 0})
				else:

					fees_table = dict(zip(fees_list[::2], fees_list[1::2]))

					for raw_age, raw_price in fees_table.items():

						# We don't care about casuals
						if raw_age == "Casual":
							continue

						# Probably means something didn't work and we ended up with an age in place of a price
						if '-' in raw_price:
							continue

						age = scrapers.getFirstNumber(raw_age.replace('Under 13', '0'))
						price = scrapers.getFirstNumber(raw_price)

						if age != 1000 and price != 1000:
							scraper.practice['prices'].append({'age': age, 'price': price})

				scraper.finishPractice()

	return scraper.finish()