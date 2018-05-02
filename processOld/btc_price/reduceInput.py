#this program writes the processed grades into the database
import csv, sys
import pandas as pd
#import utils
sys.path.append("../../myutils/")
from log import errorLog, infoLog

with open("reduced.csv", "w") as out:
	out.write("Timestamp,PriceUSD")
	colnames=['Timestamp', 'PriceUSD', 'Smth else idk']
	csvFile = pd.read_csv("coinbaseUSD.csv", names=colnames)
	count = 0
	totalCount = 0
	for index, row in csvFile.iterrows():
		timestamp = int(row['Timestamp'])
		priceUsd =  int(float(row['PriceUSD'])*100.0)
		#to reduce the data. For now we don't need much, since we don't have old tweets anyways
		if(timestamp < 1514806792):
			continue
		count += 1
		out.write("\n" + str(timestamp) + "," + str(priceUsd))
		if(count >= 1000):
			totalCount += count
			count = 0
			infoLog(totalCount)
	totalCount += count
	terminationMessage = "Terminated Normally. Wrote " + str(totalCount) + " items into the file"
	infoLog(terminationMessage)








