import sys

sys.path.append("./vaderSentiment/vaderSentiment/")

import vaderSentiment as vader

analyzer = vader.SentimentIntensityAnalyzer()
print(analyzer.polarity_scores("IOTA has a great future")[
'compound'])


