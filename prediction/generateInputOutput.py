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

startDate = datetime.datetime(2018, 03, 31)
endDate = datetime.datetime.now() - timedelta(days=1)

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
	infoLog("Extracted " + str(len(prices)) + " price items")
stopwatchEnd = time.time()
infoLog("Extracting prices took: " + str(stopwatchEnd - stopwatchStart))

infoLog("Extracting tweets...")
stopwatchStart = time.time()
#get tweets
tweets = None
with open("data/tweets2018", "rb") as tweetsFile:
	tweets = cPickle.load(tweetsFile)
	infoLog("Extracted " + str(len(tweets)) + " tweets")
stopwatchEnd = time.time()
infoLog("Extracting tweets took: " + str(stopwatchEnd - stopwatchStart))

##################################################
# STEP 5 - Creating and computing matrices
##################################################
import random
import numpy as np
from collections import deque
random.seed()

def getInputVector(pricesForFrame, tweetsForFrame, length):
	factor = (length-1)/2
	totalTweetsHere = 0.0
	tweetScoreCounter = np.zeros(length, dtype=int)
	for tweetList in tweetsForFrame:
		totalTweetsHere += len(tweetList[1])
		for tweet in tweetList[1]:
			idxForTweetScore = tweet + 1.0
			idxForTweetScore = int(idxForTweetScore*factor)
			tweetScoreCounter[idxForTweetScore] = tweetScoreCounter[idxForTweetScore] + 1
	tweetScorePartitions = []
	if(totalTweetsHere > 0.0):
		for i in range(0, len(tweetScoreCounter)):
			part = float(tweetScoreCounter[i])*100/totalTweetsHere
			tweetScorePartitions.append(part)
		return np.append(tweetScorePartitions, pricesForFrame)
	return np.append(tweetScoreCounter, pricesForFrame)

def getRawInput(pricesForFrame, tweetsForFrame):
	scores = []
	for tweetList in tweetsForFrame:
		for tweet in tweetList[1]:
			scores.append(tweet)
	return np.append(pricesForFrame, scores)

def getLongInputVector(pricesForFrame, tweetsForFrame):
	return getInputVector(pricesForFrame, tweetsForFrame, 201)


def getShortInputVector(pricesForFrame, tweetsForFrame):
	return getInputVector(pricesForFrame, tweetsForFrame, 41)

def getPriceChange(frameLower, frameUpper, interval):
	pricesForFrame = []
	itDate = frameLower
	initialPrice = float(mappedPrices[int(datetimeToTimestamp(itDate))])
	while(itDate < frameUpper):
		growth = mappedPrices[int(datetimeToTimestamp(itDate))] * 100.0 / initialPrice
		pricesForFrame.append(growth - 100.0)
		itDate += interval
	return pricesForFrame

def isTestData(frameLower, frameUpper):
	if not mode or mode == "Random_Distribution" or mode == "FramewiseRandom":
		return random.random() < 0.3
	elif mode == "Into_two" or mode == "FramewiseIntotwo":
		return frameUpper >= startDateTest
	elif mode == "Test_Frame" or mode == "FramewiseFrame":
		return frameUpper >= startDateTest and frameUpper < endDateTest
	elif mode == "Raw":
		return False


def inputOutputMatrices(startDate, endDate, interval, frameWidth, inputTrain, outputTrain, inputTest, outputTest):
	frameLower = startDate
	frameUpper = startDate + frameWidth
	tweetsIterate = tweetsDict.iteritems()
	lastTweet = tweetsIterate.next()
	tweetsForFrame = deque()
	endOn = endDate - frameWidth
	while(frameUpper < endOn):
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
			inputVector = getRawInput(pricesForFrame, tweetsForFrame)
			if isTestData(frameLower, frameUpper):
				inputTest.append(inputVector)
				outputTest.append(futurePrices)
			else:
				inputTrain.append(inputVector)
				outputTrain.append(futurePrices)
		frameLower += frameWidth
		frameUpper += frameWidth



interval = timedelta(hours=1)
frameWidth = timedelta(days=7)
postfix = "_1h-7d"
startDateTest = datetime.datetime.now()
endDateTest = endDate
mode = "Raw"
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
infoLog("Computing Phi and Z...")
stopwatchStart = time.time()
inputTrain = []
outputTrain = []
inputTest = []
outputTest = []
inputOutputMatrices(startDate, endDate, interval, frameWidth, inputTrain, outputTrain, inputTest, outputTest)
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
prefix = "data/Computed/"
np.save(prefix + mode + "/input" + postfix, Phi)
np.save(prefix + mode + "/output" + postfix, Z)
# np.save(prefix + mode + "/trainingInput" + postfix, Phi)
# np.save(prefix + mode + "/trainingOutput" + postfix, Z)
# np.save(prefix + mode + "/testingInput" + postfix, PhiTest)
# np.save(prefix + mode + "/testingOutput" + postfix, ZTest)
print(Phi.shape)
print(Z.shape)
print(PhiTest.shape)
print(ZTest.shape)
print(startDate)
print(endDate)
print(interval)
print(frameWidth)

