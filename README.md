# Scrapers for DoctorPricer

## Usage

### Setup

You'll just need Docker and docker-compose.

### Model

#### PHO

Create a PHO For each scraper.

#### Practice

Scrapers make these when they scrape. Each is associated with a PHO.

#### Log

A log is made each time a scraper is run.

##### Prices

Each practice has prices associated with it.

### Running it

#### Environment variables 

* DATABASE_PASSWORD
* SECRET_KEY

Start it up with `docker-compose up --build`

Once Postgres is up run `docker-compose exec server migrate` to apply migrations.

#### Accessing the admin backend

1. `docker-compose exec server createsuperuser` to make a superuser
2. Navigate to https://localhost:8443/admin and log in with those credentials

#### Doing a Manual import

1. Put data.json into `_manual`
2. Create a PHO with the module name `_manual`
3. Run `scrape` on `_manual`, this will create PHOs too
4. Run `submit`on the new PHOs

### Adding scrapers
Needs a file called scraper.py in the folder named after the pho.

1. Start by importing the global module: `from scrapers import common as scrapers`
1. Define a function called `scrape(name)`
1. Instantiate a scraper object in the scrape function like this: `scraper = scrapers.Scraper(name)`
1. Use `scrapers.openAndSoup(url)` to open a url and turn it into something parseable
1. When you've found a practice use `scraper.newPractice(name, url, PHO, restriction)` and add more details like this: `scraper.practice['phone'] = '5555'`
1. When you've completed the practice use `scraper.finishPractice()` to finish with it
1. When you've completed all practices `return scraper.finish()` 

other: `scraper.addError()`, `scraper.addWarning()`, `scraper.setLatLng([0, 0])`

### Testing scrapers

Because of weirdness you've got to run a scraper like this when you're devving on them or testing them or whatever:

`python -c "from scrapers import run; run.one('alliancehealthplus');"`

Some day I'll improve this.