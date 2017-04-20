# Scrapers for DoctorPricer

## Usage

### Setup

You'll just need Docker and docker-compose.

### Running it

Start it up with `docker-compose up --build`

Once Postgres is up run `docker-compose exec server migrate` to apply migrations.

Then `docker-compose exec server webpack-watch` and start develpoing.

### Adding scrapers
Needs a file called scraper.py in the folder named after the pho.

1. Start by importing the global module: `import scrapers`
1. Define a function called `scrape(name)`
1. Instantiate a scraper object in the scrape function like this: `scraper = scrapers.Scraper(name)`
1. Use `scrapers.openAndSoup(url)` to open a url and turn it into something parseable
1. When you've found a practice use `scraper.newPractice(name, url, PHO, restriction)` and add more details like this: `scraper.practice['phone'] = '5555'`
1. When you've completed the practice use `scraper.postPractice()` to send it to the database
1. When you've completed all practices use `scraper.finish()` to write the logs to a file

other: `scraper.addError()`, `scraper.addWarning()`, `scraper.setLatLng([0, 0])`