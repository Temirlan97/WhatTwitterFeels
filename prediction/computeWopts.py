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
tweetsN = 60
Phi = getPartitionedInput(PhiRaw, pricesN, tweetsN)
Wopt = (np.linalg.pinv(Phi).dot(Z)).T
np.save("actual/Wopt/Tweets" + str(tweetsN) + "_"+intervalAndFrame, Wopt)


