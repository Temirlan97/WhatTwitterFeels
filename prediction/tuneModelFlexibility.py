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

def analyzeError(name, PhiTrain, ZTrain, PhiTest, ZTest):
	W = (np.linalg.pinv(PhiTrain).dot(ZTrain)).T
	meanError = 0.0
	i = 0
	correctSide = 0
	sideTotal = 0
	N = float(len(PhiTest))
	while(i < len(PhiTest)):
		prediction = W.dot(PhiTest[i])
		# constant prediction - baseline
		# prediction = np.zeros(len(ZTest[i]))
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
		meanError += error/N
		i += 1
	# print(name)
	print("Mean error: " + str(meanError))
	accuracy = correctSide*100.0/sideTotal
	print("Side accuracy: " + str(accuracy) + "%")
	return meanError, accuracy

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
smallestMeanError = 100
optimalAccuracy = 0
optimalTweetsN = 50
meanErrors = []
partitions = []
accuracies = []
for tweetsN in range(60, 61, 1):
	print("===========================================")
	print("Computing tweetsN = " + str(tweetsN) + " ...")
	Phi = getPartitionedInput(PhiRaw, pricesN, tweetsN)
	meanError = 0.0
	meanAccuracy = 0.0
	caseCounter = 0
	for train_index, test_index in kf.split(Phi):
		name = "Train: " + str(train_index) + " Test: " + str(test_index)
		PhiTrain, PhiTest = Phi[train_index], Phi[test_index]
		ZTrain, ZTest = Z[train_index], Z[test_index]
		caseCounter += 1
		meanErrorReturned, accuracyReturned = analyzeError(name, PhiTrain, ZTrain, PhiTest, ZTest)
		meanError += meanErrorReturned
		meanAccuracy += accuracyReturned
	meanError = meanError/caseCounter
	meanAccuracy = meanAccuracy/caseCounter
	print("meanError = " + str(meanError) + " meanAccuracy = " + str(meanAccuracy) + "%")
	meanErrors.append(meanError)
	partitions.append(tweetsN)
	accuracies.append(meanAccuracy)
	if(meanError < smallestMeanError):
		optimalAccuracy = meanAccuracy
		smallestMeanError = meanError
		optimalTweetsN = tweetsN

infoLog("optimalTweetsN = " + str(optimalTweetsN))
infoLog("smallestMeanError = " + str(smallestMeanError))
infoLog("optimalAccuracy = " + str(optimalAccuracy))
plt.plot(partitions, meanErrors, color='red')
plt.title(str(optimalTweetsN) + "->" + str(smallestMeanError) + "(" + str(optimalAccuracy) + "%)")
plt.show()

plt.plot(partitions, accuracies, color='green')
plt.title(str(optimalTweetsN) + "->" + str(smallestMeanError) + "(" + str(optimalAccuracy) + "%)")
plt.show()





