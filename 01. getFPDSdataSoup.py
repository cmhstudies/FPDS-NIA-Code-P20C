# 
# example ATOM feed url
# https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q=NATIONAL_INTEREST_CODE:P20C+LAST_MOD_DATE:[2020/03/01,2020/03/28]&start=0
# use fpds.gov advanced query tool to get correct formatting of q= value

# %%
from bs4 import BeautifulSoup
import requests
import time
import datetime
import pandas as pd

# %%
# Set up queries
feedURL = "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q="
feedSize = 10
#qLastModDateStart = "2020/04/18"
#qLastModDateEnd = "2020/04/25"
#queryString = 'NATIONAL_INTEREST_CODE:P20C'
# note: query returns values included in the start and finish dates, i.e <= and >=
# queryString = 'NATIONAL_INTEREST_CODE:P20C+LAST_MOD_DATE:[2020/04/05,2020/04/08]'
queryString = 'NATIONAL_INTEREST_CODE:P20C+LAST_MOD_DATE:[2020/04/09,2020/04/17]'

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
    try:
        # response = requests.get(url, timeout=60, verify = False)
        response = requests.get(url, verify = False)
        response.raise_for_status()
    except requests.exceptions.Timeout as timeout_err:
        print(f'HTTP Error Occurred: {timeout_err}')
        print(f'sleeping')
        time.sleep(30)
        print(f'try again')
        response = requests.get(url, verify = False)
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP Error Occurred: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        print(f'HTTP Error Occurred: {conn_err}')
        print(f'sleeping')
        time.sleep(30)
        print(f'try again')
        response = requests.get(url, verify = False)
    except requests.exceptions.RetryError as retry_err:
        print(f'HTTP Error Occurred: {retry_err}')
        print(f'sleeping')
        time.sleep(300)
        print(f'try again')
        response = requests.get(url, verify = False)
    else:
        queryURL = response.url
        print("Successfully retreived: {0}".format(queryURL))

        # create soup object for extracting data
        soup = BeautifulSoup(response.text,"xml")
        # get an iterable object for each FPDS record
        awards = soup.find_all('award')

        # iterate through each entry and populate the dataframe
        for a in range(len(awards)): 
            awardDict = {
                    'awardContractID_agencyID_name' : awards[a].awardContractID.agencyID['name'] if awards[a].awardContractID.agencyID is not None else "",
                    'awardContractID_agencyID' : awards[a].awardContractID.agencyID.text if awards[a].awardContractID.agencyID is not None else "",
                    'awardContractID_PIID' : awards[a].awardContractID.PIID.text if awards[a].awardContractID.PIID is not None else "",
                    'awardContractID_modNumber' : awards[a].awardContractID.modNumber.text if awards[a].awardContractID.modNumber is not None else "",
                    'awardContractID_transactionNumber' : awards[a].awardContractID.transactionNumber.text if awards[a].awardContractID.transactionNumber is not None else "",
                    'referencedIDVID_agencyID' : awards[a].referencedIDVID.agencyID.text if awards[a].referencedIDVID is not None else "",
                    'referencedIDVID_agencyID_name' : awards[a].referencedIDVID.agencyID['name'] if awards[a].referencedIDVID is not None else "",
                    'referencedIDVID_PIID' : awards[a].referencedIDVID.PIID.text if awards[a].referencedIDVID is not None else "",
                    'referencedIDVID_modNumber' : awards[a].referencedIDVID.modNumber.text if awards[a].referencedIDVID is not None else "",
                    # relevantContractDates
                    'effectiveDate' : pd.to_datetime(awards[a].effectiveDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].effectiveDate is not None else "",
                    'signedDate' : pd.to_datetime(awards[a].signedDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].signedDate is not None else "",
                    'createdDate' : pd.to_datetime(awards[a].transactionInformation.createdDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].transactionInformation.createdDate is not None else "" ,
                    'lastModifiedDate' : pd.to_datetime(awards[a].transactionInformation.lastModifiedDate.text, format = '%Y-%m-%d %H:%M:%S' ) if awards[a].transactionInformation.lastModifiedDate is not None else "" ,
                    # dollarValues
                    'obligatedAmount' : float(awards[a].obligatedAmount.text) if awards[a].obligatedAmount is not None else "",
                    'baseAndExercisedOptionsValue' : float(awards[a].baseAndExercisedOptionsValue.text) if awards[a].baseAndExercisedOptionsValue is not None else "",
                    'baseAndAllOptionsValue' : float(awards[a].baseAndAllOptionsValue.text) if awards[a].baseAndAllOptionsValue is not None else "",
                    # totalDolarValues
                    'totalObligatedAmount' : float(awards[a].totalObligatedAmount.text) if awards[a].totalObligatedAmount is not None else "",
                    'totalBaseAndExercisedOptionsValue' : float(awards[a].totalBaseAndExercisedOptionsValue.text) if awards[a].totalBaseAndExercisedOptionsValue is not None else "",
                    'totalBaseAndAllOptionsValue' : float(awards[a].totalBaseAndAllOptionsValue.text) if awards[a].totalBaseAndAllOptionsValue is not None else "",
                    # purchaserInformation
                    'contractingOfficeAgencyID' : awards[a].contractingOfficeAgencyID.text if awards[a].contractingOfficeAgencyID is not None else "",
                    'contractingOfficeAgencyID_name' : awards[a].contractingOfficeAgencyID['name'] if awards[a].contractingOfficeAgencyID is not None else "",
                    'contractingOfficeAgencyID_departmentID' : awards[a].contractingOfficeAgencyID['departmentID'] if awards[a].contractingOfficeAgencyID is not None else "",
                    'contractingOfficeAgencyID_departmentName' : awards[a].contractingOfficeAgencyID['departmentName'] if awards[a].contractingOfficeAgencyID is not None else "",
                    'contractingOfficeID' : awards[a].contractingOfficeID.text if awards[a].contractingOfficeID is not None else "",
                    'contractingOfficeID_name' : awards[a].contractingOfficeID['name'] if awards[a].contractingOfficeID is not None else "",
                    'contractingOfficeID_country' : awards[a].contractingOfficeID['country'] if awards[a].contractingOfficeID is not None else "",
                    'fundingRequestingAgencyID' : awards[a].fundingRequestingAgencyID.text if awards[a].fundingRequestingAgencyID is not None else "",
                    'fundingRequestingAgencyID_name' : awards[a].fundingRequestingAgencyID['name'] if awards[a].fundingRequestingAgencyID is not None else "",
                    'fundingRequestingAgencyID_departmentID' : awards[a].fundingRequestingAgencyID['departmentID'] if awards[a].fundingRequestingAgencyID is not None else "",
                    'fundingRequestingAgencyID_departmentName' : awards[a].fundingRequestingAgencyID['departmentName'] if awards[a].fundingRequestingAgencyID is not None else "",
                    'fundingRequestingOfficeID' : awards[a].fundingRequestingOfficeID.text if awards[a].fundingRequestingOfficeID is not None else "",
                    'fundingRequestingOfficeID_name' : awards[a].fundingRequestingOfficeID['name'] if awards[a].fundingRequestingOfficeID is not None else "",
                    'foreignFunding' : awards[a].foreignFunding['description'] if awards[a].foreignFunding is not None else "",
                    #contractData
                    'contractActionType_description' : awards[a].contractData.contractActionType['description'] if awards[a].contractActionType is not None else "",
                    'typeOfContractPricing_description' : awards[a].contractData.typeOfContractPricing['description'] if awards[a].typeOfContractPricing is not None else "",
                    'reasonForModification_description' : awards[a].contractData.reasonForModification['description'] if awards[a].reasonForModification is not None else "",
                    'nationalInterestActionCode_description' : awards[a].contractData.nationalInterestActionCode['description'] if awards[a].nationalInterestActionCode is not None else "",
                    'descriptionOfContractRequirement' : awards[a].contractData.descriptionOfContractRequirement.text if awards[a].descriptionOfContractRequirement is not None else "",
                    'GFE-GFP_description' : getattr(awards[a].contractData, 'GFE-GFP')['description'] if getattr(awards[a].contractData, 'GFE-GFP') is not None else "",
                    'undefinitizedAction_description' : awards[a].contractData.undefinitizedAction['description'] if awards[a].contractData.undefinitizedAction is not None else "",
                    'consolidatedContract_description' : awards[a].contractData.consolidatedContract['description'] if awards[a].contractData.consolidatedContract is not None else "",
                    'performanceBasedServiceContract_description' : awards[a].contractData.performanceBasedServiceContract['description'] if awards[a].contractData.performanceBasedServiceContract is not None else "",
                    'contingencyHumanitarianPeacekeepingOperation_description' : awards[a].contractData.contingencyHumanitarianPeacekeepingOperation['description'] if awards[a].contractData.contingencyHumanitarianPeacekeepingOperation is not None else "",
                    'referencedIDVMultipleOrSingle_description' : awards[a].contractData.referencedIDVMultipleOrSingle['description'] if awards[a].contractData.referencedIDVMultipleOrSingle is not None else "",
                    'referencedIDVType_description' : awards[a].contractData.referencedIDVType['description'] if awards[a].contractData.referencedIDVType is not None else "",
                    'purchaseCardAsPaymentMethod_description' : awards[a].contractData.purchaseCardAsPaymentMethod['description'] if awards[a].contractData.purchaseCardAsPaymentMethod is not None else "",
                    'numberOfActions' : awards[a].contractData.numberOfActions.text if awards[a].contractData.numberOfActions is not None else "",
                    # legislativeMandates
                    'ClingerCohenAct' : awards[a].ClingerCohenAct['description'] if awards[a].ClingerCohenAct is not None else "",
                    'materialsSuppliesArticlesEquipment' : awards[a].materialsSuppliesArticlesEquipment['description'] if awards[a].materialsSuppliesArticlesEquipment is not None else "",
                    'laborStandards' : awards[a].laborStandards['description'] if awards[a].laborStandards is not None else "",
                    'constructionWageRateRequirements' : awards[a].constructionWageRateRequirements['description'] if awards[a].constructionWageRateRequirements is not None else "",
                    'additionalReportingValue' : awards[a].additionalReportingValue['description'] if awards[a].additionalReportingValue is not None else "",
                    'interagencyContractingAuthority' : awards[a].interagencyContractingAuthority['description'] if awards[a].interagencyContractingAuthority is not None else "",
                    # vendor
                    'isAlaskanNativeOwnedCorporationOrFirm' : awards[a].vendor.isAlaskanNativeOwnedCorporationOrFirm.text if awards[a].vendor.isAlaskanNativeOwnedCorporationOrFirm is not None else "",
                    'isAmericanIndianOwned' : awards[a].vendor.isAmericanIndianOwned.text if awards[a].vendor.isAmericanIndianOwned is not None else "",
                    'isIndianTribe' : awards[a].vendor.isIndianTribe.text if awards[a].vendor.isIndianTribe is not None else "",
                    'isNativeHawaiianOwnedOrganizationOrFirm' : awards[a].vendor.isNativeHawaiianOwnedOrganizationOrFirm.text if awards[a].vendor.isNativeHawaiianOwnedOrganizationOrFirm is not None else "",
                    'isTriballyOwnedFirm' : awards[a].vendor.isTriballyOwnedFirm.text if awards[a].vendor.isTriballyOwnedFirm is not None else "",
                    'isSmallBusiness' : awards[a].vendor.isSmallBusiness.text if awards[a].vendor.isSmallBusiness is not None else "",
                    'isVeteranOwned' : awards[a].vendor.isVeteranOwned.text if awards[a].vendor.isVeteranOwned is not None else "",
                    'isServiceRelatedDisabledVeteranOwnedBusiness' : awards[a].vendor.isServiceRelatedDisabledVeteranOwnedBusiness.text if awards[a].vendor.isServiceRelatedDisabledVeteranOwnedBusiness is not None else "",
                    'isWomenOwned' : awards[a].vendor.isWomenOwned.text if awards[a].vendor.isWomenOwned is not None else "",

                    'isSubContinentAsianAmericanOwnedBusiness' : awards[a].vendor.isSubContinentAsianAmericanOwnedBusiness.text if awards[a].vendor.isSubContinentAsianAmericanOwnedBusiness is not None else "",
                    'isAsianPacificAmericanOwnedBusiness' : awards[a].vendor.isAsianPacificAmericanOwnedBusiness.text if awards[a].vendor.isAsianPacificAmericanOwnedBusiness is not None else "",
                    'isBlackAmericanOwnedBusiness' : awards[a].vendor.isBlackAmericanOwnedBusiness.text if awards[a].vendor.isBlackAmericanOwnedBusiness is not None else "",
                    'isHispanicAmericanOwnedBusiness' : awards[a].vendor.isHispanicAmericanOwnedBusiness.text if awards[a].vendor.isHispanicAmericanOwnedBusiness is not None else "",
                    'isNativeAmericanOwnedBusiness' : awards[a].vendor.isNativeAmericanOwnedBusiness.text if awards[a].vendor.isNativeAmericanOwnedBusiness is not None else "",
                    'isOtherMinorityOwned' : awards[a].vendor.isOtherMinorityOwned.text if awards[a].vendor.isOtherMinorityOwned is not None else "",

                    'isVerySmallBusiness' : awards[a].vendor.isVerySmallBusiness.text if awards[a].vendor.isVerySmallBusiness is not None else "",
                    'isWomenOwnedSmallBusiness' : awards[a].vendor.isWomenOwnedSmallBusiness.text if awards[a].vendor.isWomenOwnedSmallBusiness is not None else "",
                    'isEconomicallyDisadvantagedWomenOwnedSmallBusiness' : awards[a].vendor.isEconomicallyDisadvantagedWomenOwnedSmallBusiness.text if awards[a].vendor.isEconomicallyDisadvantagedWomenOwnedSmallBusiness is not None else "",
                    'isJointVentureWomenOwnedSmallBusiness' : awards[a].vendor.isJointVentureWomenOwnedSmallBusiness.text if awards[a].vendor.isJointVentureWomenOwnedSmallBusiness is not None else "",
                    'isJointVentureEconomicallyDisadvantagedWomenOwnedSmallBusiness' : awards[a].vendor.isJointVentureEconomicallyDisadvantagedWomenOwnedSmallBusiness.text if awards[a].vendor.isJointVentureEconomicallyDisadvantagedWomenOwnedSmallBusiness is not None else "",

                    'isCommunityDevelopedCorporationOwnedFirm' : awards[a].vendor.isCommunityDevelopedCorporationOwnedFirm.text if awards[a].vendor.isCommunityDevelopedCorporationOwnedFirm is not None else "",
                    'isLaborSurplusAreaFirm' : awards[a].vendor.isLaborSurplusAreaFirm.text if awards[a].vendor.isLaborSurplusAreaFirm is not None else "",

                    'isFederalGovernment' : awards[a].vendor.isFederalGovernment.text if awards[a].vendor.isFederalGovernment is not None else "",
                    'isFederallyFundedResearchAndDevelopmentCorp' : awards[a].vendor.isFederallyFundedResearchAndDevelopmentCorp.text if awards[a].vendor.isFederallyFundedResearchAndDevelopmentCorp is not None else "",
                    'isFederalGovernmentAgency' : awards[a].vendor.isFederalGovernmentAgency.text if awards[a].vendor.isFederalGovernmentAgency is not None else "",

                    'isStateGovernment' : awards[a].vendor.isStateGovernment.text if awards[a].vendor.isStateGovernment is not None else "",

                    'isLocalGovernment' : awards[a].vendor.isLocalGovernment.text if awards[a].vendor.isLocalGovernment is not None else "",
                    'isCityLocalGovernment' : awards[a].vendor.isCityLocalGovernment.text if awards[a].vendor.isCityLocalGovernment is not None else "",
                    'isCountyLocalGovernment' : awards[a].vendor.isCountyLocalGovernment.text if awards[a].vendor.isCountyLocalGovernment is not None else "",
                    'isInterMunicipalLocalGovernment' : awards[a].vendor.isInterMunicipalLocalGovernment.text if awards[a].vendor.isInterMunicipalLocalGovernment is not None else "",
                    'isLocalGovernmentOwned' : awards[a].vendor.isLocalGovernmentOwned.text if awards[a].vendor.isLocalGovernmentOwned is not None else "",
                    'isMunicipalityLocalGovernment' : awards[a].vendor.isMunicipalityLocalGovernment.text if awards[a].vendor.isMunicipalityLocalGovernment is not None else "",
                    'isSchoolDistrictLocalGovernment' : awards[a].vendor.isSchoolDistrictLocalGovernment.text if awards[a].vendor.isSchoolDistrictLocalGovernment is not None else "",
                    'isTownshipLocalGovernment' : awards[a].vendor.isTownshipLocalGovernment.text if awards[a].vendor.isTownshipLocalGovernment is not None else "",

                    'isTribalGovernment' : awards[a].vendor.isTribalGovernment.text if awards[a].vendor.isTribalGovernment is not None else "",
                    'isForeignGovernment' : awards[a].vendor.isForeignGovernment.text if awards[a].vendor.isForeignGovernment is not None else "",

                    'isCorporateEntityNotTaxExempt' : awards[a].vendor.isCorporateEntityNotTaxExempt.text if awards[a].vendor.isCorporateEntityNotTaxExempt is not None else "",
                    'isCorporateEntityTaxExempt' : awards[a].vendor.isCorporateEntityTaxExempt.text if awards[a].vendor.isCorporateEntityTaxExempt is not None else "",
                    'isPartnershipOrLimitedLiabilityPartnership' : awards[a].vendor.isPartnershipOrLimitedLiabilityPartnership.text if awards[a].vendor.isPartnershipOrLimitedLiabilityPartnership is not None else "",
                    'isSolePropreitorship' : awards[a].vendor.isSolePropreitorship.text if awards[a].vendor.isSolePropreitorship is not None else "",
                    'isSmallAgriculturalCooperative' : awards[a].vendor.isSmallAgriculturalCooperative.text if awards[a].vendor.isSmallAgriculturalCooperative is not None else "",
                    'isInternationalOrganization' : awards[a].vendor.isInternationalOrganization.text if awards[a].vendor.isInternationalOrganization is not None else "",
                    'isUSGovernmentEntity' : awards[a].vendor.isUSGovernmentEntity.text if awards[a].vendor.isUSGovernmentEntity is not None else "",


                    'isCommunityDevelopmentCorporation' : awards[a].vendor.isCommunityDevelopmentCorporation.text if awards[a].vendor.isCommunityDevelopmentCorporation is not None else "",
                    'isDomesticShelter' : awards[a].vendor.isDomesticShelter.text if awards[a].vendor.isDomesticShelter is not None else "",
                    'isEducationalInstitution' : awards[a].vendor.isEducationalInstitution.text if awards[a].vendor.isEducationalInstitution is not None else "",
                    'isFoundation' : awards[a].vendor.isFoundation.text if awards[a].vendor.isFoundation is not None else "",
                    'isHospital' : awards[a].vendor.isHospital.text if awards[a].vendor.isHospital is not None else "",
                    'isManufacturerOfGoods' : awards[a].vendor.isManufacturerOfGoods.text if awards[a].vendor.isManufacturerOfGoods is not None else "",
                    'isVeterinaryHospital' : awards[a].vendor.isVeterinaryHospital.text if awards[a].vendor.isVeterinaryHospital is not None else "",
                    'isHispanicServicingInstitution' : awards[a].vendor.isHispanicServicingInstitution.text if awards[a].vendor.isHispanicServicingInstitution is not None else "",

                    'receivesContracts' : awards[a].vendor.receivesContracts.text if awards[a].vendor.receivesContracts is not None else "",
                    'receivesGrants' : awards[a].vendor.receivesGrants.text if awards[a].vendor.receivesGrants is not None else "",
                    'receivesContractsAndGrants' : awards[a].vendor.receivesContractsAndGrants.text if awards[a].vendor.receivesContractsAndGrants is not None else "",

                    'isAirportAuthority' : awards[a].vendor.isAirportAuthority.text if awards[a].vendor.isAirportAuthority is not None else "",
                    'isCouncilOfGovernments' : awards[a].vendor.isCouncilOfGovernments.text if awards[a].vendor.isCouncilOfGovernments is not None else "",
                    'isHousingAuthoritiesPublicOrTribal' : awards[a].vendor.isHousingAuthoritiesPublicOrTribal.text if awards[a].vendor.isHousingAuthoritiesPublicOrTribal is not None else "",
                    'isInterstateEntity' : awards[a].vendor.isInterstateEntity.text if awards[a].vendor.isInterstateEntity is not None else "",
                    'isPlanningCommission' : awards[a].vendor.isPlanningCommission.text if awards[a].vendor.isPlanningCommission is not None else "",
                    'isPortAuthority' : awards[a].vendor.isPortAuthority.text if awards[a].vendor.isPortAuthority is not None else "",
                    'isTransitAuthority' : awards[a].vendor.isTransitAuthority.text if awards[a].vendor.isTransitAuthority is not None else "",

                    'isSubchapterSCorporation' : awards[a].vendor.isSubchapterSCorporation.text if awards[a].vendor.isSubchapterSCorporation is not None else "",
                    'isLimitedLiabilityCorporation' : awards[a].vendor.isLimitedLiabilityCorporation.text if awards[a].vendor.isLimitedLiabilityCorporation is not None else "",
                    'isForeignOwnedAndLocated' : awards[a].vendor.isForeignOwnedAndLocated.text if awards[a].vendor.isForeignOwnedAndLocated is not None else "",

                    'isForProfitOrganization' : awards[a].vendor.isForProfitOrganization.text if awards[a].vendor.isForProfitOrganization is not None else "",
                    'isNonprofitOrganization' : awards[a].vendor.isNonprofitOrganization.text if awards[a].vendor.isNonprofitOrganization is not None else "",
                    'isOtherNotForProfitOrganization' : awards[a].vendor.isOtherNotForProfitOrganization.text if awards[a].vendor.isOtherNotForProfitOrganization is not None else "",

                    'isShelteredWorkshop' : awards[a].vendor.isShelteredWorkshop.text if awards[a].vendor.isShelteredWorkshop is not None else "",

                    'stateOfIncorporation' : awards[a].vendor.stateOfIncorporation['name'] if awards[a].vendor.stateOfIncorporation is not None else "",
                    'countryOfIncorporation' : awards[a].vendor.countryOfIncorporation['name'] if awards[a].vendor.countryOfIncorporation is not None else "",

                    'organizationalType' : awards[a].vendor.organizationalType.text if awards[a].vendor.organizationalType is not None else "",

                    'is1862LandGrantCollege' : awards[a].vendor.is1862LandGrantCollege.text if awards[a].vendor.is1862LandGrantCollege is not None else "",
                    'is1890LandGrantCollege' : awards[a].vendor.is1890LandGrantCollege.text if awards[a].vendor.is1890LandGrantCollege is not None else "",
                    'is1994LandGrantCollege' : awards[a].vendor.is1994LandGrantCollege.text if awards[a].vendor.is1994LandGrantCollege is not None else "",
                    'isHistoricallyBlackCollegeOrUniversity' : awards[a].vendor.isHistoricallyBlackCollegeOrUniversity.text if awards[a].vendor.isHistoricallyBlackCollegeOrUniversity is not None else "",
                    'isMinorityInstitution' : awards[a].vendor.isMinorityInstitution.text if awards[a].vendor.isMinorityInstitution is not None else "",
                    'isPrivateUniversityOrCollege' : awards[a].vendor.isPrivateUniversityOrCollege.text if awards[a].vendor.isPrivateUniversityOrCollege is not None else "",
                    'isSchoolOfForestry' : awards[a].vendor.isSchoolOfForestry.text if awards[a].vendor.isSchoolOfForestry is not None else "",
                    'isStateControlledInstitutionofHigherLearning' : awards[a].vendor.isStateControlledInstitutionofHigherLearning.text if awards[a].vendor.isStateControlledInstitutionofHigherLearning is not None else "",
                    'isTribalCollege' : awards[a].vendor.isTribalCollege.text if awards[a].vendor.isTribalCollege is not None else "",
                    'isVeterinaryCollege' : awards[a].vendor.isVeterinaryCollege.text if awards[a].vendor.isVeterinaryCollege is not None else "",
                    'isAlaskanNativeServicingInstitution' : awards[a].vendor.isAlaskanNativeServicingInstitution.text if awards[a].vendor.isAlaskanNativeServicingInstitution is not None else "",
                    'isNativeHawaiianServicingInstitution' : awards[a].vendor.isNativeHawaiianServicingInstitution.text if awards[a].vendor.isNativeHawaiianServicingInstitution is not None else "",
    
                    'isDOTCertifiedDisadvantagedBusinessEnterprise' : awards[a].vendor.isDOTCertifiedDisadvantagedBusinessEnterprise.text if awards[a].vendor.isDOTCertifiedDisadvantagedBusinessEnterprise is not None else "",
                    'isSelfCertifiedSmallDisadvantagedBusiness' : awards[a].vendor.isSelfCertifiedSmallDisadvantagedBusiness.text if awards[a].vendor.isSelfCertifiedSmallDisadvantagedBusiness is not None else "",
                    'isSBACertifiedSmallDisadvantagedBusiness' : awards[a].vendor.isSBACertifiedSmallDisadvantagedBusiness.text if awards[a].vendor.isSBACertifiedSmallDisadvantagedBusiness is not None else "",
                    'isSBACertified8AProgramParticipant' : awards[a].vendor.isSBACertified8AProgramParticipant.text if awards[a].vendor.isSBACertified8AProgramParticipant is not None else "",
                    'isSelfCertifiedHUBZoneJointVenture' : awards[a].vendor.isSelfCertifiedHUBZoneJointVenture.text if awards[a].vendor.isSelfCertifiedHUBZoneJointVenture is not None else "",
                    'isSBACertifiedHUBZone' : awards[a].vendor.isSBACertifiedHUBZone.text if awards[a].vendor.isSBACertifiedHUBZone is not None else "",
                    'isSBACertified8AJointVenture' : awards[a].vendor.isSBACertified8AJointVenture.text if awards[a].vendor.isSBACertified8AJointVenture is not None else "",

                    'vendor_streetAddress' : awards[a].vendor.streetAddress.text if awards[a].vendor.streetAddress is not None else "",
                    'vendor_city' : awards[a].vendor.city.text if awards[a].vendor.city is not None else "",
                    'vendor_state' : awards[a].vendor.state.text if awards[a].vendor.state is not None else "",
                    'vendor_ZIPCode' : awards[a].vendor.ZIPCode.text if awards[a].vendor.ZIPCode is not None else "",
                    'vendor_countryCode' : awards[a].vendor.countryCode.text if awards[a].vendor.countryCode is not None else "",
                    'vendor_phoneNo' : awards[a].vendor.phoneNo.text if awards[a].vendor.phoneNo is not None else "",
                    'vendor_faxNo' : awards[a].vendor.faxNo.text if awards[a].vendor.faxNo is not None else "",
                    'vendor_congressionalDistrictCode' : awards[a].vendor.congressionalDistrictCode.text if awards[a].vendor.congressionalDistrictCode is not None else "",

                    'vendor_vendorSiteCode' : awards[a].vendor.vendorSiteCode.text if awards[a].vendor.vendorSiteCode is not None else "",
                    'vendor_vendorAlternateSiteCode' : awards[a].vendor.vendorAlternateSiteCode.text if awards[a].vendor.vendorAlternateSiteCode is not None else "",

                    'vendor_DUNSNumber' : awards[a].vendor.DUNSNumber.text if awards[a].vendor.DUNSNumber is not None else "",
                    'vendor_cageCode' : awards[a].vendor.cageCode.text if awards[a].vendor.cageCode is not None else "",
                    'vendor_vendorName' : awards[a].vendor.vendorName.text if awards[a].vendor.vendorName is not None else "",
                    'vendor_globalParentDUNSNumber' : awards[a].vendor.globalParentDUNSNumber.text if awards[a].vendor.globalParentDUNSNumber is not None else "",
                    'vendor_globalParentDUNSName' : awards[a].vendor.globalParentDUNSName.text if awards[a].vendor.globalParentDUNSName is not None else "",

                    'vendor_registrationDate' : awards[a].vendor.registrationDate.text if awards[a].vendor.registrationDate is not None else "",
                    'vendor_renewalDate' : awards[a].vendor.renewalDate.text if awards[a].vendor.renewalDate is not None else "",

                    'contractingOfficerBusinessSizeDetermination' : awards[a].vendor.contractingOfficerBusinessSizeDetermination.text if awards[a].vendor.contractingOfficerBusinessSizeDetermination is not None else "",
                    # placeOfPerformance
                    # 'GFE-GFP_description' : getattr(awards[a].contractData, 'GFE-GFP')['description'] if getattr(awards[a].contractData, 'GFE-GFP') is not None else "",
                    'placeOfPerformance_stateCode' : awards[a].placeOfPerformance.stateCode.text if awards[a].placeOfPerformance.stateCode is not None else "",
                    'placeOfPerformance_stateCode_name' : getattr(awards[a].placeOfPerformance, 'stateCode')['name'] if getattr(awards[a].placeOfPerformance, 'stateCode') is not None else "",
                    'placeOfPerformance_countryCode' : awards[a].placeOfPerformance.countryCode.text if awards[a].placeOfPerformance.countryCode is not None else "",
                    'placeOfPerformance_countryCode_name' : getattr(awards[a].placeOfPerformance, 'countryCode')['name'] if getattr(awards[a].placeOfPerformance, 'countryCode') is not None else "",
                    'placeOfPerformanceZIPCode' : awards[a].placeOfPerformance.placeOfPerformanceZIPCode.text[0:5] if awards[a].placeOfPerformance.placeOfPerformanceZIPCode is not None else "",
                    # 'placeOfPerformanceZIPCode_county' : getattr(awards[a].placeOfPerformance, 'placeOfPerformanceZIPCode')['county'] if getattr(awards[a].placeOfPerformance, 'placeOfPerformanceZIPCode') is not None else "",
                    # 'placeOfPerformanceZIPCode-city' : getattr(awards[a].placeOfPerformance, 'placeOfPerformanceZIPCode')['city'] if getattr(awards[a].placeOfPerformance, 'placeOfPerformanceZIPCode') is not None else "",
                    'placeOfPerformanceCongressionalDistrict' : awards[a].placeOfPerformance.placeOfPerformanceCongressionalDistrict.text if awards[a].placeOfPerformance.placeOfPerformanceCongressionalDistrict is not None else "",

                    # competition
                    'extentCompeted' : getattr(awards[a].competition, 'extentCompeted')['description'] if getattr(awards[a].competition, 'extentCompeted') is not None else "",
                    'solicitationProcedures' : getattr(awards[a].competition, 'solicitationProcedures')['description'] if getattr(awards[a].competition, 'solicitationProcedures') is not None else "",
                    'idvTypeOfSetAside' : getattr(awards[a].competition, 'idvTypeOfSetAside')['description'] if getattr(awards[a].competition, 'idvTypeOfSetAside') is not None else "",
                    'typeOfSetAsideSource' : getattr(awards[a].competition, 'typeOfSetAsideSource')['description'] if getattr(awards[a].competition, 'typeOfSetAsideSource') is not None else "",
                    'evaluatedPreference' : getattr(awards[a].competition, 'evaluatedPreference')['description'] if getattr(awards[a].competition, 'evaluatedPreference') is not None else "",
                    'statutoryExceptionToFairOpportunity' : getattr(awards[a].competition, 'statutoryExceptionToFairOpportunity')['description'] if getattr(awards[a].competition, 'statutoryExceptionToFairOpportunity') is not None else "",
                    'idvNumberOfOffersReceived' : awards[a].competition.idvNumberOfOffersReceived.text if awards[a].competition.idvNumberOfOffersReceived is not None else "",
                    'numberOfOffersReceived' : awards[a].competition.numberOfOffersReceived.text if awards[a].competition.numberOfOffersReceived is not None else "",
                    'numberOfOffersSource' : getattr(awards[a].competition, 'numberOfOffersSource')['description'] if getattr(awards[a].competition, 'numberOfOffersSource') is not None else "",
                    'commercialItemAcquisitionProcedures' : getattr(awards[a].competition, 'commercialItemAcquisitionProcedures')['description'] if getattr(awards[a].competition, 'commercialItemAcquisitionProcedures') is not None else "",
                    'commercialItemTestProgram' : getattr(awards[a].competition, 'commercialItemTestProgram')['description'] if getattr(awards[a].competition, 'commercialItemTestProgram') is not None else "",
                    'A76Action' : getattr(awards[a].competition, 'A76Action')['description'] if getattr(awards[a].competition, 'A76Action') is not None else "",
                    'fedBizOpps' : getattr(awards[a].competition, 'fedBizOpps')['description'] if getattr(awards[a].competition, 'fedBizOpps') is not None else "",
                    'localAreaSetAside' : getattr(awards[a].competition, 'localAreaSetAside')['description'] if getattr(awards[a].competition, 'localAreaSetAside') is not None else "",
                    'priceEvaluationPercentDifference' : float(awards[a].competition.priceEvaluationPercentDifference.text) if awards[a].competition.priceEvaluationPercentDifference is not None else "",

                    # preferencePrograms
                    'subcontractPlan' : getattr(awards[a].competition, 'subcontractPlan')['description'] if getattr(awards[a].competition, 'subcontractPlan') is not None else "",

                    # productOrServiceInformation
                    'productOrServiceCode' :  awards[a].productOrServiceInformation.productOrServiceCode.text if awards[a].productOrServiceInformation.productOrServiceCode is not None else "",
                    'productOrServiceCode_description':  getattr(awards[a].productOrServiceInformation, 'productOrServiceCode')['description'] if getattr(awards[a].productOrServiceInformation, 'productOrServiceCode') is not None else "",
                    'productOrServiceCode_productOrServiceType':  getattr(awards[a].productOrServiceInformation, 'productOrServiceCode')['productOrServiceType'] if getattr(awards[a].productOrServiceInformation, 'productOrServiceCode') is not None else "",
                    'principalNAICSCode': awards[a].productOrServiceInformation.principalNAICSCode.text if awards[a].productOrServiceInformation.principalNAICSCode is not None else "",
                    'principalNAICSCode_description':  getattr(awards[a].productOrServiceInformation, 'principalNAICSCode')['description'] if getattr(awards[a].productOrServiceInformation, 'principalNAICSCode') is not None else "",
                    'contractBundling' : awards[a].contractBundling['description'] if awards[a].contractBundling is not None else "",
                    'recoveredMaterialClauses' : awards[a].recoveredMaterialClauses['description'] if awards[a].recoveredMaterialClauses is not None else "",
                    'manufacturingOrganizationType' : awards[a].manufacturingOrganizationType['description'] if awards[a].manufacturingOrganizationType is not None else "",
                    'useOfEPADesignatedProducts' : awards[a].useOfEPADesignatedProducts['description'] if awards[a].useOfEPADesignatedProducts is not None else "",
                    'countryOfOrigin' : awards[a].countryOfOrigin['name'] if awards[a].countryOfOrigin is not None else "",
                    'placeOfManufacture' : awards[a].placeOfManufacture['description'] if awards[a].placeOfManufacture is not None else "",
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