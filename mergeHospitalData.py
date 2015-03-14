"""
Join tables Medicare Hospital Finding by Claim
            MedianZip
            Timely and effective care
            HCAPS by hospital
            
Variables kept:
From Timely and effective care
OP_6
OP_7
SCIP_INF_3
SCIP_CARD_2
SCIP_VTE_2
SCIP_INF_9
PN_6
HF_1
HF_2
IMM_2
Hospital name + address (for lat long retrieval using maps api)

from medicare hospital spending by claim
TOTAL expenditure for each hospital

from MedianZip
Median

from HCAPS
Percentages of respondents who answered:
"NO", patients would not recommend the hospital (they probably would not or definitely would not recommend it)
"YES", patients would definitely recommend the hospital
"YES", patients would probably recommend the hospital
Patients who gave a rating of "6" or lower (low)
Patients who gave a rating of "7" or "8" (medium)
Patients who gave a rating of "9" or "10" (high)
"""

from csv import reader, writer
import math

def saveMedian(medianZipFile, delim=','):
    """
    Read the MedianZip file, save the median for each Zip
    Save the smallest and the largest medians to divide the areas into n categories later
    """
    medians = dict()

    
    with open(medianZipFile) as src:
        rdr = reader(src, delimiter=delim)
        headers = next(rdr)
        
        for k in range(len(headers)):
            if headers[k] == 'Zip':
                zztop = k
            elif headers[k] == 'Median':
                median = k        
        for row in rdr:
            row_split = row
            #row_split = row.split(',')
            medians[row_split[zztop]] = row_split[median]
            
    return medians

def retrieveHCAPSInfo(hcaps,delim=','):
    """
    Retrieve percentages of respondents who answered
    "NO", patients would not recommend the hospital (they probably would not or definitely would not recommend it)
    "YES", patients would definitely recommend the hospital
    "YES", patients would probably recommend the hospital
    Patients who gave a rating of "6" or lower (low)
    Patients who gave a rating of "7" or "8" (medium)
    Patients who gave a rating of "9" or "10" (high)
    """
    ans = dict()
    potentialAnswers = ['\"NO\", patients would not recommend the hospital (they probably would not or definitely would not recommend it)',
    '\"YES\", patients would definitely recommend the hospital',
    '\"YES\", patients would probably recommend the hospital',
    'Patients who gave a rating of \"6\" or lower (low)',
    'Patients who gave a rating of \"7\" or \"8\" (medium)',
    'Patients who gave a rating of \"9\" or \"10\" (high)']

    with open(hcaps) as src:
        rdr = reader(src,delimiter=delim)
        headers = next(rdr)

        for k in range(len(headers)):
            if headers[k] == 'Provider ID':
                providerId = k
            if headers[k] == 'HCAHPS Answer Description':
                ansDesc = k
            if headers[k] == 'HCAHPS Answer Percent':
                percent = k

        for row in rdr :
            if not row[providerId] in ans:
                ans[row[providerId]] = dict()
            if row[ansDesc] in potentialAnswers:
                ans[row[providerId]][row[ansDesc]] = row[percent]

    return ans
            
def retrieveTimelyInfo(timelyAndEffectiveCare, delim=','):
    """
    Retrieve for each zip code the following info for each hospital:
        - OP_6
        - OP_7
        - SCIP_INF_3
        - SCIP_CARD_2
        - SCIP_VTE_2
        - SCIP_INF_9
        - PN_6
        - HF_1
        - HF_2
        - IMM_2
        - Hospital name and address
    """
    info = dict()
    conditions = ['OP_6','OP_7','SCIP_INF_3','SCIP_CARD_2',
                  'SCIP_VTE_2','SCIP_INF_9','PN_6','HF_1',
                  'HF_2','IMM_2']
    
    with open(timelyAndEffectiveCare) as src:
        rdr = reader(src, delimiter=delim)
        headers = next(rdr)

        for k in range(len(headers)):
            if headers[k] == 'Provider ID':
                providerId = k
            if headers[k] == 'ZIP Code':
                zztop = k
            if headers[k] == 'Measure ID':
                measureId = k
            if headers[k] == 'Score':
                score = k
            if headers[k] == 'Hospital Name':
                hospName = k
            if headers[k] =='Address':
                address = k
                
        for row in rdr:
            row_split = row
            #row_split = row.split(',')
            currentZztop = row_split[zztop]
            currentProviderId = row_split[providerId]
            currentMeasureId = row_split[measureId]
            currentScore = row_split[score]
            currentAddress = row_split[hospName] + ' ' + row_split[address]
            
            if not currentZztop in info.keys():
                info[currentZztop] = dict()
                info[currentZztop][currentProviderId] = dict()
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
                info[currentZztop][currentProviderId]['Address'] = currentAddress
            elif not currentProviderId in info[currentZztop]:
                info[currentZztop][currentProviderId] = dict()
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
                info[currentZztop][currentProviderId]['Address'] = currentAddress
            else:
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
                info[currentZztop][currentProviderId]['Address'] = currentAddress
                
   
    return info

