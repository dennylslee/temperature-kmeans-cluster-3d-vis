
import urllib
import csv
import datetime
from time import gmtime, strftime

import matplotlib.pyplot as plt
from matplotlib import style
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
style.use('ggplot')

from mpl_toolkits.basemap import Basemap

import numpy as np
import sklearn
from sklearn.cluster import KMeans

import py_compile
py_compile.compile('weather_station_processing.py')

#---------------------------------------------------- read in the city temperature for cross reference

with open("NormalTemp.txt",'rb') as f :	# in python 2, csv should always open in binary mode to avoid extra line
	file = csv.reader(f)
	normaltemp_list = [row for row in file]   # readrows read the whole list as one

#---------------------------------------------------- build a dict with key = std id for lookup
normaltemp_dict = {}
for row in normaltemp_list:
	# row4 is the std id, it is used as key in dict
	normaltemp_dict[int(row[4])] = int(row[0]), int(row[1]), int(row[2]), row[3]

print normaltemp_dict

# ---------------------------------------------------- print average temps

def avg_list(l):
	return float(sum(l))/len(l)		# convert one of the operand as floating point first before divison

templist0 = [int(row[0]) for row in normaltemp_list]
templist1 = [int(row[1]) for row in normaltemp_list]
templist2 = [int(row[2]) for row in normaltemp_list]
TodayAvgHigh = int(avg_list(templist0))
TodayAvgLow  = int(avg_list(templist1))
TodayAvgTemp = int(avg_list(templist2))

print ("Today normal max average temp across Ontario is: "), TodayAvgHigh
print ("Today normal min average temp across Ontario is: "), TodayAvgLow
print ("Today average temp across Ontario is: "), TodayAvgTemp

# ---------------------------------------------------- read the lat/long and other station info

with open("Station Inventory EN.csv", 'rb') as g:
	CanStationfile = csv.reader(g)
	CanStationlist = []
	for row in CanStationfile:
		CanStationlist = CanStationlist + [row]

CanStationlist = CanStationlist[4:]														# remove the first 4 rows
CanStationlist = [(row[0], row[1], row[3], row[6], row[7]) for row in CanStationlist]	# pick out 5 specific columns for name/province/std id/lat/long

OnStationdict = {}				# creat a dictionary for lookup
for row in CanStationlist:		# create a loop to filter out the Ontario entries into a dictionary
	if row[1] == 'ONTARIO':
		OnStationdict[int(row[2])] = row[0],row[1],int(row[2]),float(row[3]),float(row[4]) # std id as key, value = std name/province/std id/lat/long

# ---------------------------------------------------- generation the lat/long list & clean up abnormal

templist_lat = [float(row[3]) for row in dict.values(OnStationdict)]  # note index is wrt the value tuple
templist_long = [float(row[4]) for row in dict.values(OnStationdict)]
# replace the abnormal zero pair lat-long in floating pt value; if the lat/long is zero zero, we replace it with the avg lat long
avg_lat = avg_list(templist_lat)
avg_long = avg_list(templist_long)
templist_lat = [row  if row != 0 else avg_lat for row in templist_lat]
templist_long = [row  if row != 0 else avg_long for row in templist_long]
	
# create station id list as key
templist_sid = [int(row[2]) for row in dict.values(OnStationdict)]

templist_currenttemp = []
for row in templist_sid:
	if normaltemp_dict.has_key(row): # x-ref to city based dict to find the current temp for the station
		# create list of sid/temp/lat/long (all for dict lookup)
		templist_currenttemp.append([row, normaltemp_dict[row][2], OnStationdict[row][3], OnStationdict[row][4]])
		
#print templist_currenttemp

x = [row[3] for row in templist_currenttemp]
y = [row[2] for row in templist_currenttemp]
z = [row[1] for row in templist_currenttemp]

#some logic to find the max/min temp and its station name
mintemp = min(z)
maxtemp = max(z)
mintemp_stdid = templist_currenttemp[z.index(mintemp)][0]
maxtemp_stdid = templist_currenttemp[z.index(maxtemp)][0]
mintemp_stdname = OnStationdict[mintemp_stdid][0]
maxtemp_stdname = OnStationdict[maxtemp_stdid][0]
mintemp_stdlat = templist_currenttemp[z.index(mintemp)][2]
mintemp_stdlong = templist_currenttemp[z.index(mintemp)][3]
maxtemp_stdlat = templist_currenttemp[z.index(maxtemp)][2]
maxtemp_stdlong = templist_currenttemp[z.index(maxtemp)][3]
print mintemp, maxtemp
print mintemp_stdid, maxtemp_stdid
print mintemp_stdname, mintemp_stdlat, mintemp_stdlong
print maxtemp_stdname, maxtemp_stdlat, maxtemp_stdlong

