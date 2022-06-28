import sys, codecs, os
import json
import re
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)
	rootUrl = 'http://www.ethc.co.nz'
	listUrlSouped = scrapers.openAndSoup(rootUrl + "/121/all-clinics")

	feesUrl = rootUrl + '/fees'
	feesUrlSouped = scrapers.openAndSoup(feesUrl)
	feesBlob = feesUrlSouped.find('input', {'id': 'clinic-fees-data'})
	feesDict = json.loads(feesBlob.get('value'))

	rows = listUrlSouped.findAll('li', {'class': ['c-clinic-list']})

	for row in rows:
		enrolling = row.find('span', {'class': 'c-find-a-clinic__open-tagline'})
		if "Open" not in enrolling:
			scraper.notEnrolling()

		name =  row.find('a').get_text(strip=True)
		url = rootUrl + row.find('a').get('href')
		scraper.newPractice(name, url, "East Tamaki Healthcare", "")

		scraper.practice['address'] = row.find('p', {'class': 'u-mb--xs'}).get_text(strip=True)
		scraper.practice['phone'] = row.find('ul', {'class': 'c-find-a-clinic__contact-list'}).find('span').get_text(strip=True)

		practicePage = scrapers.openAndSoup(url)

		try:
			clinicCode = practicePage.find('input', {'id': 'clinic-fees-code'}).get('value')
		except AttributeError:
			scraper.addError("No fee data available, skipping.")
			scraper.finishPractice()
			continue

		filteredFees = [x for x in feesDict if x['ClinicCode'] == clinicCode and x['ServiceType'] == "Normal Hours Medical Consult" and (x['EnrolmentStatus'] == "Enrolled" or x['EnrolmentStatus'] == "Enrolled + CSC") ]

		scraper.practice['prices'] = []
		scraper.practice['prices_csc'] = []

		for fee in filteredFees:
			if fee['CSCCardStatus'] == "With CSC" or fee['EnrolmentStatus'] == "Enrolled + CSC":
				feeObj = {'age': scrapers.getFirstNumber(fee['AgeGroup']), 'price': scrapers.getFirstNumber(fee['Price'])}
				scraper.practice['prices_csc'].append(feeObj)
			else:
				feeObj = {'age': scrapers.getFirstNumber(fee['AgeGroup']), 'price': scrapers.getFirstNumber(fee['Price'])}
				scraper.practice['prices'].append(feeObj)

		scraper.finishPractice()

	return scraper.finish()