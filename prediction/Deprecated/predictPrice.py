#This program tries to predict the price using the linear regression on the old data
#################################
# Importing myutils					
#################################
import sys
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail
#import time for stopwatch
import time

##################################################
# STEPS
# 1) Make a timeline, i.e. points in time with certain interval 
# 2) Extract all price data
# 3) Extract all tweet scores from the database 
# 4) Make a map of prices for this timeline
# 5) Make matrix inputs(In), which will contain one input on each row
# an input is a vector of mood partition and prices for the last 24h
# 6) Make matrix outputs(Out), which contains the output on each column
# an output is a vector which contains prices for the next 24h
# 7) Calculate Wopt = ((InIn')^(-1))In Out
# 8) Store Wopt in some file
##################################################

##################################################
# STEP 1 - Creating a timeline
##################################################
import datetime

infoLog("Creating a timeline...")
stopwatchStart = time.time()

epoch = datetime.datetime(1970, 01, 01)
def datetimeToTimestamp(date):
	global epoch
	return (date - epoch).total_seconds()

timeline = []
startDate = datetime.datetime(2018, 01, 05)
endDate = datetime.datetime(2018,04,15)
interval = datetime.timedelta(minutes = 5)
itDate = startDate
while(itDate < endDate):
	timeline.append(int(datetimeToTimestamp(itDate)))
	itDate += interval

stopwatchEnd = time.time()
infoLog("Creating a timeline took: " + str(stopwatchEnd - stopwatchStart))
##################################################
# STEP 2 & 3 - Extract all price and twitter data
##################################################
from collections import OrderedDict
import MySQLdb

infoLog("Creating a price dict...")
stopwatchStart = time.time()

#connect
configs = readOutValues("keyfile.txt")
db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)

#get prices
getPricesQuery = "SELECT * FROM twitter.btc_price WHERE timestamp > 1514822518 ORDER BY timestamp;"
cursorPrices = db.cursor()
cursorPrices.execute(getPricesQuery)
prices = cursorPrices.fetchall()
pricesDict = OrderedDict()
for row in prices:
	pricesDict[int(row[0])] = int(row[1])
cursorPrices.close()
del prices


stopwatchEnd = time.time()
infoLog("Creating a price dict took: " + str(stopwatchEnd - stopwatchStart))


infoLog("Creating a tweets dict...")
stopwatchStart = time.time()

#get tweets
getTweetsQuery = "SELECT timestamp, score FROM twitter.tweets WHERE timestamp > 1514822518 ORDER BY timestamp;"
cursorTweets = db.cursor()
cursorTweets.execute(getTweetsQuery)
tweets = cursorTweets.fetchall()
tweetsDict = OrderedDict()
for row in tweets:
	timestamp = int(row[0])
	timestamp /= 1000 # convert from ms to seconds
	if not timestamp in tweetsDict:
		tweetsDict[timestamp] = []
	tweetsDict[timestamp].append(float(row[1]))
cursorTweets.close()
del tweets

db.close()

stopwatchEnd = time.time()
infoLog("Creating a tweets dict took: " + str(stopwatchEnd - stopwatchStart))

##################################################
# STEP 4 - Mapping price data
##################################################
infoLog("Mapping price data...")
stopwatchStart = time.time()

itPrice = pricesDict.iteritems()
mappedPrices = OrderedDict()
try:
	priceItem = itPrice.next()
	closestLowerPriceItem = priceItem
	for t in timeline:
		while True:
			if(priceItem[0] < t):
				closestLowerPriceItem = priceItem
				priceItem = itPrice.next()
			else:
				#linear interpolation of price
				t1 = closestLowerPriceItem[0]
				p1 = closestLowerPriceItem[1]
				t2 = priceItem[0]
				p2 = priceItem[1]
				priceForT = p1 + (p2-p1)*(t-t1)/(t2-t1)
				mappedPrices[t] = int(priceForT)
				break
except StopIteration:
	pass

stopwatchEnd = time.time()
infoLog("Mapping price data took: " + str(stopwatchEnd - stopwatchStart))

##################################################
# STEP 5 - Creating and computing matrices
##################################################
import numpy as np
from collections import deque

infoLog("Computing Phi and Z...")
stopwatchStart = time.time()

frameLower = startDate
frameUpper = startDate + datetime.timedelta(days=1)
instancesInFrame = 0;
itDate = frameLower
while itDate < frameUpper:
	itDate += interval
	instancesInFrame += 1
#Input matrix	
endOn = endDate - datetime.timedelta(days=1)
tweetsIterate = tweetsDict.iteritems()
lastTweet = tweetsIterate.next()

def getInputVector(pricesForFrame, tweetsForFrame):
	length = 201
	totalTweetsHere = 0.0
	tweetScoreCounter = np.zeros(length, dtype=int)
	for tweetList in tweetsForFrame:
		totalTweetsHere += len(tweetList[1])
		for tweet in tweetList[1]:
			idxForTweetScore = tweet + 1.0
			idxForTweetScore = int(idxForTweetScore*100)
			tweetScoreCounter[idxForTweetScore] = tweetScoreCounter[idxForTweetScore] + 1
	tweetScorePartitions = []
	if(totalTweetsHere > 0.0):
		for i in range(0, len(tweetScoreCounter)):
			part = float(tweetScoreCounter[i])*100/totalTweetsHere
			tweetScorePartitions.append(part)
		return np.append(tweetScorePartitions, pricesForFrame)
	return np.append(tweetScoreCounter, pricesForFrame)

def getPriceChange(frameLower, frameUpper):
	pricesForFrame = []
	itDate = frameLower
	initialPrice = float(mappedPrices[int(datetimeToTimestamp(itDate))])
	while(itDate < frameUpper):
		growth = mappedPrices[int(datetimeToTimestamp(itDate))] * 100.0 / initialPrice
		pricesForFrame.append(growth - 100.0)
		itDate += interval
	return pricesForFrame

inputMatrixArray = []
outputMatrixArray = []
tweetsForFrame = deque()
while(frameUpper < endOn):
	frameLower += interval
	frameUpper += interval
	pricesForFrame = getPriceChange(frameLower, frameUpper)
	futurePrices = getPriceChange(frameUpper, frameUpper + datetime.timedelta(days=1))
	try:
		frameLowerTimestamp = datetimeToTimestamp(frameLower)
		while tweetsForFrame:
			itemInDeque = tweetsForFrame.popleft()
			if(itemInDeque[0] >= frameLowerTimestamp):
				tweetsForFrame.appendleft(itemInDeque)
				break
		frameUpperTimestamp = datetimeToTimestamp(frameUpper)
		while(lastTweet[0] < frameUpperTimestamp):
			tweetsForFrame.append(lastTweet)
			lastTweet = tweetsIterate.next()
	except StopIteration:
		pass
	#minimum tweets in a day for an input to count
	if(len(tweetsForFrame) > 10000):
		inputVector = getInputVector(pricesForFrame, tweetsForFrame)
		inputMatrixArray.append(inputVector)
		outputMatrixArray.append(futurePrices)

Phi = np.array(inputMatrixArray)
Z = np.array(outputMatrixArray)

stopwatchEnd = time.time()
infoLog("Computing Phi and Z took: " + str(stopwatchEnd - stopwatchStart))

infoLog("Saving Phi and Z...")
stopwatchStart = time.time()
np.save("trainingInput", Phi)
np.save("trainingOutput", Z)
stopwatchEnd = time.time()
infoLog("Saving Phi and Z took: " + str(stopwatchEnd - stopwatchStart))

