import csv, json
import os, sys, codecs
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import scrapers
current_dir = './#manual/'
warning_list = []

def scrape(name):

	scraper = scrapers.Scraper(name)

	with open(current_dir + 'data.json', 'r') as inFile:
		prac_dict = json.load(inFile)
		for practice in prac_dict:
			scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
			scraper.practice = practice
			scraper.postPractice()
		scraper.finish()
