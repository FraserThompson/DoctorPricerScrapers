import sys, codecs, os
import json
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	practice_list_url = 'https://www.alliancehealth.org.nz/find-a-clinic/'
	listUrlSouped = scrapers.openAndSoup(practice_list_url, 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/102.0.0.0 Safari/537.36')

	clinics = listUrlSouped.find('main', {'id': 'PAGES_CONTAINER'}).find_all('a', {'data-testid': "linkElement"})

	for clinic in clinics:

		name = clinic.get_text(strip=True)
		url = clinic.get('href')

		if not url:
			continue

		scraper.newPractice(name, url, "Alliance Health Plus", "")
		practice_soup = scrapers.openAndSoup(url, 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/102.0.0.0 Safari/537.36')

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

		potential_addresses = practice_soup.find_all('div', {'class': '_1Q9if'})

		for i, p_address in enumerate(potential_addresses):
			if p_address.get_text(strip=True) == "Location":
				address = scrapers.better_strip(potential_addresses[i + 1].stripped_strings)

				if "not currently taking" in address:
					scraper.notEnrolling()

				scraper.practice['address'] = scrapers.better_strip(potential_addresses[i + 1].stripped_strings)

		scraper.finishPractice()

	return scraper.finish()