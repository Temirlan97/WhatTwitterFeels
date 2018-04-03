import tweepy as tw
import time
import MySQLdb
import Queue

#################################
# LOGGING						
#################################
def Log(output, filename):
	#First prepare the output
	readyOutput = str(time.asctime(time.localtime())) + ":\n"
	for line in str(output).split("\n"):
		readyOutput += "\t" + line + "\n"
	#then print and write to the file
	print(readyOutput)
	with open(filename, "a") as logfile:
		logfile.write(readyOutput)

def errorLog(output):
	Log(output, "errorlog.txt");

def infoLog(output):
	Log(output, "infolog.txt");


#################################
# READING OUT KEYS						
#################################
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

#################################
# TWITTER AUTHORIZATION						
#################################
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
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



myListener = TweetListenerAndWriter()
myStream = tw.Stream(auth = api.auth, listener = myListener)

myStream.filter(track=['BTC', 'Bitcoin', 'bitcoin', 'btc', "BITCOIN"], async = True)


#################################
# STORING PROCESSED TWEETS					
#################################
import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()

db = MySQLdb.connect(host = mysqlHost, user = mysqlUser, passwd = mysqlPass, db = mysqlSchema, port = 3306)
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

db.close()


