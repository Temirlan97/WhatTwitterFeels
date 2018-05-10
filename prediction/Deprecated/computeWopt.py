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

def analyzeError(name, Phi, Z, PhiTest, ZTest):
	W = (np.linalg.pinv(Phi).dot(Z)).T
	meanError = 0.0
	i = 0
	correctSide = 0
	sideTotal = 0
	N = float(len(PhiTest))
	print(PhiTest.shape)
	while(i < len(PhiTest)):
		prediction = W.dot(PhiTest[i])
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
	print(name)
	print("Mean error: " + str(meanError))
	accuracy = correctSide*100.0/sideTotal
	print("Side accuracy: " + str(accuracy) + "%")

postfixesStandard = ["1m-1h", "5m-1h", "1h-1d", "12h-3d", "12h-7d", "1d-7d"]
postfixes = ["1d-7d"]
prefix = "data/Computed/FramewiseIntotwo/"
print(prefix)
for intervalAndFrame in postfixes:
	Phi = np.load(prefix + "trainingInput_" + intervalAndFrame + ".npy")
	Z = np.load(prefix + "trainingOutput_" + intervalAndFrame + ".npy")
	PhiTest = np.load(prefix + "testingInput_" + intervalAndFrame + ".npy")
	ZTest = np.load(prefix + "testingOutput_" + intervalAndFrame + ".npy")

	PhiPrices = []
	PhiTweets = []
	for i in range(0, len(Phi)):
		PhiPrices.append(Phi[i][201:])
		PhiTweets.append(Phi[i][:201])
	PhiTestPrices = []
	PhiTestTweets = []
	for i in range(0, len(PhiTest)):
		PhiTestPrices.append(PhiTest[i][201:])
		PhiTestTweets.append(PhiTest[i][:201])
	PhiPrices = np.array(PhiPrices)
	PhiTestPrices = np.array(PhiTestPrices)
	PhiTweets = np.array(PhiTweets)
	PhiTestTweets = np.array(PhiTestTweets)

	# print(PhiPrices.shape)
	# print(Phi.shape)
	# print(Z.shape)
	# print(PhiTest.shape)
	# print(ZTest.shape)

	analyzeError("[" + intervalAndFrame + "]With prices and tweets", Phi, Z, PhiTest, ZTest)
	print("\n")
	analyzeError("[" + intervalAndFrame + "]With prices", PhiPrices, Z, PhiTestPrices, ZTest)
	print("\n")
	analyzeError("[" + intervalAndFrame + "]With tweets", PhiTweets, Z, PhiTestTweets, ZTest)
	print("\n")


	i = 0
	W = (np.linalg.pinv(Phi).dot(Z)).T
	WPrices = (np.linalg.pinv(PhiPrices).dot(Z)).T
	WTweets = (np.linalg.pinv(PhiTweets).dot(Z)).T
	alpha = 1
	# WTweets = (((np.linalg.inv(PhiTweets.T.dot(PhiTweets) + alpha*alpha*np.identity(len(PhiTweets[1])))).dot(PhiTweets.T)).dot(Z)).T 
	while(i < len(PhiTest)):
		prediction = W.dot(PhiTest[i])
		predictionWithPrices = WPrices.dot(PhiTestPrices[i])
		predictionWithTweets = WTweets.dot(PhiTestTweets[i])
		actual = ZTest[i]
		plt.plot(prediction, color ='red')
		plt.plot(predictionWithPrices, color ='green')
		plt.plot(predictionWithTweets, color ='black')
		plt.plot(actual, color = 'blue')
		plt.ylabel(str(i))
		plt.show()
		i += 1

	# # best alpha is 334
	# #best alpha is 99.4
	# alpha = 3.0
	# # W = (((np.linalg.inv(Phi.T.dot(Phi) + alpha*alpha*np.identity(len(Phi[1])))).dot(Phi.T)).dot(Z)).T
	# W = (np.linalg.pinv(Phi).dot(Z)).T
	# meanError = 0.0
	# i = 0
	# correctSide = 0
	# sideTotal = 0
	# N = float(len(PhiTest))
	# while(i < len(PhiTest)):
	# 	prediction = W.dot(PhiTest[i])
	# 	actual = ZTest[i]
	# 	error = 0.0
	# 	k = float(len(prediction))
	# 	sideTotal += k
	# 	for j in range(0, len(prediction)):
	# 		p = prediction[j]
	# 		a = actual[j]
	# 		if (p > 0 and a > 0) or (p < 0 and a < 0):
	# 			correctSide += 1
	# 		error += abs(prediction[j] - actual[j])/k
	# 	meanError += error/N
	# 	i += 1
	# errorOutput = intervalAndFrame + "With tweets and prices. Mean error(real - predicted): " + str(meanError) + "\n"
	# errorOutput += "Movement direction accuracy: " + str(correctSide*100.0/sideTotal) + "%"
	# infoLog(errorOutput)


	# meanError = 0.0
	# i = 0
	# correctSide = 0
	# sideTotal = 0
	# N = float(len(PhiTestPrices))
	# WPrices = (np.linalg.pinv(PhiPrices).dot(Z)).T
	# while(i < len(PhiTestPrices)):
	# 	prediction = WPrices.dot(PhiTestPrices[i])
	# 	actual = ZTest[i]
	# 	error = 0.0
	# 	k = float(len(prediction))
	# 	sideTotal += k
	# 	for j in range(0, len(prediction)):
	# 		p = prediction[j]
	# 		a = actual[j]
	# 		if (p > 0 and a > 0) or (p < 0 and a < 0):
	# 			correctSide += 1
	# 		error += abs(prediction[j] - actual[j])/k
	# 	meanError += error/N
	# 	i += 1
	# errorOutput = intervalAndFrame + "With prices. Mean error(real - predicted): " + str(meanError) + "\n"
	# errorOutput += "Movement direction accuracy: " + str(correctSide*100.0/sideTotal) + "%"
	# infoLog(errorOutput)


	# meanError = 0.0
	# i = 0
	# correctSide = 0
	# sideTotal = 0
	# N = float(len(PhiTestTweets))
	# WTweets = (np.linalg.pinv(PhiTweets).dot(Z)).T
	# while(i < len(PhiTestTweets)):
	# 	prediction = WTweets.dot(PhiTestTweets[i])
	# 	actual = ZTest[i]
	# 	error = 0.0
	# 	k = float(len(prediction))
	# 	sideTotal += k
	# 	for j in range(0, len(prediction)):
	# 		p = prediction[j]
	# 		a = actual[j]
	# 		if (p > 0 and a > 0) or (p < 0 and a < 0):
	# 			correctSide += 1
	# 		error += abs(prediction[j] - actual[j])/k
	# 	meanError += error/N
	# 	i += 1
	# errorOutput = intervalAndFrame + "With tweets. Mean error(real - predicted): " + str(meanError) + "\n"
	# errorOutput += "Movement direction accuracy: " + str(correctSide*100.0/sideTotal) + "%"
	# infoLog(errorOutput)


# bestAlpha = 0.0
# alpha = 0.0
# Wopt = None
# N = float(len(PhiTest))
# leastError = 10**10
# while alpha < 1000:
# 	alpha += 1
# 	print(str(alpha) + " Least error: " + str(leastError))
# 	W = (((np.linalg.inv(Phi.T.dot(Phi) + alpha*alpha*np.identity(len(Phi[1])))).dot(Phi.T)).dot(Z)).T
# 	# W = (np.linalg.pinv(Phi).dot(Z)).T
# 	meanError = 0.0
# 	for i in range(0, len(PhiTest)):
# 		prediction = W.dot(PhiTest[i])
# 		# print(prediction)
# 		# print(Z[i])
# 		error = prediction - ZTest[i]
# 		for x in error:
# 			meanError += (x*x)/N
# 	if(meanError < leastError):
# 		Wopt = W
# 		bestAlpha = alpha
# 		leastError = meanError

# np.save("Wopt", Wopt)
# print(bestAlpha)
# print(leastError)

