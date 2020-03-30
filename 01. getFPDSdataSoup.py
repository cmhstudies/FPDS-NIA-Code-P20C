# 
# example ATOM feed url
# https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q=NATIONAL_INTEREST_CODE:P20C+LAST_MOD_DATE:[2020/03/01,2020/03/28]&start=0
# use fpds.gov advanced query tool to get correct formatting of q= value

# %%
from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd

# %%
# Set up queries
feedURL = "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q="
feedSize = 10
queryString = 'NATIONAL_INTEREST_CODE:P20C'
# query_string = 'NATIONAL_INTEREST_CODE:P20C+LAST_MOD_DATE:[2020/03/01,2020/03/28]'

#%%
# set filenames
# Create timestamp for file name
tsobj = datetime.datetime.now()
ts = tsobj.strftime("%Y%m%d-%H%M")
outFilename = 'data/FPDS-NIA-P20C-' + ts + '.xlsx'



# %%
#Set up dataframe for storage of information collected
columnNames = [
               'vendorName',
               'DUNSNumber',
               'cageCode',
               'obligatedAmount',
               'descriptionOfContractRequirement',
               'fundingRequestingAgencyID_name',
               'productOrServiceCode',
               'productOrServiceCode_description',
               'principalNAICSCode',
               'principalNAICSCode_description',
               'placeOfPerformanceZIPCode',
               'extentCompeted',
               'solicitationProcedures'
              ]

df = pd.DataFrame(columns=columnNames)


#%%
# initialize values for looping through multiple ATOM feed calls
# note that FPDS returns 10 records at a time

# sets the url's &start= value
i = 0

# set number of records to retrieve
numRecords=15
#numRecords="all"

while numRecords == "all" or i < numRecords:
    # form the query url
    url = feedURL + queryString + '&start='+ str(i) 
    print("querying {0}".format(url))
    response = requests.get(url, timeout=60, verify = False)
    queryURL = response.url
    print("finished querying {0}".format(queryURL))

    # create soup object for extracting data
    soup = BeautifulSoup(response.text,"xml")
    # get an iterable object for each FPDS record
    entries = soup.find_all('entry')

    # iterate through each entry and populate the dataframe
    for e in range(len(entries)): 
        if entries[e].award != None :
            awardDict = {
                'vendorName' : entries[e].vendor.find('vendorName').text,
                'DUNSNumber' : entries[e].vendor.find('DUNSNumber').text,
                'cageCode' : entries[e].vendor.find('cageCode').text,
                'obligatedAmount' : float(entries[e].obligatedAmount.text),
                'descriptionOfContractRequirement' : entries[e].descriptionOfContractRequirement.text,
                'fundingRequestingAgencyID_name' : entries[e].fundingRequestingAgencyID['name'],
                'effectiveDate' : pd.to_datetime(entries[e].effectiveDate.text, format = '%Y-%m-%d %H:%M:%S' ),
                'productOrServiceCode' :  entries[e].productOrServiceInformation.productOrServiceCode.text,
                'productOrServiceCode_description':  entries[e].productOrServiceInformation.productOrServiceCode['description'],
                'principalNAICSCode': entries[e].productOrServiceInformation.principalNAICSCode.text,
                'placeOfPerformanceZIPCode' : entries[e].placeOfPerformance.placeOfPerformanceZIPCode.text[0:5],
                'principalNAICSCode_description':  entries[e].productOrServiceInformation.principalNAICSCode['description'],
                'extentCompeted' : entries[e].competition.extentCompeted['description'],
                'solicitationProcedures' : entries[e].competition.solicitationProcedures['description']
                }

            df = df.append(
                awardDict,
                ignore_index=True
                )

    # set the &start= value for the next query
    i += 10

# %%
with pd.ExcelWriter(outFilename, mode = 'w') as f:
    df.to_excel(f, index=False)

# %%
