import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

details_dict = {}

# Access the URLs
def scrape(name):
	scraper = scrapers.Scraper(name)

	root_url = 'http://www.midlandshn.health.nz/patient-fees/'
	extensions = ['lakes/', 'tairawhiti/', 'taranaki/', 'waikato/']

	with open('./scrapers/' + name + '/legacy_data.json', 'r') as inFile:
		prac_dict = json.load(inFile)

	for extension in extensions:
		listUrlSouped = scrapers.openAndSoup(root_url + extension)
		tables = listUrlSouped.find_all('table')

		for table in tables:

			rows = table.find_all('tr')

			for row in rows:

				cells = row.find_all('td')
				name = cells[0].get_text(strip=True)

				if len(cells) == 1 or not name:
					continue
				
				# the first row contains the ages
				if name == "Medical Centre":
					ages = []
					for cell in cells[1:]:

						age = scrapers.getFirstNumber(cell.get_text(strip=True))

						if age != 1000:
							ages.append(age)

					continue
				elif name == "Enrolled" or name == "Casual":
					continue

				scraper.newPractice(cells[0].get_text(strip=True), "https://www.midlandshn.health.nz", 'Midlands Health Network', "")

				print(ages)
				print(cells)

				if scraper.practice['name'] == "Hakanoa Health Centre":
					ages[1] = 10

				# now we can give each of those ages a price (if we're not students)
				if name != "Wintec Health Services":
					scraper.practice['prices'] = []

					for index, age in enumerate(ages):

						if cells[index + 1].get_text(strip=True):

							if scraper.practice['name'] == "Hakanoa Health Centre" and (index + 1) < 3: # this guy's weird
								price = float(cells[index + 1].get_text(strip=True).split(")")[1].replace("$", ""))
							else:
								price = float(cells[index + 1].get_text(strip=True).replace("$", ""))

						scraper.practice['prices'].append({'age': age, 'price': price })
				else:
					scraper.practice['prices'] = [{'age': 0, 'price': 10.00}]
					scraper.practice["restriction"] = "Student"

				for thing in prac_dict:
					if (thing['name'] == scraper.practice['name']):
						scraper.practice['address'] = thing['address']
						scraper.practice['url'] = thing['url']
						scraper.practice['phone'] = thing['phone']
						scraper.practice['lat'] = thing['coordinates'][0]
						scraper.practice['lng'] = thing['coordinates'][1]

				if 'address' not in scraper.practice:
					scraper.addError("Couldn't get info.")
					continue

				scraper.finishPractice()
	return scraper.finish()