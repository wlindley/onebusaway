#!/usr/bin/env python

import sys
import time
import traceback
import onebusaway

logger = onebusaway.getLogger()

def addToFile(stopId, busId, arrivalIndex):
	requestLine = _generateRequestLine(stopId, busId, arrivalIndex)
	handle = _getFile()
	_addUniqueLineToFile(requestLine, handle)
	handle.close()

def _generateRequestLine(stopId, busId, arrivalIndex):
	return ",".join([stopId, busId, arrivalIndex]) + "\n"

def _getFile():
	handle = open(onebusaway.getRequestedBusesPath(), 'a+')
	handle.seek(0)
	return handle

def _addUniqueLineToFile(requestLine, handle):
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

	for i in range(10):
		try:
			addToFile(stopId, busId, arrivalIndex)
			break
		except Exception as e:
			logger.exception(str(e) + "\n" + traceback.format_exc())
			time.sleep(.1)
