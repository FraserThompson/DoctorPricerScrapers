import sys, codecs, os, time
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

def scrape(name):

	infoUrl = "https://www.thinkhauora.nz/general-practice"
	listUrl = "https://www.thinkhauora.nz/general-practice-fees"

	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup(listUrl)
	infoURLSouped = scrapers.openAndSoup(infoUrl)

	fees_rows = listUrlSouped.find('div', {'class': 'practicefeeslist'}).find_all('li', {'class': 'row'})
	info_rows = infoURLSouped.find('div', {'class': 'practiceslist'}).find_all('li', {'class': 'row'})
	
	practices = {}

	# Build a dictionary for the details
	for row in info_rows:
		name = row.find('div', {'class': 'centre'}).find('a').get_text(strip=True)

		if not name:
			continue

		practice = {}
		practice['enrolling'] = 'check-circle-solid' in row.find('div', {'class': 'enrolling'}).find('img').get('src')
		practice['csc'] = 'check-circle-solid' in row.find('div', {'class': 'csc'}).find('img').get('src')
		practice['phone'] = row.find('div', {'class': 'phone'}).find('p').get_text(strip=True)
		practice['address'] = row.find('div', {'class': 'address'}).find('p').get_text(strip=True)
		practices[name] = practice

	# Get prices
	for row in fees_rows:
		title_element = row.find('div', {'class': 'centre'}).find('a')
		title = title_element.get_text(strip=True)

		if not title:
			continue

		url = "https://www.thinkhauora.nz" + title_element.get('href')
		
		print(title)

		scraper.newPractice(title, url, "THINK Hauora", "")
		scraper.practice['phone'] = practices[title]['phone']
		scraper.practice['address'] = practices[title]['address']
		
		if not practices[title]['enrolling']:
			scraper.notEnrolling()

		zero = row.find('div', {'class': 'feeone'}).find('p').get_text(strip=True)
		fourteen = row.find('div', {'class': 'feetwo'}).find('p').get_text(strip=True)
		eighteen = row.find('div', {'class': 'feethree'}).find('p').get_text(strip=True)
		twentyfive = row.find('div', {'class': 'feefour'}).find('p').get_text(strip=True)
		fortyfive = row.find('div', {'class': 'feefive'}).find('p').get_text(strip=True)
		oversixtyfive = row.find('div', {'class': 'feesix'}).find('p').get_text(strip=True)

		if not zero:
			continue

		if zero == "-":
			continue

		scraper.practice['prices_csc'] = [
			{
			'age': 0,
			'price': 0,
			},
			{
			'age': 14,
			'price': 13,
			},
			{
			'age': 18,
			'price': 19.50,
			},
		]

		scraper.practice['prices'] = [
			{
			'age': 0,
			'price': float(zero.replace("$", "")),
			},
			{
			'age': 14,
			'price': float(fourteen.replace("$", "")),
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