def computeIncomeCategory(income, mini, maxi, numCat):
    """
    Given an income, mini, maxi and the number of categories, get
    the category number of the income
    """
    diff = float(maxi)-float(mini)
    step = diff/numCat
    return math.floor(float(income.replace(',',''))/step)

def saveTotalExpenditure(totalExpFile, timelyInfo, delim=','):
    """
    Read the medicare hospital spending by claim file and save the
    total for each hospital (keeping the zip and hospital id)
    """
    totalExp = dict()
    with open(totalExpFile) as src:
        rdr = reader(src, delimiter = delim)
        headers = next(rdr)

        for k in range(len(headers)):
            if headers[k] == 'Provider Number':
                providerId = k
            if headers[k] == 'Claim Type':
                claimType = k
            if headers[k] == 'Avg Spending Per Episode (Hospital)':
                avg = k

        for row in rdr:
            row_split = row
            #row_split = row.split(',')
            if row_split[claimType] == 'Total':
                totalExp[row_split[providerId]] = row_split[avg]

    return totalExp

def writeResults(hcapsDict, totalExpDict, timelyInfoDict, medianDict, outputFile, delim=';',numCats=5):
    """
    Generate csv zipCode\tproviderId\tTotalExpenditures\tvariablesInTimelyCare\tMedian
    """
    variables = ['Zip', 'Provider Id', 'Address', 'total Expenditures','OP_6',
                 'OP_7','SCIP_INF_3','SCIP_CARD_2',
                 'SCIP_VTE_2','SCIP_INF_9','PN_6','HF_1',
                 'HF_2','IMM_2', 'Median', '\"NO\", patients would not recommend the hospital (they probably would not or definitely would not recommend it)',
    '\"YES\", patients would definitely recommend the hospital',
    '\"YES\", patients would probably recommend the hospital',
    'Patients who gave a rating of \"6\" or lower (low)',
    'Patients who gave a rating of \"7\" or \"8\" (medium)',
    'Patients who gave a rating of \"9\" or \"10\" (high)']


    with open(outputFile,'w') as dst:
        wrt = writer(dst, delimiter=delim)
        wrt.writerow(variables)
        for k in medianDict:
            currentZip = k
            if k in timelyInfoDict:
                for provider in timelyInfoDict[k]:
                    if provider in totalExpDict:
#                        print(provider)
#                        to_write = [currentZip]+";"+provider+";"+totalExpDict[provider]]
                        to_write = [currentZip,provider,timelyInfoDict[k][provider]['Address'],totalExpDict[provider]]

                        for var in variables[4:14]:
#                            print(k,provider,var,len(timelyInfoDict[k][provider]))
                            if var in timelyInfoDict[k][provider]:
                                to_write.append(timelyInfoDict[k][provider][var])
                            else:
                                to_write.append("Not Available")
                        to_write.append(medianDict[currentZip])
                        if provider in hcapsDict:
                            for var in variables[15:len(variables)]:
                                to_write.append(hcapsDict[provider][var])
                        else:
                            for var in variables[15:len(variables)]:
                                to_write.append("Not Available")
                            
                        wrt.writerow(to_write)

def appendIncomeCategories(inputFile, newOutputFile,numCats=5,delim=','):
    """

    """
    mini = 1e5
    maxi= -1
    # find the min and max median incomes
    with open(inputFile) as src:
        rdr = reader(src, delimiter = delim)
        headers = next(rdr)
        for k in range(len(headers)):
            if headers[k] == 'Median':
                med = k

        for row in rdr:
            if float(row[med].replace(',','')) > float(maxi):
                maxi = float(row[med].replace(',',''))
            elif float(row[med].replace(',','')) < float(mini):
                mini = float(row[med].replace(',',''))

    variables = []
    
    with open(inputFile) as src, open(newOutputFile,'w') as dst:
        rdr = reader(src, delimiter = delim)
        headers = next(rdr)
        for var in headers:
            variables.append(var)
        variables.append('Income Category')
        wrt = writer(dst, delimiter=delim)
        wrt.writerow(variables)
        for row in rdr:
            to_write = row
            to_write.append(computeIncomeCategory(row[med],mini,maxi,numCats))
            wrt.writerow(to_write)

if __name__ == '__main__':
    from sys import argv
    # argv[1] medianZipFile
    # argv[2] timelyAndEffectiveCare
    # argv[3] totalExpFile
    # argv[4] outputFile
    # argv[5] outputWithCategories
    # argv[6] hcaps
    medians = saveMedian(argv[1], delim=',')
    timelyInfo = retrieveTimelyInfo(argv[2], delim=',')
    totalExp = saveTotalExpenditure(argv[3], timelyInfo, delim=',')
    hcaps = retrieveHCAPSInfo(argv[6],delim=',')
    writeResults(hcaps, totalExp, timelyInfo, medians, argv[4], delim=',')
    # append income categories using only the areas where there is a hospital
    appendIncomeCategories(argv[4],argv[5])
