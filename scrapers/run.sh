#! /bin/sh

echo "Testing $1"

if [ "$1" == "all" ]; then
    python -c "from scrapers import run; run.all();"
else
    python -c "from scrapers import run; run.one('$1');"
fi