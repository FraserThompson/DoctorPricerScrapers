import importlib, codecs, time
import traceback

phos = [
    'alliance',
    'aucklandpho',
    'centralpho',
    'compasshealth',
    'comprehensivecare',
    'easternbaypho',
    'easthealth',
    #'haurakipho',
    'healthhb',
    'lowerhutt',
    'malborough',
    'manaia',
    'midlands',
    'nationalhauora',
    'nelsonbays',
    'nmo',
    'nph',
    'procare',
    'ra',
    'rcpho',
    'scdhb',
    'southernpho',
    'tetaitokerau',
    'wboppho',
    'westcoast',
    'wrpho',
    '#manual'
]

modules = {}
failed = []

for name in phos:
    modules[name] = importlib.import_module("scrapers." + name + ".scraper")

def all():
    for name, module in modules.items():
        try:
            module.scrape(name)
        except Exception as e:
            print("Failed!")
            failed.append("%s: %s \n" % (name, traceback.format_exc()))
            print(traceback.format_exc())
            continue

def one(name):
    try:
        modules[name].scrape(name)
    except Exception as e:
        print("Failed!")
        failed.append("%s: %s \n" % (name, traceback.format_exc()))
        print(traceback.format_exc())

    if len(failed) > 0:
        fail_file = codecs.open('not_scraped' + str(time.time()) + '.txt', encoding='utf-8', mode='w')
        for fail in failed:
            fail_file.write(fail)

        fail_file.close()

if __name__ == "__main__":
    import sys
    one(sys.argv[1])