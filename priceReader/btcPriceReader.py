import urllib, json, time, MySQLdb
import sys
#import utils
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail

btcUrl = "https://api.coinbase.com/v2/prices/spot?currency=USD"

failedOnce = False

configs = readOutValues("keyfile.txt")
db = MySQLdb.connect(host = configs['mysqlHost'], user = configs['mysqlUser'], passwd = configs['mysqlPass'], db = configs['mysqlSchema'], port = 3306)
insertQuery = "INSERT INTO twitter.btc_price(timestamp, btc_spot_price) VALUES(%s,%s);"
while True:
	try:
		response = urllib.urlopen(btcUrl)
		jsonResponse = json.loads(response.read())
		price = str(int(float(jsonResponse['data']['amount'])*100.0))
		timestamp = str(int(time.time()))
		infoLog(price +" "+ timestamp)
		cursor = db.cursor()
		cursor.execute(insertQuery, (price, timestamp))
		db.commit()
		cursor.close()
		time.sleep(60)
	except Exception as error:
		errorLog(error)
		if (failedOnce):
			notifyViaEmail("BTC reader crashed", str(error))
			break
		failedOnce = True
db.close()


