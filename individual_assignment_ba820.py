# -*- coding: utf-8 -*-
"""Individual_Assignment_BA820.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vYgzrvrLOHOaNVYQEMuyHqygF3zon9c5
"""

# installs

# notebook/colab
! pip install scikit-plot

# imports

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots

# what we need for today
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn import metrics 

import scikitplot as skplt

# color maps
from matplotlib import cm

# for distance and h-clustering
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist, squareform


# sklearn does have some functionality too, but mostly a wrapper to scipy
from sklearn.metrics import pairwise_distances 
from sklearn.preprocessing import StandardScaler

"""DataFrames

- df
- temp
- df_2018
- stock (copy of df_2018)
- stock_num
- st (transformed)
-

## Loading the Data
"""

from google.colab import drive
drive.mount('/content/drive')

path = "/content/stock-fundamentals.csv"
df = pd.read_csv(path)

df.shape

df.head(3)

df.describe()

df.dtypes

"""# Data Cleaning """

|#each ticker is unique
temp2 = df.copy()
temp2 = df.reset_index().groupby(['ticker'])['quarter_end'].nunique().reset_index()
temp2

#each ticker is unique
temp2[temp2['quarter_end'] >1].count()

#converting quarter_end to a datetime variable and creating additional features consisting of year, quarter and month 
df['quarter_end'] = pd.to_datetime(df['quarter_end'])
df['Year'] = df['quarter_end'].dt.year
df['Quarter'] = df['Year'].astype(str) + 'Q' + df['quarter_end'].dt.quarter.astype(str)
df['Yearmonth'] = df['Year'].astype(str) + 'M' + df['quarter_end'].dt.month.astype(str)

#the dataset has observations from 2006-2018
df.Year.unique()

#the dataset has observations from 2006-2018
df.groupby(['Year','Quarter'])['quarter_end'].count()

#only filtering for 2018 observations and creating a new dataframe 'df_2018'
df_2018 = df[(df['Year']== 2018) & (df['Quarter'] == '2018Q3')]

# Most of the stock movement takes place in September 2018
df_2018.groupby(['Yearmonth', 'Quarter'])['Quarter'].count()

#filtering only for data in September 2018 
df_2018 = df_2018[df_2018['Yearmonth'] == '2018M9']

df_2018.index = df_2018['ticker']

df_2018.head(3)

df_2018.isna().sum()

#removing the Quarter End column since the date for quarter_end has already been given
df_2018.drop(columns=['Quarter end'], inplace=True)

#both current assets and current liabilities have 104 missing values each
df_2018[(df_2018['Current Assets'].isna()) & (df_2018['Current Liabilities'].isna())]

df_2018['Current Assets'] = df_2018['Current Assets'].fillna(0)
df_2018['Current Liabilities'] = df_2018['Current Liabilities'].fillna(0)
#current ratio = current assets/current liabilities
#current ratio is null when either current assets or current liabilities or both are valued at 0
#replacing null values of current ratio with 0
df_2018['Current ratio'] = df_2018['Current ratio'].fillna(0)

#Shareholders equity = Asses - Liabilities - Non-controlling interest
#Reviewing that this equation holds true in this dataset 
temp = df_2018.copy()
temp['shareholders_equity'] = temp['Assets'] - temp['Liabilities'] - temp['Non-controlling interest']
temp['diff'] = temp['shareholders_equity'] - temp['Shareholders equity']
temp[np.abs(temp['diff'] != 0)]

#non-controlling interest and preferred equity are valued at $0 for observations with null values for cash from operating, investing and finaning activities 
df_2018[(df_2018['Cash from operating activities']).isnull()]

#replacing null values with 0
df_2018['Cash from operating activities'] = df_2018['Cash from operating activities'].fillna(0)
df_2018['Cash from investing activities'] = df_2018['Cash from investing activities'].fillna(0)
df_2018['Cash from financing activities'] = df_2018['Cash from financing activities'].fillna(0)

#Equity to assets ratio = Shareholders Equity/Total Assets
df_2018['Equity to assets ratio'] = df_2018['Equity to assets ratio'].fillna(( df_2018['Shareholders equity']/df_2018['Assets'] ))