# ---------------------------------------------------- plot all station

fig1 = plt.figure(figsize=(5.7*3.13,3.8*3.13))

stationplot = fig1.add_subplot(221)
stationplot = Basemap(	projection='mill',
						llcrnrlat = 40,
            			llcrnrlon = -100,
            			urcrnrlat = 58,
            			urcrnrlon = -70,
            			resolution='l')
stationplot.drawcoastlines()
stationplot.drawcountries(linewidth=2)
stationplot.drawstates(color='black')
stationplot.fillcontinents(color='green', lake_color='aqua',zorder=1)	# using zorder to control the order of overlay
stationplot.drawlsmask(ocean_color='aqua')

x1,y1=stationplot(templist_long,templist_lat)  # secret sauce; convert all std to map projection coordinate 
std_x1,std_y1 =stationplot(x,y)				   # convert observing station with temp to map proj coord
max_x1, max_y1 = stationplot(maxtemp_stdlong, maxtemp_stdlat)
min_x1, min_y1 = stationplot(mintemp_stdlong, mintemp_stdlat)

# stationplot.scatter(x1, y1, c=z, cmap=plt.cm.coolwarm, markersize=10, marker="o")
stationplot.scatter(x1, y1, color='yellow', s=10, marker="o",zorder=2)
stationplot.scatter(std_x1, std_y1, c=z, cmap=plt.cm.coolwarm, s=30, marker="o", edgecolors='black', zorder=3)
stationplot.plot(max_x1, max_y1, color='red', markersize=12, marker="o", zorder=4)
stationplot.plot(min_x1, min_y1, color='blue', markersize=12, marker="o",zorder=4)
plt.text(max_x1, max_y1, s=maxtemp_stdname, color='black', weight='bold', zorder=5)
plt.text(min_x1, min_y1, s=mintemp_stdname, color='black', weight='bold', zorder=5)
plt.title ('Observing Stations with Max-Min Loc', loc='left', weight='bold', color='Orange')

# ---------------------------------------------------- plot station with temp heatmap

px = fig1.add_subplot(222, projection='3d')
# this needs to follow the add subplot; use pad to control the space around the plot
fig1.tight_layout(h_pad=3, w_pad=0)			

px.set_xlabel ('longtitude', weight='bold')
px.set_ylabel ('latitude', weight='bold')
px.set_zlabel ('Today\'s temp', weight='bold', horizontalalignment ='right')
plt.title('Station Loc Temperature (with heatmap)', loc='left', weight='bold', color='Orange')

# create p as the mappable for colorbar method later; and add max min std name overlay
p = px.scatter(x, y, z, s=80, c=z, cmap=plt.cm.coolwarm, edgecolors='grey', linewidths=1)
px.text(mintemp_stdlong, mintemp_stdlat, mintemp-1, str(mintemp_stdname), zdir=None)
px.text(maxtemp_stdlong, maxtemp_stdlat, maxtemp+1, str(maxtemp_stdname), zdir=None)

cbar = plt.colorbar(p, orientation = 'vertical', shrink = 0.5, aspect = 5)
cbar.ax.set_ylabel('Temperature in C', color='white')
cbar.ax.tick_params(axis='y', colors='white')

# ---------------------------------------------------- plot station with temp

textplot = fig1.add_subplot(223, frame_on=False)
frame1 = plt.gca()
frame1.axes.get_xaxis().set_visible(False)
frame1.axes.get_yaxis().set_visible(False)

lines = ['']*6	# match the multiplier with expected no of line of text
lines[0] = "Current date and time is: " + strftime('%d/%m/%Y %H:%M:%S')
lines[1] = "Today\'s average temp across Ontario is: " + str(TodayAvgTemp) + "C"
lines[2] = "Today\'s normal max temp across Ontario is: " + str(TodayAvgHigh) + "C"
lines[3] = "Today\'s normal min temp across Ontario is: " +  str(TodayAvgLow) + "C"
lines[4] = "Today\'s hottest temp in Ontario is " + str(maxtemp) + "C observed at " + maxtemp_stdname 
lines[5] = "Today\'s coldest temp in Ontario is " + str(mintemp) + "C observed at " + mintemp_stdname 


