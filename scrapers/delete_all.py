import csv, json
import os, sys, codecs
import requests, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import scrapers

#stupid shit because the windows console can't print stuff properly
sys.stdout = codecs.getwriter('cp850')(sys.stdout.buffer, 'xmlcharrefreplace')
sys.stderr = codecs.getwriter('cp850')(sys.stderr.buffer, 'xmlcharrefreplace')

practices = scrapers.Database.findQuery("pho=Procare%20Networks")

for practice in practices:
	scrapers.Database.deletePractice(practice['name'])