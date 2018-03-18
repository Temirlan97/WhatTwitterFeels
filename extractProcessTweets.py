import tweepy as tw
import time
import MySQLdb

consumer_key = "N5R3atfOkOp3TS2JySlSzs5Hz"
consumer_secret = "Q517Ja3Xb43NcCd08HOlui42VaY2kMQzrr4c5RuLXZZlKPaTTC"

access_token = "968869225820557315-0kXd718oUshKiim6Z7y5VUHJU0wxsFK"
access_token_secret = "B1OuaTeL2VkOfJNMSdQMsFyZQnjvxV4C65bbAIrUULaaI"

auth = tw.OAuthHandler("N5R3atfOkOp3TS2JySlSzs5Hz", "Q517Ja3Xb43NcCd08HOlui42VaY2kMQzrr4c5RuLXZZlKPaTTC")
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)



