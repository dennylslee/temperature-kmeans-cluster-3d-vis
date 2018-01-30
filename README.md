# Introduction

This project's objectives are to collect instantaneous temperature as reported from government of Canada website for all the weather stations from the province of Ontario. It then clusters the temperature readings into 4 clusters using simple K-means.  3D scatter plots are generated using matplotlib.  The project is written with Python 2.7.

Example temperature as reported from the government website can be found [here](https://weather.gc.ca/city/pages/on-82_metric_e.html)

The temperature readings are first scraped from the website using regex. The collected data are stored in a local csv file.  The following is responsible for the data scraping function.  Obviously scraping website is not a recommended production approach due to its inflexibility to adapt to changes.

	weather_city_crawler.py

The data cleansing, K-means clustering, and graphical plots are in this file:

	weather_station_processing.py

## Multi threading experiment

The "w_thread" file uses the built-in python multi-threading support. It reduced the overall crawling speed marginally (~10-20% gain).  The modest result is due to python's inherent limitation called Global Interpreter Lock (GIL).

## K-means clustering

The simple K means is implemented using sktlearn.cluster Kmeans.  The choice of 4 clusters is arbitrary.

```python
xarray = np.array(x)
yarray = np.array(y)
zarray = np.array(z)
X = np.column_stack((xarray,yarray,zarray))

kmeans = KMeans(n_clusters=4)
kmeans.fit(X)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

```

Since the cluster results from Kmeans are simply separation. There is no inherent ranking of any sort from the sklearn method.  Therefore the 4 resulting clusters need to sorted accroding to their average temperature and apply the correct color coding. 


```python
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

```

## Resulting UI panel 

The resulting clusters are plotted on the right hand side whereas the top left plot is the raw data (temperature) overlayed onto the Ontario map.

The package used for plotting the map is [Basemap](https://matplotlib.org/basemap/)

The interctive and scroll-abilty of the 3D plot comes nicely with matplotlib's capability. 

![image stack layer](https://github.com/dennylslee/temperature-kmeans-cluster-3d-vis/blob/master/weather_vis_panel.png)
