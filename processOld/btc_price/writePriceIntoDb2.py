#this program writes the processed grades into the database
import csv, sys, MySQLdb
import pandas as pd
#import utils
sys.path.append("../../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail

configs = readOutValues("keyfile.txt")

db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)
insertQuery = "INSERT INTO twitter.btc_price(timestamp, btc_spot_price)" \
	"VALUES(%s,%s) ON DUPLICATE KEY UPDATE btc_spot_price=btc_spot_price;"
try:
	csvFile = pd.read_csv("reduced.csv")
	cursor = db.cursor()
	count = 0
	totalCount = 0
	for index, row in csvFile.iterrows():
		if(index == 0):
			continue
		args = (int(row['Timestamp']), int(row['PriceUSD']))
		count += 1
		cursor.execute(insertQuery, args)
		if(count >= 1000):
			totalCount += count
			count = 0
			infoLog(totalCount)
			db.commit()
	db.commit()
	cursor.close()
	totalCount += count
	terminationMessage = "Terminated Normally. Inserted " + str(totalCount) + " items into the DB"
	infoLog(terminationMessage)
	notifyViaEmail("SUCCESS: Writing Old prices into DB", terminationMessage)
except Exception as error:
	errorLog(error)
	notifyViaEmail("CRASHED: Writing Old prices into DB", str(error))
finally:
	db.close()








