# Scrapers for DoctorPricer

## Usage

### Setup

You'll just need Docker and docker-compose.

### Running it in production

#### Environment variables

* DATABASE_PASSWORD
* SECRET_KEY
* ADMIN_PASSWORD
* RABBITMQ_DEFAULT_PASS
* DOCKER_USERNAME
* DOCKER_PASSWORD
* GEOLOCATION_API_KEY

Start it up with `docker-compose up --build -d`

Once Postgres is up run `docker-compose exec server migrate` to apply migrations.

#### Deploying it

Scripts in `./_ops` are for managing the live deployment.

I use Dockerhub for my docker images, and it builds from git, so commit and push changes to git, then check Dockerhub to see when it's built.

To deploy it run `./_ops/deploy.sh` from the root directory.

To provision a new server run `DP_SERVER=[server adddress] ./_ops/provision.sh`.

### Backups

To backup run `docker-compose -f docker-compose.extra.yml run backup` and it'll backup to `./backups` in a file called backup.

To restore run `docker-compose -f docker-compose.extra.yml run restore` and it'll restore `./backups/backup`.

### Accessing the admin backend

1. Navigate to https://localhost:8443/admin and log in with your credentials

In dev this is `fraserdev` and `dev`.

### Doing a Manual import

1. Put data.json into `_manual`
2. Create a PHO with the module name `_manual`
3. Run `scrape` on `_manual`, this will create PHOs too
4. Run `submit`on the new PHOs

### Adding scrapers

Needs a file called scraper.py in the folder named after the PHO.

1. Start by importing the global module: `from scrapers import common as scrapers`
1. Define a function called `scrape(name)`
1. Instantiate a scraper object in the scrape function like this: `scraper = scrapers.Scraper(name)`
1. Use `scrapers.openAndSoup(url)` to open a url and turn it into something parseable
1. When you've found a practice use `scraper.newPractice(name, url, PHO, restriction)` and add more details like this: `scraper.practice['phone'] = '5555'`
1. When you've completed the practice use `scraper.finishPractice()` to finish with it
1. When you've completed all practices `return scraper.finish()`

The pricing object should be under `scraper.practice['prices']` and should like a bit like this:

```JSON
[
    {"age": 0, "price": 0},
    {"age": 13, "price": 20},
]
```

If don't provide a latitude, longitude then it will geolocate these based on the address. If you don't supply an address then it will try to geolocate based on the name. 

If you don't provide a phone number it will default to "None supplied"

other: `scraper.addError()`, `scraper.addWarning()`, `scraper.setLatLng([0, 0])`

### Testing scrapers

Because of weirdness you've got to run a scraper like this when you're devving on them or testing them or whatever:

`python -c "from scrapers import run; run.one('alliancehealthplus');"`

Some day I'll improve this (or maybe just make a script which does this)

### Model

#### PHO

Each Scraper needs a PHO object.

##### Required

* name
* module

##### Optional

* website
* region

#### Practice

Scrapers make these when they scrape. Each is associated with a PHO.

##### Required

* name
* address
* pho
* url
* lat
* lng

##### Optional

* phone
* restriction
* place_id

#### Log

A log is made each time a scraper is run. These are displayed under each PHO/scraper at stats.doctorpricer.co.nz.

##### Prices

Each practice has prices associated with it. These are seperate objects to make them easy to do database stuff with.
