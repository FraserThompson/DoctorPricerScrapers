import importlib, codecs, time, os, json
import traceback

def all():

    return_object = {'results': None, 'failed': None}
    scrapers = [ f.name for f in os.scandir('./') if f.is_dir() ]

    for scraper in scrapers:
        try:
            result = one(scraper)
            return_object['results'].append(result)
        except:
            print('FAILED ' + scraper)
            return_object['failed'].append(scraper)

    return return_object

def one(name, scraperFileName = "scraper"):
    
    module = importlib.import_module("scrapers." + name + "." + scraperFileName)

    return_object = {'data': None, 'error': None}

    try:
        return_object['data'] = module.scrape(name)
    except Exception as e:
        print(traceback.format_exc())
        return_object['error'] = traceback.format_exc()
        return return_object

    if os.environ.get('ENV') == "dev" or os.environ.get('ENV') == None:
        print(json.dumps(return_object, indent=4, sort_keys=True))

        with open('./scrapers/data.json', 'w+') as outfile:
            json.dump(return_object, outfile)
    
    return return_object

if __name__ == "__main__":
    import sys
    one(sys.argv[1])