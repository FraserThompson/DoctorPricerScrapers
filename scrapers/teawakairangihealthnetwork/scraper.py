import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	url = 'http://teawakairangihealth.org.nz/practice-info/practice-information-fees/'
	listUrlSouped = scrapers.openAndSoup(url)

	ages = []
	fees_dict = {}

	fees_rows = listUrlSouped.find('table', {'class', 'tg practice-price'}).find_all('tr')

	# Get the fees into a dict
	for index, row in enumerate(fees_rows):

		if index == 0:
			cells = row.find_all('th')
		else:
			cells = row.find_all('td')

		# Get ages
		if index == 0:

			for cell in cells[1:]:

				age = scrapers.getFirstNumber(cell.get_text(strip=True).replace('Under 13', '0'))

				if age != 1000:
					ages.append(age)
			
			continue
		
		name = cells[0].get_text(strip=True)
		fees_dict[name] = []

		# Assign prices to ages
		for index, age in enumerate(ages):
	
			if cells[index + 1].get_text(strip=True):
				price = scrapers.getFirstNumber(cells[index + 1].get_text(strip=True))

				if price == 1000:
					continue

				fees_dict[name].append({'age': age, 'price': price })


	# Get practice details from the other table
	prac_rows = listUrlSouped.find('table', {'class', 'practice-info'}).find_all('tr')[1:]

	for row in prac_rows:
		cells = row.find_all('td')

		name = row.find('td', {'class': 'practice-name'}).get_text(strip=True)
		url = row.find('td', {'class': 'practice-name'}).find('a').attrs['href']

		scraper.newPractice(name, url, 'Te Awakairangi Health Network', "")

		if cells[1].get_text(strip=True) == "No":
			scraper.notEnrolling()

		scraper.practice['phone'] = row.find('td', {'class': 'practice-phone'}).get_text(strip=True)
		scraper.practice['address'] = row.find('td', {'class': 'practice-address'}).get_text(strip=True).replace('\n', ', ')
		scraper.practice['prices'] = fees_dict[name]

		scraper.finishPractice()

	return scraper.finish()