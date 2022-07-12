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

		all_text = practice_soup.find_all('div', {'class': '_3bcaz'})

		scraper.practice['prices'] = []

		fees_start = 0
		address_start = 0

		# Get fees very looseley
		for i, text_block in enumerate(all_text):

			text_gotten = text_block.get_text(strip=True)

			#print(str(i) + text_gotten)

			if "Phone: " in text_gotten or "Ph: " in text_gotten:
				phone_lines = text_block.find_all('p')
				scraper.practice['phone'] = phone_lines[0].get_text(strip=True).split(":")[1].strip()

			if "Fees" in text_gotten:
				fees_start = i

			if "Location" in text_gotten:
				address_start = i
				
			# This would mean we're in the paragraph with the fees (hopefully, but we'll check)
			if fees_start > 0 and i == fees_start+1:
				print(text_gotten)
				if "$" not in text_gotten:
					# We got it wrong. It's probably the next one?
					fees_start = fees_start + 1
					continue

				lists = text_block.find_all('ul')

				for i, list in enumerate(lists):
					lines = list.find_all('li')

					for fee in lines:

						fee_text = fee.get_text(strip=True)

						# We've gone too far and we're done
						if "After 5pm weekdays" in fee_text or "Saturdays" in fee_text:
							break

						# Probably some other random shit if no : so skip it
						if ":" not in fee_text:
							continue

						fee_tuple = fee_text.split(":")

						# One of them has a double price, lets just skip it
						if "in an educational programme" in fee_tuple[0]:
							continue

						age = scrapers.getFirstNumber(fee_tuple[0])
						price = scrapers.getFirstNumber(fee_tuple[1])

						# Means it couldn't get a number, so probably not a real price
						if age == 1000:
							continue

						price_dict = {'age': age, 'price': price}

						# The first table is not CSC, the second is CSC
						if i == 0 and "with CSC" not in fee_tuple[1]:
							scraper.practice['prices'].append(price_dict)
						else:

							if not scraper.practice.get('prices_csc'):
								scraper.practice['prices_csc'] = []

							scraper.practice['prices_csc'].append(price_dict)

			# This would mean we're in the paragraph with the address (hopefully)
			if address_start > 0 and i == address_start+1:
				address = scrapers.better_strip(text_block.stripped_strings)

				if "not currently taking" in address:
					scraper.notEnrolling()

				scraper.practice['address'] = address.split("This practice")[0]

		scraper.finishPractice()

	return scraper.finish()