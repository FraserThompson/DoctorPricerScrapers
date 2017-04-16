from bs4 import BeautifulSoup, Comment
import json
from urllib.request import urlopen, Request
import urllib.parse
import requests, ssl
from requests.auth import HTTPBasicAuth
import httplib2
import re, sys
import codecs
from datetime import datetime, date
from pygeocoder import Geocoder

################### DATABASE ###########################################
# Contains all logic for interacting with the database.
# Not to be instantiated.
class Database:
    apiUrl = 'https://api.doctorpricer.co.nz/api/dp/'

    #################################################
    # Post a practice to the database
    def addPractice(practice, exists):
        headers = {'Content-type': 'application/json'}

        if exists == 0:
            Scraper.cprint("Inserting: " + str(practice), "OKGREEN")
            r = requests.post(Database.apiUrl + 'update', headers=headers, json=practice, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))
        else:
            Scraper.cprint("Updating: " + str(practice), "OKGREEN")
            r = requests.put(Database.apiUrl + 'update/' + urllib.parse.quote(practice['name']), headers=headers, json=practice, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))
            response_json = r.json()

        if (r.status_code != 200):
            print("Posting" + practice['name'] + " produced HTTP error: "  + str(r.status_code))
        return r

    ################################################
    # Delete a practice from the database
    def deletePractice(name):
        r = requests.post(Database.apiUrl + 'update/' + name, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))
        Scraper.cprint("Deleting...", "WARNING")
        if (r.status_code != 200):
            print("Deleting " + name + " produced HTTP error: " + str(r.status_code))
        print(r)

    ################################################
    # Find a practice in the database
    def findPractice(name):
        exists = requests.get(Database.apiUrl + 'practices?name=' + urllib.parse.quote(name))
        if exists.status_code != 200 or exists.json()['rowCount'] == 0:
            return 0
        else:
            return exists.json()['rows'][0]

   ################################################
    # Find all via a query
    def findQuery(name):
        exists = requests.get(Database.apiUrl + 'practices?' + urllib.parse.quote(name))
        if exists.status_code != 200 or exists.json()['rowCount'] == 0:
            return 0
        else:
            return exists.json()['rows']

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

    # geolocate()
    # Called before each submission. Gets the place_id from Google using the coordinates
    # If there are no coords it will try to geolocate based on address.
    def geolocate(self):
        if not self.practice.get('lat'):
            try:
                result_array = Geocoder.geocode(self.practice['address'] + ", New Zealand")
                coord = result_array[0].coordinates
            except:
                self.addWarning("Could not geocode address: " + self.practice['address'])
                return 0

            self.practice['lat'] = coord[0]
            self.practice['lng'] = coord[1]

        req = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?key=AIzaSyD2fzuhGAI8NIym12WKRkKKzQt-AzJqClE&location=" + str(self.practice['lat']) + "," + str(self.practice['lng']) + "&radius=30&query=" + self.practice['name'] + ' &key=' + self.google_key)
        if req.json()['status'] == 'OK':
            self.practice['place_id'] = req.json()['results'][0]['place_id']
        else:
            print('GOOGLE MAPS API OVER LIMIT')
            self.addWarning("Could not get place ID: " + req.json()['status'])

    def cprint(message, style):
        print(getattr(Scraper, style) + message + Scraper.ENDC)

    def openAndSoup(self):
        print("Accessing URL: " + self.practice['url'])
        req = Request(self.practice['url'], None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'})
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

    def finish(self):
        return {"name": self.name, "scraped": self.practice_list, "errors": self.error_list, "warnings": self.warning_list}

    def newPractice(self, name, url, pho, restriction):
        self.practice = {'name': name, 'url': url, 'pho': pho, 'restriction': ''}

    def finishPractice(self):
        exists = Database.findPractice(self.practice['name'])

        # Get Google place ID and/or geolocate the address if it's not already there
        if exists == 0 or not exists['place_id']:
            self.geolocate()
        else:
            self.practice['place_id'] = exists['place_id']
            self.practice['lat'] = exists['lat']
            self.practice['lng'] = exists['lng']

        if not self.practice.get('phone'):
            self.practice['phone'] = "None supplied"
        
         # Verify data
        for price in self.practice['prices']:
            if price['age'] > 70:
                self.addWarning("Possible issue with ages: " + str(price['age']))
            if price['price'] > 100 and price['price'] != 999:
                self.addWarning("Possible issue with prices: " + str(price['price']))

        if len(self.practice['name']) > 60:
            self.addWarning("Possible issue with: " + self.practice['name'])

        if len(self.practice['phone']) > 14:
            self.addWarning("Possible issue with: " + self.practice['phone'])

        if len(self.practice['address']) > 100:
            self.addWarning("Possible issue with: " + self.practice['address'])

        self.practice_list.append(self.practice)
        #Database.addPractice(self.practice, exists)

    def setLatLng(self, coord):
        self.practice['lat'] = coord[0]
        self.practice['lng'] = coord[1]

    def addWarning(self, message):
        self.warning_list.append(self.practice['url'] + " " + self.practice['name'] + ": " + message)

    def addError(self, message):
        self.error_list.append(self.practice['url'] + " " + self.practice['name'] + ": " + message)

    def notEnrolling(self):
        Scraper.cprint("Not enrolling.", "WARNING")
        self.addError("Not enrolling patients.")
        if Database.findPractice(self.practice['name']):
            Database.deletePractice(self.practice['name'])

    def __init__(self, name):
        Scraper.cprint("SCRAPING: " + name, "OKBLUE")
        self.current_dir = "./" + name
        self.name = name
        self.practice_list = []
        self.warning_list = []
        self.error_list = []

#####################################################################
# Delete a practice from the database
def deletePractice(practice_name):
    r = requests.post(apiUrl + 'update/' + practice_name, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))
    print(bcolors.WARNING + "Deleting..." + bcolors.ENDC)
    if (r.status_code != 200):
        print("Deleting " + practice_name + " produced HTTP error: " + str(r.status_code))
    print(r)

