import sys, codecs, os
import requests
import json, urllib
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	root_url = 'https://www.nbph.org.nz'

	# Ok... now this is epic
	r = requests.get('https://www.nbph.org.nz/services/find-a-gp?format=json', verify=False)
	practices_json = r.json()
	practices = practices_json['items']

	for practice in practices:
		link = root_url + practice['fullUrl']

		name = practice['title']
		url = practice['customContent']['gpWebsite']
		scraper.newPractice(name, url, "Nelson Bays PHO", "")

		scraper.practice['address'] = practice['location']['addressLine1'] + ', ' + practice['location']['addressLine2']
		scraper.practice['phone'] = practice['customContent']['gpContact']

		if not practice['customContent']['gpNewPatients']:
			scraper.notEnrolling()

		scraper.setLatLng([practice['location']['markerLat'], practice['location']['markerLng']])
		
		scraper.practice['prices'] = [
			{
			'age': 0,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFeesUnder14']),
			},
			{
			'age': 14,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFees14-17']),
			},
			{
			'age': 18,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFees18-24']),
			},
			{
			'age': 25,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFees25-44']),
			},
			{
			'age': 45,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFees45-64']),
			},
			{
			'age': 65,
			'price': scrapers.getFirstNumber(practice['customContent']['gpFees65']),
			},
		]

		scraper.practice['prices_csc'] = [
			{
			'age': 0,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFeesUnder14']),
			},
			{
			'age': 14,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFees14-17']),
			},
			{
			'age': 18,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFees18-24']),
			},
			{
			'age': 25,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFees25-44']),
			},
			{
			'age': 45,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFees45-64']),
			},
			{
			'age': 65,
			'price': scrapers.getFirstNumber(practice['customContent']['gpCSCFees65']),
			},
		]

		scraper.finishPractice()

	return scraper.finish()