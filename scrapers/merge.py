import json
import glob2

json_files = []
data_out = []
count = 0

# Grab JSON files from subdirectories
for thing in glob2.glob('./*/data.json'):
	print(thing)
	with open(thing, 'r') as infile:
		json_files.append(json.load(infile))

# Merge the files into JSON object
for json_file in json_files:
	for item in json_file:
		count += 1
		data_out.append(item)

# Write JSON object to file
with open('data.json', 'w') as outfile:
	json.dump(data_out, outfile, ensure_ascii=False, sort_keys=True, indent=4)
	
with open('count.txt', 'w') as outfile:
	outfile.write(str(count))