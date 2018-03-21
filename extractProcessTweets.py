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
		print("Program encountered an error " + status_code)
		if status_code == 420:
			return False



myListener = TweetListenerAndWriter()
myStream = tw.Stream(auth = api.auth, listener = myListener)

myStream.filter(track=['BTC', 'Bitcoin', 'bitcoin', 'btc'], async = True)


import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()

while(True):
	status = statusQueue.get()
	cursor = db.cursor()
	count = 1;
	try:
		while(True):
			score = analyzer.polarity_scores(status.text)['compound']
			if(score != 0.0):
				args = (int(status.user.id), status.timestamp_ms, int(status.id), float(score))
				cursor.execute(insertQuery, args)
			if statusQueue.empty():
				break;
			count += 1
		db.commit()
		print("Commiting " + str(count) + " items to the DB")
	except MySQLdb.Error as error:
		print(error)
	finally:
		cursor.close()

