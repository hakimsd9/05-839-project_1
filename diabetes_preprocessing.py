"""
Preprocess http://www.cdc.gov/diabetes/atlas/countydata/DMPREV/DM_PREV_ALL_STATES.xls
1. Transform 'year' as an attribute
2. Lowercase state and county names
3. Reorganize data

output format:
year, state, county, number, percent, lower confidence, upper confidence, age-adjusted percent, age-adjusted lower confidence, age-adjusted upper confidence limit
"""

import csv
data = {}
year = []
for i in range(2004, 2012):
	year.append(str(i))
fout = csv.writer(open('diabetes.csv', 'wb'))
with open("DM_PREV_ALL_STATES.csv", 'rU') as csvfile: 
	rdr = csv.reader(csvfile, delimiter=',')
	ls = list(rdr)

	header = ls[1][3:10]
	header.insert(0, 'year')
	header.insert(1, 'state')
	header.insert(2, 'county')
	body = ls[2:3148]
	# Remove keyword ' County' after county names
	for row in body:
		a = row[2].find(' County')
		if a != -1:
			row[2] = row[2][0:a]
	for y in year:
		data[y] = []
	# Extract data of each year from single row
	for row in body:
		index = 3
		for y in year:
			r = row[index:index+7]
			r.insert(0, y)
			r.insert(1, row[0].lower())
			r.insert(2, row[2].lower())
			data[y].append(r)
			index = index + 7
	# Output .csv file
	fout.writerow(header)
	for y in year:
		for row in data[y]:
			fout.writerow(row)
fout.close()