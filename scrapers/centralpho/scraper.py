import sys, codecs, os, time
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):

	infoUrl = "http://www.centralpho.org.nz/general-practices"
	listUrl = "http://www.centralpho.org.nz/practice-fees"

	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup(listUrl)
	infoURLSouped = scrapers.openAndSoup(infoUrl)

	fees_rows = listUrlSouped.find('div', {'class': 'view-id-general_practices_and_fees'}).find_all('tr')
	info_rows = infoURLSouped.find('div', {'class': 'view-id-general_practices_and_fees'}).find_all('tr')
	
	practices = {}

	# Build a dictionary for the details
	for row in info_rows[1:]:
		practice = {}
		practice['enrolling'] = row.find('td', {'class': 'views-field-field-enrolling-patients'}).get_text(strip=True)
		practice['phone'] = row.find('td', {'class': 'views-field views-field-field-phone'}).get_text(strip=True)
		practice['address'] = row.find('td', {'class': 'views-field views-field-field-address'}).get_text(strip=True)
		practices[row.find('td', {'class': 'views-field-title'}).get_text(strip=True)] = practice

	# Get prices
	for row in fees_rows[1:]:
		cells = row.findAll('td')
		title_element = row.find('td', {'class': 'views-field-title'})
		title = title_element.get_text(strip=True)
		url = "http://www.centralpho.org.nz" + title_element.find('a').get('href')
		
		print(title)

		scraper.newPractice(title, url, "Central PHO", "")
		scraper.practice['phone'] = practices[title]['phone']
		scraper.practice['address'] = practices[title]['address']
		
		if practices[title]['enrolling']:
			scraper.notEnrolling()

		zero = row.find('td', {'class': 'views-field-field-under-6'}).get_text(strip=True)

		# If there's no zero column then probably no prices so skip it
		if zero != "":
			six = row.find('td', {'class': 'views-field-field-6-to-12'}).get_text(strip=True)
			thirteen = row.find('td', {'class': 'views-field-field-13-to-17'}).get_text(strip=True)
			eighteen = row.find('td', {'class': 'views-field-field-18-to-24'}).get_text(strip=True)
			twentyfive = row.find('td', {'class': 'views-field-field-25-to-44'}).get_text(strip=True)
			fortyfive = row.find('td', {'class': 'views-field-field-45-to-65'}).get_text(strip=True)
			oversixtyfive = row.find('td', {'class': 'views-field-field-over-65'}).get_text(strip=True)

			scraper.practice['prices'] = [
				{
				'age': 0,
				'price': float(zero.replace("$", "")),
				},
				{
				'age': 6,
				'price': float(six.replace("$", "")),
				},
				{
				'age': 13,
				'price': float(thirteen.replace("$", "")),
				},
				{
				'age': 18,
				'price': float(eighteen.replace("$", "")),
				},
				{
				'age': 25,
				'price': float(twentyfive.replace("$", "")),
				},
				{
				'age': 45,
				'price': float(fortyfive.replace("$", "")),
				},
				{
				'age': 65,
				'price': float(oversixtyfive.replace("$", "")),
				},
			]

		scraper.finishPractice()

	return scraper.finish()