fs, ls, fw, fc = 12, 0, 'medium', 'white'
for i in range(len(lines)):
	if i ==0:
		# print the first line as bold
		plt.text(0.15, 0.9-0.1*(i+1), lines[i], size=fs*1.1, linespacing=ls, weight='bold', color='orange')
	elif i==4:
		plt.text(0.15, 0.9-0.1*(i+1), lines[i], size=fs, linespacing=ls, weight=fw, color='red')
	elif i==5:
		plt.text(0.15, 0.9-0.1*(i+1), lines[i], size=fs, linespacing=ls, weight=fw, color='cyan')
	else:
		plt.text(0.15, 0.9-0.1*(i+1), lines[i], size=fs, linespacing=ls, weight=fw, color=fc)

# ------------------------------ set up for K-means clustering

xarray = np.array(x)
yarray = np.array(y)
zarray = np.array(z)
X = np.column_stack((xarray,yarray,zarray))

kmeans = KMeans(n_clusters=4)
kmeans.fit(X)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

print'4 Clusters Centroids: ', centroids
print 'Labales matrix: ', labels
		
# ------------------------------ do the 3D scatter plot

# fig3 = plt.figure()
clusterplot = fig1.add_subplot(224, projection='3d')

colors = ["blue","cyan", "yellow","orange"]     # coldest cluster picked up the first color
cluster0, cluster1, cluster2, cluster3 = [], [], [], []

# separate out N number of clusters for different color scatter plotting
for i in range(len(X)):
    # print("coordinate:",X[i], "label:", labels[i])
    if labels[i] == 0:
    	cluster0.append([x[i], y[i], z[i]])
    elif labels[i] == 1:
    	cluster1.append([x[i], y[i], z[i]])
    elif labels[i] == 2:
    	cluster2.append([x[i], y[i], z[i]])
    else:
		cluster3.append([x[i], y[i], z[i]])

# figure out which is the coldest cluster
cluster0_tempavg = avg_list([row[2] for row in cluster0])
cluster1_tempavg = avg_list([row[2] for row in cluster1])
cluster2_tempavg = avg_list([row[2] for row in cluster2])
cluster3_tempavg = avg_list([row[2] for row in cluster3])
tempavg_dict = {cluster0_tempavg:0, cluster1_tempavg:1, cluster2_tempavg:2, cluster3_tempavg:3}
k = sorted(tempavg_dict)
tempavg_cluster_seq, color_seq = [], []
for row in k:
	tempavg_cluster_seq.append(tempavg_dict[row])
print tempavg_cluster_seq
print 'cluster 0 average temp is', cluster0_tempavg
print 'cluster 1 average temp is', cluster1_tempavg
print 'cluster 2 average temp is', cluster2_tempavg
print 'cluster 3 average temp is', cluster3_tempavg

i = 0
for row in tempavg_cluster_seq:
	color_seq.append(tempavg_cluster_seq.index(i))
	i += 1

xplot = [row[0] for row in cluster0]
yplot = [row[1] for row in cluster0]
zplot = [row[2] for row in cluster0]
clusterplot.scatter(xplot, yplot, zplot, s=70, c=colors[color_seq[0]], edgecolors='grey', linewidths=1)

xplot = [row[0] for row in cluster1]
yplot = [row[1] for row in cluster1]
zplot = [row[2] for row in cluster1]
clusterplot.scatter(xplot, yplot, zplot, s=70, c=colors[color_seq[1]], edgecolors='grey', linewidths=1)  

xplot = [row[0] for row in cluster2]
yplot = [row[1] for row in cluster2]
zplot = [row[2] for row in cluster2]
clusterplot.scatter(xplot, yplot, zplot, s=70, c=colors[color_seq[2]], edgecolors='grey', linewidths=1) 

xplot = [row[0] for row in cluster3]
yplot = [row[1] for row in cluster3]
zplot = [row[2] for row in cluster3]
clusterplot.scatter(xplot, yplot, zplot, s=70, c=colors[color_seq[3]], edgecolors='grey', linewidths=1)   

# scatter plot using array format as inputs
clusterplot.set_xlabel ('longtitude',weight='bold')
clusterplot.set_ylabel ('latitude',weight='bold')
clusterplot.set_zlabel ('Today\'s temp',weight='bold')
plt.title('Station Temperature (4 clusters K-means Unsupervised ML)', loc='left', weight='bold', color='Orange')
clusterplot.scatter(centroids[:, 0],centroids[:, 1], centroids[:, 2], marker = "x", c="red", s=80, linewidths = 5, zorder = 10)
# add the labels to the centroiods data points
offset = 1
for i in range(4):   
	clusterplot.text(centroids[i,0]+offset, centroids[i,1]+offset, centroids[i,2], str(int(centroids[i,2])), zdir=None)

clusterplot.figure.set_facecolor('black')

plt.show()