import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	fees_dict = {}
	root = 'http://www.wboppho.org.nz/'

	feesUrlSouped = scrapers.openAndSoup(root + 'medical-centres/what-is-primary-health-general-practice-fees/')
	fees_rows = feesUrlSouped.find('div', {'class': 'col-md-8'}).find('table').find_all('tr')[1:]

	# Assemble fees dict
	for row in fees_rows:
		cells = row.find_all('td')

		name = cells[0].get_text(strip=True)
		if name == '':
			break
		if name == "Papamoa Pines Health Centre":
			name = "Papamoa Pines Medical Centre"

		prices = [
				{
				'age': 0,
				'price': float(cells[1].get_text(strip=True).replace('$', '')),
				},
				{
				'age': 13,
				'price': float(cells[2].get_text(strip=True).replace('$', '')),
				},
				{
				'age': 18,
				'price': float(cells[3].get_text(strip=True).replace('$', '')),
				},
				{
				'age': 25,
				'price': float(cells[4].get_text(strip=True).replace('$', '')),
				},
				{
				'age': 45,
				'price': float(cells[5].get_text(strip=True).replace('$', '')),
				},
				{
				'age': 65,
				'price': float(cells[6].get_text(strip=True).replace('$', '')),
				}
			]

		fees_dict[scrapers.normalize(name)] = prices

	pracsURLSouped = scrapers.openAndSoup(root + 'medical-centres/')
	pracs_rows = pracsURLSouped.find('div', {'class': 'col-md-8'}).find_all('article', {'class': re.compile('medicalList *')})

	# Scrape practices
	for row in pracs_rows:
		scraper.newPractice(row.find('span', {'class': 'practice'}).get_text(strip=True), "http://www.wboppho.org.nz/", "Western Bay of Plenty PHO", "")

		if row.find('span', {'class': 'accepting'}).get_text(strip=True) == 'No':
			scraper.notEnrolling()
			continue

		try:
			scraper.practice['url'] = row.find('a').get('href')
		except AttributeError:
			scraper.addWarning('Could not get website.')

		try:
			prices = fees_dict[scrapers.normalize(scraper.practice['name'])]
		except:
			scraper.addWarning('Could not get fees.')
			prices = []

		scraper.practice['address'] = row.find('span', {'class': 'address'}).get_text(strip=True) + " " + row.find('span', {'class': 'suburb'}).get_text(strip=True)
		scraper.practice['phone'] = row.find('span', {'class': 'phone'}).get_text(strip=True)
		scraper.practice['prices'] = prices

		scraper.postPractice()

	scraper.finish()