#filling null values for price, price high and price low
temp = df_2018.copy()
temp['book_value_calculated'] = (temp['Shareholders equity'] - temp['Preferred equity'])
temp['book_value_per_share_calculated'] = temp['book_value_calculated']/temp['Shares']
temp['calculated_stock_price'] = temp['P/B ratio']*temp['Book value of equity per share']

df_2018.loc[df_2018.Price.isnull(), 'Price'] = temp['calculated_stock_price']
df_2018.loc[df_2018['Price high'].isnull(), 'Price high'] = temp['calculated_stock_price']
df_2018.loc[df_2018['Price low'].isnull(), 'Price low'] = temp['calculated_stock_price']

#dropping rows with null values for net margin
df_2018.dropna(subset=['Net margin', 'Free cash flow per share'], inplace=True)

#calculating ROE to fill missing values
temp = df_2018.copy()
temp['calculated_net_income'] = temp['Net margin']*temp['Revenue']
temp['calculated_roe'] = temp['calculated_net_income']/temp['Shareholders equity']

df_2018.loc[df_2018['ROE'].isnull(), 'ROE'] = temp['calculated_roe']

#calculating long term debt to equity ratio to fill missing values 
temp = df_2018.copy()
temp['calculated_longtermdebt'] = temp['Long-term debt']/temp['Shareholders equity']

df_2018.loc[df_2018['Long-term debt to equity ratio'].isnull(), 'Long-term debt to equity ratio'] = temp['calculated_longtermdebt']

#calculating p/e ratio to fill missing values 
temp = df_2018.copy()
temp['calculated_pe_ratio'] = temp['Price']/temp['EPS basic']

df_2018.loc[df_2018['P/E ratio'].isnull(), 'P/E ratio'] = temp['calculated_pe_ratio']

# Book Value Per Share = (Shareholder's Equity - Preferred Stock)/ Average Shares Outstanding
# P/B ratio = Market Price Per Share/Book Value Per Share
df_2018['calculated_book_val_per_share'] = (df_2018['Shareholders equity'] - df_2018['Preferred equity']) / (df_2018['Shares'].mean())
df_2018.loc[df_2018['P/B ratio'].isnull(), 'P/B ratio'] = df_2018['Price'] / df_2018['calculated_book_val_per_share']

# Dataset after cleaning (final)
df_2018.shape

#confirming that there are no null values
df_2018.isnull().sum()

df_2018['Dividend Yield'] = df_2018['Dividend per share']/df_2018['Price']
df_2018['Current-Highest Price Ratio'] = df_2018['Price']/df_2018['Price high']

df_2018.describe()

#removing outliers only for Price
df_clean = df_2018.copy()
# columns_list = ['Shares', 'Shares split adjusted', 'Split factor',
#        'Assets', 'Current Assets', 'Liabilities', 'Current Liabilities',
#        'Shareholders equity', 'Non-controlling interest', 'Preferred equity',
#        'Goodwill & intangibles', 'Long-term debt', 'Revenue', 'Earnings',
#        'Earnings available for common stockholders', 'EPS basic',
#        'EPS diluted', 'Dividend per share', 'Cash from operating activities',
#        'Cash from investing activities', 'Cash from financing activities',
#        'Cash change during period', 'Cash at end of period',
#        'Capital expenditures', 'Price', 'Price high', 'Price low', 'ROE',
#        'ROA', 'Book value of equity per share', 'P/B ratio', 'P/E ratio',
#        'Cumulative dividends per share', 'Dividend payout ratio',
#        'Long-term debt to equity ratio', 'Equity to assets ratio',
#        'Net margin', 'Asset turnover', 'Free cash flow per share',
#        'Current ratio']

columns_list = ['Price','P/B ratio','P/E ratio','ROE','Dividend Yield']
df_clean.describe()

for i in columns_list:
  print(i)
  df_clean = df_clean[(df_clean[i] < np.percentile(df_clean[i],99.5)) & (df_clean[i] > np.percentile(df_clean[i], 1))]
  print(df_clean[i].describe())

df_2018.shape

"""# Hierarchical Clustering"""

stock = df_clean.copy()

stock_num = stock.select_dtypes('number')

#data needs to be standardized 
stock_num.sample(5)

sc = StandardScaler()
st = sc.fit_transform(stock_num)

st = pd.DataFrame(st, columns=stock_num.columns)

st.sample(5)

# going to do euclidean and cosine distance
diste = pdist(st.values)
distc = pdist(st.values, metric="cosine")

