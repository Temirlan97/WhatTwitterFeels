import numpy as np
#################################
# Importing myutils					
#################################
import sys
import csv
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail
#import time for stopwatch
import time
import matplotlib.pyplot as plt
import pandas as pd

area = np.pi * 1

prefix = "data/Computed/Raw/Results/PricesAndTweets/1000to300000/errors"
# intervalsAndFrames = [["1m","1h", [0,0,1]],["1h","1d", [0,1,0]],["1h","7d", [0,1,1]],["1d","7d", [1,0,0]]]
intervalsAndFrames = [["1h","1d", [0,1,0]],["1h","7d", [0,1,1]],["1d","7d", [1,0,0]]]
legends = []
names = []
yLabel = "Mean Deviation"
colName = "mean_error"
# yLabel = "Accuracy"
# colName = "meanAccuracy"
for x in intervalsAndFrames:
	interval = x[0]
	framewidth = x[1]
	colors = x[2]
	name = interval + "-" + framewidth
	csvFile = pd.read_csv(prefix+ name +".csv")
	#tweetsN,mean_error, meanAccuracy
	legend = plt.scatter(csvFile["tweetsN"], csvFile[colName], s=area, c=colors)
	legends.append(legend)
	names.append(name)
	print(name)
	print(np.amax(csvFile["meanAccuracy"]))
	print(np.amin(csvFile["mean_error"]))
	plt.title("Correlation of " + yLabel + " to M (interval - frame width)")
	plt.xlabel('M')
	plt.ylabel(yLabel)
plt.legend(legends, names, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.grid()
plt.show()

# for x in intervalsAndFrames:
# 	interval = x[0]
# 	framewidth = x[1]
# 	colors = x[2]
# 	name = interval + "-" + framewidth
# 	csvFile = pd.read_csv(prefix+ name +".csv")
# 	#tweetsN,mean_error, meanAccuracy
# 	legend = plt.scatter(csvFile["tweetsN"], csvFile["mean_error"], s=area, c=colors)
# 	legends.append(legend)
# 	names.append(name)
# 	plt.title("Correlation of error to M (interval - frame width)")
# 	plt.xlabel('M')
# 	plt.ylabel('Error (Mean deviation)')
# plt.legend(legends, names, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
# plt.grid()
# plt.show()

