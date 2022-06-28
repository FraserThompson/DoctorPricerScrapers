import sys, codecs, os
import json, io
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
current_dir = './scrapers/haurakipho/'

# These guys have like a bunch of guys under them with better website
korowai_url = 'https://www.korowai.co.nz/book-appointment'

def scrape(name):
	scraper = scrapers.Scraper(name)

	######## Korowai practices
	korowai_soup = scrapers.openAndSoup(korowai_url)
	korowai_list = korowai_soup.find('section', {'class': 'location'}).find_all('div', {'class': 'add-list'})
	fees_table = korowai_soup.find('div', {'class': 'fees-table'}).find_all('tr')

	prices = []
	for row in fees_table[1:]:
		age = scrapers.getFirstNumber(row.find('th').get_text(strip=True))

		# If we couldnt get a number its time to go
		if (age == 1000):
			break

		price = {
			'age': age,
			'price': scrapers.getFirstNumber(row.find('td').get_text(strip=True))
		}
		prices.append(price)

	for practice in korowai_list[1:]:
		name = practice.find('h3').get_text(strip=True)
		url = korowai_url

		scraper.newPractice(name, url , "Hauraki PHO", "")

		peas = practice.find_all('p')

		# This isn't reliable, so we'll just stick with what we have.
		#scraper.practice['address'] = peas[0].get_text(strip=True).split("/n")[0]

		try:
			scraper.practice['phone'] = peas[0].find('a').get_text(strip=True)
		except AttributeError:
			scraper.practice['phone'] = peas[2].find('a').get_text(strip=True)

		scraper.practice['prices'] = prices

		scraper.finishPractice()
	
	###### All other practices come from data.json
	with open(current_dir + 'data.json', 'r') as inFile:
		
		prac_dict = json.load(inFile)

		for practiceObj in prac_dict:
			
			practice = practiceObj['practice'] if 'practice' in practiceObj else practiceObj

			if 'prices' in practice and practice['prices'] and 'lat' in practice and practice['lat']:
				scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
				scraper.practice = practice
				scraper.finishPractice()

	return scraper.finish()
