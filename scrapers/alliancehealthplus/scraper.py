import sys, codecs, os
import json
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	# this is a wix site and to get a wix site to return plain HTML you add /?_escaped_fragment_= on the end lol
	practice_list_url = 'https://www.alliancehealth.org.nz/find-a-clinic/?_escaped_fragment_='
	listUrlSouped = scrapers.openAndSoup(practice_list_url)

	clinics = listUrlSouped.find('section', {'class': 'page'}).find_all('a')

	for clinic in clinics:

		name = clinic.get_text(strip=True)
		url = clinic.get('href')

		if not url:
			continue

		scraper.newPractice(name, url, "Alliance Health Plus", "")
		practice_soup = scrapers.openAndSoup(url + '/?_escaped_fragment_=')

		all_text = practice_soup.find_all('div', {'class': 'Text'})

		scraper.practice['prices'] = []

		# Get fees very looseley
		for text_block in all_text:

			text_gotten = text_block.get_text(strip=True)

			if "Phone: " in text_gotten or "Ph: " in text_gotten:
				phone_lines = text_block.find_all('p')
				scraper.practice['phone'] = phone_lines[0].get_text(strip=True).split(":")[1].strip()

			if "$" in text_gotten:

				lines = text_block.find('ul').find_all('li')

				for fee in lines:

					fee_text = fee.get_text(strip=True)

					# We've gone too far and we're done
					if "After 5pm weekdays" in fee_text or "Saturdays" in fee_text:
						break

					# Probably some other random shit if no : so skip it
					if ":" not in fee_text:
						continue

					fee_tuple = fee_text.split(":")

					age = scrapers.getFirstNumber(fee_tuple[0])
					price = scrapers.getFirstNumber(fee_tuple[1])

					price_dict = {'age': age, 'price': price}

					scraper.practice['prices'].append(price_dict)

		map = practice_soup.find('div', {'class': 'google-map'}).find('img')
		coord = map.get('src').split('&sensor=true')[0].split('markers=color:red%7C')[1].split(',')

		scraper.practice['lat'] = float(coord[0])
		scraper.practice['lng'] = float(coord[1])
		scraper.practice['address'] = map.get('alt')

		scraper.finishPractice()

	return scraper.finish()