import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
from scrapers import common as scrapers

url = 'http://www.haurakipho.org.nz/medical-centres/our-medical-centres'
fees_url = 'http://www.haurakipho.org.nz/medical-centres/hpho-practice-fees'

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup(url)
	feesUrlSouped = scrapers.openAndSoup(fees_url)

	fees_rows = feesUrlSouped.find('table', {'style': 'border: currentColor; border-collapse: collapse;'}).find_all('tr')[1:]
	fees_dict = {}

	current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

	# Fees, assemble!
	for row in fees_rows:
		cells = row.find_all('td')
		name = cells[1].get_text(strip=True)
		if name == '0.00' or name == '-':
			name = cells[0].get_text(strip=True)
		try:
			prices = [
						{
						'age': 0,
						'price': 0,
						},
						{
						'age': 6,
						'price': float(cells[2].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
						},
						{
						'age': 18,
						'price': float(cells[3].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
						},
						{
						'age': 25,
						'price': float(cells[4].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
						},
						{
						'age': 45,
						'price': float(cells[5].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
						},
						{
						'age': 65,
						'price': float(cells[6].get_text(strip=True).replace('-', '1000').replace("Koha", "1000").replace("$", "")),
						},
					]
			fees_dict[scrapers.normalize(name)] = prices
		except (ValueError, IndexError):
			scraper.addWarning("Could not get fees.")

	# Iterate practices
	for i in range(0, 25):
		address = ''
		phone = ''
		practice = listUrlSouped.find('div', {'class': 'items-row cols-1 row-'+str(i)}).find('div', {'class': 'item column-1'})
		name = practice.find('h2').get_text(strip='true')
		lines = practice.find_all('p')

		scraper.newPractice(name, url, "Hauraki PHO", "")

		try:
			scraper.practice['prices'] = scrapers.partial_match(scrapers.normalize(name), fees_dict)
		except:
			scraper.addWarning('Could not get fees because of an exception.')

		if len(scraper.practice['prices']) == 0:
			scraper.practice['prices'] = scrapers.partial_match(scrapers.normalize('hamilton ' + name.replace('centre', 'centres')), fees_dict)
			if len(scraper.practice['prices']) == 0:
				scraper.addWarning('Could not find fees in dict.')

		if '-' in lines[0].get_text():
			scraper.practice['address'] = ', '.join(lines[0].strings).split('-')[1].strip()

		for line in lines:
			if 'Location:' in line.get_text(strip='true'):
				scraper.practice['address'] = ', '.join(line.strings).split('Location:')[1].replace(',,', ',').strip()
			if 'Contact details:' in line.get_text(strip='true'):
				scraper.practice['phone'] = line.get_text(strip='true').split('Contact details:')[1].split('     ')[0].strip()
			if 'Contact Details:' in line.get_text(strip='true'):
				scraper.practice['phone'] = line.get_text(strip='true').split('Contact Details:')[1].split('     ')[0].strip()
			if 'Contact:' in line.get_text(strip='true'):
				scraper.practice['phone'] = line.get_text(strip='true').split('Contact:')[1].split('     ')[0].strip()

		if address == '':
			scraper.addError("Cannot find address.")
			continue

		if ' - ' in scraper.practice['phone']:
			scraper.practice['phone'] = scraper.practice['phone'].split(' - ')[1]

		scraper.finishPractice()

	return scraper.finish()
