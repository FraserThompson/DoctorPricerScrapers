# Scrapers for DoctorPricer

## Usage

### Setup

You'll just need Docker and docker-compose (and node if you want to use the easy npm scripts)

Start it up with `npm start`

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

Start it up with `npm start`

Once Postgres is up run `npm run migrate` to apply migrations.

#### Deploying it

Scripts in `./_ops` are for managing the live deployment. These are bash scripts, so you gotta run them in a bash shell. We also have a package.json for standardizing how we run scripts across projects.

I use Dockerhub for my docker images. To build and push use `npm run docker-push`.

To deploy it run `npm run deploy` from the root directory.

#### Provisioning a brand new server

To provision a new server:

1. Run `DP_SERVER=[whatever] ./_ops/provision.sh`. This upgrades the distribution and adds a user called fraser with sudo permissions
1. SSH in to verify you can, and then disable SSH for the root user by editing `/etc/ssh/sshd_config` and changing `PermitRootLogin yes` to `PermitRootLogin no` then restart SSH with `service ssh restart`

Before you deploy you'll need to point the DNS at it since it needs to be on the domain for letsencrypt to work.

Then it's ready to be deployed with the deploy script.

### Backups

# Prod

To trigger a backup on the remote of the live data run `npm run backup-live`.

To get the latest backup you just made so you can use it locally run `npm run backup-get`.

To restore the latest backup on the remote, put a backup file in `~/docker-services/doctorpricer/restore` then run `npm run restore-live`.

# Dev

To backup run `npm run backup-dev` and it'll backup to `./backups` in a file called backup.

To restore run `npm run restore-dev` and it'll restore `./backups/backup`. You'll need to run `npm start` after to get the dev user back.

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

To do this run `npm run test [scraper]`. It'll run the scraper and spit the output to scrapers/data.json for your perusal.

### Cleaning

It turns out that practices will change their names quite a lot online for no good reason, meaning we end up with lots of duplicated practices.

To combat this I made a cleaning method which can be accessed from the homepage of the scrapers UI and does this:

1. Search for practices with addresses similar to other addresses (ie. 39 Something Road, Suburb, Auckland and 39 Something Road, Auckland)
1. Search for practices within 10m of each other
1. Delete them following this algorithm

1. If one is newer, keep that and disable the others
1. If they're all the initial date (ie. haven't been touched since we added creation dates) disable the ones with the smallest IDs (these are presumably older)

We don't delete anything because then we'd lose price history, so we just disable them which means they won't show up anywhere.

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

If you get some bullshit about the migration PKEY being wrong then I guess the migrations table got messed up somehow, try reindexing it after logging into psql:

`REINDEX TABLE django_migrations;`

If you have an issue with old data needing to be altered for a scheme change you can get into a db shell with

`python manage.py dbshell`

Then run a query like:

`UPDATE dp_server_prices SET csc = False;`

If the backup can't backup because of permissions, make sure the directory outside Docker has the same UID as the one inside. This means for Django www-data.

`sudo chown www-data:www-data backups`

If you can't restore a backup because of index not existing errors... Just edit the .psql file and replace `DROP INDEX` with `DROP INDEX IF EXISTS ` (this is weird, idk why it does that)

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

A log is made each time a scraper is run. These are displayed under each PHO/scraper at data.doctorpricer.co.nz.

##### Prices

Each practice has prices associated with it. These are seperate objects to make them easy to do database stuff with.
