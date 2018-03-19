import tweepy as tw
import time


keyfile = open("keyfile.txt", "r")

consumer_key = keyfile.readline().strip()
consumer_secret = keyfile.readline().strip()

access_token = keyfile.readline().strip()
access_token_secret = keyfile.readline().strip()

keyfile.close()

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)


import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()
class MyStreamListener(tw.StreamListener):

	def on_status(self, status):
		score = analyzer.polarity_scores(status.text)['compound']
		print(type(status.user.id))
		print(type(status.timestamp_ms))
		print(type(status.id))
		print(type(score))


myListener = MyStreamListener()
myStream = tw.Stream(auth = api.auth, listener = myListener)

myStream.filter(track=['BTC', 'bitcoin', 'cryptocurrency', 'Bitcoin', 'crypto'], async = True)

