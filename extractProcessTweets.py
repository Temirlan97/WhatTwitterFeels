import tweepy as tw
import time
import MySQLdb

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

import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()

class TweetListenerAndWriter(tw.StreamListener):

	def on_status(self, status):
		score = analyzer.polarity_scores(status.text)['compound']
		if(score != 0.0):
			try:
				cursor = db.cursor()
				print(str(score) + status.text)
				args = (int(status.user.id), status.timestamp_ms, int(status.id), float(score))
				cursor.execute(insertQuery, args)
				db.commit()
			except MySQLdb.Error as error:
				print(error)
			finally:
				cursor.close()



myListener = TweetListenerAndWriter()
myStream = tw.Stream(auth = api.auth, listener = myListener)

myStream.filter(track=['BTC', 'Bitcoin', 'bitcoin', 'btc'], async = True)

