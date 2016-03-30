import xlrd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from extract_landlord_registration import extract_landlord_registration

master_list_url = 'http://www.indy.gov/eGov/City/DCE/Licenses/Documents/2016/Landlord_Registration_2016-03-27-04-00-41.xls'
#f = requests.get(master_list_url)
#xlsfile = f.content
#master_list_workbook = xlrd.open_workbook(file_contents=xlsfile)
master_list_workbook = xlrd.open_workbook('Landlord_Registration_2016-03-27-04-00-41.xls')
master_list_worksheet = master_list_workbook.sheet_by_index(0)

accella_url = 'http://permitsandcases.indy.gov/CitizenAccess/Cap/CapHome.aspx?module=Licenses&TabName=Licenses&TabList=HOME|0|Permits|1|Enforcement|2|Licenses|3|Planning|4|HHC|5|CurrentTabIndex|3'

#driver = webdriver.PhantomJS()
driver = webdriver.Firefox() # helpful for debugging
driver.set_window_size(1120, 550)

row = 1 # skip header in 0
while True:
	try:
		record = master_list_worksheet.cell(row, 0).value
		print record
	except IndexError: # if we reach the end of the sheet before encountering an empty cell we are done
		break
	if record == xlrd.empty_cell.value: # if we encounter an empty cell we are done
		break

	driver.get(accella_url)

	# wait for search page to load
	try:
		element = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber"))
		)
	except:
		print "search page didn't load"
		break

	# enter record number and click submit
	finally:
		driver.find_element_by_id('ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber').clear()	
		driver.find_element_by_id('ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber').send_keys(record)
		driver.find_element_by_id("ctl00_PlaceHolderMain_btnNewSearch").click()

	# wait for record result page to load 
	try:
		element = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_lblPermitNumber"))
		)
	except:
		print "record page didn't load"
		break
	finally:
		driver.save_screenshot("screenshot-{0}.png".format(record,))
		driver.find_element_by_id("imgMoreDetail").click()
		driver.find_element_by_id("imgRc").click()
		driver.find_element_by_id("imgASIT").click()
		f = open('record-{0}.html'.format(record,), 'w')
		f.write(driver.page_source.encode('ascii','ignore'))
		f.close()
		extract_landlord_registration(driver.page_source)
		
	row = row+1
driver.close()	
