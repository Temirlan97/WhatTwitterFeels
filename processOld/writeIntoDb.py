#this program writes the processed grades into the database
import csv, sys, MySQLdb
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
	with open("processedTweets.csv", "r") as csvFile:
		reader = csv.reader(csvFile, delimiter = ';')
		reader.next()
		cursor = db.cursor()
		count = 0
		for row in reader:
			#username;timestamp;tweetid;score
			timestamp = row[1]
			tweetId = row[2]
			score = float(row[3])
			if(score != 0.0):
				args = (timestamp, tweetId, score)
				count += 1
				cursor.execute(insertQuery, args)
				if(count % 1000 == 0):
					infoLog(count)
		db.commit()
		cursor.close()
	notifyViaEmail("Writing Old tweets finished", "Terminated Normally")
except Exception as error:
	errorLog(error)
	notifyViaEmail("CRASHED Writing Old tweets into DB", str(error))
finally:
	db.close()




