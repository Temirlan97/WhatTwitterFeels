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
import cPickle
import MySQLdb

#connect
configs = readOutValues("keyfile.txt")
db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)
infoLog("Getting prices...")
stopwatchStart = time.time()
#get prices
getPricesQuery = "SELECT * FROM twitter.btc_price WHERE timestamp > 1522412546 ORDER BY timestamp;"
cursorPrices = db.cursor()
cursorPrices.execute(getPricesQuery)
prices = cursorPrices.fetchall()
with open("data/prices2018", "wb") as filePrices:
	cPickle.dump(prices, filePrices)
del prices
stopwatchEnd = time.time()
infoLog("Getting prices took: " + str(stopwatchEnd - stopwatchStart))


infoLog("Getting tweets...")
stopwatchStart = time.time()
#get tweets
getTweetsQuery = "SELECT timestamp, score FROM twitter.tweets WHERE timestamp > 1522412546 ORDER BY timestamp;"
cursorTweets = db.cursor()
cursorTweets.execute(getTweetsQuery)
tweets = cursorTweets.fetchall()
with open("data/tweets2018", "wb") as fileTweets:
	cPickle.dump(tweets, fileTweets)
del tweets
stopwatchEnd = time.time()
infoLog("Getting tweets took: " + str(stopwatchEnd - stopwatchStart))

db.close()
