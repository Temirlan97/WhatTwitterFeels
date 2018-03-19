import tweepy as tw
import time
import MySQLdb

f = open("keyfile.txt", "r")

consumer_key = f.readline().strip()
consumer_secret = f.readline().strip()

access_token = f.readline().strip()
access_token_secret = f.readline().strip()

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)

print(api)


