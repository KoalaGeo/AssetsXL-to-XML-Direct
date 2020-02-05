# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 15:48:42 2019

@author: jpass
"""

import pandas as pd
import uuid
import os
import logging
from time import strftime, localtime


#logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

md_datedef = strftime("%Y-%m-%d", localtime())
logging.debug(str(md_datedef))

''' 
row['Asset Identifier (Asset ID)'] is blank in exemplar spreadsheet template
and is used synonymously with metadata identifer.
However, it could be used to give an idenifier to the asset, which is separate 
to the metadata identifier (UUID).

In the XML there is a location for an id for the dataset, which doesn't allow a
UUID, so in the code we will generate a dataset id based on some prefix and row
number...
'''

idprefix = 'IAR_KEN_'
assetIDisPopulated = False
sampleNumber = 1461
standardName = 'National Geodata Centre for Kenya Schema'
standardVersion = '1.0'
md_poc_org = 'Ministry of Petroleum and Mining (National Geodata Centre for Kenya)'
md_poc_email = 'gdckenya@hotmail.com'
md_poc_indiv = 'enquiries'
showIndividual = True
useListedIndiv = False

write_to = "X:\\md\\kenxml"
#write_to = "X:\\md\\xmlout"

if not os.path.exists(write_to):
    os.makedirs(write_to)
    
os.chdir(write_to)

#diart2 = 'X:\md\BGS_Data&Info_AssetRegister_Template_v2.xlsx'
#diart2 = 'X:\md\BGS_Data&Info_AssetRegister_Template_v2_Kenya.xlsx'
diart2 = 'X:\md\BGS_Data&Info_AssetRegister_Template_v2_Kenya_20191114.xlsx'

# assets is the dataframe
#assets = pd.read_excel(diart2, sheet_name='Data&Info Asset Register', header=2, dtype=str)
assets = pd.read_excel(diart2, sheet_name='Data&Info Asset Register', header=2)

# ref https://stackoverflow.com/questions/45148292/python-pandas-read-excel-dtype-str-replace-nan-by-blank-when-reading-or-whe
# Replace NaN values in spreadsheet with empty string, otherwise get 'nan' literal in output
assets = assets.fillna('')

headings =  assets.columns
logging.debug("Column headings" + str(headings))

data_types = assets.dtypes
logging.debug("data types" + str(data_types))

headOutput = assets.head()
logging.debug("head()" + str(headOutput))

# First two rows are examples and we should remove them from the dataframe 
# (or possibly the spreadsheet)
#assets.drop(assets.index[[0,1]])

# Make a copy of the data frame dropping first two rows
actual_assets = assets.drop(assets.index[[0,1]]).copy()

gmd_start = '<?xml version="1.0" encoding="UTF-8"?>\n<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmx="http://www.isotc211.org/2005/gmx" xmlns:gsr="http://www.isotc211.org/2005/gsr" xmlns:gss="http://www.isotc211.org/2005/gss" xmlns:gts="http://www.isotc211.org/2005/gts" xmlns:srv="http://www.isotc211.org/2005/srv" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:geonet="http://www.fao.org/geonetwork" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\nxsi:schemaLocation="http://www.isotc211.org/2005/gmd http://inspire.ec.europa.eu/draft-schemas/inspire-md-schemas/apiso-inspire/apiso-inspire.xsd">\n'
gmd_end = '</gmd:MD_Metadata>'

elemAtt_close = '">'
empty_elemAtt_close = '"/>'

# We'll need to insert a UUID as the metadata record unique identifier
file_id_start = '<gmd:fileIdentifier>\n<gco:CharacterString>'
file_id_end = '</gco:CharacterString>\n</gmd:fileIdentifier>\n'

# Language of the metadata should always be English (for us)
md_lang = '<gmd:language>\n<gmd:LanguageCode codeList="ML_gmxCodelists.xml#LanguageCode" codeListValue="eng">English</gmd:LanguageCode>\n</gmd:language>\n'

# Below assumes everything is a dataset (not service, series, nongeographic...)
md_hlevelds = '<gmd:hierarchyLevel>\n<gmd:MD_ScopeCode codeList="gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode>\n</gmd:hierarchyLevel>\n'
md_hlevelsr = '<gmd:hierarchyLevel>\n<gmd:MD_ScopeCode codeList="gmxCodelists.xml#MD_ScopeCode" codeListValue="series">series</gmd:MD_ScopeCode>\n</gmd:hierarchyLevel>\n'
md_hlevelng = '<gmd:hierarchyLevel>\n<gmd:MD_ScopeCode codeList="gmxCodelists.xml#MD_ScopeCode" codeListValue="nonGeographicDataset">information applies to non-geographic data</gmd:MD_ScopeCode>\n</gmd:hierarchyLevel>\n'

# Just using dummy name and version below
md_standard = '<gmd:metadataStandardName>\n<gco:CharacterString>' + standardName + '</gco:CharacterString>\n</gmd:metadataStandardName>\n'
md_standard_version = '<gmd:metadataStandardVersion>\n<gco:CharacterString>' + standardVersion + '</gco:CharacterString>\n</gmd:metadataStandardVersion>\n'

# We'll need to insert the actual contact details for the metadata
md_contact_start = '<gmd:contact>\n<gmd:CI_ResponsibleParty>\n'
md_pocInd_start = '<gmd:individualName>\n<gco:CharacterString>'
md_pocInd_end =  '</gco:CharacterString>\n</gmd:individualName>\n'
md_pocOrg_start = '<gmd:organisationName>\n<gco:CharacterString>'
md_pocOrg_end = '</gco:CharacterString>\n</gmd:organisationName>\n'
md_conInfo_start = '<gmd:contactInfo>\n<gmd:CI_Contact>\n<gmd:address>\n<gmd:CI_Address>\n<gmd:electronicMailAddress>\n<gco:CharacterString>'
md_conInfo_end = '</gco:CharacterString>\n</gmd:electronicMailAddress>\n</gmd:CI_Address>\n</gmd:address>\n</gmd:CI_Contact>\n</gmd:contactInfo>\n'
md_contact_end = '<gmd:role>\n<gmd:CI_RoleCode codeList="gmxCodelists.xml#CI_RoleCode" codeListValue="pointOfContact">pointOfContact</gmd:CI_RoleCode>\n</gmd:role>\n</gmd:CI_ResponsibleParty>\n</gmd:contact>\n'

# Date when metadata was created / last published, it could be Now(), or it could reflect a date of asset registration (TBD)
# If the former, then assset registration date should probably also be recorded somewhere (report)
md_date_start = '<gmd:dateStamp>\n<gco:Date>'
md_date_end = '</gco:Date>\n</gmd:dateStamp>\n'

# Simple variant of wrapper for Coordinate reference system used by the dataset/asset
refsys_start = '<gmd:referenceSystemInfo>\n<gmd:MD_ReferenceSystem>\n<gmd:referenceSystemIdentifier>\n<gmd:RS_Identifier>\n<gmd:code>\n<gco:CharacterString>'
refsys_end = '</gco:CharacterString>\n</gmd:code>\n</gmd:RS_Identifier>\n</gmd:referenceSystemIdentifier>\n</gmd:MD_ReferenceSystem>\n</gmd:referenceSystemInfo>\n'

title_start = '<gmd:title>\n<gco:CharacterString>'
title_end = '</gco:CharacterString>\n</gmd:title>\n'
abstract_start = '<gmd:abstract>\n<gco:CharacterString>'
abstract_end = '</gco:CharacterString>\n</gmd:abstract>\n'

# There are many variants for keywords, listing individually or grouped, +/- relating to thesauri 
ds_keyword_part1_start = '<gmd:descriptiveKeywords>\n<gmd:MD_Keywords>\n'
ds_keyword_part1_end = '</gmd:MD_Keywords>\n</gmd:descriptiveKeywords>\n'
ds_keyword_part2_start = '<gmd:keyword>\n<gco:CharacterString>'
ds_keyword_part2_end = '</gco:CharacterString>\n</gmd:keyword>\n'
no_mineral_kw = '<gmd:keyword>\n<gco:CharacterString>No Mineral commodity/Keywords supplied</gco:CharacterString>\n</gmd:keyword>\n'

ds_maintenance_start = '<gmd:resourceMaintenance>\n<gmd:MD_MaintenanceInformation>\n'
ds_maintenance_end = '</gmd:MD_MaintenanceInformation>\n</gmd:resourceMaintenance>\n'
ds_updateFreq_start = '<gmd:maintenanceAndUpdateFrequency>\n<gmd:MD_MaintenanceFrequencyCode codeList="gmxCodelists.xml#MD_MaintenanceFrequencyCode" codeListValue="'
ds_updateFreq_end = '</gmd:MD_MaintenanceFrequencyCode>\n</gmd:maintenanceAndUpdateFrequency>\n'

ds_identInfo_start = '<gmd:identificationInfo>\n'
ds_ident_start = '<gmd:MD_DataIdentification id="'
ds_identInfo_end = '</gmd:MD_DataIdentification>\n</gmd:identificationInfo>\n'

missing_date_start = '<gmd:date>\n<gmd:CI_Date>\n<gmd:date gco:nilReason="missing" />\n'
publication_type2 = '<gmd:dateType>\n<gmd:CI_DateTypeCode codeList="gmxCodelists.xml#CI_DateTypeCode" codeListValue="publication">Date of publication</gmd:CI_DateTypeCode>\n</gmd:dateType>'
missing_date_end = '</gmd:CI_Date>\n</gmd:date>\n'

ds_citation_start = '<gmd:citation>\n<gmd:CI_Citation>\n'
ds_citation_end = '</gmd:CI_Citation>\n</gmd:citation>\n'
ds_citation_date_start = '<gmd:date>\n<gmd:CI_Date>\n<gmd:date>\n<gco:Date>'
ds_citation_date_mid = '</gco:Date>\n</gmd:date>\n<gmd:dateType>\n<gmd:CI_DateTypeCode codeList="gmxCodelists.xml#CI_DateTypeCode" codeListValue="'
ds_citation_date_end = '</gmd:CI_DateTypeCode>\n</gmd:dateType>\n</gmd:CI_Date>\n</gmd:date>\n'
publication_type = 'publication' + elemAtt_close + 'Date of publication'

# Edition
ds_citation_edit_start = '<gmd:edition>\n<gco:CharacterString>'
ds_citation_edit_end = '</gco:CharacterString>\n</gmd:edition>\n'
ds_citation_edit_notdef = '<gmd:edition gco:nilReason="unknown"/>\n'

ds_citation_presform_start = '<gmd:presentationForm>\n<gmd:CI_PresentationFormCode codeList="gmxCodelists.xml#CI_PresentationFormCode" codeListValue="'
ds_citation_presform_end = '</gmd:CI_PresentationFormCode>\n</gmd:presentationForm>\n'

# Our scale
spatialRes_start = '<gmd:spatialResolution>\n<gmd:MD_Resolution>\n<gmd:equivalentScale>\n<gmd:MD_RepresentativeFraction>\n<gmd:denominator>\n<gco:Integer>'
spatialRes_end = '</gco:Integer>\n</gmd:denominator>\n</gmd:MD_RepresentativeFraction>\n</gmd:equivalentScale>\n</gmd:MD_Resolution>\n</gmd:spatialResolution>\n'
spatialRes_notdefined = '<gmd:spatialResolution>\n<gmd:MD_Resolution>\n<gmd:equivalentScale gco:nilReason="unknown" />\n</gmd:MD_Resolution>\n</gmd:spatialResolution>\n'

ds_lang_start = '<gmd:language>\n<gmd:LanguageCode codeList="http://www.loc.gov/standards/iso639-2/php/code_list.php" codeListValue="'
ds_lang_end = '</gmd:LanguageCode>\n</gmd:language>\n'

eng_lang = 'eng' + elemAtt_close + 'English'
fre_lang = 'fre' + elemAtt_close + 'French'
kin_lang = 'kin' + elemAtt_close + 'Kinyarwanda'
swa_lang = 'swa' + elemAtt_close + 'Swahili'
vie_lang = 'vie' + elemAtt_close + 'Vietnamese'

giTopicCat_start = '<gmd:topicCategory>\n<gmd:MD_TopicCategoryCode>'
giTopicCat_end = '</gmd:MD_TopicCategoryCode>\n</gmd:topicCategory>\n'

ds_distribs_open = '<gmd:distributionInfo>\n<gmd:MD_Distribution>\n'
ds_distribs_close = '</gmd:MD_Distribution>\n</gmd:distributionInfo>\n'
md_format_start = '<gmd:distributionFormat>\n<gmd:MD_Format>\n<gmd:name>\n<gco:CharacterString>'
md_format_end = '</gco:CharacterString>\n</gmd:name>\n<gmd:version gco:nilReason="unknown"/>\n</gmd:MD_Format>\n</gmd:distributionFormat>\n'

transOpt_start = '<gmd:transferOptions>\n<gmd:MD_DigitalTransferOptions>\n'
transOpt_end = '</gmd:MD_DigitalTransferOptions>\n</gmd:transferOptions>\n'
onlineLink = '<gmd:onLine>\n<gmd:CI_OnlineResource>\n<gmd:linkage>\n<gmd:URL>'
oLLnkName = '</gmd:URL>\n</gmd:linkage>\n<gmd:name>\n<gco:CharacterString>'
oLLnkDesc = '</gco:CharacterString>\n</gmd:name>\n<gmd:description>\n<gco:CharacterString>'
oLLnkFunc = '</gco:CharacterString>\n</gmd:description>\n<gmd:function>\n<gmd:CI_OnLineFunctionCode codeList="gmxCodelists.xml#CI_OnLineFunctionCode" codeListValue="download"/>\n</gmd:function>\n</gmd:CI_OnlineResource>\n</gmd:onLine>\n'

ds_dqinfo_start = '<gmd:dataQualityInfo>\n<gmd:DQ_DataQuality>\n<gmd:scope gco:nilReason="unknown"/>\n'
ds_dqinfo_end = '</gmd:DQ_DataQuality>\n</gmd:dataQualityInfo>\n'
lineage_start = "<gmd:lineage>\n<gmd:LI_Lineage>\n<gmd:statement>\n<gco:CharacterString>"
lineage_end = "</gco:CharacterString>\n</gmd:statement>\n</gmd:LI_Lineage>\n</gmd:lineage>\n"

# Status
ds_prog_start = '<gmd:status>\n<gmd:MD_ProgressCode codeList="gmxCodelists.xml#MD_ProgressCode" codeListValue="'
ds_prog_end = '</gmd:status>\n'
ds_prog_notdefined = '<gmd:status gco:nilReason="missing" />\n'

# Series Name/Parent Title
''' 
Not sure where to map this to, there is a series section at the end of the document,
but it really needs a fullish metadata description.

Using instead parent identifier at top of document...
'''
# Note ds_series XML is invalid as <gmd:composedOf> is element only, but in the code we have text

ds_series_notdefined = '<gmd:series gco:nilReason="inapplicable"/>\n'
ds_series_start = '<gmd:series>\n<gmd:DS_ProductionSeries>\n<gmd:composedOf>'
ds_series_end = '</gmd:composedOf>\n<gmd:seriesMetadata gco:nilReason="unknown" />\n</gmd:DS_ProductionSeries>\n</gmd:series>\n'

ds_parent_notdef = '<gmd:parentIdentifier gco:nilReason="inapplicable"/>\n'
ds_parent_start = '<gmd:parentIdentifier>\n<gco:CharacterString>'
ds_parent_end = '</gco:CharacterString>\n</gmd:parentIdentifier>\n'

ds_collective_start = '<gmd:collectiveTitle>\n<gco:CharacterString>'
ds_collective_end = '</gco:CharacterString>\n</gmd:collectiveTitle>\n'
ds_collective_nodef = '<gmd:collectiveTitle gco:nilReason="inapplicable" />\n'

ds_extent_notdef = '<gmd:extent gco:nilReason="unknown" />\n'
ds_extent_start = '<gmd:extent>\n<gmd:EX_Extent>\n<gmd:description>\n<gco:CharacterString>'
ds_descriptEnd = '</gco:CharacterString>\n</gmd:description>\n'
ds_extent_end = '</gmd:EX_Extent>\n</gmd:extent>\n'
ds_geogElem_start = '<gmd:geographicElement>\n<gmd:EX_GeographicBoundingBox>\n'
ds_geogElem_end = '</gmd:EX_GeographicBoundingBox>\n</gmd:geographicElement>\n'
westStart = '<gmd:westBoundLongitude>\n<gco:Decimal>'
westEndEastStart = '</gco:Decimal>\n</gmd:westBoundLongitude>\n<gmd:eastBoundLongitude>\n<gco:Decimal>'
eastEndSouthStart = '</gco:Decimal>\n</gmd:eastBoundLongitude>\n<gmd:southBoundLatitude>\n<gco:Decimal>'
southEndNorthStart = '</gco:Decimal>\n</gmd:southBoundLatitude>\n<gmd:northBoundLatitude>\n<gco:Decimal>'
northEnd = '</gco:Decimal>\n</gmd:northBoundLatitude>\n'

'''
Temporal extent may be not populated, one time (instant), or a range (period)
'''
ds_tempo_notdef = '<gmd:extent>\n<gmd:EX_Extent>\n<gmd:temporalElement gco:nilReason="unknown" />\n</gmd:EX_Extent>\n</gmd:extent>\n'
ds_tempo_start = '<gmd:extent>\n<gmd:EX_Extent>\n<gmd:temporalElement>\n<gmd:EX_TemporalExtent>\n<gmd:extent>\n'
ds_tempo_end = '</gmd:extent>\n</gmd:EX_TemporalExtent>\n</gmd:temporalElement>\n</gmd:EX_Extent>\n</gmd:extent>\n'
ds_tempo_TI_start = '<gml:TimeInstant gml:id="ti_1">\n<gml:timePosition>'
ds_tempo_TI_end = '</gml:timePosition>\n</gml:TimeInstant>\n'
ds_tempo_TP_start = '<gml:TimePeriod gml:id="tp_1">\n<gml:beginPosition>'
ds_tempo_TP_mid = '</gml:beginPosition>\n<gml:endPosition>'
ds_tempo_TP_end = '</gml:endPosition>\n</gml:TimePeriod>\n'

ds_usecon_start = '<gmd:resourceConstraints xlink:title="Limitations/Use_constraints">\n<gmd:MD_Constraints>\n<gmd:useLimitation>\n<gco:CharacterString>'
ds_usecon_end = '</gco:CharacterString>\n</gmd:useLimitation>\n</gmd:MD_Constraints>\n</gmd:resourceConstraints>\n'
ds_accesscon_start = '<gmd:resourceConstraints xlink:title="Limitations/Access constraints">\n<gmd:MD_LegalConstraints>\n<gmd:accessConstraints>\n<gmd:MD_RestrictionCode codeList="gmxCodelists.xml#MD_RestrictionCode" codeListValue="otherRestrictions"/>\n</gmd:accessConstraints>\n<gmd:otherConstraints>\n<gco:CharacterString>'
ds_accesscon_end = '</gco:CharacterString>\n</gmd:otherConstraints>\n</gmd:MD_LegalConstraints>\n</gmd:resourceConstraints>\n'
ds_lic_start = '<gmd:resourceConstraints xlink:title="Conditions/Licence/Restriction Code">\n<gmd:MD_LegalConstraints>\n<gmd:useConstraints>\n<gmd:MD_RestrictionCode codeList="gmxCodelists.xml#MD_RestrictionCode" codeListValue="'
ds_lic_end = '</gmd:useConstraints>\n<gmd:otherConstraints>\n<gmx:Anchor xlink:href="#">Conditions apply</gmx:Anchor>\n</gmd:otherConstraints>\n</gmd:MD_LegalConstraints>\n</gmd:resourceConstraints>\n'
ds_lic_notdef = '<gmd:resourceConstraints xlink:title="Conditions/Licence/Restriction Code">\n<gmd:MD_LegalConstraints>\n<gmd:useConstraints gco:nilReason="missing" />\n<gmd:otherConstraints>\n<gmx:Anchor xlink:href="#">No specifed conditions apply</gmx:Anchor>\n</gmd:otherConstraints>\n</gmd:MD_LegalConstraints>\n</gmd:resourceConstraints>\n'
'''
Template has 'Translation Needs' as ISO 19115, but not sure where this would go
mapping to otherCitationDetails below.
'''
ds_cit_otherdet_start = '<gmd:otherCitationDetails>\n<gco:CharacterString>'
ds_cit_otherdet_end = '</gco:CharacterString>\n</gmd:otherCitationDetails>\n'
ds_cit_otherdet_notdef = '<gmd:otherCitationDetails gco:nilReason="inapplicable"/>\n'
'''
Contacts
'''
aut_poc = '<gmd:pointOfContact xlink:title="Author">\n<gmd:CI_ResponsibleParty>\n'
pub_poc = '<gmd:pointOfContact xlink:title="Publisher">\n<gmd:CI_ResponsibleParty>\n'
cud_poc = '<gmd:pointOfContact xlink:title="Custodian">\n<gmd:CI_ResponsibleParty>\n'
own_poc = '<gmd:pointOfContact xlink:title="Owner">\n<gmd:CI_ResponsibleParty>\n'
poc_poc = '<gmd:pointOfContact xlink:title="PointOfContact">\n<gmd:CI_ResponsibleParty>\n'

indNam_start = '<gmd:individualName>\n<gco:CharacterString>'
indNam_end =  '</gco:CharacterString>\n</gmd:individualName>\n'
orgNam_start = '<gmd:organisationName>\n<gco:CharacterString>'
orgNam_end = '</gco:CharacterString>\n</gmd:organisationName>\n'
conAdd_start = '<gmd:contactInfo>\n<gmd:CI_Contact>\n<gmd:address>\n<gmd:CI_Address>\n'
conAdd_end = '</gmd:CI_Address>\n</gmd:address>\n</gmd:CI_Contact>\n</gmd:contactInfo>\n'

adminArea_start = '<gmd:administrativeArea>\n<gco:CharacterString>'
adminArea_end = '</gco:CharacterString>\n</gmd:administrativeArea>\n'

role_start = '<gmd:role>\n<gmd:CI_RoleCode codeList="gmxCodelists.xml#CI_RoleCode" codeListValue="'
aut_role = 'author">Author'
pub_role = 'publisher">Publisher'
cud_role = 'custodian">Custodian'
own_role = 'owner">Owner'
poc_role = 'pointOfContact">Point of Contact'
pocEnd = '</gmd:CI_RoleCode>\n</gmd:role>\n</gmd:CI_ResponsibleParty>\n</gmd:pointOfContact>\n'

suppInf_start = '<gmd:supplementalInformation>\n<gco:CharacterString>\n<![CDATA[ {'
suppInf_end = '} ]]>\n</gco:CharacterString>\n</gmd:supplementalInformation>\n'
ar_tn = '"Translation Needs":"'
ar_nop = '"Number of pages (Hardcopy)":"'
ar_alh = '"Archive Location (Hardcopy)":"'
ar_lin = '"Location in Archive (Hardcopy)":"'
ar_rai = '"Risk and Impact":"'
ar_vat = '"Vital asset to the organisation?":"'
ar_cav = '"Current Asset Volume":"'
ar_ds = '"Digitalizing status":"'
ar_sd = '"Scanned Date":"'
ar_nsc = '"Name of Staff Scanning":"'
ar_dal = '"Digital Asset location":"'
ar_rp = '"Retention period":"'
ar_sw = '"Shared with":"'
ar_com = '"Comments":"'
qc = '",\n'

graphic_start = '<gmd:graphicOverview>\n<gmd:MD_BrowseGraphic>\n'
graphic_end = '</gmd:MD_BrowseGraphic>\n</gmd:graphicOverview>\n'
fileName_start = '<gmd:fileName>\n<gco:CharacterString>'
fileName_end = '</gco:CharacterString>\n</gmd:fileName>\n'
fileDesc_start = '<gmd:fileDescription>\n<gco:CharacterString>'
fileDesc_end = '</gco:CharacterString>\n</gmd:fileDescription>\n'
fileType_start = '<gmd:fileType>\n<gco:CharacterString>'
fileType_end = '</gco:CharacterString>\n</gmd:fileType>'
fileName_default = 'http://www.sciencekids.co.nz/images/pictures/flags680/Kenya.jpg'
fileDesc_default = 'National flag of Kenya'
fileType_default = 'image/jpeg'


for index, row in actual_assets.head(n=sampleNumber).iterrows():
    ''' Start file here '''
    file_id = str(uuid.uuid4())
    fileout = open(file_id + ".xml","a")
    
    '''# 1 <gmd:fileIdentifier> '''
    file_id_x = file_id_start + file_id + file_id_end
    
    '''#2  <gmd:language> '''
    
    '''#3 <gmd:parentIdentifier> '''   
    if not row["Series Name/Parent Title"]:
        ds_series_x = ds_parent_notdef
        ds_coll_x = ds_collective_nodef
    else:
        ds_series_x = ds_parent_start + str(row["Series Name/Parent Title"]) + ds_parent_end
        ds_coll_x = ds_collective_start + str(row["Series Name/Parent Title"]) + ds_collective_end
        
    '''#4 <gmd:hierarchyLevel>'''
    logging.debug(str(row["Resource Type"]))
    if row["Resource Type"] == 'dataset':
        md_hlevel = md_hlevelds
    elif row["Resource Type"] == 'series':
        md_hlevel = md_hlevelsr
    else:
        md_hlevel = md_hlevelng
        
    '''#5 <gmd:hierarchyLevelName> '''
    
    '''#6 <gmd:contact> (contact for metadata) '''
    if not useListedIndiv:
        md_pocIndx = md_pocInd_start + md_poc_indiv + md_pocInd_end
    else:
        md_pocIndx = md_pocInd_start + str(row["Name of staff member entering metadata records"]) + md_pocInd_end
    
    md_pocOrgx = md_pocOrg_start + md_poc_org + md_pocOrg_end
    md_pocEmailx = md_conInfo_start + md_poc_email + md_conInfo_end
    
    if showIndividual:
        md_contact_x = md_contact_start + md_pocIndx + md_pocOrgx + md_pocEmailx + md_contact_end
    else:
        md_contact_x = md_contact_start + md_pocOrgx + md_pocEmailx + md_contact_end
        
    '''#7 <gmd:dateStamp> (metadata date)'''
    # Date is converted to format like '2019-07-25 00:00:00'
    # which is not correct format for gco:Date or gco:DateTime
    # need to convert to either `2019-07-25` or '2019-07-25T00:00:00'
    if not row["Date of record entered"]:
        md_date_x = md_date_start + md_datedef + md_date_end
    else:
        if (str(row["Date of record entered"]).find('-') == 0):
            # date is invalid like --05-16
            # reformat to 2016-05
            reformattedDate = "20" +  str(row["Date of record entered"])[4:5] + "-" + str(row["Date of record entered"])[2:3]
            md_date_x = md_date_start + reformattedDate + md_date_end
        else:
            md_date_x = md_date_start + str(row["Date of record entered"])[0:10] + md_date_end
            
    ''' #8 <gmd:metadataStandardName> '''
    
    ''' #9 <gmd:metadataStandardVersion> '''
    
    ''' #10 <gmd:dataSetURI> '''
    
    ''' #11 <gmd:spatialRepresentationInfo> '''
    
    ''' #12 <gmd:referenceSystemInfo> '''
       
    '''
    We could have more than one refsys, but we can't really use a reliable 
    splitting mechanism even if more than one becuase this is free text
    '''
    refsys_x = refsys_start + str(row["Spatial Reference System"]) + refsys_end
    
    ''' #13 <gmd:identificationInfo> starts '''
    if assetIDisPopulated:
        ds_ident_x = ds_ident_start + idprefix + str(row['Asset Identifier (Asset ID)']).strip() + elemAtt_close
    else:
        ds_ident_x = ds_ident_start + idprefix + str(index) + elemAtt_close
        
    ''' #14 <gmd:citation> starts '''
    ''' #15 <gmd:title> '''
    titleText = str(row['Name of Information asset or collection (Asset Name/Title)']).replace('&', 'and').strip()
    ds_title_x = title_start + titleText + title_end
    
    ''' #16 gmd:alternateTitle> '''
    
    ''' #17 <gmd:date> '''
    # Could be more than one, but assuming one here
    # Need to cater for missing, and also different formats
    # --05-16 as option specified in template is not valid for XML date type,
    # but otherwise length doesn't matter.
    if not row["Publication Date"]:
        ds_citation_date_x = missing_date_start + publication_type2 + missing_date_end
    else:
        if (str(row["Publication Date"]).find('-') == 0):
            # date is invalid like --05-16
            # reformat to 2016-05
            reformattedPDate = "20" +  str(row["Date of record entered"])[4:5] + "-" + str(row["Date of record entered"])[2:3]
            ds_citation_date_x = ds_citation_date_start + reformattedPDate + ds_citation_date_mid + publication_type + ds_citation_date_end
        else:
            ds_citation_date_x = ds_citation_date_start + str(row["Publication Date"])[0:10] + ds_citation_date_mid + publication_type + ds_citation_date_end
    
    ''' #18 <gmd:edition> '''
    if not row["Edition"]:
        ds_edition_x = ds_citation_edit_notdef
    else:
        ds_edition_x = ds_citation_edit_start + str(row["Edition"]) + ds_citation_edit_end
    
    ''' #19 <gmd:presentationForm> '''
    ds_presform = ds_citation_presform_start + row["Asset Category/Presentation Form"] + elemAtt_close + row["Asset Category/Presentation Form"] + ds_citation_presform_end
    
    ''' #20 <gmd:otherCitationDetails> '''
    if not row["Translation Needs"]:
        ds_cit_otherdet_x = ds_cit_otherdet_notdef
    else:
        ds_cit_otherdet_x = ds_cit_otherdet_start  + str(row["Translation Needs"]) + ds_cit_otherdet_end
    ''' End of citation '''
    ds_citation_x = ds_citation_start + ds_title_x + ds_citation_date_x + ds_edition_x + ds_presform + ds_cit_otherdet_x + ds_coll_x + ds_citation_end
    
    ''' #21  <gmd:abstract> '''
    abstract_text = str(row['Asset Description (Abstract)']).replace('&', 'and').strip()
    ds_abstract_x = abstract_start + abstract_text + abstract_end
    
    ''' #22 <gmd:status> '''
    if not row["Status"]:
        ds_status_x = ds_prog_notdefined
    else:
        ds_status_x = ds_prog_start + str(row["Status"]) + empty_elemAtt_close + ds_prog_end
        
    ''' #23 Points of contact '''
    ds_auth_x = aut_poc + indNam_start + str(row["Author (s)"]).replace('&', 'and') + indNam_end + role_start + aut_role + pocEnd
    ds_pub_x = pub_poc + orgNam_start + str(row["Publisher"]).replace('&', 'and') + orgNam_end + conAdd_start + adminArea_start + str(row["Place of Publication"])  + adminArea_end + conAdd_end + role_start + pub_role + pocEnd
    ds_cud_x = cud_poc + orgNam_start + str(row["Custodian"]).replace('&', 'and') + orgNam_end + role_start + cud_role + pocEnd
    ds_poc_x = poc_poc + orgNam_start + str(row["Point of Contact"]).replace('&', 'and') + orgNam_end + role_start + poc_role + pocEnd
    ds_own_x = own_poc + indNam_start + str(row["Information Asset Owner"]).replace('&', 'and') + indNam_end + role_start + own_role + pocEnd
    
    ''' #24 <gmd:resourceMaintenance> '''
    ds_maintenance_x = ds_maintenance_start + ds_updateFreq_start + str(row["Maintenance/Update Schedule"]) + elemAtt_close + str(row["Maintenance/Update Schedule"]) + ds_updateFreq_end + ds_maintenance_end
    
    ''' #24B <gmd:graphicOverview> '''
    if not row["Thumbnail Digital location (include network/local file path if appropriate)"]:
        ds_graphic_x = graphic_start + fileName_start + fileName_default + fileName_end + fileDesc_start + fileDesc_default + fileDesc_end + fileType_start + fileType_default + fileType_end + graphic_end
    else:
        ds_graphic_x = graphic_start + fileName_start + str(row["Thumbnail Digital location (include network/local file path if appropriate)"]) + fileName_end + fileDesc_start + "Thumbnail" + fileDesc_end + fileType_start + fileType_default + fileType_end + graphic_end
    
    ''' #25 <gmd:descriptiveKeywords> '''
    # We should have more than one keyword
    keywordString = ""
    keywordList = []
    if not row["Mineral commodity/Keywords"]:
        ds_keyword_x = ds_keyword_part1_start + no_mineral_kw + ds_keyword_part1_end
    else:
        for keyword in [k.strip() for k in row["Mineral commodity/Keywords"].split(',')]:
            keywordList.append(ds_keyword_part2_start + keyword + ds_keyword_part2_end)
            ds_keyword_x = ds_keyword_part1_start + keywordString.join(keywordList) + ds_keyword_part1_end

    ''' #26 <gmd:resourceConstraints> (more than one)'''
    if not row["Use Constraints"]:
        ds_usec_x = ds_usecon_start + "No known usage conditions apply" + ds_usecon_end
    else:
        ds_usec_x = ds_usecon_start + str(row["Use Constraints"]) + ds_usecon_end

    if not row["Access Constraints"]:
        ds_accc_x = ds_accesscon_start + "No known access constraints apply" + ds_accesscon_end
    else:
        ds_accc_x = ds_accesscon_start + str(row["Access Constraints"]) + ds_accesscon_end

    if not row["Licence/Restriction Code"]:
        ds_lic_x = ds_lic_notdef
    else:
        ds_lic_x = ds_lic_start + str(row["Licence/Restriction Code"]) + empty_elemAtt_close + ds_lic_end
 
    ''' #27 <gmd:spatialRepresentationType> '''
    
    ''' #28 <gmd:spatialResolution> '''
    if not row["Scale"]:
        spatialRes_x = spatialRes_notdefined
    else:
        spatialRes_x = spatialRes_start + str(row["Scale"]) + spatialRes_end
    
    ''' #29 <gmd:language> '''
    # Asset language
    # Can have multiple here assuming English
    if not row["Language"]:
        ds_lang_x = ds_lang_start + eng_lang + ds_lang_end
    else:
        # To do but currently using English
        ds_lang_x = ds_lang_start + eng_lang + ds_lang_end
        
    ''' #30 <gmd:characterSet> '''
    
    ''' #40 <gmd:topicCategory> '''
    giTopicCat = giTopicCat_start + str(row["Topic"]) + giTopicCat_end
    
    ''' #41 <gmd:extent> ( several geo + temporal ) '''
    
    if not row["Temporal Extent"]:
        ds_tempo_x = ds_tempo_notdef
    else:
        if (str(row["Temporal Extent"]).find('/') != -1):
            logging.debug(str(row["Temporal Extent"]) + " is a time period")
            tempo_values = str(row["Temporal Extent"]).split('/')
            ds_tempo_x = ds_tempo_start + ds_tempo_TP_start + tempo_values[0] + ds_tempo_TP_mid + tempo_values[1] + ds_tempo_TP_end + ds_tempo_end
        else:
            logging.debug(str(row["Temporal Extent"]) + " is a time instant")
            ds_tempo_x = ds_tempo_start + ds_tempo_TI_start + str(row["Temporal Extent"]) + ds_tempo_TI_end + ds_tempo_end
    
    ''' Writing Geographic Area and Bounding Box as one Extent section '''
    if not row["Geographic Area"]:
        #ds_extent_x = ds_extent_notdef
        ds_extent_x = ds_extent_start + "Geographic area not described" + ds_descriptEnd
    else:
        ds_extent_x = ds_extent_start + str(row["Geographic Area"]).replace('&', 'and').strip() + ds_descriptEnd
    
    ''' Have an issue trying to force decimal values with our string data 
    Instead of casting all data as string, can work with data in 'native' format and cast when required.
    native data is float for coordinates, here we format as string with 8 decimal places
    '''
    if row["x_min"]:
        westDec = f'{row["x_min"]:.8f}'
        eastDec = f'{row["x_max"]:.8f}'
        sudDec = f'{row["y_min"]:.8f}'
        nordDec = f'{row["y_max"]:.8f}'
        
        ds_geogEx_x = ds_geogElem_start + westStart + westDec + westEndEastStart + eastDec + eastEndSouthStart + sudDec + southEndNorthStart + nordDec + northEnd + ds_geogElem_end + ds_extent_end
    else:
        ds_geogEx_x = ds_extent_end
        
    ''' #42 <gmd:supplementalInformation> '''
    ds_supp_x = suppInf_start +  ar_tn + str(row["Translation Needs"]) + qc + ar_nop + str(row[" Number of pages (Hardcopy)"]) + qc + ar_alh + str(row["Archive Location (Hardcopy)"]) + qc + ar_lin + str(row["Location in Archive (Hardcopy)"]) + qc + ar_rai + str(row["Risk and Impact"]) + qc + ar_vat + str(row["Vital asset to the organisation?"]) + qc + ar_cav + str(row["Current Asset Volume MB"]) + qc + ar_ds + str(row["Digitalizing status"]) + qc + ar_sd + str(row["Scanned Date"]) + qc + ar_nsc + str(row["Name of Staff Scanning"]) + qc + ar_dal + str(row["Digital Asset location (include network/local file path if appropriate)"]) + qc + ar_rp + str(row["Retention period"]) + qc + ar_sw + str(row["Shared with"]) + qc + ar_com + str(row["Comments"]) + '"' + suppInf_end
    
    ''' End of gmd:identificationInfo '''
    
    ''' #43 <gmd:contentInfo> (several) '''
    
    ''' Start of <gmd:distributionInfo> '''
    
    ''' #44  <gmd:distributionFormat> (several) '''
    mformatString = ""
    mformatList = []    
    if not row["MD_Format"]:
        md_format_x = ds_distribs_open + md_format_start + "No MD_FORMAT defined" + md_format_end  
    else:
        for mformat in [m.strip() for m in row["MD_Format"].split(',')]:
            mformatList.append(md_format_start + mformat + md_format_end)
            md_format_x = ds_distribs_open + mformatString.join(mformatList)
    
    transOptString = ""
    transOptList = []  
    if not row["Digital Asset location (include network/local file path if appropriate)"]:
        trans_x = ds_distribs_close
    else:
        for transOpt in [t.strip() for t in row["Digital Asset location (include network/local file path if appropriate)"].split(',')]:
            transOptList.append(transOpt_start + onlineLink + transOpt + oLLnkName + titleText + oLLnkDesc + abstract_text + oLLnkFunc + transOpt_end)
            trans_x = transOptString.join(transOptList) + ds_distribs_close

    ''' End of gmd:distributionInfo '''
    
    ''' Start of <gmd:dataQualityInfo> (may have many but one is probably sufficient ? )'''
    
    ''' #45 <gmd:scope> (principal same as resource type ?) '''
    
    ''' #46 gmd:report> (many) '''
    
    ''' #47 <gmd:lineage> one per DQI '''
    if not row["Lineage/Source"]:
        lineage_x = lineage_start + "No lineage information supplied" + lineage_end
    else:
        lineage_x = lineage_start + str(row["Lineage/Source"]).replace('&', 'and').strip() + lineage_end
        
    ''' End of first <gmd:dataQualityInfo> '''
    
    ''' #48 <gmd:series> '''
    '''
    if not row["Series Name/Parent Title"]:
        ds_series_x = ds_series_notdefined
    else:
        ds_series_x = ds_series_start + str(row["Series Name/Parent Title"]) + ds_series_end
    '''
    
    ''' End of metadata record '''
    # Put the WIP together to view
    # Could we just open a file and append values as we create them?
    
    md_x = gmd_start + file_id_x + md_lang + ds_series_x + md_hlevel + md_contact_x + md_date_x + md_standard + md_standard_version + refsys_x + ds_identInfo_start + ds_ident_x + ds_citation_x + ds_abstract_x + ds_status_x + ds_auth_x + ds_pub_x + ds_cud_x + ds_poc_x + ds_own_x + ds_maintenance_x + ds_graphic_x + ds_keyword_x + ds_usec_x + ds_accc_x + ds_lic_x + spatialRes_x + ds_lang_x + giTopicCat + ds_tempo_x + ds_extent_x + ds_geogEx_x + ds_supp_x + ds_identInfo_end + md_format_x + trans_x + ds_dqinfo_start + lineage_x + ds_dqinfo_end + gmd_end
    #print(md_x)
    fileout.write(md_x)
    fileout.close()