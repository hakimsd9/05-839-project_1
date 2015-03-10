"""
Join tables Medicare Hospital Finding by Claim
            MedianZip
            Timely and effective care

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

from medicare hospital spending by claim
TOTAL expenditure for each hospital

from MedianZip
Median
"""

from csv import reader, writer

def saveMedian(medianZipFile, delim=','):
    """
    Read the MedianZip file, save the median for each Zip
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

        for row in rdr:
            row_split = row
            #row_split = row.split(',')
            currentZztop = row_split[zztop]
            currentProviderId = row_split[providerId]
            currentMeasureId = row_split[measureId]
            currentScore = row_split[score]
            
            if not currentZztop in info.keys():
                info[currentZztop] = dict()
                info[currentZztop][currentProviderId] = dict()
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
            elif not currentProviderId in info[currentZztop]:
                info[currentZztop][currentProviderId] = dict()
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
            else:
                info[currentZztop][currentProviderId][currentMeasureId] = currentScore
   
    return info

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

def writeResults(totalExpDict, timelyInfoDict, medianDict, outputFile, delim=';'):
    """
    Generate csv zipCode\tproviderId\tTotalExpenditures\tvariablesInTimelyCare\tMedian
    """
    variables = ['Zip', 'Provider Id', 'total Expenditures','OP_6',
                 'OP_7','SCIP_INF_3','SCIP_CARD_2',
                 'SCIP_VTE_2','SCIP_INF_9','PN_6','HF_1',
                 'HF_2','IMM_2', 'Median']


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
                        to_write = [currentZip,provider,totalExpDict[provider]]

                        for var in variables[3:-1]:
#                            print(k,provider,var,len(timelyInfoDict[k][provider]))
                            if var in timelyInfoDict[k][provider]:
                                to_write.append(timelyInfoDict[k][provider][var])
                            else:
                                to_write.append("Not Available")
                        to_write.append(medianDict[currentZip])
                        wrt.writerow(to_write)


if __name__ == '__main__':
    from sys import argv
    # argv[1] medianZipFile
    # argv[2] timelyAndEffectiveCare
    # argv[3] totalExpFile
    # argv[4] outputFile
    medians = saveMedian(argv[1], delim=',')
    timelyInfo = retrieveTimelyInfo(argv[2], delim=',')
    totalExp = saveTotalExpenditure(argv[3], timelyInfo, delim=',')
    writeResults(totalExp, timelyInfo, medians, argv[4], delim=',')