#  going to start with complete linkage
# remember: when we pass in a 1d distance matrix, the metric arg is not applicable
# b/c we already did it 

# put both on the same linkage for now, but you could always generate multiple plots!
hclust_e = linkage(diste)
hclust_c = linkage(distc)

# both plots
LINKS = [hclust_e, hclust_c]
TITLE = ['Euclidean', 'Cosine']

plt.figure(figsize=(15, 5))

# loop and build our plot
for i, m in enumerate(LINKS):
  plt.subplot(1, 2, i+1)
  plt.title(TITLE[i])
  dendrogram(m,
            #  labels = ps.index,
             leaf_rotation=90,
            #  leaf_font_size=10,
             orientation="left")
  
plt.show()

"""The plots are hard to read, but we can get a sense of the shape of how the clustering is taking place. Euclidean is incremental, with larger groups joining late. Both identified outliers, though cosine appears to suggest more with smaller groups uniting earlier in the algorithm. I will go with cosine."""

METHODS = ['single', 'complete', 'average', 'ward']
plt.figure(figsize=(20, 5))


# loop and build our plot
for i, m in enumerate(METHODS):
  plt.subplot(1, 4, i+1)
  plt.title(m)
  dendrogram(linkage(distc, method=m), 
             leaf_rotation=90)
  
plt.show()

# the labels 
labs = fcluster(linkage(distc, method="complete"), 7, criterion="maxclust")

# confirm
np.unique(labs)

# lets put this back onto the players dataset
stock['cluster'] = labs

# quick review
stock.head(3)

# lets profile the cluster solutions
clus_profile = stock.groupby("cluster").mean()

clus_profile.T

# we can also plot this as a heatmap, but we should normalize the data
scp = StandardScaler()
cluster_scaled = scp.fit_transform(clus_profile)

cluster_scaled = pd.DataFrame(cluster_scaled, 
                              index=clus_profile.index, 
                              columns=clus_profile.columns)

sns.heatmap(cluster_scaled, cmap="Blues", center=0)

# group by team and pivot on cluster, count
stock_cluster = pd.crosstab(stock.index, stock.cluster, normalize = 0)
stock_cluster

stock_cluster.head(3)

stock1 = df_2018.copy()
stock1 = stock1.reset_index(drop=True)
stock1.head(3)

stock_group = stock1.loc[:, ["ticker", "P/E ratio"]]
stock_group

# now lets get the cluster profile aligned
stock_cluster2 = stock_cluster.reset_index(drop=False, inplace=False)
stock_cluster2.rename(columns={'row_0':'ticker'}, inplace=True)
stock_cluster2.head(3)

# finally append the data
stock_profile = pd.merge(stock_group, stock_cluster2, how="inner")
stock_profile.head(3)

# lets create a compounded key
stock_profile['stock_pe_ratio'] = stock_profile.ticker + "-" + stock_profile['P/E ratio'].astype('str')

stock_profile.head(3)

"""# K-Means Clustering"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
sns.set_context('notebook')
plt.style.use('fivethirtyeight')
from warnings import filterwarnings
filterwarnings('ignore')

# Plot the data
plt.figure(figsize=(6, 6))
plt.scatter(stock['Price'], stock['EPS basic'])
plt.xlabel('Price')
plt.ylabel('Earnings Per Share')
plt.title('Relationship between stock price and earnings per share');

# Plot the data
plt.figure(figsize=(6, 6))
plt.scatter(stock['Current-Highest Price Ratio'], stock['EPS basic'])
plt.xlabel('Current-Highest Price Ratio')
plt.ylabel('Earnings Per Share')
plt.title('Earnings Per Share by Current/Highest Price Ratio');

# Plot the data
plt.figure(figsize=(6, 6))
plt.scatter(stock['Price'], stock['P/E ratio'])
plt.xlabel('Stock Price')
plt.ylabel('p/E ratio')
plt.title('Stock price by P/E ratio');

"""# K-Means Clustering """

stock.head(3)

stock = df_clean.copy()
stock_num = stock.select_dtypes('number')

sc = StandardScaler()
st = sc.fit_transform(stock_num)

st = pd.DataFrame(st, columns=stock_num.columns)

eps_price = st[['EPS basic', 'Price']]

