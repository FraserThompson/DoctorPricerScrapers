import csv, json
import os, sys, codecs
from scrapers import common as scrapers
current_dir = './scrapers/christchurchpho/'

def scrape(name):

	scraper = scrapers.Scraper(name)

	with open(current_dir + 'data.json', 'r') as inFile:

		prac_dict = json.load(inFile)

		for practiceObj in prac_dict:
			
			practice = practiceObj['practice'] if 'practice' in practiceObj else practiceObj

			if 'prices' in practice and practice['prices'] and 'lat' in practice and practice['lat']:
				scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
				scraper.practice = practice
				scraper.finishPractice()

	return scraper.finish()
