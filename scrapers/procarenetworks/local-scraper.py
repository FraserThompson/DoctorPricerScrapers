import csv, json
import os, sys, codecs
import requests, time, operator
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from scrapers import common as scrapers

current_dir = './scrapers/procarenetworks/'

def scrape(name):
    scraper = scrapers.Scraper(name)
    root_url = "https://api.procare.co.nz/api/v2/members/practices/suburb/"
    suburbs = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    headers = {'authorization-apikey': 'C66B0FDF-AA8C-4851-8642-9694840D7C17'}

    for suburb in suburbs:

        time.sleep(3)
        print("Getting: " + root_url + suburb)
        r = requests.get(root_url + suburb, headers=headers)
        response = r.json()
        print("Got " + str(len(response)) + " results")

        for practice in response:

            scraper.newPractice(practice['PracticeName'], practice['WebSiteURL'] if practice['WebSiteURL'] else "http://procare.co.nz/", "Procare Networks", "")
            scraper.practice['address'] = practice['Address1_Line1'] + ", " + ((practice['Address1_Line2'] + ", ") if practice['Address1_Line2'] else "") + practice['Address1_Line3'] + ((", " + practice['Address1_City']) if practice['Address1_City'] else "")
            scraper.practice['phone'] = practice['Telephone']

            scraper.practice['prices'] = []

            for fee in practice['PracticeFees']:
                fee_item = {
                    'age': scrapers.getFirstNumber(fee['AgeBand']),
                    'price': scrapers.getFirstNumber(fee['Fee'])
                }

                scraper.practice['prices'].append(fee_item)

            scraper.practice['prices'].sort(key=operator.itemgetter('age'))
            scraper.finishPractice()

    result = scraper.finish()

    with open(current_dir + 'data.json', 'w') as outfile:
        json.dump(result, outfile)

    return result