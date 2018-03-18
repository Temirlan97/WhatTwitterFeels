import tweepy as tw
import time

consumer_key = "N5R3atfOkOp3TS2JySlSzs5Hz"
consumer_secret = "Q517Ja3Xb43NcCd08HOlui42VaY2kMQzrr4c5RuLXZZlKPaTTC"

access_token = "968869225820557315-0kXd718oUshKiim6Z7y5VUHJU0wxsFK"
access_token_secret = "B1OuaTeL2VkOfJNMSdQMsFyZQnjvxV4C65bbAIrUULaaI"

auth = tw.OAuthHandler("N5R3atfOkOp3TS2JySlSzs5Hz", "Q517Ja3Xb43NcCd08HOlui42VaY2kMQzrr4c5RuLXZZlKPaTTC")
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

