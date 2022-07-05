import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	fees_url = 'https://teawakairangihealth.org.nz/practice-fees/'
	practice_url = 'https://teawakairangihealth.org.nz/find-doctor/'
	feesUrlSouped = scrapers.openAndSoup(fees_url)

	tables = feesUrlSouped.find_all('table', {'class', 'uael-table'})
	fees_table = tables[0]
	csc_fees_table = tables[1]

	ages_header = fees_table.find_all('th')
	ages = scrapers.parseAgeHeader(ages_header)

	fees_rows = fees_table.find('tbody').find_all('tr')
	csc_fees_rows = csc_fees_table.find('tbody').find_all('tr')

	fees_dict = {}
	csc_fees_dict = {}

	# Get the fees into a dict
	for row in fees_rows:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)
		name = name.split("(")[0].strip()

		fees_dict[name] = []

		for i, cell in enumerate(cells[1:]):
			price = {
				'age': ages[i],
				'price': scrapers.getFirstNumber(cell.get_text(strip=True))
			}
			fees_dict[name].append(price)

	for row in csc_fees_rows:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)
		name = name.split("(")[0].strip()

		csc_fees_dict[name] = []

		for i, cell in enumerate(cells[1:]):
			price = {
				'age': ages[i],
				'price': scrapers.getFirstNumber(cell.get_text(strip=True))
			}
			csc_fees_dict[name].append(price)

	practiceUrlSouped = scrapers.openAndSoup(practice_url)

	practice_boxes = practiceUrlSouped.select('div[class*="elementor-inner-column"]')

	for box in practice_boxes:

		try:
			name = box.find('h3').get_text(strip=True)
		except AttributeError:
			continue

		try:
			address = box.find('div', {'class': 'elementor-widget-icon-list'}).find('li').get_text(strip=True)
		except AttributeError:
			print("Skipping because it doesn't look like a practice: " + name)
			continue

		# Because they're inconsistent
		name = name.split("(")[0].strip()

		if name == "Whai Oranga O Te Iwi Health Centre":
			name = "Whai Oranga O Te Iwi Health"

		url = box.find_all('a')[-1].get('href')

		scraper.newPractice(name, url, 'Te Awakairangi Health Network', "")

		if "NOT" in box.find_all('div')[1].get_text(strip=True):
			scraper.notEnrolling()

		scraper.practice['address'] = address + ", New Zealand"

		phone = box.find('div', {'class': 'elementor-widget-icon-list'}).find_all('li')[1].get_text(strip=True)

		scraper.practice['phone'] = phone if ": " not in phone else phone.split(": ")[1]

		try:
			scraper.practice['prices'] = fees_dict[name]
			scraper.practice['prices_csc'] = csc_fees_dict[name]
		except KeyError:
			pass

		scraper.finishPractice()

	return scraper.finish()