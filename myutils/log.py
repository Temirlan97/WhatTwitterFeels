import datetime
#################################
# LOGGING						
#################################
def _Log(output, filename):
	#First prepare the output
	readyOutput = str(datetime.datetime.now()) + ":\n"
	for line in str(output).split("\n"):
		readyOutput += "\t" + line + "\n"
	#then print and write to the file
	print(readyOutput)
	with open(filename, "a") as logfile:
		logfile.write(readyOutput)

def errorLog(output):
	_Log(output, "errorlog.txt");

def infoLog(output):
	_Log(output, "infolog.txt");