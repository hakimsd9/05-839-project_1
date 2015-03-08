"""
Preprocessing on http://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data.aspx
in order to concatenate with other data files
Rename the states using their abreviations
Regroup data by county (regroup the census tracts)

- LILATracts_1And10: Low income and low access measured at 1 and 10 miles
(original food desert measure)
 binary variable
 Since the variable depends on the census tract, we use a majority vote
 to get it for each county (eg. if a county has 2 zeros and 1 one, then vote 0)


- POP2010: Population, tract total
         -> sum over the tracts


output csv format:
State name \t County \t Population \t LILATracts_1And10
"""

from csv import reader, writer
    # IMPORTANT write everything in lower case
    # NOTA no need to use intermediate file. TODO 

# Create a dictionary {state abbreviation:state name}
abbreviationsDic = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}


# Filter csv file so as to keep only the variables 
# State, County, LILATracts_1And10, and POP2010
# First write all the rows for the filtered variable
# Then regroup by county
def createIntermediateCsv(csvInput, csvOutput='foodDeserts_intermediate.csv', delim=','):
    filtered_vars = ['State', 'County', 'LILATracts_1And10', 'POP2010', 'Urban', 'LowIncomeTracts']
    with open(csvInput) as src, open(csvOutput, 'w', newline=',') as dst:
        rdr = reader(src, delimiter=delim)
        wrt = writer(dst, delimiter=delim)
        headers = next(rdr)
        wrt.writerow(filtered_vars)


        # save the indices of the variables
        for k in range(len(headers)):
            if headers[k] == 'State':
                state = k
            elif headers[k] == 'County':
                county = k
            elif headers[k] == 'LILATracts_1And10':
                lila = k
            elif headers[k] == 'POP2010':
                population = k
            elif headers[k] == 'Urban':
                urban = k
            elif headers[k] == 'LowIncomeTracts':
                lowIncomeTracts = k
        
        to_write = [[abbreviationsDic[row[state]]+'\t'+row[county].lower()+'\t'+row[lila]+'\t'+row[population]+'\t'+row[urban]+'\t'+row[lowIncomeTracts]] for row in rdr]

        wrt.writerows(to_write)

# regroup by county
def createFinalCsv(csvInput='foodDeserts_intermediate.csv', csvOutput='foodDeserts.csv',delim=','):
    # combine the data by county
    # majority vote for the nominal variables
    # sum the cardinal variables
    filtered_vars = ['State', 'County', 'LILATracts_1And10', 'POP2010', 'Urban', 'LowIncomeTracts']

    currentCounty = ''
    currentLILASum = 0
    currentPopulationSum = 0
    currentUrbanSum = 0
    currentLISum = 0
    counter = 0

    with open(csvInput) as src, open(csvOutput, 'w', newline = ',') as dst:
        rdr = reader(src, delimiter=delim)
        wrt = writer(dst, delimiter=delim)
        headers = next(rdr)
        wrt.writerow(filtered_vars)

        # save the indices of the variables
        for k in range(len(headers)):
            if headers[k] == 'State':
                state = k
            elif headers[k] == 'County':
                county = k
            elif headers[k] == 'LILATracts_1And10':
                lila = k
            elif headers[k] == 'POP2010':
                population = k
            elif headers[k] == 'Urban':
                urban = k
            elif headers[k] == 'LowIncomeTracts':
                lowIncomeTracts = k

        for row in rdr:
            row_split = row[0].split('\t')
            
            if row_split[county] == currentCounty:
                counter += 1
                currentLILASum = currentLILASum + float(row_split[lila])
                currentPopulationSum = currentPopulationSum + float(row_split[population])
                currentUrbanSum = currentUrbanSum + float(row_split[urban])
                currentLISum = currentLISum + float(row_split[lowIncomeTracts])
            else:
                # votes for the nominal values
                lilaResult = 1 if currentLILASum >= 0.5*counter else 0
                urbanResult = 1 if currentUrbanSum >= 0.5*counter else 0
                liResult = 1 if currentLISum >= 0.5*counter else 0

                if currentCounty != '':
                    to_write = [row_split[state]+'\t'+str(currentCounty)+'\t'+str(lilaResult)+'\t'+str(currentPopulationSum)+'\t'+str(urbanResult)+'\t'+str(liResult)]
                    wrt.writerow(to_write)
                
                currentCounty = row_split[county]
                currentLILASum = float(row_split[lila])
                currentPopulationSum = float(row_split[population])
                currentUrbanSum = float(row_split[urban])
                currentLISum = float(row_split[lowIncomeTracts])
                counter = 1

        # write the last element
        to_write = [row_split[state]+'\t'+str(currentCounty)+'\t'+str(lilaResult)+'\t'+str(currentPopulationSum)+'\t'+str(urbanResult)+'\t'+str(liResult)]
        wrt.writerow(to_write)
        
        
if __name__ == '__main__':
    from sys import argv
    createIntermediateCsv(argv[1])
    createFinalCsv()
