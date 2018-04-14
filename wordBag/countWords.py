import csv
import io
from nltk.tokenize import word_tokenize

import sys
reload(sys)
sys.setdefaultencoding('ISO-8859-1')

def findLowest(topWords):
	result = topWords.keys()[0]
	for word in topWords:
		if(topWords[word] < topWords[result]):
			result = word
	return result

with io.open("old_tweets.csv", encoding = "ISO-8859-1") as csvFile:
	#fieldnames = ['username', 'date', 'text', 'id']
	#reader = csv.DictReader(csvFile, fieldnames = fieldnames)
	reader = csv.reader(csvFile, delimiter = ';')
	reader.next()
	i = 0;
	counter = {}
	topWords = {}
	topsLowest = ""
	topMaxAllowed = 2000
	for row in reader:
		for word in word_tokenize(row[2]):
			counter[word] = counter.get(word, 0) + 1
		if(len(topWords) < topMaxAllowed):
			topWords[word] = counter[word]
			if((not hasattr(topWords, topsLowest)) or topWords[topsLowest] > counter[word]):
				topsLowest = word
		elif (topWords[topsLowest] < counter[word]):
			del topWords[topsLowest]
			topWords[word] = counter[word]
			topsLowest = findLowest(topWords)
	with io.open("word_count.csv", mode="w", encoding="ISO-8859-1") as outputFile:
		outputFile.write(unicode("word;frequency"))
		for word in topWords:
			outputFile.write(unicode("\n%s;%d" % (word, topWords[word])))
