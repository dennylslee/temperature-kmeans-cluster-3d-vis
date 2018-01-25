# -*- coding: utf-8 -*-
import urllib
import re			#import regex library
import csv

import py_compile
py_compile.compile('weather_city_crawler.py')

import time
# -------------------------------------------------------------------------------

htmlfile = urllib.urlopen("http://weather.gc.ca/forecast/canada/index_e.html?id=on")
htmltext = htmlfile.read()

# scrape the title text
regextitle = '<title>(.+?)</title>'
patterntitle = re.compile(regextitle)
title = re.findall(patterntitle, htmltext)
print 'Title of webpage is: ', title[0]

# ---------------------------------------------------- build the ontario cities list

# scrape the city text into list based on observed html heuristics
regexcity ='<a href="/city/pages/on-(.+)_metric_e.html">(.+?)</a>'
patterncity = re.compile(regexcity)
cities = re.findall(patterncity, htmltext)  # return in the list with tuple

# count the number of duplication after scrape using first element in list as test
# numofalex = cities.count(('1', 'Algonquin Park (Brent)'))
numofalex = cities.count(cities[0])
print 'Number of duplication in original list is ',numofalex

# de-duplicate the city list
i=0
cities_dedup =[]   #this is a list of tuple
while i < len(cities):
	if cities[i] not in cities_dedup:
		cities_dedup.append(cities[i])
	i += 1

# first, convert into a new list of list; tuple is immutable. And added an index column - just for the hack of it!
# second, change the index from string to integer 

cities_dedup_list = []

i=0
while i < len(cities_dedup):
	cities_dedup_list.append([i]+list(cities_dedup[i]))  # added an index column; equivalent to enumerate
	# print list(enumerate(list(cities_dedup)))			 # create list of nested tuple with index
	cities_dedup_list[i][1] = int(cities_dedup_list[i][1])
	i += 1

# write the list into a csv
with open("OntarioCities.txt",'wb') as f :	# in python 2, csv should always open in binary mode to avoid extra line
	f_writer = csv.writer(f)
	f_writer.writerows(cities_dedup_list)   # writerows write the whole list as one

# ---------------------------------------------------- build the temperature matrix
start = time.time()

normaltemp_list = []
normaltemp_tuple = ()
city_crawl = 0 						# limit the crawl for dev
for row in cities_dedup:
	url = "http://weather.gc.ca/city/pages/on-" + row[0] + "_metric_e.html"
	print url
	htmlfile = urllib.urlopen(url)
	htmltext = htmlfile.read()
	# print htmltext

	# scrape the title text and extract the '7'
	# regextitle ='<title>\D*(.)\D*</title>'
	# patterntitle = re.compile(regextitle)
	# title = re.findall(patterntitle, htmltext)
	# print 'Title of webpage is: ', title

	regex ='<span class="wxo-metric-hide" title="max">(.+?)&deg;<abbr title="Celsius">C</abbr>.</span>'
	pattern1 = re.compile(regex)
	normalmax = re.findall(pattern1,htmltext)
	normalmaxint = int(normalmax[0])
	print 'Normal max is: ', normalmaxint

	regex ='<span class="wxo-metric-hide" title="min">(.+?)&deg;<abbr title="Celsius">C</abbr>.</span>'
	pattern2 = re.compile(regex)
	normalmin = re.findall(pattern2,htmltext)
	normalminint = int(normalmin[0])
	print 'Normal min is: ', normalminint

	regex ='<p class="text-center mrgn-tp-md mrgn-bttm-sm lead"><span class="wxo-metric-hide">(.+?)&deg;<abbr title="Celsius">'
	pattern3 = re.compile(regex)
	currenttemp = re.findall(pattern3,htmltext)
	if currenttemp != []:
		currenttempint = int(currenttemp[0])
	else:
		currenttempint = int(float(normalmaxint + normalminint)/2)  # if the city temp is not measured, then use historical average
	print 'Current temperature is: ', currenttempint

	regex = '<dl class="dl-horizontal mrgn-bttm-0 hidden-xs wxo-conds-tmp mrgn-tp-sm">\s*<dt>Observed at:</dt>\s*<dd class="mrgn-bttm-0">(.+?)</dd>\s*<dt>Date: </dt>'
	pattern4 = re.compile(regex)
	observingstation = re.findall(pattern4,htmltext)
	if observingstation == []:
		observingstation = ['']
	print "The observing station for this city is: ", str(observingstation[0])

	regex = '<a href="http://climate\.weather\.gc\.ca/climate_data/daily_data_e\.html\?StationID=(\d*)">Historical Weather</a>'
	regex2 = '<a href="http://climate\.weather\.gc\.ca/climate_data/hourly_data_e\.html\?StationID=(\d*)">Historical Weather</a>'
	pattern5 = re.compile(regex)
	observingstation_id = re.findall(pattern5,htmltext)
	if observingstation_id == []:
			regex2 = '<a href="http://climate\.weather\.gc\.ca/climate_data/hourly_data_e\.html\?StationID=(\d*)">Historical Weather</a>'
			pattern5_2 = re.compile(regex2)
			observingstation_id = re.findall(pattern5_2,htmltext)
	print "The observing station ID for this city is: ", observingstation_id[0]

	normaltemp_item = (normalmaxint, normalminint, currenttempint, str(observingstation[0]), int(observingstation_id[0]))
	normaltemp_list.append(normaltemp_item)

	# if city_crawl == 4:		# limit the crawl for dev
	# 	break
	# else:
	# 	city_crawl += 1

print('Entire job took:',time.time() - start)

with open("NormalTemp.txt",'wb') as f :	# in python 2, csv should always open in binary mode to avoid extra line
	f_writer = csv.writer(f)
	f_writer.writerows(normaltemp_list)   # writerows write the whole list as one

# print normaltemp_list
normaltemp_dict = {}
for row in normaltemp_list:
	normaltemp_dict[row[4]] = row[0], row[1], row[2], row[3]

print normaltemp_dict

# ---------------------------------------------------- print average temps

def avg_list(l):
	return float(sum(l))/len(l)		# convert one of the operand as floating point first before divison

templist0 = [row[0] for row in normaltemp_list]
templist1 = [row[1] for row in normaltemp_list]
templist2 = [row[2] for row in normaltemp_list]
TodayAvgHigh = int(avg_list(templist0))
TodayAvgLow  = int(avg_list(templist1))
TodayAvgTemp = int(avg_list(templist2))

print ("Today historical max average temp across Ontario is: "), TodayAvgHigh
print ("Today historical min average temp across Ontario is: "), TodayAvgLow
print ("Today average temp across Ontario is: "), TodayAvgTemp



