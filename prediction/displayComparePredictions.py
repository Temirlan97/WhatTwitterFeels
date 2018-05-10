import numpy as np
#################################
# Importing myutils					
#################################
import sys
sys.path.append("../myutils/")
from log import errorLog, infoLog
from readKeyfile import readOutValues
from sendEmail import notifyViaEmail
#import time for stopwatch
import time
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold

def getPartitionedInput(PhiRaw, pricesN, tweetsN):
	Phi = []
	factor = (tweetsN)/2.0
	for row in PhiRaw:
		# Phi.append(row[:pricesN])
		tweetScores = row[pricesN:]
		tweetScoreCounter = np.zeros(tweetsN, dtype=int)
		for score in tweetScores:
			idxForTweetScore = int((score + 1.0)*factor)
			if(score == 1):
				idxForTweetScore = tweetsN - 1
			tweetScoreCounter[idxForTweetScore] = tweetScoreCounter[idxForTweetScore] + 1
		tweetScorePartitions = np.zeros(tweetsN, dtype=float)
		for i in range(0, len(tweetScoreCounter)):
			tweetScorePartitions[i] = float(tweetScoreCounter[i]*100)/len(tweetScores)
		# Phi.append(np.append(row[:pricesN], tweetScorePartitions))
		Phi.append(tweetScorePartitions)
	return np.array(Phi)


prefix = "data/Computed/Raw/"
intervalAndFrame = "1h-7d"
PhiRaw = np.load(prefix + "input_" + intervalAndFrame + ".npy")
Z = np.load(prefix + "output_" + intervalAndFrame + ".npy")

pricesN = len(Z[0])
kf = KFold(n_splits=4, shuffle=False)
tweetsN = 60
print("===========================================")
print("Computing tweetsN = " + str(tweetsN) + " ...")
Phi = getPartitionedInput(PhiRaw, pricesN, tweetsN)
for train_index, test_index in kf.split(Phi):
	name = "Train: " + str(train_index) + " Test: " + str(test_index)
	PhiTrain, PhiTest = Phi[train_index], Phi[test_index]
	ZTrain, ZTest = Z[train_index], Z[test_index]
	W = (np.linalg.pinv(PhiTrain).dot(ZTrain)).T
	meanDeviation = 0.0
	i = 0
	correctSide = 0
	sideTotal = 0
	N = float(len(PhiTest))
	while(i < len(PhiTest)):
		# prediction = W.dot(PhiTest[i])
		prediction = np.zeros(len(ZTest[i]))
		actual = ZTest[i]
		error = 0.0
		k = float(len(prediction))
		sideTotal += (k - 1)
		for j in range(1, len(prediction)):
			p = prediction[j]
			a = actual[j]
			if (p >= 0 and a >= 0) or (p < 0 and a < 0):
				correctSide += 1
			error += abs(prediction[j] - actual[j])/k
		meanDeviation += error/N
		i += 1
		accuracy = correctSide*100.0/sideTotal
		plt.plot(prediction, color='blue')
		plt.plot(actual, color='red')
		plt.xlabel('Hours')
		plt.ylabel('Price Change')
		plt.title("Mean deviation: " + str(meanDeviation) + " Accuracy: " + str(accuracy))
		plt.show()





