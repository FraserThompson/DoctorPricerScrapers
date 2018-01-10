import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

url = 'http://www.haurakipho.org.nz/medical-centres/hpho-practice-fees'

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup(url)

	fees_rows = listUrlSouped.find('table', {'style': 'width: 780px; border-collapse: collapse;'}).find_all('tr')
	ages = []

	for index, row in enumerate(fees_rows[1:]):

		cells = row.find_all('td')
		everything = cells[0].get_text(strip=True).replace('\xa0', '')

		# Get ages
		if index == 0:

			for cell in cells[1:]:
				age = scrapers.getFirstNumber(cell.get_text(strip=True))

				if age != 1000:
					ages.append(age)
			
			continue

		# Some of them don't do double spaces between name and address, most do
		if everything.split(" ")[0] == "Raukura" or everything.split(" ")[1] == "Korowai":
			working = everything.split(" ")
			name_split = [' '.join(working[0:7]), ' '.join(working[7:])]
		elif everything.split(" ")[0] == "Avalon":
			working = everything.split(" ")
			name_split = [' '.join(working[0:2]), ' '.join(working[2:])]
		elif everything.split(" ")[0] == "University":
			working = everything.split(" ")
			name_split = [' '.join(working[0:3]), ' '.join(working[4:])]
		elif everything.split(" ")[0] == "Raungaiti":
			continue
		else:
			name_split = everything.split("  ")

		try:
			phone_split = name_split[1].split(" – Ph:")
		except IndexError:
			print("Problem: " + str(name_split))
			continue

		scraper.newPractice(name_split[0], "http://www.haurakipho.org.nz/medical-centres/our-medical-centres", "Hauraki PHO", "")

		scraper.practice['prices'] = []

		# Assign fees to prices
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True).replace('Koha', '$0'))

			scraper.practice['prices'].append({'age': age, 'price': price })
		
		scraper.practice['address'] = phone_split[0].strip()
		scraper.practice['phone'] = phone_split[1].strip()

		scraper.finishPractice()

	return scraper.finish()
