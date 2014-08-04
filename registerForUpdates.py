#!/usr/bin/env python

import sys
import os
import inspect

_filename = "requestedBuses.dat"

def addToFile(stopId, busId, arrivalIndex):
	requestLine = generateRequestLine(stopId, busId, arrivalIndex)
	handle = getFile()
	addUniqueLineToFile(requestLine, handle)
	handle.close()

def generateRequestLine(stopId, busId, arrivalIndex):
	return ",".join([stopId, busId, arrivalIndex]) + "\n"

def getFile():
	scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	fname = os.path.join(scriptDir, _filename)
	handle = open(fname, 'a+')
	handle.seek(0)
	return handle

def addUniqueLineToFile(requestLine, handle):
	for line in handle.readlines():
		if line == requestLine:
			return
	handle.write(requestLine)

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Usage: %s stop_id bus_id arrival_index" % sys.argv[0]
		sys.exit(-1)

	stopId = sys.argv[1]
	busId = sys.argv[2]
	arrivalIndex = sys.argv[3]

	addToFile(stopId, busId, arrivalIndex)
