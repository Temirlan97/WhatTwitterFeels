
#################################
# READING OUT KEYS						
#################################

def readOutValues(fileName):
	result = {}
	with open(fileName, "r") as keyfile:
		for line in keyfile:
			splitted = line.split("=", 1)
			if(len(splitted) > 1):
				result[splitted[0]] = splitted[1].strip()

	keyfile = open(fileName, "r")
	return result