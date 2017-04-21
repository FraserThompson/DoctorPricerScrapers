import csv, json
import os, sys, codecs
from scrapers import common as scrapers
current_dir = './scrapers/#manual/'

def scrape(name):

	scraper = scrapers.Scraper(name)

	with open(current_dir + 'data.json', 'r') as inFile:

		prac_dict = json.load(inFile)

		for practice in prac_dict:
			if practice['prices'] and practice['lat']:
				print(practice['name'])
				scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
				scraper.practice = practice
				scraper.finishPractice()

	return scraper.finish()
