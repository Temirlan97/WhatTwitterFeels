import codecs
import sys
import time

sys.path.append("./GetOldTweets-python")

import got
#################################
# LOGGING						
#################################
def Log(output, filename):
	#First prepare the output
	readyOutput = str(time.asctime(time.localtime())) + ":\n"
	for line in str(output).split("\n"):
		readyOutput += "\t" + line + "\n"
	#then print and write to the file
	print(readyOutput)
	with open(filename, "a") as logfile:
		logfile.write(readyOutput)

def errorLog(output):
	Log(output, "errorlog.txt");

def infoLog(output):
	Log(output, "infolog.txt");

tweetCriteria = got.manager.TweetCriteria()
outputFileName = "old_tweets.csv"

tweetCriteria.querySearch = "BTC btc bitcoin Bitcoin BITCOIN"

#we need all tweets
#tweetCriteria.maxTweets = 100

tweetCriteria.since = "2018-01-01"

tweetCriteria.until = "2018-04-01"

outputFile = codecs.open(outputFileName, "a", "utf-8")

outputFile.write("username;date;text;id")

infoLog("Searching...")

def receiveBuffer(tweets):
	for t in tweets:
		outputFile.write(('\n%s;%s;"%s";"%s"' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.text, t.id)))
	outputFile.flush()
	infoLog('More ' + str(len(tweets)) + ' saved on file...')

got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)

outputFile.close()
infoLog("Done!")

