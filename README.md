# Segmentation of Publicly Traded Stocks as of September 2018

## Introduction
Cluster analysis enables us to group a set of objects in such a way that objects in the same group (called a cluster) are more similar (in some sense) to each other than to those in other groups (clusters). One can preset the number of clusters before grouping variables into their respective clusters. An advantage of using cluster analysis over other regression techniques is its ability to classify sets of like-minded groups. This report explores the possibility of clustering publicly traded stocks into a set of like groups.

## About the Dataset 
This dataset consists of 755 observations and 43 features, with some of the most important features spanning across current assets and liabilities, P/E ratio, earnings per share (EPS), share price, stock price at high and low, ROA and dividend payout ratio. Most of the features are floats/integers except for ‘ticker’ and ‘quarter_end’, which are objects.

## Key Insights and Recommendations
When plotting the share price by earnings per share, we note that the light colored clustered (Cluster 0) has stocks with low price and EPS. This cluster segments those companies that are not profitable, as reflected in the stock price value. Cluster 2 (purple) displays values of high stock price and higher EPS, which groups companies that are high performing and well established. Clusters 1 and 2 in the middle have moderately priced share prices with slightly lower EPS values, which are well performing companies that have potential to grow. 

The final recommendation is to invest in companies with more potential of stock appreciation. Stocks in the above chart which are reasonably priced (between $100-$200) and with lower EPS have greater potential to increase in the longer run. Investors should consider investing in stocks which will yield greater returns in future. However, additional qualitative factors such as industry type, employee turnover, etc should also be taken into consideration before making investment decisions. 
