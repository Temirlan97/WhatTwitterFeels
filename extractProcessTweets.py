import tweepy as tw
import time
import MySQLdb
import Queue

keyfile = open("keyfile.txt", "r")

consumer_key = keyfile.readline().strip()
consumer_secret = keyfile.readline().strip()

access_token = keyfile.readline().strip()
access_token_secret = keyfile.readline().strip()

mysqlHost = keyfile.readline().strip()
mysqlUser = keyfile.readline().strip()
mysqlPass = keyfile.readline().strip()
mysqlSchema = keyfile.readline().strip()

keyfile.close()

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)

db = MySQLdb.connect(host = mysqlHost, user = mysqlUser, passwd = mysqlPass, db = mysqlSchema, port = 3306)
insertQuery = "INSERT INTO twitter.tweets(user_id, timestamp, tweet_id, score)" \
	"VALUES(%s,%s,%s,%s)"

statusQueue = Queue.Queue()

class TweetListenerAndWriter(tw.StreamListener):

	def on_status(self, status):
		statusQueue.put(status)

	def on_error(self, status_code):
		print("Program encountered an error " + str(status_code))
		if status_code == 420:
			return False



myListener = TweetListenerAndWriter()
myStream = tw.Stream(auth = api.auth, listener = myListener)

myStream.filter(track=['BTC', 'Bitcoin', 'bitcoin', 'btc'], async = True)


import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()
STATUS_BUFFER_SIZE = 100
while(True):
	cursor = db.cursor()
	count = 1;
	try:
		while(count < STATUS_BUFFER_SIZE):
			status = statusQueue.get()
			score = analyzer.polarity_scores(status.text)['compound']
			if(score != 0.0):
				args = (int(status.user.id), status.timestamp_ms, int(status.id), float(score))
				cursor.execute(insertQuery, args)
			count += 1
		db.commit()
		print(str(time.asctime(time.localtime())) + ": Committing " + str(count) + " items to the DB")
		print(str(statusQueue.qsize()) + " more items waiting in the queue");
	except MySQLdb.Error as error:
		print(error)
	finally:
		cursor.close()

