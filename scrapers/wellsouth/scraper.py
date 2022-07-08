import sys, codecs, os
import json
import re
import requests
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	practice_links = scrapers.openAndSoup('https://healthpoint.co.nz/gps-accident-urgent-medical-care/wellsouth-primary-health-network/').find('ul', {'class': 'service-locations'}).find_all('a')

	for link in practice_links:

		url = "https://healthpoint.co.nz" + link.get('href')
		name = link.find('span', {'class': 'practice-name'}).get_text(strip=True)

		# if name != "Broadway Medical Centre Dunedin":
		# 	continue

		if "gps-accident-urgent-medical-care" in url:

			scraper.newPractice(name, url, "WellSouth PHO")

			scraper.practice  = scraper.practice | scrapers.scrapeHealthpoint(url)

			scraper.finishPractice(['address'])

	return scraper.finish()