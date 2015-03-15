"""


"""

import numpy as np
import matplotlib.pyplot as plt

from csv import reader

def createPlots(inputFile, delim=','):
    """

    """

    highRating = []
    lowRating = []
    costPerClaimRating = []
    costPerClaimRecommend = []
    r = []
    notR = []
    
    with open(inputFile) as src:
        rdr = reader(src, delimiter=delim)
        headers = next(rdr)

        for k in range(len(headers)):
            if headers[k] == 'Patients who gave a rating of "9" or "10" (high)':
                hRating = k
            if headers[k] == 'Patients who gave a rating of "6" or lower (low)':
                lRating = k
            if headers[k] == 'total Expenditures':
                cost = k
            if headers[k] == '"NO", patients would not recommend the hospital (they probably would not or definitely would not recommend it)':
                notRecommend = k
            if headers[k] == '"YES", patients would definitely recommend the hospital':
                recommend = k
                
        for row in rdr:
            if row[cost] != 'Not Available' and row[hRating] != 'Not Available' and row[lRating] != 'Not Available':
                costPerClaimRating.append(float(row[cost][1:].replace(',','')))
                highRating.append(float(row[hRating]))
                lowRating.append(float(row[lRating]))
                
            if row[cost] != 'Not Available' and row[recommend] != 'Not Available' and row[notRecommend] != 'Not Available':
                costPerClaimRecommend.append(float(row[cost][1:].replace(',','')))
                r.append(float(row[recommend]))
                notR.append(float(row[notRecommend]))
        
    plt.scatter(costPerClaimRating,lowRating)
    plt.xlabel("Percentage of patients giving a low rating to the hospital")
    plt.ylabel("Cost per claim")
    plt.savefig('lowRatingVsCost.png')
    plt.close()

    plt.scatter(costPerClaimRating,highRating)
    plt.xlabel("Percentage of patients giving a high rating to the hospital")
    plt.ylabel("Cost per claim")
    plt.savefig('highRatingVsCost.png')
    plt.close()

    plt.scatter(costPerClaimRecommend,r)
    plt.xlabel("Percentage of patients who would recommend the hospital")
    plt.ylabel("Cost per claim")
    plt.savefig('recommendVsCost.png')
    plt.close()

    plt.scatter(costPerClaimRecommend,notR)
    plt.xlabel("Percentage of patients who would not recommend the hospital")
    plt.ylabel("Cost per claim")
    plt.savefig('notRecommendVsCost.png')
    plt.close()

    
if __name__ == '__main__':
    from sys import argv
    # argv[1] outputWithCategories.csv
    #         or any file that contains both the cost per claim and ratings    
    createPlots(argv[1])
