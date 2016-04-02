"""
This module extracts all the various fields from an Accella Landlord Registration record.
It can either be called from the command line with -f pointing to the HTML file or called directly
from another module that scrapes Accella.

"""

import lxml
from lxml import html

import argparse


def extract_landlord_registration(html_string):
	record = {}
	html_object = lxml.html.fromstring(html_string)
	# and now we can actually extract the data we need.
	owner_column = html_object.xpath("//table[@id='ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList']//div[@class='MoreDetail_ItemCol1']/h2/text()")

	#print html_object.xpath("//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span[position()=3]/text()")
	record['owner_fname'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span[position()=1]/text())")
	if html_object.xpath("count(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span)") == 3.0:
		record['owner_middle'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span[position()=2]/text())")
		record['lname'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span[position()=3]/text())")

	else:
		record['lname'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/span[position()=2]/text())")

	record['owner_corporation'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=2 and preceding-sibling::br])")
	record['owner_mailing_1'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=3 and preceding-sibling::br])")
	#print html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=4 and preceding-sibling::br])").split(',')
	record['owner_city'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=last() and preceding-sibling::br])").split(',')[0]
	record['owner_state'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=last() and preceding-sibling::br])").split(',')[1]
	record['owner_zip'] = html_object.xpath("normalize-space(//td[@class='ACA_Table_Align_Top']/div[@class='MoreDetail_ItemCol MoreDetail_ItemCol1']//td/text()[position()=last() and preceding-sibling::br])").split(',')[2]

	#record['owner_primary_phone'] = html_object.xpath("//table[@id='ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList']//div[@class='ACA_PhoneNumberLTR' and position()=1]/text()")
	record['owner_primary_phone'] = html_object.xpath("//table[@id='ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList']//td[normalize-space(text())='Primary Phone:']/following-sibling/text()")
	record['owner_primary_phone'] = html_object.xpath("//table[@id='ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList']//td")
	##owner primary phone
	##owner secondary phone
	##owner fax
	##owner email
	landlord_column = html_object.xpath("//table[@id='ctl00_PlaceHolderMain_PermitDetailList1_RelatContactList']//table[@class='table_child ACA_SmLabel ACA_SmLabel_FontSize']/tr//td[position()=2]//text()")
	#print landlord_column
	##landlord fname
	##landlord lname
	##landlord corp
	##landlord mailing 1
	##landlord mailing 2
	##landlord city
	##landlord state
	##landlord zip
	##landlord primary phone
	##landlord secondary phone?
	##landlord fax
	##landlord email

	## for each property:
	## Chg Type:
	##property_parcel Parcel No.:
	##property_name Prop Name:
	##property_num_units No. of Units:
	##property_manager Prop Mgr:
	##property_manager_address Prop Mgt Addr:
	##property_manager_phone Prop Mgt Phone:
	##property_street_addr
	##property_street_dir Dir:
	##property_street_name Street Name:
	##property_street_type Type:
	##property_address_city
	##property_address_state
	##property_address_zip

	for key, value in record.viewitems():
		print key,value

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Extract relevant fields from Landlord Registration records')
	parser.add_argument('-f', '--file', help='HTML input file, from accella', required=True)
	args = parser.parse_args()
	f = open(args.file)
	extract_landlord_registration(f.read())
