import codecs
import sys

sys.path.append("./GetOldTweets-python")

import got

tweetCriteria = got.manager.TweetCriteria()
outputFileName = "old_tweets.csv"

tweetCriteria.querySearch = "BTC btc bitcoin Bitcoin BITCOIN"

#we need all tweets
#tweetCriteria.maxTweets = 100

tweetCriteria.since = "2018-01-01"

tweetCriteria.until = "2018-04-01"

outputFile = codecs.open(outputFileName, "a", "utf-8")

outputFile.write("username;date;text;id")

print("Searching...")

def receiveBuffer(tweets):
	for t in tweets:
		outputFile.write(('\n%s;%s;"%s";"%s"' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.text, t.id)))
	outputFile.flush()
	print('More %d saved on file...\n' % len(tweets))

got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)

outputFile.close()
print("Done!")