#####################################################################
# Find a practice in the database
def findInDatabase(name):
    exists = requests.get(apiUrl + 'practices?name=' + name)
    if exists.json()['rowCount'] == 0:
        return 0
    else:
        return exists.json()['rows'][0]

#####################################################################
# Post a practice to the database
def postToDatabase(practice, warning_list):
    print("posting: " + str(practice))

    # Verify data
    for price in practice['prices']:
        if price['age'] > 70:
            print("warning");
            warning_list.append(practice['name'] + " Possible issue with ages: " + str(price['age']))
        if price['price'] > 100 and price['price'] != 999:
            print("warning")
            warning_list.append(practice['name'] + " Possible issue with prices: " + str(price['price']))

    if len(practice['name']) > 60:
        print("warning")
        warning_list.append(practice['name'] + " Possible issue with: " + practice['name'])

    if len(practice['phone']) > 14:
        print("warning")
        warning_list.append(practice['name'] + " Possible issue with: " + practice['phone'])

    if len(practice['address']) > 100:
        print("warning")
        warning_list.append(practice['name'] + " Possible issue with: " + practice['address'])

    headers = {'Content-type': 'application/json'}

    exists = findInDatabase(practice['name'])
    if exists == 0:
        print(bcolors.HEADER + "Inserting..." + bcolors.ENDC)
        r = requests.post(apiUrl + 'update', headers=headers, json=practice, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))
    else:
        print(bcolors.HEADER + "Updating..." + bcolors.ENDC)
        # check if changed
        oldPrices = exists['prices']
        try:
            for i, price in enumerate(practice['prices']):
                if price['price'] > oldPrices[i]['price']:
                    print(bcolors.WARNING + "EXPENSIVER: Old for " + str(price['age']) + " was " + str(oldPrices[i]['price']) + " new is " + str(price['price']) + bcolors.ENDC) 
                elif price['price'] < oldPrices[i]['price']:
                    print(bcolors.WARNING + "CHEAPER: Old for " + str(price['age']) + " was " + str(oldPrices[i]['price']) + " new is " + str(price['price']) + bcolors.ENDC)
        except IndexError:
            print("whatever")

        r = requests.put(apiUrl + 'update/' + practice['name'], headers=headers, json=practice, auth=('c7b20243-5b68-4ab8-81b6-6a89c954da22', '1dde7cea-4f71-4437-ace5-49a338c6b13c'))

    if (r.status_code != 200):
        print("Posting practice " + practice['name'] + " produced HTTP error" + str(r.status_code))
    try:
        return r.json()
    except ValueError:
        return r

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
    params['oauth_version'] = '1.0'
    params['oauth_nonce'] = oauth.generate_nonce()
    params['oauth_timestamp'] = str(int(time.time()))
    params['oauth_consumer_key'] = consumer.key
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
    if results['bossresponse']['responsecode'] != '200':
        print("URL Error: " + results['bossresponse']['responsecode'])
        return 0
    if results['bossresponse']['web']['totalresults'] != '0':
        return results['bossresponse']['web']['results'][0]['url']

