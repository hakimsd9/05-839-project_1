__author__ = 'patrickwedgeworth'  '
#Citation 1: http://stackoverflow.com/questions/13643363/linear-regression-of-arrays-containing-nans-in-python-numpy
#Citation 2: http://blog.yhathq.com/posts/logistic-regression-and-python.html


import pandas as pd
from statsmodels import api as sm
import pylab as pl
import numpy as np

# read the data in"
df = pd.read_csv("/Users/patrickwedgeworth/Desktop/Mankoffdev/ProfByte1/Project1/cherrypyfooddessert-1.csv")

# take a look at the dataset
print df.head()


# rename the 'rank' column because there is also a DataFrame method called 'rank'
df.columns = ["DiabetesBool", "FoodDesert", "Population","Urban","LowIncome","Percent","Low CI","High CI","Statelist","Index"]
print df.columns

# summarize the data
print df.describe()
 
# take a look at the standard deviation of each column
print df.std()

# frequency table
print pd.crosstab(df['Percent'], df['FoodDesert'], rownames=['Percent'])
 
# plot all of the columns
df.hist()
pl.show()

# dummify FoodDesert, Urban, LowIncome
dummy_ranks = pd.get_dummies(df['FoodDesert'], prefix='FoodDesert')
print dummy_ranks.head()
 
dummy_ranks2 = pd.get_dummies(df['Urban'], prefix='Urban')
print dummy_ranks2.head()

dummy_ranks3 = pd.get_dummies(df['LowIncome'], prefix='LowIncome')
print dummy_ranks3.head()

# create a clean data frame for the regression
# DiabetesBool is a variable that determines whether a state has a rate of diabetes over 1 standard deviation 
# above the mean (this would return a value of 1) or not (returns a value of 0)
# FoodDesert determines whether area is a food desert (returns 1) or not (returns 0)
# Population is simply the population
# "LowIncome" was left out because low income is part of the definition of food desert, so this would be inappropriate to add here
cols_to_keep = ['DiabetesBool','FoodDesert', 'Population']
data = df[cols_to_keep].join(dummy_ranks2.ix[:,'Urban_1':])

print data.head()
 
# manually add the intercept
data['intercept'] = 0.5  

train_cols = data.columns[1:]

mask = ~np.isnan(data['DiabetesBool']) & ~np.isnan(data['Population']) & ~np.isnan(data['DiabetesBool']) & ~np.isnan(data['Urban_1']) 
logit = sm.Logit(data['DiabetesBool'][mask], data[train_cols][mask])

# fit the model
result = logit.fit() 

# Did not add state because the number of different variables was beyond the ability of python's logit fxn to handle
# DiabetesBool is a variable
print result.summary() 
