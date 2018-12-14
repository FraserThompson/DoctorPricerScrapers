#! /bin/sh

echo "Testing $1"

python -c "from scrapers import run; run.one('$1');"