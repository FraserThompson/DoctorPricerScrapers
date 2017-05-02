import importlib, codecs, time
import traceback
from dp_server import models

failed = []

def import_all():

    modules = {}
    phos = models.Pho.objects.all()

    for obj in phos:
        modules[obj.module] = importlib.import_module("scrapers." + obj.module + ".scraper")

    return modules

def all():
    
    modules = import_all()

    for name, module in modules.items():
        try:
            module.scrape(name)
        except Exception as e:
            print("Failed!")
            failed.append("%s: %s \n" % (name, traceback.format_exc()))
            print(traceback.format_exc())
            continue

def one(name):
    
    module = importlib.import_module("scrapers." + name + ".scraper")

    return_object = {'data': None, 'error': None}

    try:
        return_object['data'] = module.scrape(name)
    except Exception as e:
        print(traceback.format_exc())
        return_object['error'] = traceback.format_exc()
    
    return return_object

if __name__ == "__main__":
    import sys
    one(sys.argv[1])