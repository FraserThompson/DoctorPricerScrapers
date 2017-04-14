import sys, codecs, os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

def scrape(name):
	scraper = scrapers.Scraper(name)

	listUrlSouped = scrapers.openAndSoup('http://www.marlboroughpho.org.nz/general_practices_fees.php')
	rows = listUrlSouped.find('table', {'id': 'fees'}).find_all('tr')[1:]

	for row in rows:
		cells = row.find_all('td')
		try:
			name = cells[0].find('a').get_text(strip=True).replace("# ", "")
		except AttributeError:
			print("Skipping empty row")
			continue

		url = cells[0].find('a').get('href')
		if (name == "Marlborough Urgent GP Afterhours"):
			continue
		scraper.newPractice(name, url, "Malborough PHO", "")

		is_enrolling = cells[1].get_text(strip=True)
		if (is_enrolling == "No"):
			scraper.notEnrolling()
			continue
		elif (is_enrolling != "Yes"):
			scraper.practice['restriction'] = is_enrolling;

		scraper.practice['prices'] = [
			{
			'age': 0,
			'price': float(cells[2].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 13,
			'price': float(cells[3].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 18,
			'price': float(cells[4].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 25,
			'price': float(cells[5].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 45,
			'price': float(cells[6].get_text(strip=True).replace("$", "")),
			},
			{
			'age': 65,
			'price': float(cells[7].get_text(strip=True).replace("$", "")),
			}
		]

		prac_website_souped = scraper.openAndSoup().find_all('p')
		i = 0
		j = 4
		k = 0
		address = prac_website_souped[i].get_text()
		address = re.sub(' +', ' ', address).split('\n')[k:j]
		address[:] = [part.strip() for part in address if part != '']
		scraper.practice['address'] = ', '.join(address).replace('c/0', '')

		try:
			scraper.practice['phone'] = prac_website_souped[2].get_text(strip=True).split('Phone:')[1].split('Fax:')[0]
		except IndexError:
			scraper.practice['phone'] = prac_website_souped[1].get_text(strip=True).split('Phone:')[1].split('Fax:')[0]

		coord = scraper.geolocate()
		if coord:
			scraper.addError("Couldn't geocode address: " + address)
			continue

		scraper.postPractice()

	scraper.finish()