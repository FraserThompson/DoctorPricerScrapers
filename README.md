# Scrapers for DoctorPricer

## Starting it up

### Dependencies

If you want a virtualenv (it's like node_modules but for python) then do this:

`pip install virtualenv`
`virtualenv my_project`
`./my_project/Scripts/activate` 

Then:

`npm install`
`pip install -r py-requirements.txt`

### Running it

Webpack: `.\node_modules\.bin\webpack --config webpack.config.js --watch`
Django: `python manage.py runserver`
Postgres: `docker run --name some-postgres -p 5432:5432 -e POSTGRES_PASSWORD=password123 -d postgres`

## Scraping
`python run.py` will scrape all practices
`python run.py [name]` will scrape individual practice

## Deleting
`python delete.py [name']`

## Adding scrapers
Needs a file called scraper.py in the folder named after the pho.

1. Start by importing the global module: `import scrapers`
1. Define a function called `scrape(name)`
1. Instantiate a scraper object in the scrape function like this: `scraper = scrapers.Scraper(name)`
1. Use `scrapers.openAndSoup(url)` to open a url and turn it into something parseable
1. When you've found a practice use `scraper.newPractice(name, url, PHO, restriction)` and add more details like this: `scraper.practice['phone'] = '5555'`
1. When you've completed the practice use `scraper.postPractice()` to send it to the database
1. When you've completed all practices use `scraper.finish()` to write the logs to a file

other: `scraper.addError()`, `scraper.addWarning()`, `scraper.setLatLng([0, 0])`