import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers

#stupid shit because the windows console can't print stuff properly
# sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
# sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

def scrape(name):
	scraper = scrapers.Scraper(name)

	url = 'http://www.teawakairangihealth.org.nz/practice-and-fees'
	listUrlSouped = scrapers.openAndSoup(url)

	fees_dict = {}
	fees_rows = listUrlSouped.find_all('table', {'class', 'tw'})[1].find_all('tr')[1:]

	for row in fees_rows:
		cells = row.find_all('td')
		name = cells[0].get_text(strip=True)
		if name == "Fitzherbert St Medical Centre":
			name = "Fitzherbert Road Medical Centre"
		try:
			prices = [
				{
				'age': 0,
				'price': 0,
				},
				{
				'age': 13,
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
			print('no fees')

	prac_rows = listUrlSouped.find_all('table', {'class', 'tw'})[0].find_all('tr')[1:]
	for row in prac_rows:
		cells = row.find_all('td')
		scraper.newPractice(cells[0].get_text(strip=True), 'http://www.teawakairangihealth.org.nz/practice-and-fees', 'Te Awakairangi Health Network', "")
		scraper.practice['address'] = cells[1].get_text(strip=True)
		scraper.practice['phone'] = cells[2].get_text(strip=True)

		try:
			scraper.practice['prices'] = scrapers.partial_match(scrapers.normalize(scraper.practice['name'].replace(' Street ', ' st ')), fees_dict)
		except:
			scraper.addWarning('Could not get fees because of an exception.')

		if 'prices' not in scraper.practice:
			scraper.addWarning("Cannot get prices")

		scraper.postPractice()

	scraper.finish()