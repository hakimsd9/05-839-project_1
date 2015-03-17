from csv import reader, writer
import math


def getNewMedian(inputFile, delim=','):
    """

    """
    incomeByZip = dict()

    with open(inputFile) as src:
        rdr = reader(src, delimiter=delim)
        headers = next(rdr)

        for k in range(len(headers)):
            if headers[k] == ' Median household income in the past 12 months (in 2013 inflation-adjusted dollars)':
                income = k
            if  headers[k] == 'Geography':
                zztop = k

        for row in rdr:
            z = row[zztop].split(' ')[1]
            if row[income] == '**':
                toWrite = 'N/A'
            else:
                toWrite = row[income]
            incomeByZip[z] = toWrite
    return incomeByZip

def replaceInCsv(newMedian,inputCsv,outputCsv,delim=','):
    """

    """
    with open(inputCsv) as src, open(outputCsv,'w') as dst:
        rdr = reader(src, delimiter=delim)
        wrt = writer(dst, delimiter=delim)

        headers = next(rdr)
        wrt.writerow(headers)

        for k in range(len(headers)):
            if headers[k] == 'Zip':
                zz = k
            if headers[k] == 'Median':
                med = k
                
        for row in rdr:
            nr = row
            nr[med] = newMedian[row[zz]]
            wrt.writerow(nr)

if __name__ == '__main__':
    from sys import argv
    # argv[1] old csv
    # argv[2] new csv
    # argv[3] newMedianCsv
    newMed = getNewMedian(argv[3], delim=',')
    replaceInCsv(newMed,argv[1],argv[2],delim=',')
