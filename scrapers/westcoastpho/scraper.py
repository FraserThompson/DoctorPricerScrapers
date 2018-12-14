import sys, codecs, os
import json, io, unicodedata
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers
import re

def scrape(name):
	scraper = scrapers.Scraper(name)

	url = 'http://www.westcoastpho.org.nz/general-practices'
	listUrlSouped = scrapers.openAndSoup(url)
	prac_links = listUrlSouped.find('div', {'id': 'block-views-locations-block'}).find_all('div', {'class': 'views-row'})

	for link in prac_links:
		name = link.find('div', {'class': 'views-field-title'}).find('a').get_text(strip=True)
		url = "http://www.westcoastpho.org.nz" + link.find('div', {'class': 'views-field-title'}).find('a').attrs['href']

		scraper.newPractice(name, url, "West Coast PHO", "")

		scraper.practice['address'] =  scrapers.better_strip(link.find('div', {'class': 'views-field-location'}).stripped_strings)

		practice_page = scrapers.openAndSoup(url).find('div', {'id': 'primary'})

		scraper.practice['phone'] = practice_page.find(text=re.compile('Phone')).parent.parent.get_text(strip=True).split("Phone:")[1].split("Fax:")[0].replace('\xa0', '')

		fees_list = list(practice_page.find(text=re.compile('Price to Patient')).findNext('p').stripped_strings)

		for fee in fees_list:
			normalized_fee = unicodedata.normalize("NFKD", fee)
			split = normalized_fee.split(' - ')

			if split[0] == "Adult":
				split[0] = "18"

			# some of them have slightly different formatting (doesn't split prices with - for the first two) so hit with a hammer until it works
			if len(split) != 2:
				split = normalized_fee.split(" ")
				if len(split) != 2:
					split = [(' ').join(split[0:2]), split[2]]
	
			age = scrapers.getFirstNumber(split[0])
			try:
				price = scrapers.getFirstNumber(split[1])
			except:
				print(name + ": Weird fees")
				continue
			scraper.practice['prices'].append({'age': age, 'price': price})

		scraper.finishPractice()

	return scraper.finish()