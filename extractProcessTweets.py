import tweepy as tw
import time
import MySQLdb
import Queue

#################################
# Importing myutils					
#################################
import sys
sys.path.append("./myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail

#################################
# READING OUT KEYS						
#################################
configs = readOutValues("keyfile.txt")

#################################
# TWITTER AUTHORIZATION						
#################################
auth = tw.OAuthHandler(configs['consumer_key'], configs['consumer_secret'])
auth.set_access_token(configs['access_token'], configs['access_token_secret'])
api = tw.API(auth)

#################################
# TWEETS STREAMING						
#################################
statusQueue = Queue.Queue()

class TweetListenerAndWriter(tw.StreamListener):

	def on_status(self, status):
		statusQueue.put(status)

	def on_error(self, status_code):
		errorLog("Program encountered an error " + str(status_code))
		if status_code == 420:
			return False
		notifyViaEmail("error on extractProcessTweets", "Status code: " + str(status_code))

	def on_exception(self, exception):
		notifyViaEmail("extractProcessTweets crashed", str(exception))



myListener = TweetListenerAndWriter()
myStream = tw.Stream(auth = api.auth, listener = myListener)
try:
	myStream.filter(track=['BTC', 'Bitcoin', 'bitcoin', 'btc', "BITCOIN"], async = True)
except Exception as error:
	notifyViaEmail("extractProcessTweets crashed", str(error))

#################################
# STORING PROCESSED TWEETS					
#################################
import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()


try:
	db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)
	insertQuery = "INSERT INTO twitter.tweets(user_id, timestamp, tweet_id, score)" \
		"VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE user_id=user_id;"
	insertUserQuery = "INSERT INTO twitter.users (user_id)" \
		"SELECT %s FROM dual WHERE NOT EXISTS (SELECT * FROM twitter.users WHERE user_id = %s);"
	STATUS_BUFFER_SIZE = 100
	while(True):
		cursor = db.cursor()
		count = 0;
		try:
			while(count < STATUS_BUFFER_SIZE):
				status = statusQueue.get()
				score = analyzer.polarity_scores(status.text)['compound']
				if(score != 0.0):
					args = (int(status.user.id), status.timestamp_ms, int(status.id), float(score))
					cursor.execute(insertQuery, args)
					cursor.execute(insertUserQuery, (int(status.user.id), int(status.user.id)))
				count += 1
			db.commit()
			infoLog("Committing " + str(count) + " items to the DB.\n" + 
				str(statusQueue.qsize()) + " more items waiting in the queue")
		except MySQLdb.Error as error:
			errorLog(error)
		finally:
			cursor.close()
except Exception as error:
	notifyViaEmail("extractProcessTweets crashed", str(error))
finally:
	db.close()

notifyViaEmail("extractProcessTweets terminated", "For some reasons the process reached the end.\nCheck out the server.")