eps_highpriceratio = st[['EPS basic', 'Current-Highest Price Ratio']]

peratio_price = st[['P/E ratio', 'Price']]

"""## Identifying Segments Based on EPS and Price

### Elbow Method
"""

import sklearn.cluster as cluster
K=range(1,12)
wss = []
for k in K:
    kmeans=cluster.KMeans(n_clusters=k,init="k-means++")
    kmeans=kmeans.fit(eps_price)
    wss_iter = kmeans.inertia_
    wss.append(wss_iter)

#We Store the Number of clusters along with their WSS Scores in a DataFrame
mycenters = pd.DataFrame({'Clusters' : K, 'WSS' : wss})
mycenters

#plotting the elbow plot
sns.lineplot(x = 'Clusters', y = 'WSS', data = mycenters)
#5

"""### Silhouette Method"""

for i in range(3,13):
    labels=cluster.KMeans(n_clusters=i,init="k-means++",random_state=200).fit(eps_price).labels_
    print ("Silhouette score for k(clusters) = "+str(i)+" is "
           +str(metrics.silhouette_score(eps_price,labels,metric="euclidean",sample_size=1000,random_state=200)))

# We will use 2 Variables for this example
kmeans = cluster.KMeans(n_clusters=4 ,init="k-means++")
kmeans = kmeans.fit(stock[['EPS basic','Price']])

stock['Clusters'] = kmeans.labels_

sns.scatterplot(x="Price", y="EPS basic",hue = 'Clusters',  data=stock)

"""## Identifying Segments Based on EPS and Current/High Price Ratio

### Elbow Method
"""

import sklearn.cluster as cluster
K=range(1,12)
wss = []
for k in K:
    kmeans=cluster.KMeans(n_clusters=k,init="k-means++")
    kmeans=kmeans.fit(eps_highpriceratio)
    wss_iter = kmeans.inertia_
    wss.append(wss_iter)

#We Store the Number of clusters along with their WSS Scores in a DataFrame
mycenters = pd.DataFrame({'Clusters' : K, 'WSS' : wss})
mycenters

#plotting the elbow plot
sns.lineplot(x = 'Clusters', y = 'WSS', data = mycenters)
#5

"""### Silhouette Method"""

for i in range(3,13):
    labels=cluster.KMeans(n_clusters=i,init="k-means++",random_state=200).fit(eps_highpriceratio).labels_
    print ("Silhouette score for k(clusters) = "+str(i)+" is "
           +str(metrics.silhouette_score(eps_highpriceratio,labels,metric="euclidean",sample_size=1000,random_state=200)))

# We will use 3 Variables for this example
kmeans = cluster.KMeans(n_clusters=3 ,init="k-means++")
kmeans = kmeans.fit(stock[['EPS basic','Current-Highest Price Ratio']])

stock['Clusters'] = kmeans.labels_

sns.scatterplot(x="Current-Highest Price Ratio", y="EPS basic",hue = 'Clusters',  data=stock)

"""## Identifying Segments Based on P/E ratio and Stock Price

### Elbow Method
"""

import sklearn.cluster as cluster
K=range(1,12)
wss = []
for k in K:
    kmeans=cluster.KMeans(n_clusters=k,init="k-means++")
    kmeans=kmeans.fit(peratio_price)
    wss_iter = kmeans.inertia_
    wss.append(wss_iter)

#We Store the Number of clusters along with their WSS Scores in a DataFrame
mycenters = pd.DataFrame({'Clusters' : K, 'WSS' : wss})
mycenters

#plotting the elbow plot
sns.lineplot(x = 'Clusters', y = 'WSS', data = mycenters)
#5

"""### Silhouette Method"""

for i in range(3,13):
    labels=cluster.KMeans(n_clusters=i,init="k-means++",random_state=200).fit(peratio_price).labels_
    print ("Silhouette score for k(clusters) = "+str(i)+" is "
           +str(metrics.silhouette_score(peratio_price,labels,metric="euclidean",sample_size=1000,random_state=200)))

# We will use 3 Variables for this example
kmeans = cluster.KMeans(n_clusters=3 ,init="k-means++")
kmeans = kmeans.fit(stock[['Price','P/E ratio']])

stock['Clusters'] = kmeans.labels_

sns.scatterplot(x="Price", y="P/E ratio",hue = 'Clusters',  data=stock)

