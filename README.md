# Scrapers for DoctorPricer

## Usage

### Setup

You'll just need Docker and docker-compose.

Start it up with `docker-compose up --build -d`

Then you can get to the admin interface on `https://localhost:8443/admin` and login with the dev credentials which are `fraserdev` and `dev`.

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

To deploy it run `DP_SERVER=[whatever]./_ops/deploy.sh` from the root directory.

#### Provisioning a brand new server

To provision a new server:

1. Run `DP_SERVER=[whatever] ./_ops/provision.sh`. This upgrades the distribution and adds a user called fraser with sudo permissions
1. SSH in to verify you can, and then disable SSH for the root user by editing `/etc/ssh/sshd_config` and changing `PermitRootLogin yes` to `PermitRootLogin no` then restart SSH with `service ssh restart`

Now it's ready to be deployed with the deploy script.

### Backups

# Prod

The scripts in `./_ops` are for fiddling with the remote server. To trigger a backup on the remote of the live data run `./_ops/backup.sh`.

To get the latest backup you just made so you can use it locally run `./_ops/backup_get.sh`.

# Dev

To backup run `docker-compose -f docker-compose.extra.yml run backup` and it'll backup to `./backups` in a file called backup.

To restore run `docker-compose -f docker-compose.extra.yml run restore` and it'll restore `./backups/backup`.

DEV GOTCHA: In dev the password is `password123` so you might to prepend these commands with `PGPASSWORD=password123`

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

I made a docker image for testing them in Docker so we don't have to mess up our user environment!!!!

To do this run `docker-compose run scraper-test [scraper]`. It'll run the scraper and spit the output to scrapers/data.json for your perusal.

### Big disaster hints

If you get:

`OperationalError: could not access file "$libdir/postgis-X.X`

On a new deploy that means the postgis image has updated their version of postgis. To fix it run the built in update-postgis script:

`docker exec doctorpricer-postgres_1 update-postgis.s`

If this gives you some annoying error about there not being a root role then you'll have to run its commands manually. 

Get in the db with:

`psql --user=postgres --dbname="postgres"`

Then run those ALTER commands.

https://github.com/appropriate/docker-postgis/blob/master/update-postgis.sh

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
