#this program writes the processed grades into the database
import csv, sys, MySQLdb
import pandas as pd
#import utils
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail

configs = readOutValues("keyfile.txt")

db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)
insertQuery = "INSERT INTO twitter.tweets(timestamp, tweet_id, score)" \
	"VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE tweet_id=tweet_id;"
try:
	csvFile = pd.read_csv("processedTweets.csv", delimiter=";")
	cursor = db.cursor()
	count = 0
	totalCount = 0
	for index, row in csvFile.iterrows():
		#username;timestamp;tweetid;score
		score = float(row['score'])
		if(score != 0.0):
			args = (int(row['timestamp']), int(row['tweetid']), float(row['score']))
			count += 1
			cursor.execute(insertQuery, args)
			if(count >= 1000):
				totalCount += count
				count = 0
				infoLog(totalCount)
				db.commit()
	db.commit()
	cursor.close()
	terminationMessage = "Terminated Normally. Inserted " + str(totalCount) + " items into the DB"
	infoLog(terminationMessage)
	notifyViaEmail("Writing Old tweets finished", terminationMessage)
except Exception as error:
	errorLog(error)
	notifyViaEmail("CRASHED Writing Old tweets into DB", str(error))
finally:
	db.close()




