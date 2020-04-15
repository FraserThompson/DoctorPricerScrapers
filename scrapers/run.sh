#! /bin/sh

echo "Testing $1"

if [ "$1" == "all" ]; then
    python -c "from scrapers import run; run.all();"
else
    if [ ! -z "$2" ]; then
        python -c "from scrapers import run; run.one('$1', '$2');"
    else
        python -c "from scrapers import run; run.one('$1');"
    fi
fi