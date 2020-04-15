import csv, json
import os, sys, codecs
from scrapers import common as scrapers
current_dir = './scrapers/_manual/'

def scrape(name):

	scraper = scrapers.Scraper(name)

	files = ['data.manual.json']

	for filename in files:
		with open(current_dir + filename, 'r') as inFile:

			prac_dict = json.load(inFile)

			for practiceObj in prac_dict:
				
				practice = practiceObj['practice'] if 'practice' in practiceObj else practiceObj

				if 'prices' in practice and practice['prices'] and 'lat' in practice and practice['lat']:
					print(practice['name'])
					scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
					scraper.practice = practice
					scraper.finishPractice()

	return scraper.finish()
