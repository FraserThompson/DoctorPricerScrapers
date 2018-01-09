from bs4 import BeautifulSoup, Comment
import json
from urllib.request import urlopen, Request
import urllib.parse
import requests, ssl
from requests.auth import HTTPBasicAuth
import httplib2
import re, sys, os
import codecs
from datetime import datetime, date
from pygeocoder import Geocoder

################### DATABASE ###########################################
# Contains all logic for interacting with the database.
# Not to be instantiated.
class Database:
    apiUrl = 'https://api.doctorpricer.co.nz/dp/api/'

    ################################################
    # Find a practice in the database
    def findPractice(name):
        exists = requests.get(Database.apiUrl + 'practices/?name=' + urllib.parse.quote(name))
        response = exists.json()

        if exists.status_code != 200 or len(response) == 0:
            return 0
        else:
            return response[0]

   ################################################
    # Find all via a query
    def findQuery(name):
        exists = requests.get(Database.apiUrl + 'practices/?' + urllib.parse.quote(name))
        response = exists.json()

        if exists.status_code != 200 or len(response) == 0:
            return 0
        else:
            return response[0]

############################# SCRAPER #################################
# Common methods and logic for scraping.
# Should be instantiated with the name of the directory before scraping.
class Scraper:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    google_key = 'AIzaSyCoNNjdQ4ZGHJhP5HwiLf0mnjydOc2iwik'

    def newPractice(self, name, url, pho, restriction):
        self.practice = {"name": name, "url": url, "pho": pho, "restriction": '', "active": True}

    def openAndSoup(self):
        print("Accessing URL: " + self.practice["url"])
        req = Request(self.practice["url"], None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'})
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

    # Geolocate using Google Maps API
    def geolocate(self):
        if os.environ['ENV'] != "dev":
            try:
                result_array = Geocoder.geocode(self.practice["address"] + ", New Zealand")
                coord = result_array[0].coordinates
                self.practice["lat"] = coord[0]
                self.practice["lng"] = coord[1]
            except:
                self.addWarning("Could not geocode address: " + self.practice["address"])
                return 0
        else:
            coord = ['-45.86101900000001', '170.51175549999994'] # dummy cordinates in dev so we don't deplete our google supply

    # Gets the place ID
    def get_place_id(self):
        if os.environ['ENV'] != "dev":
            req = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?location=" + str(self.practice["lat"]) + "," + str(self.practice["lng"]) + "&radius=30&query=" + self.practice["name"] + ' &key=' + self.google_key)

            if req.json()["status"] == 'OK':
                self.practice["place_id"] = req.json()["results"][0]["place_id"]
                return 1
            else:
                print('GOOGLE MAPS API OVER LIMIT')
                self.addWarning("Could not get place ID: " + req.json()["status"])
                return 0
        else:
            self.practice["place_id"] = "100"

    def setLatLng(self, coord):
        self.practice["lat"] = coord[0]
        self.practice["lng"] = coord[1]

    def addWarning(self, message):
        self.warning_list.append(self.practice["url"] + " " + self.practice["name"] + ": " + message)

    def addError(self, message):
        self.error_list.append(self.practice["url"] + " " + self.practice["name"] + ": " + message)

    def notEnrolling(self):
        Scraper.cprint("Not enrolling.", "WARNING")
        self.practice["active"] = False
        self.addError("Not enrolling patients.")

    def cprint(message, style):
        print(getattr(Scraper, style) + message + Scraper.ENDC)

    def finishPractice(self):
        self.exists = Database.findPractice(self.practice["name"])

        # Use existing information if address hasn't changed
        if self.exists and self.exists["address"] == self.practice["address"]:
            self.practice["place_id"] = self.exists["place_id"]
            self.practice["lat"] = self.exists["lat"]
            self.practice["lng"] = self.exists["lng"]

        # If we don't have coordinate data then geolocate
        if 'lat' not in self.practice or not self.practice['lat']:
            self.geolocate()

        # If we still don't have the place ID then get it
        if 'place_id' not in self.practice or not self.practice["place_id"]:
            self.get_place_id()

        if 'phone' not in self.practice or not self.practice.get('phone'):
            self.practice["phone"] = "None supplied"
        
        # Verify data
        ages = []
        for price in self.practice["prices"]:

            if price["age"] in ages:
                self.addWarning("Price already exists for this age: " + str(price["age"]))

            ages.append(price["age"])

            if price["age"] > 70:
                self.addWarning("Possible issue with ages: " + str(price["age"]))
            if price["price"] > 100 and price["price"] != 999:
                self.addWarning("Possible issue with prices: " + str(price["price"]))

        if len(self.practice["name"]) > 60:
            self.addWarning("Possible issue with: " + self.practice["name"])

        if len(self.practice["phone"]) > 14:
            self.addWarning("Possible issue with: " + self.practice["phone"])

        if len(self.practice["address"]) > 100:
            self.addWarning("Possible issue with: " + self.practice["address"])

        self.practice_list.append({'practice': self.practice, 'exists': self.exists})

    def finish(self):
        return {"name": self.name, "scraped": self.practice_list, "errors": self.error_list, "warnings": self.warning_list }

    def __init__(self, name):
        Scraper.cprint("SCRAPING: " + name, "OKBLUE")
        self.current_dir = "./" + name
        self.name = name
        self.practice_list = []
        self.warning_list = []
        self.error_list = []

#####################################################################
# Return student if student is contained in the string
def checkForStudent(string):
    if "student" in string.lower():
        return "student"
    return ""

#####################################################################
# Converst an array of strings into floats
def coordsToFloat(coords):
    return [float(string) for string in coords]

#####################################################################
# Returns the first number in a string
def getFirstNumber(string):
    return float(re.findall('[-+]?\d*\.\d+|\d+', string)[0])

#####################################################################
# Checks if a string is contained in something
def partial_match(string, dictin):
    result = ""
    for key in dictin:
        if key.startswith(string):
            result = dictin.get(key)
            break
    # Go for a less accurate search if nothing is found
    if len(result) == 0:
        for key in dictin:
            if key.startswith(' '.join(string.split()[:2])):
                result = dictin.get(key)
                break
    return result

#####################################################################
# Does an Oauth request
def oauth_request(url, params={}):
    oauth_key = 'dj0yJmk9MGFaZE1MY1k3eVZYJmQ9WVdrOVVXTm1iWGRDTm1jbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD0xMg--'
    oauth_secret = 'f57f0b969e9eab5262786c33e7f9519345bf24b2'
    consumer = oauth.Consumer(key=oauth_key, secret=oauth_secret)
    params["oauth_version"] = '1.0'
    params["oauth_nonce"] = oauth.generate_nonce()
    params["oauth_timestamp"] = str(int(time.time()))
    params["oauth_consumer_key"] = consumer.key
    req = oauth.Request(method="GET", url=url, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    return req

#####################################################################
# Healthpages get their own method because they're weird about stuff
def getHealthpagesURLFromSearch(name):
    name = name.replace('&', ' and ')
    print('Trying to get url ' + name)
    url = 'http://yboss.yahooapis.com/ysearch/web?q=' + urlify(name) +'&format=json&sites=www.healthpages.co.nz'
    req = oauth_request(url)
    req_opened = urlopen(req.to_url().replace('+', '%20'))
    results = json.loads(req_opened.read().decode())
    if results["bossresponse"]["responsecode"] != '200':
        print("URL Error: " + results["bossresponse"]["responsecode"])
        return 0
    if results["bossresponse"]["web"]["totalresults"] != '0':
        return results["bossresponse"]["web"]["results"][0]["url"]

#########################################################################
# Try's to find a practice URL by searching health websites.
# Takes an array as a parameter to fill up with possible sites.
# Returns 0 if fail, dict object of parameters if success
def getDetailsFromSearch(name):
    if name.strip() == '':
        return 0
    name = name.replace('&', ' and ')
    print('Trying to get url ' + name)
    results = bingSearch('(site:www.healthpages.co.nz OR site:www.healthpoint.co.nz OR site:www.itsmyhealth.co.nz) ' + name)["d"]["results"]

    if len(results) == 0: #if we have no results then it's a fail
        return 0

    return scrapeDetails([results[0]["Url"]])

########################################################################
# Try's to scrape details from each site in an array
# Returns result if success, and 0 if fail
def scrapeDetails(urls):
    for url in urls:
        print("Trying to scrape from: " + url)
        try:
            soup = openAndSoup(url)
        except:
            print("Failed to open soup for url: " + url)
            return 0

        if "itsmyhealth" in url:
            print("Scraping Itsmyhealth")
            result = scrapeItsmyhealthDetails(soup)

        elif "healthpages" in url:
            print("Scraping Healthpages")
            result = scrapeHealthpagesDetails(soup)

        elif "healthpoint" in url:
            print("Scraping Healthpoint")
            result = scrapeHealthpointDetails(soup)

        if result:
            result["url"] = url
            return result

    print("Couldn't find any details.")
    return 0

def scrapeHealthpointDetails(soup):
    result = {}
    books = soup.find('div', {'id': 'section-books'})
    if (books != None and books.find('h4').get_text() == 'Closed'):
        return 2
    try:
        map_div = soup.find('section', {'class':'service-map'}).find('div', {'class':'map'})
        result["address"] = ", ".join(map_div.find('p').strings)
        result["phone"] = soup.find('ul', {'class':'contact-list'}).find('p').get_text()

        coord = map_div.get('data-position').split(', ')
        if not coord[0]:
            coord = geolocate(result[0] + ", Auckland")
        result["lat"] = float(coord[0])
        result["lng"] = float(coord[1])
    except AttributeError:
        return 0
    return result

def scrapeItsmyhealthDetails(soup):
    result = {}
    try:
        result["address"] = ', '.join(soup.find('dl', {'class':'medical-centre__address medical-centre__address_contact'}).find('dd').get_text().split('\n'))
        result["phone"] = soup.find('dl', {'class': 'medical-centre__details medical-centre__details_contact'}).find('dd').get_text(strip=True)
    except AttributeError:
        return 0
    try:
        coord = soup.find('div', {'class':'white-frame clearfix'}).find_all('script')[2].get_text().split('LatLng(')[1].split('),')[0].split(',')
        if coord == '' and coord == 0:
            coord = geolocate(result[0] + ", Auckland")
    except IndexError:
        coord = geolocate(result[0] + ", Auckland")

    result["lat"] = float(coord[0])
    result["lng"] = float(coord[1])
    return result

def scrapeHealthpagesDetails(soup):
    result = {}
    result["phone"] = soup.find('th', {'class': 'phone-number'}).get_text(strip=True)
    result["address"] = " ".join(soup.find('div', {'class': 'address_single'}).find('div', {'class', 'profile-contact'}).strings).strip()
    coord = soup.find('a', {'class': 'view-map'})["onclick"].split('", ')[2].split(', ')
    result["lat"] = float(coord[0])
    result["lng"] = float(coord[1])
    return result

def openAndSoup(url):
    print("Accessing URL: " + url)
    req = Request(url, None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'})
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

def normalize(input):
    string = re.sub('[^0-9a-zA-Z ]+', '', input.strip().lower().replace('mt ', 'mount '))
    return re.sub(' +',' ', string).replace(' ', '')

def replaceSpacesWithDashes(input):
    normal = re.sub('[^0-9a-zA-Z ]+', '', input.strip())
    return normal.lower().replace(' ', '-') + "/"

def replaceSpacesWithPluses(input):
    normal = re.sub('[^0-9a-zA-Z ]+', '', input.strip())
    return normal.lower().replace(' ', '+')

def urlify(input):
    return input.replace("'", '%27').replace('"', '%27').replace('+', '%2b').replace(' ', '%20').replace(':', '%3a')

def getFirstNumber(string):
    try:
        result = float(re.findall('[-+]?\d*\.\d+|\d+', string.replace("No charge", "0"))[0])
    except IndexError:
        result = 1000
    return result