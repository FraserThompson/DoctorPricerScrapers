import time
from bs4 import BeautifulSoup
import json
from urllib.request import urlopen, Request
import urllib.parse
import requests, ssl
import re, os
from difflib import SequenceMatcher as SM
from geopy.geocoders import GoogleV3

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

    GEOLOCATOR = GoogleV3(api_key=os.environ.get('GEOLOCATION_API_KEY'))

    def newPractice(self, name, url, pho, restriction=""):
        self.practice = {"name": name, "url": url, "pho": pho, "restriction": restriction, "active": True, "prices": [], "prices_csc": []}

    def openAndSoup(self, userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.23 Safari/537.36'):
        print("Accessing URL: " + self.practice["url"])
        req = Request(self.practice["url"], None, headers={'User-Agent': userAgent})
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

    # Geolocate
    def geolocate(self):

        if os.environ.get('ENV') and os.environ.get('ENV') != "dev":
            search_key = self.practice["address"] + ", New Zealand" if self.practice.get('address') else self.practice['name']
            coord, place_id, address, error = get_lat_lng(search_key)

            if not error:
                if coord: self.setLatLng(coord)
                if place_id: self.practice['place_id'] = place_id
                if address: self.practice['address'] = address
            else:
                self.addError("Could not geocode: " + error)

        else:
            coord = ['-45.86101900000001', '170.51175549999994'] # dummy cordinates in dev so we don't deplete our google supply
            self.setLatLng(coord)

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
        self.addWarning("Not enrolling patients.")

    def cprint(message, style):
        print(getattr(Scraper, style) + message + Scraper.ENDC)

    # Finish this practice.
    # One argument: An array of fields which should allow existing data to take priority over new data.
    # This is useful if the site sucks now, but it was ok in the past.
    def finishPractice(self, prioritizeExisting=[], debug=False):
        self.exists = Database.findPractice(self.practice["name"])

        self.practice['scraper_source'] = "Web" if 'scraper_source' not in self.practice else self.practice['scraper_source']

        self.practice["name"] = self.practice["name"].strip()

        # Prefer to use existing information to save on API limits
        if self.exists:

            if not self.practice.get('address') or 'address' in prioritizeExisting:
                self.practice['address'] = self.exists['address']

            if not self.practice.get('phone') or 'phone' in prioritizeExisting:
                self.practice['phone'] = self.exists['phone']

            # If the address hasn't changed we can use the existing co-ordinates
            if self.exists["address"] == self.practice["address"]:
                self.practice["place_id"] = refreshPlaceID(self.exists["place_id"])
                self.practice["lat"] = self.exists["lat"]
                self.practice["lng"] = self.exists["lng"]

        # If we still don't have location details then get them
        if not self.practice.get("place_id") or not self.practice.get("address") or not self.practice.get("lat"):
            self.geolocate()

        if not self.practice.get('phone'):
            self.practice["phone"] = "None supplied"
        else:
            self.practice["phone"] = self.practice["phone"].strip()
        
        # Verifying data
        if not self.practice.get("lat") or not self.practice.get("lng"):
            self.addError("No coordinates.")
            return

        if not self.practice.get('address'):
            self.addError("No address.")
            return

        # Clean address
        self.practice["address"] = self.practice["address"].strip()

        if "new zealand" not in self.practice["address"].lower():
            self.practice["address"] += ", New Zealand"

        ages = []
        for price in self.practice["prices"]:

            if price["age"] in ages:
                self.addWarning("Price already exists for this age: " + str(price["age"]))

            ages.append(int(price["age"]))

            if price["age"] > 80:
                self.addWarning("Possible issue with ages: " + str(price["age"]))
            if price["price"] > 100 and price["price"] != 999:
                self.addWarning("Possible issue with prices: " + str(price["price"]))

        # If we had prices but no zero price, we should add a zero price
        if 0 not in ages and len(self.practice["prices"]):
            self.practice["prices"].insert(0, {'age': 0, 'price': 0})

        if "prices_csc" in self.practice and len(self.practice["prices_csc"]) > 0:
            ages_csc = []
            for price in self.practice["prices_csc"]:

                if price["age"] in ages_csc:
                    self.addWarning("Price already exists for this age: " + str(price["age"]))

                ages_csc.append(int(price["age"]))

                if price["age"] > 80:
                    self.addWarning("Possible issue with ages: " + str(price["age"]))
                if price["price"] > 100 and price["price"] != 999:
                    self.addWarning("Possible issue with prices: " + str(price["price"]))

            # If we had CSC prices but no zero, we should add a zero
            if 0 not in ages_csc and len(self.practice["prices_csc"]):
                self.practice["prices_csc"].insert(0, {'age': 0, 'price': 0})

        if len(self.practice["name"]) > 60:
            self.addWarning("Possible issue with practice name: " + self.practice["name"])

        if len(self.practice["phone"]) > 14:
            self.addWarning("Possible issue with practice phone: " + self.practice["phone"])

        if len(self.practice["address"]) > 100:
            self.addWarning("Possible issue with practice address: " + self.practice["address"])

        if not self.practice["prices"] or len(self.practice["prices"]) == 0:
            self.addError("No prices.")

        if debug:
            print(self.practice)

        self.practice_list.append({'practice': self.practice, 'exists': self.exists})

    def doWeHaveItAlready(self, name):
        for practice in self.practice_list:
            if practice.get('practice') and practice['practice']['name'] == name:
                return True

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
# Geocodes an address
# Returns a threeple of latlng, place_id and address
def get_lat_lng(address):
    result = Scraper.GEOLOCATOR.geocode(address, exactly_one=True, region="nz")

    if result:
        place_id = result.raw.get('place_id', None)
        address = result.address if 'address' in result else None
        return ([result.latitude, result.longitude], place_id, address, False)
    else:
        return (None, None, None, result.error)

#####################################################################
# Refreshes the Place ID using Google's API (free request doesn't count towards limits)
def refreshPlaceID(placeId):
    req = requests.get('https://maps.googleapis.com/maps/api/place/details/json?fields=place_id&place_id=' + placeId + '&key=' + os.environ.get('GEOLOCATION_API_KEY'))

    if req.status_code != 200:
        Scraper.cprint("Failed to get PlaceID, will get new one: " + req.text, "WARNING")
        return None

    res = req.json()
    
    if res['status'] != 'NOT_FOUND' and res['status'] != 'INVALID_REQUEST':
        return res['result']['place_id']
    else:
        Scraper.cprint("Failed to get PlaceID, retaining original: " + req.text, "WARNING")
        return None

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
# Does a fuzzy string comparison and returns true if they're pretty similar
def fuzzyMatch(s1, s2):
    return True if SM(None, s1, s2).quick_ratio() > 0.7 else False

#####################################################################
# Checks if a string is contained in something
def partial_match(string, dictin):
    result = None
    for key in dictin:
        print('does ' + key + ' start with ' + string)
        if key.startswith(string):
            print('yes')
            result = dictin.get(key)
            break
    # Go for a less accurate search if nothing is found
    # just try to match the first three words
    if not result:
        for key in dictin:
            if key.startswith(' '.join(string.split()[:2])):
                result = dictin.get(key)
                break
    return result

#####################################################################
# Opens a URL and returns soup
def openAndSoup(url, userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.23 Safari/537.36'):
    time.sleep(3) # don't want to be too aggressive
    print("Accessing URL: " + url)
    req = Request(urllib.parse.quote_from_bytes(url.encode('utf-8'), safe='/:'), None, headers={'User-Agent': userAgent})
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    return BeautifulSoup(urlopen(req, context=context).read().decode('utf-8', 'ignore'), 'html5lib')

#####################################################################
# Give it a find('a').stripped_strings and it MIGHT end up with a better result than strip=true
# Good for addresses
def better_strip(string):
	return ', '.join(string).replace('\xa0', ' ').replace('  ', ' ').strip()

#####################################################################
# Make a string more normal
def normalize(input, keepSpaces=False):
    string = re.sub('[^0-9a-zA-Z ]+', '', input.strip().lower().replace('mt ', 'mount '))
    string = re.sub(' +',' ', string)
    if keepSpaces:
        return string
    else:
        return string.replace(' ', '')

#####################################################################
# Replace spaces in a string with dashes
def replaceSpacesWithDashes(input):
    normal = re.sub('[^0-9a-zA-Z ]+', '', input.strip())
    return normal.lower().replace(' ', '-') + "/"

#####################################################################
# Replace spaces in a string with plusses
def replaceSpacesWithPluses(input):
    normal = re.sub('[^0-9a-zA-Z ]+', '', input.strip())
    return normal.lower().replace(' ', '+')

#####################################################################
# Turn a string into A URL
def urlify(input):
    return input.replace("'", '%27').replace('"', '%27').replace('+', '%2b').replace(' ', '%20').replace(':', '%3a')

#####################################################################
# Returns the first number in a string. Also does some replacing of common words into numbers. Good for prices.
def getFirstNumber(string):
    try:
        result = float(re.findall('[-+]?\d*\.\d+|\d+', string.lower().replace("koha", "0").replace("adults", "18").replace("no charge", "0").replace('zero', '0').replace("free", "0").replace("n/a", "999").replace("under", "0").replace("--", "0"))[0])
    except IndexError:
        result = 1000
    return result

#####################################################################
# Takes a stab at scraping details from a healthpoint page.
# Returns a practice object and takes a soup.
def scrapeHealthpoint(url):
    practiceSouped = openAndSoup(url)
    practice = {}

    practice['url'] = url
    practice['name'] = practiceSouped.find('div', {'id': 'heading'}).find('h1').get_text(strip=True)

    try:
        practice['address'] = practiceSouped.find('div', {'class': 'service-location'}).find('h3').get_text(strip=True)
    except:
        return

    practice['phone'] = practiceSouped.find('ul', {'class', 'contact-list'}).find('p').get_text(strip=True)
    
    map_el = practiceSouped.find('div', {'class', 'map'})
    if (map_el):
        coords = map_el.get('data-position').split(",")
        practice['lat'] = coords[0].strip()
        practice['lng'] = coords[1].strip()

    enrolling_el = practiceSouped.find('div', {'id': 'section-books'})

    if enrolling_el:
        enrolling = enrolling_el.find('h4').get_text(strip=True) == "Yes"
        if not enrolling:
            practice['active'] = False

    fees_section = practiceSouped.find('div', {'id': 'section-fees'})

    if fees_section:
        fees_table = fees_section.find('table')

        if fees_table:
            fees_rows = fees_table.find_all('tr')

            practice['prices'] = []
            practice['prices_csc'] = []

            header_count = 0
            ages_added = []

            for row in fees_rows:
                age_cell = row.find('th')
                
                # Most tables put the age in a th, some don't
                if age_cell:
                    age_text = age_cell.get_text(strip=True)
                    price_text = row.find('td').get_text(strip=True)
                else:
                    cells = row.find_all('td')

                    # If we're on a row with only one cell skip it
                    if len(cells) < 2:
                        continue

                    age_cell = cells[0]

                    # Guessing if we're in a header based on boldness of the text
                    if age_cell.find('strong'):

                        header_count += 1
                        
                        # If we're in the next section we've gone too far
                        if header_count == 2:
                            break

                        continue

                    age_text = age_cell.get_text(strip=True)

                    price_cell = cells[1]
                    price_text = price_cell.get_text(strip=True)

                age = int(getFirstNumber(age_text))
                price = getFirstNumber(price_text)

                # If we already have this age... Well I mean we can't have it again
                if age in ages_added:
                    continue

                # If we couldn't get an age, we can probably bounce
                if age == 1000:
                    break

                price = {
                    'age': age,
                    'price':  price,
                }

                age_text_lower = age_text.lower()
                
                if ("community services" in age_text_lower and "without" not in age_text_lower) or ("csc" in age_text_lower and "without" not in age_text_lower):
                    practice['prices_csc'].append(price)
                else:
                    ages_added.append(age)
                    practice['prices'].append(price)

    return practice


#####################################################################
# Scrape from a data.json file
def localScrape(inFile, name):
    
    scraper = Scraper(name)

    prac_dict = json.load(inFile)

    for practiceObj in prac_dict:
        
        practice = practiceObj['practice'] if 'practice' in practiceObj else practiceObj

        if 'prices' in practice and practice['prices'] and 'lat' in practice and practice['lat']:
            scraper.newPractice(practice['name'], practice['url'], practice['pho'], practice['restriction'])
            scraper.practice = practice
            scraper.practice['scraper_source'] = "Manual"
            scraper.finishPractice()

    return scraper.finish()

def parseAgeHeader(th):
    ages = []
    for age in th[1:]:
        ages.append(getFirstNumber(age.get_text(strip=True)))
    return ages