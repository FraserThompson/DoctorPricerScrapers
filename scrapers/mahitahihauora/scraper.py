import sys, codecs, os
import requests
from bs4 import BeautifulSoup
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '\\..\\')
from scrapers import common as scrapers

def scrape(name):
	scraper = scrapers.Scraper(name)

	# These guys have some tables populated via AJAX at these endpoints
	table_ids = ['808', '1151', '1152']
	table_url = "https://mahitahihauora.co.nz/wp-admin/admin-ajax.php?action=wp_ajax_ninja_tables_public_action&target_action=get-all-data&default_sorting=old_first&skip_rows=0&limit_rows=0&ninja_table_public_nonce=aa8ea2bd32&table_id="

	for table_id in table_ids:
		r = requests.get(table_url + str(table_id), verify=False)
		table_content = r.json()

		for row in table_content:

			# Their tables have different keys...
			try:
				row_html = row['value']['table_headline_one']
			except:
				row_html = row['value']['practice']

			row_soup = BeautifulSoup(row_html, 'html5lib')
			url = row_soup.find('a').get('href')
			name = row_soup.get_text(strip=True)
			scraper.newPractice(name, url, 'Mahitahi Hauora', "")
			scraper.practice = scraper.practice | scrapers.scrapeHealthpoint(url)
			scraper.finishPractice()

	return scraper.finish()