#####################################################################
# DOESNT WORK ANYMORE
def bingSearch(searchString):
    BING_KEY = 'c19k1i8ZrV/k6NISLuTWF/94wndoxwst8FstA1OTDSU='
    url = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + urlify(searchString) + '%27&$top=10&$format=json'
    auth = HTTPBasicAuth(BING_KEY, BING_KEY)
    req = requests.get(url, auth=auth)
    return req.json()

#########################################################################
# Try's to find a practice URL by searching health websites.
# Takes an array as a parameter to fill up with possible sites.
# Returns 0 if fail, dict object of parameters if success
def getDetailsFromSearch(name):
    if name.strip() == '':
        return 0
    name = name.replace('&', ' and ')
    print('Trying to get url ' + name)
    results = bingSearch('(site:www.healthpages.co.nz OR site:www.healthpoint.co.nz OR site:www.itsmyhealth.co.nz) ' + name)['d']['results']

    if len(results) == 0: #if we have no results then it's a fail
        return 0

    return scrapeDetails([results[0]['Url']])

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
            result['url'] = url
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
        result['address'] = ", ".join(map_div.find('p').strings)
        result['phone'] = soup.find('ul', {'class':'contact-list'}).find('p').get_text()

        coord = map_div.get('data-position').split(', ')
        if not coord[0]:
            coord = geolocate(result[0] + ", Auckland")
        result['lat'] = float(coord[0])
        result['lng'] = float(coord[1])
    except AttributeError:
        return 0
    return result

def scrapeItsmyhealthDetails(soup):
    result = {}
    try:
        result['address'] = ', '.join(soup.find('dl', {'class':'medical-centre__address medical-centre__address_contact'}).find('dd').get_text().split('\n'))
        result['phone'] = soup.find('dl', {'class': 'medical-centre__details medical-centre__details_contact'}).find('dd').get_text(strip=True)
    except AttributeError:
        return 0
    try:
        coord = soup.find('div', {'class':'white-frame clearfix'}).find_all('script')[2].get_text().split('LatLng(')[1].split('),')[0].split(',')
        if coord == '' and coord == 0:
            coord = geolocate(result[0] + ", Auckland")
    except IndexError:
        coord = geolocate(result[0] + ", Auckland")

    result['lat'] = float(coord[0])
    result['lng'] = float(coord[1])
    return result

def scrapeHealthpagesDetails(soup):
    result = {}
    result['phone'] = soup.find('th', {'class': 'phone-number'}).get_text(strip=True)
    result['address'] = " ".join(soup.find('div', {'class': 'address_single'}).find('div', {'class', 'profile-contact'}).strings).strip()
    coord = soup.find('a', {'class': 'view-map'})['onclick'].split('", ')[2].split(', ')
    result['lat'] = float(coord[0])
    result['lng'] = float(coord[1])
    return result

def openAndSoup(url):
    print("Accessing URL: " + url)
    req = Request(url, None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'})
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

def dealWithFailure(error_list, warning_list, current_dir):
    if ((len(error_list) > 0) or (len(warning_list) > 0)):
        errorcount = str(len(error_list))
        warningcount = str(len(warning_list))
        print(errorcount +  " practices had errors.")
        print(warningcount +  " practices had warnings.")
        failed_file = codecs.open(current_dir + '//failed_list.txt', encoding='utf-8', mode='w')
        failed_file.write("============" + str(datetime.now()) + "===========\r\n")
        failed_file.write("============" + errorcount + "===========\r\n")
        for f in error_list:
            failed_file.write("ERROR %s\r\n" % f)
        failed_file.write("============" + warningcount + "===========\r\n")
        for w in warning_list:
            failed_file.write("WARNING %s\r\n" % w)
        failed_file.close()

def normalize(input):
    string = re.sub('[^0-9a-zA-Z ]+', '', input.strip().lower().replace('mt ', 'mount '))
    return re.sub(' +',' ', string).replace(' ', '')

    
def geolocate(address):
    # Try find the coordinates of the address for Google Maps to display
    if address == "":
        return [0, 0]
    try:
        result_array = Geocoder.geocode(address + ", New Zealand")
        coord = result_array[0].coordinates
    except:
        print("Could not geocode address: " + address)
        return [0, 0]
    return coord

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