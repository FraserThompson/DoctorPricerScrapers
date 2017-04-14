import importlib, codecs, sys, time
import traceback

if len(sys.argv) < 2:
	phos = [
		'alliance',
		'aucklandpho',
		'centralpho',
		'christchurchpho',
		'compasshealth',
		'comprehensivecare',
		'easternbaypho',
		'easthealth',
		'haurakipho',
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
else:
	phos = []
	for arg in sys.argv[1:]:
		phos.append(arg)

modules = {}
failed = []

for name in phos:
	modules[name] = importlib.import_module(name + ".scraper")

for name, module in modules.items():
	try:
		module.scrape(name)
	except Exception as e:
		print("Failed!")
		failed.append("%s: %s \n" % (name, traceback.format_exc()))
		print(traceback.format_exc())
		continue

if len(failed) > 0:
	fail_file = codecs.open('not_scraped' + str(time.time()) + '.txt', encoding='utf-8', mode='w')
	for fail in failed:
		fail_file.write(fail)

	fail_file.close()