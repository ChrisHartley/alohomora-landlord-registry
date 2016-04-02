#!/usr/bin/python
"""
This is a brute force scraping utility for the Indianapolis Accella data portal.
It scrapes by iterating record numbers in the URL, rather than searching and then saving each
resulting record. As such, it doesn't need Javascript and all the overhead that comes with it.
This used to work much better, but some point in 2015 Accella switched from a 7 digit [0-9] record ID
to [0-9A-Z]. It isn't clear to me really how this numbering system works since there are big gaps between
valid records, so you end up having to hit 100s of URLS to find a few scattered valid records. The whole thing
takes a ton of time to run, so in the end it might be faster to just use the Javascript Selenium scraper, which
is why I wrote it.

- Chris H., chris.hartley@anymouse.org

(C)opyright 2013-2016 Chris Hartley, GPL License v3

"""

import urllib2
import cookielib
from lxml import etree
import lxml.html
import StringIO
import string
import os
import sys
import argparse
import sqlite3
import zlib
from urllib2 import URLError
from httplib import BadStatusLine
import itertools

parser = argparse.ArgumentParser(description='Scrape the Indianapolis Citizens Access Portal')
parser.add_argument('-c', '--casetype', help='the case or permit prefix', required=True, choices=['TRA', 'DEM', 'REP', 'VBO', 'HIN', 'HSG', 'STR', 'HWG', 'WRK', 'ELC', 'ILP','CAP','VIO','LLR'])
parser.add_argument('-y', '--year', type=int, help='two digit year to scrape', required=True)
parser.add_argument('-e', '--maxerrors', type=int, help='number of allowed errors while scraping', default=100, required=False)
parser.add_argument('-f', '--file', help='sqlite3 database file', required=True)
parser.add_argument('-s', '--start', help='first record to scrape', required=False)
parser.add_argument('-d', '--end', help='last record to scrape', required=False)
args = parser.parse_args()


caseType = args.casetype
if caseType == 'ILP':
	tabName = 'Permits'
	module = 'Permits'
	howTheyCount = '0123456789'
if caseType == 'TRA':
	tabName = 'HHC'
	module = 'HHC'
	howTheyCount = '0123456789'
if caseType == 'DEM':
	tabName = 'Enforcement'
	module = 'Enforcement'
	caseType = 'VIO'
	howTheyCount = '0123456789'

if caseType == 'HWG':
	tabName = 'Enforcement'
	module = 'Enforcement'
	howTheyCount = '0123456789'
if caseType == 'VBO':
	tabName = 'Enforcement'
	module = 'Enforcement'
	caseType = 'CAP'
	howTheyCount = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
if caseType == 'VIO':
	tabName = 'Enforcement'
	module = 'Enforcement'
	caseType = 'VIO'
	howTheyCount = '0123456789'
	#howTheyCount = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
if caseType == 'LLR':
	tabName = 'Licenses'
	module = 'Licenses'
	caseType = 'CAP'
	howTheyCount = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

if args.start:
	start_casenumber = args.start.zfill(5)
else:
	start_casenumber = "00000"

if args.end:
	end_casenumber = args.end.zfill(5)
else:
	end_casenumber = 'ZZZZZ'

print "Start: " + start_casenumber
print "End: " + end_casenumber

caseYear = args.year

if args.maxerrors:
	allowedErrors = args.maxerrors
else:
	allowedErrors = 100

#howTheyCount = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#howTheyCount = '0123456789'


def main():
	con = sqlite3.connect(args.file)
	cur = con.cursor()

	# Set up cookies to work like regular browser and access entry URL to get set up properly
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	first = opener.open("http://www.indy.gov/eGov/City/DCE/Pages/Citizen%20Access%20Portal.aspx")
	errorCount = 0
	start = False
	for i in itertools.product(howTheyCount, repeat=5):
		if i == (start_casenumber[0], start_casenumber[1], start_casenumber[2], start_casenumber[3], start_casenumber[4]):
			start = True

		if start == True:
			case = "".join(i)

			if end_casenumber == case:
				break

			case_number = caseType + case
			cur.execute('SELECT case_error FROM cases WHERE case_number = ?', (case_number,))
			row = cur.fetchone()
			if row:
				if row[0] == 0:
					print case+ ": fetched previously, skipped"
					continue
				if row[0] == 1:
					print case+ ": url error on previously, skipped"
					continue
				if row[0] == 2:
					print case + ": accella gave error previously, re-trying"
					#continue

#				   http://permitsandcases.indy.gov/CitizenAccess/Cap/CapDetail.aspx?Module=Enforcement&TabName=Enforcement&capID1=15VIO&capID2=00000&capID3=14044&agencyCode=INDY&IsToShowInspection=
			url = 'http://permitsandcases.indy.gov/CitizenAccess/Cap/CapDetail.aspx?Module=%(module)s&TabName=%(tabName)s&capID1=%(year)d%(caseType)s&capID2=00000&capID3=%(case)s&agencyCode=INDY&IsToShowInspection=' % {"year": caseYear, "caseType": caseType , "case": case, "module": module, "tabName": tabName}
			print url
			try:
				f = opener.open(url)
			except URLError:
				print url
				cur.execute("INSERT OR REPLACE INTO cases (case_number, case_error) values (?, '1')", (case_number,))
				con.commit()
				errorCount += 1
				print case + ": url error detected and logged to db"
				continue
			except BadStatusLine:
				print 'bad status exception'
				continue

			html = f.read()
			isError = string.find(html, '<span id="ctl00_PlaceHolderMain_systemErrorMessage_lblMessageTitle" class="ACA_Show">An error has occurred.</span>')
			isError = isError + string.find(html, '<span id="ctl00_PlaceHolderMain_acc_login_label_login">')
			if (isError > -1):
				cur.execute("INSERT OR REPLACE INTO cases (case_number, case_error) values (?, '2')", (case_number,))
				con.commit()
				print case + ": accella error detected and logged to db"
				errorCount += 1
			else:
				cur.execute("INSERT OR REPLACE INTO cases (case_number, case_error, case_text) values (?, '0', ?)", (case_number, buffer(zlib.compress(html)),))
				con.commit()
				print case + ": written to db"
				errorCount = 0

	db.close()


if __name__ == '__main__':
	try:
		try:
			db = sqlite3.connect(args.file)
			cursor = db.cursor()
			cursor.execute('''
				create table if not exists cases(
				case_number TEXT,
				case_text BLOB,
				case_error INTEGER
				)
				''')
			db.commit()
		except Exception as e:
			# Roll back any change if something goes wrong
			db.rollback()
			raise e
		main()

	except KeyboardInterrupt:
		print 'Interrupted'
		db.commit()
		db.close()
		sys.exit(0)
