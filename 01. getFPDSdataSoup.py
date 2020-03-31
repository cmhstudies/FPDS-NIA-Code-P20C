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

df = pd.DataFrame()


#%%
# initialize values for looping through multiple ATOM feed calls
# note that FPDS returns 10 records at a time

# sets the url's &start= value
i = 0

# set number of records to retrieve
#numRecords=9
numRecords="all"

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
    awards = soup.find_all('award')

    # iterate through each entry and populate the dataframe
    for a in range(len(awards)): 
        awardDict = {
                'vendorName' : awards[a].vendor.vendorName.text if awards[a].vendor.vendorName is not None else "",
                'DUNSNumber' : awards[a].vendor.DUNSNumber.text if awards[a].vendor.DUNSNumber is not None else "",
                'cageCode' : awards[a].vendor.cageCode.text if awards[a].vendor.cageCode is not None else "",
                'obligatedAmount' : float(awards[a].obligatedAmount.text) if awards[a].obligatedAmount is not None else "",
                'baseAndExercisedOptionsValue' : float(awards[a].baseAndExercisedOptionsValue.text) if awards[a].baseAndExercisedOptionsValue is not None else "",
                'totalObligatedAmount' : float(awards[a].totalObligatedAmount.text) if awards[a].totalObligatedAmount is not None else "",
                'totalBaseAndExercisedOptionsValue' : float(awards[a].totalBaseAndExercisedOptionsValue.text) if awards[a].totalBaseAndExercisedOptionsValue is not None else "",
                'totalBaseAndAllOptionsValue' : float(awards[a].totalBaseAndAllOptionsValue.text) if awards[a].totalBaseAndAllOptionsValue is not None else "",
                'descriptionOfContractRequirement' : awards[a].descriptionOfContractRequirement.text if awards[a].descriptionOfContractRequirement is not None else "",
                'contractingOfficeAgencyID_name' : awards[a].contractingOfficeAgencyID['name'] if awards[a].contractingOfficeAgencyID is not None else "",
                'contractingOfficeID_name' : awards[a].contractingOfficeID['name'] if awards[a].contractingOfficeID is not None else "",
                'fundingRequestingAgencyID_name' : awards[a].fundingRequestingAgencyID['name'] if awards[a].fundingRequestingAgencyID is not None else "",
                'effectiveDate' : pd.to_datetime(awards[a].effectiveDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].effectiveDate is not None else "",
                'signedDate' : pd.to_datetime(awards[a].signedDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].signedDate is not None else "",
                'createdDate' : pd.to_datetime(awards[a].transactionInformation.createdDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].transactionInformation.createdDate is not None else "" ,
                'lastModifiedDate' : pd.to_datetime(awards[a].transactionInformation.lastModifiedDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].transactionInformation.lastModifiedDate is not None else "" ,
                'productOrServiceCode' :  awards[a].productOrServiceInformation.productOrServiceCode.text if awards[a].productOrServiceInformation.productOrServiceCode is not None else "",
                'productOrServiceCode_description':  awards[a].productOrServiceInformation.productOrServiceCode['description'] if awards[a].productOrServiceInformation.productOrServiceCode is not None else "",
                'principalNAICSCode': awards[a].productOrServiceInformation.principalNAICSCode.text if awards[a].productOrServiceInformation.principalNAICSCode is not None else "",
                'placeOfPerformanceZIPCode' : awards[a].placeOfPerformance.placeOfPerformanceZIPCode.text[0:5] if awards[a].placeOfPerformance.placeOfPerformanceZIPCode is not None else "",
                'principalNAICSCode_description':  awards[a].productOrServiceInformation.principalNAICSCode['description'] if awards[a].productOrServiceInformation.principalNAICSCode is not None else "",
                'extentCompeted' : awards[a].competition.extentCompeted['description'] if awards[a].competition.extentCompeted is not None else "",
                'solicitationProcedures' : awards[a].competition.solicitationProcedures['description'] if awards[a].competition.solicitationProcedures is not None else ""
                }
        df = df.append(
            awardDict,
            ignore_index=True
            )
    if len(soup.find_all('entry')) < 10:
        break
    # set the &start= value for the next query
    i += 10

# %%
with pd.ExcelWriter(outFilename, mode = 'w') as f:
    df.to_excel(f, index=False)

# %%
