
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[104]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[105]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[106]:


print(states.items())


# In[121]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Remove newline character '\n'. '''
    ut_list = []
    
    with open('university_towns.txt') as f:
        for line in f:
            if 'edit' in line:
                current_city = line.split('[')[0].strip()
            else:
                ut_list.append((current_city, line.split('(')[0].strip()))
                
    ut_df = pd.DataFrame.from_records(ut_list)
    ut_df.columns = ['State', 'RegionName']
    return ut_df


# In[122]:


def get_gdp_df():
    '''this function reads the gdp data and returns a dataframe with only the required columns'''
    gdplev = pd.ExcelFile('gdplev.xls')
    gdplev = gdplev.parse("Sheet1", skiprows=219)
    gdplev = gdplev[['1999q4', 9926.1]]
    gdplev.columns = ['quarter','gdp']
    return gdplev


# In[123]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdplev = get_gdp_df()
    for i in range(2, len(gdplev)):
        if (gdplev.iloc[i-2][1] > gdplev.iloc[i-1][1]) and (gdplev.iloc[i-1][1] > gdplev.iloc[i][1]):
            return gdplev.iloc[i-2][0]

get_recession_start()


# In[124]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''

    gdplev = get_gdp_df()
    start = get_recession_start()
    start_index = gdplev[gdplev['quarter'] == start].index.tolist()[0]
    gdplev=gdplev.iloc[start_index:]
    for i in range(2, len(gdplev)):
        if (gdplev.iloc[i-2][1] < gdplev.iloc[i-1][1]) and (gdplev.iloc[i-1][1] < gdplev.iloc[i][1]):
            return gdplev.iloc[i][0]


# In[125]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp = pd.read_excel('gdplev.xls',header = 219,names = ['Time', 'GDP','GDP Chained','none'])
    c_to_keep = ['Time','GDP Chained']
    gdp = gdp[c_to_keep].set_index(gdp['Time'])
    gdp = gdp['GDP Chained']
    rec = None
    end = None
    for i in range(0,len(gdp)-2):
        if (gdp[i] > gdp[i+1]) & (gdp[i+1] > gdp[i+2]):
            rec = i
            break
    for i in range(rec,len(gdp)-2):
        if (gdp[i+2] > gdp[i+1]) & (gdp[i+1] > gdp[i]):
            end = i+2
            break
    mini = str(gdp[gdp == min(gdp[rec:end])].index.values)[2:8]
    
    return mini
get_recession_bottom()


# In[126]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean housing price    
    values in a dataframe. This  is a dataframe with
    columns for 2000q1 through 2016q3, and have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the definition, they are
    not arbitrary three month periods.
        
    '''
    zillow = pd.read_csv('City_Zhvi_AllHomes.csv')
    zillow['State'] = zillow['State'].map(states)
    zillow.set_index(['State', 'RegionName'], inplace=True)
    zillow = zillow.loc[:, '2000-01': ]
    
    new_columns = [str(x)+y for x in range(2000, 2017) for y in ['q1', 'q2', 'q3', 'q4']]
    new_columns = new_columns[:-1] # drop the last quarter of 2016
    
    x = 0

    for c in new_columns:
        zillow[c] = zillow.iloc[:, x:x+3].mean(axis=1)
        x = x+3
    
    zillow = zillow.loc[:, '2000q1':]
    
    
    return zillow


# In[131]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    # get the start of recession
    start = get_recession_start()
    #get the bottom of the recession
    bottom = get_recession_bottom()
    # get the zillow housing data in desired format
    housing_data = convert_housing_data_to_quarters()
    # keep only the columns from recession starting point and bottom.
    housing_data = housing_data.loc[:, start: bottom]
    # compute price ratio between the recession points and add it as a column.
    housing_data.reset_index(inplace=True)
    housing_data['price_ratio'] = (housing_data[start] - housing_data[bottom]) / housing_data[start]
    # get the university town list to split the data.
    uni_towns = get_list_of_university_towns()  
    uni_town_list = uni_towns['RegionName'].tolist()
    # add a column to use as splitting condition
    housing_data['isUniTown'] = housing_data.RegionName.apply(lambda x: x in uni_town_list)
    #split the data into two separate dataframes and drop rows with missing values. The dropping step is needed to 
    #perform the t-test
    uni_data = housing_data[housing_data.isUniTown].copy().dropna()
    not_uni_data = housing_data[~housing_data.isUniTown].copy().dropna()
    # get the p-value by applying t-test on these two dataframe columns.
    p = ttest_ind(uni_data['price_ratio'], not_uni_data['price_ratio'])[1]
    # this boolean value will tell us whether we can reject the null hyopthesis or not.
    different = p < 0.01   
    # this metric will tell us which type of town has the lower housing price ratio (mean) during the recession
    lower = 'university town' if uni_data['price_ratio'].mean() < not_uni_data['price_ratio'].mean() else 'non-university town'
    
    return (ttest_ind(uni_data['price_ratio'], not_uni_data['price_ratio']))
run_ttest()
  


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




