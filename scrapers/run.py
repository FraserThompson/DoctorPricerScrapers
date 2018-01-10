import importlib, codecs, time, os, json
import traceback

failed = []

def one(name):
    
    module = importlib.import_module("scrapers." + name + ".scraper")

    return_object = {'data': None, 'error': None}

    try:
        return_object['data'] = module.scrape(name)
    except Exception as e:
        print(traceback.format_exc())
        return_object['error'] = traceback.format_exc()
        return return_object

    if os.environ['ENV'] == "dev":
        print(json.dumps(return_object, indent=4, sort_keys=True))
    
    return return_object

if __name__ == "__main__":
    import sys
    one(sys.argv[1])