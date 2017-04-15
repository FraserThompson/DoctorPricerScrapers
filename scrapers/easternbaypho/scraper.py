import sys, codecs, os
import json, io
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '//..//')
import scrapers
import re

regex = re.compile(r'[\n\r\t]')

fees_dict = {}
root = 'http://www.ebpha.org.nz'

def scrape(name):
	scraper = scrapers.Scraper(name)

	feesUrlSouped = scrapers.openAndSoup(root + '/index.php?option=com_content&view=article&id=12&Itemid=139')
	fees_rows = feesUrlSouped.find('table', {'class': 'table_style_yellow'}).find('tbody').find_all('tr')[1:]

	for row in fees_rows:
		cells = row.find_all('td')
		name = cells[0].get_text(strip='true')
		if name == '':
			break

		prices = [
				{
				'age': 0,
				'price': float(cells[1].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 13,
				'price': float(cells[2].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 18,
				'price': float(cells[3].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 25,
				'price': float(cells[4].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 45,
				'price': float(cells[5].get_text(strip=True).replace("$", "")),
				},
				{
				'age': 65,
				'price': float(cells[6].get_text(strip=True).replace("$", "").replace("Koha", "0")),
				}
			]

		fees_dict[scrapers.normalize(name)] = prices

	pracsURLSouped = scrapers.openAndSoup(root + '/index.php?option=com_content&view=article&id=95&Itemid=125')
	pracs_rows = pracsURLSouped.find_all('ul', {'class': 'nav-child unstyled small'})[1].find_all('li')

	for row in pracs_rows:
		plan_b = 0
		fail = 0
		coord = [0,0]
		url = root + row.find('a').get('href')
		name = row.find('a').get_text(strip=True)
		if url == 'http://www.ebpha.org.nz/index.php?option=com_content&view=article&id=12&Itemid=139':
			continue

		scraper.newPractice(name, url, "Eastern Bay PHO", "")

		practiceSouped = scraper.openAndSoup().find('div', {'itemprop': 'articleBody'})
		try:
			if practiceSouped.find_all('a')[1].get_text(strip=True) == 'View map':
				maps_url = practiceSouped.find_all('a')[1].get('href')
			else:
				plan_b = 1
		except IndexError:
			plan_b = 1

		if plan_b:
			if scraper.practice['name'] == "Whakatohea Health Centre":
				scraper.practice['address'] = "117 Church Street, Opotiki"
				coord = scraper.geolocate()
			elif scraper.practice['name'] == "Med Central":
				scraper.practice['address']  = "52B King Street, Whakatane, NZ"
				coord = scraper.geolocate()
			elif scraper.practice['name'] == "Toi Ora":
				scraper.practice['address'] = "32A King Street, Opotiki"
				coord = scraper.geolocate()
			else:
				try:
					i = 0
					while coord == 0 and i < 4:
						address = practiceSouped.find_all('p')[i].get_text()
						address = re.sub('<br\s*?>', ', ', address).strip()
						scraper.practice['address'] = regex.sub(' ', address)
						coord = scraper.geolocate()
						i += 1
				except IndexError:
					scraper.addError('Could not get address or coordinates during Plan B.')
					fail = 1

				if coord[0] == 0:
					scraper.addError("Couldn't geocode address: " + address)
					fail = 1
		else:
			try:
				address = maps_url.split('q=')[1].split('&')[0]
				coord = maps_url.split('ll=')[1].split('&')[0].split(',')
			except IndexError:
				try:
					address = maps_url.split('place/')[1].split('/@')[0]
					coord = maps_url.split('@')[1].split(',17z/')[0].split(',', maxsplit=1)
				except IndexError:
					scraper.addError(url + ': Could not get address or coordinates.')
					fail = 1
			try:
				scraper.practice['lat'] = float(coord[0])
				scraper.practice['lng'] = float(coord[1])
			except ValueError:
				scraper.addError(url + ': Could not get address or coordinates.')
				fail = 1
			
			scraper.practice['address'] = address.replace('+', ' ')

		try:
			fees = scrapers.partial_match(scrapers.normalize(name), fees_dict)
		except:
			scraper.addWarning('Could not get fees.')

		if fail == 1:
			continue

		# Make the dictionary object
		scraper.practice['phone'] = "See website"
		scraper.practice['prices'] = fees
		scraper.postPractice()
	scraper.finish()