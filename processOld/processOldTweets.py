import io
import csv
from threading import Thread
import Queue
import datetime
import time
#set the encoding
import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')

#import utils
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail
#import vader 
sys.path.append("../vaderSentiment/vaderSentiment/")
import vaderSentiment as vader

#################################
# READING OUT KEYS						
#################################
configs = readOutValues("keyfile.txt")

#################################
# TWITTER AUTHORIZATION						
#################################
import tweepy as tw
auth = tw.OAuthHandler(configs['consumer_key'], configs['consumer_secret'])
auth.set_access_token(configs['access_token'], configs['access_token_secret'])
api = tw.API(auth)

analyzer = vader.SentimentIntensityAnalyzer()
statusQueue = Queue.Queue()
doneReading = False

def consumeTweetsTest():
	while not doneReading:
		try:
			status = statusQueue.get(True, 5)
			score = analyzer.polarity_scores(status.text)['compound']
			infoLog("Score: " + str(score) + "\ntext: " + status.text)
		except Queue.Empty:
			pass

processedAndWrote = 0
def processTweetsIntoFile():
	with open("processedTweets.csv", "w") as outputCSV:
		outputCSV.write("userid;timestamp;tweetid;score")
		currentProcessed = 0
		while not doneReading:
			try:
				status = statusQueue.get(True, 5)
				score = analyzer.polarity_scores(status.text)['compound']
				timestamp_ms = (status.created_at - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0
				args = (int(status.user.id), timestamp_ms, int(status.id), float(score))
				outputCSV.write("\n%s;%s;%s;%s" % args)
				currentProcessed += 1
				if(currentProcessed >= 10000):
					processedAndWrote += currentProcessed
					currentProcessed = 0
					infoLog("Processed " + str(processedAndWrote))
			except Queue.Empty:
				pass
	infoLog("------------------> Done processing.")

processThread = Thread(target = processTweetsIntoFile)
processThread.start()


readAndQueued = 0
try:
	with io.open("old_tweets.csv", encoding = "ISO-8859-1") as csvFile:
		#input file columns are ['username', 'date', 'text', 'id']
		reader = csv.reader(csvFile, delimiter = ';')
		reader.next()
		currentQueued = 0
		for row in reader:
			#try getting it from twitter using the status id
			try:
				status = api.get_status(row[3])
				if status:
					statusQueue.put(status)
					currentQueued += 1
					if(currentQueued >= 10000):
						readAndQueued += currentQueued
						currentQueued = 0
						info("Queued " + str(readAndQueued))
			except Exception as error:
				errorLog(error)
				infoLog("Sleeping for 10 secs")
				time.sleep(60)

except Exception as error:
	terminationMessage = (str(error))
	errorLog(terminationMessage)
	notifyViaEmail("Process old tweets crashed",  terminationMessage)
finally:
	doneReading = True
infoLog("------------------> Done reading.")
processThread.join()
infoLog("DONE!")
infoLog("Process Old Tweets done", "The process has terminated normally")






