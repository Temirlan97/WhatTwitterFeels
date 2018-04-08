import codecs
import sys
import datetime

sys.path.append("./GetOldTweets-python")

import got
#################################
# Importing myutils					
#################################
import sys
sys.path.append("../myutils/")
from log import errorLog, infoLog
from sendEmail import notifyViaEmail

tweetCriteria = got.manager.TweetCriteria()
outputFileName = "old_tweets.csv"

# Queries are case insensitive
queries = ["btc", "bitcoin"]
#tweetCriteria.querySearch = "btc bitcoin"

#we need all tweets
#tweetCriteria.maxTweets = 20

#tweetCriteria.since = "2018-04-06"

#tweetCriteria.until = "2018-04-07"

startDate =  datetime.date(2018, 04, 01)
numberOfDays = 7

outputFile = codecs.open(outputFileName, "w", "utf-8")

outputFile.write("\nusername;date;text;id")

totalExtracted = 0

def receiveBuffer(tweets):
	try:
		for t in tweets:
			outputFile.write(('\n%s;%s;"%s";"%s"' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.text, t.id)))
		outputFile.flush()
		global totalExtracted
		totalExtracted += len(tweets)
		infoLog('More ' + str(len(tweets)) + ' saved in file. (' + str(totalExtracted) + ' total)')
	except Exception as error:
		errorLog("Failed to write tweets into the file")
		errorLog(error)

for query in queries:
	tweetCriteria.querySearch = query
	for date in (startDate + datetime.timedelta(n) for n in range(numberOfDays)):
		tweetCriteria.since = str(date)
		tweetCriteria.until = str(date + datetime.timedelta(1))
		infoLog("Extracting query '"+ query +"' for " + str(date))
		try: 
			got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer, 100)
		except Exception as error:
			errorLog(error)

outputFile.close()
terminationMessage = "The extraction of old tweets was (partially) successful\n"
terminationMessage += "for " + str(numberOfDays) + " days starting form " + str(startDate)
infoLog(terminationMessage)
notifyViaEmail("Done extracting old tweets",  terminationMessage)


