import csv, json
import os, sys, codecs
from scrapers import common as scrapers
current_dir = './scrapers/_legacy/'

def scrape(name):

	scraper = scrapers.Scraper(name)

	with open(current_dir + 'data.json', 'r') as inFile:

		prac_dict = json.load(inFile)

		for practice in prac_dict:
			if practice['prices'] and practice['lat']:
				scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
				scraper.practice = practice
				scraper.practice['active'] = True
				scraper.finishPractice()

	return scraper.finish()
