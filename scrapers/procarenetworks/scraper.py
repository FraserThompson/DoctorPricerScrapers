import csv
import json
import os
import sys
import codecs
from scrapers import common as scrapers
current_dir = './scrapers/procarenetworks/'


def scrape(name):

    scraper = scrapers.Scraper(name)

    with open(current_dir + 'data.json', 'r') as inFile:

        prac_dict = json.load(inFile)

        for practiceObj in prac_dict['data']['scraped']:

            practice = practiceObj['practice'] if 'practice' in practiceObj else practiceObj

            if 'prices' in practice and practice['prices'] and 'lat' in practice and practice['lat']:
                print(practice['name'])
                scraper.newPractice(
                    practice['name'], practice['url'], practice['pho'], practice['restriction'])
                scraper.practice = practice
                scraper.finishPractice()

    return scraper.finish()
