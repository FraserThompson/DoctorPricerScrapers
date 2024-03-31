# What's happening here?

This PHO in their infinite wisdom have blocked all traffic from certain countries, including the country which contains my server.

So instead of scraping from my server, we scrape locally and store it in a JSON, then absorb it on the server.

So we have a `local-scraper.py` which we run locally to scrape to a JSON file, and a `scraper.py` which we run on the server which just imports this JSON file.

To run this locally:

`docker compose run scraper-test procarenetworks local-scraper`