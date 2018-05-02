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
# STEP 1 - Creating a timeline
##################################################
import datetime
from datetime import timedelta

epoch = datetime.datetime(1970, 01, 01)
def datetimeToTimestamp(date):
	global epoch
	return (date - epoch).total_seconds()

def generateTimeline(startDate, endDate, interval):
	timeline = []
	itDate = startDate
	while(itDate < endDate):
		timeline.append(int(datetimeToTimestamp(itDate)))
		itDate += interval
	return timeline

# intervals = [timedelta(minutes=5), timedelta(minutes=10), timedelta(minutes=30), 
# timedelta(hours=1), timedelta(hours=3), timedelta(hours=5), timedelta(hours=12)]
# frameWidths = [timedelta(hours=1), timedelta(hours=3), timedelta(hours=5), timedelta(hours=12),
# timedelta(days=1),timedelta(days=3),timedelta(days=7)]

intervals = [timedelta(minutes=5), timedelta(minutes=10), timedelta(minutes=15), timedelta(minutes=30), 
timedelta(hours=1), timedelta(hours=3), timedelta(hours=5)]
frameWidths = [timedelta(hours=1), timedelta(hours=2), timedelta(hours=3), timedelta(hours=6), 
timedelta(hours=12),timedelta(hours=36),timedelta(hours=60)]

# intervals = [timedelta(hours=1), timedelta(hours=3)]
# frameWidths = [timedelta(days=1),timedelta(days=2)]
setWidth = datetime.timedelta(days=4)


startDate = datetime.datetime(2018, 03, 31)
endDate = datetime.datetime.now() - timedelta(days=1)

frames = []
itDate = startDate
itEndDate = itDate + setWidth
while(itEndDate < endDate):
	frames.append({"startDate": itDate, "endDate" : itEndDate})
	itDate += setWidth
	itEndDate = itDate + setWidth
##################################################
# STEP 2 & 3 - Extract all price and twitter data
##################################################
from collections import OrderedDict
import cPickle
infoLog("Extracting prices...")
stopwatchStart = time.time()
#get prices
prices = None
with open("data/prices2018", "rb") as pricesFile:
	prices = cPickle.load(pricesFile)
stopwatchEnd = time.time()
infoLog("Extracting prices took: " + str(stopwatchEnd - stopwatchStart))

infoLog("Extracting tweets...")
stopwatchStart = time.time()
#get tweets
tweets = None
with open("data/tweets2018", "rb") as tweetsFile:
	tweets = cPickle.load(tweetsFile)
stopwatchEnd = time.time()
infoLog("Extracting tweets took: " + str(stopwatchEnd - stopwatchStart))

##################################################
# STEP 5 - Creating and computing matrices
##################################################
import numpy as np
from collections import deque

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

def getPriceChange(frameLower, frameUpper, interval):
	pricesForFrame = []
	itDate = frameLower
	initialPrice = float(mappedPrices[int(datetimeToTimestamp(itDate))])
	while(itDate < frameUpper):
		growth = mappedPrices[int(datetimeToTimestamp(itDate))] * 100.0 / initialPrice
		pricesForFrame.append(growth - 100.0)
		itDate += interval
	return pricesForFrame

def inputOutputMatrices(startDate, endDate, interval, frameWidth, inputTrain, outputTrain, inputTest, outputTest, validationFrame):
	frameLower = startDate
	frameUpper = startDate + frameWidth
	tweetsIterate = tweetsDict.iteritems()
	lastTweet = tweetsIterate.next()
	tweetsForFrame = deque()
	endOn = endDate - frameWidth
	while(frameUpper < endOn):
		frameLower += interval
		frameUpper += interval
		pricesForFrame = getPriceChange(frameLower, frameUpper, interval)
		futurePrices = getPriceChange(frameUpper, frameUpper + frameWidth, interval)
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
		if(len(tweetsForFrame) > 100):
			inputVector = getInputVector(pricesForFrame, tweetsForFrame)
			if(frameUpper >= validationFrame["startDate"] and frameUpper < validationFrame["endDate"]):
				inputTest.append(inputVector)
				outputTest.append(futurePrices)
			else:
				inputTrain.append(inputVector)
				outputTrain.append(futurePrices)


mappedPrices = None
intervalOpt = None
frameWidthOpt = None
leastError = 10**10
# for interval in intervals:
# 	for frameWidth in frameWidths:
for i in range(0, len(intervals)):
	interval = intervals[i]
	frameWidth = frameWidths[i]	
	if(interval >= frameWidth):
		continue
	timeline = generateTimeline(startDate, endDate, interval)
	infoLog("Creating a price dict...")
	stopwatchStart = time.time()
	#get prices
	pricesDict = OrderedDict()
	for row in prices:
		pricesDict[int(row[0])] = int(row[1])
	stopwatchEnd = time.time()
	infoLog("Creating a price dict took: " + str(stopwatchEnd - stopwatchStart))

	infoLog("Creating a tweets dict...")
	stopwatchStart = time.time()
	#get tweets
	tweetsDict = OrderedDict()
	for row in tweets:
		timestamp = int(row[0])
		timestamp /= 1000 # convert from ms to seconds
		if not timestamp in tweetsDict:
			tweetsDict[timestamp] = []
		tweetsDict[timestamp].append(float(row[1]))
	stopwatchEnd = time.time()
	infoLog("Creating a tweets dict took: " + str(stopwatchEnd - stopwatchStart))

	infoLog("Mapping price data...")
	stopwatchStart = time.time()
	itPrice = pricesDict.iteritems()
	if mappedPrices:
		del mappedPrices
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
	meanError = 0.0
	infoLog(str(interval) + " " + str(frameWidth))
	infoLog("Optimal so far: " + str(intervalOpt) + " " + str(frameWidthOpt))
	for f in frames:
		validationFrame = f
		infoLog("Computing Phi and Z...")
		stopwatchStart = time.time()
		inputTrain = []
		outputTrain = []
		inputTest = []
		outputTest = []
		inputOutputMatrices(startDate, endDate, interval, frameWidth, inputTrain, outputTrain, inputTest, outputTest, validationFrame)
		if (not inputTrain) or (not outputTrain) or (not inputTest) or (not outputTest):
			errorLog("Empty input or output. Skipping frame: " + str(f))
			continue
		Phi = np.array(inputTrain)
		Z = np.array(outputTrain)
		del inputTrain
		del outputTrain
		PhiTest = np.array(inputTest)
		ZTest = np.array(outputTest)
		del inputTest
		del outputTest
		stopwatchEnd = time.time()
		infoLog("Computing Phi and Z took: " + str(stopwatchEnd - stopwatchStart))
		# print(Phi.shape)
		# print(Z.shape)
		# print(PhiTest.shape)
		# print(ZTest.shape)
		# print(startDate)
		# print(endDate)
		# print(interval)
		# print(frameWidth)
		# print(validationFrame)
		W = (np.linalg.pinv(Phi).dot(Z)).T
		# print(W.shape)
		N = float(len(PhiTest))*len(ZTest[1])
		for i in range(0, len(PhiTest)):
			prediction = W.dot(PhiTest[i])
			error = prediction - ZTest[i]
			for x in error:
				meanError += (x*x)/N
	infoLog(str(meanError) + " " + str(leastError))
	if(meanError < leastError):
		leastError = meanError
		intervalOpt = interval
		frameWidthOpt = frameWidth

infoLog(str(leastError))
infoLog(str(intervalOpt))
infoLog(str(frameWidthOpt))

