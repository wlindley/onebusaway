#!/usr/bin/env python

import sys
import urllib2
import math
import time
import onebusaway

logger = onebusaway.getLogger()

def getAndSubmitUpdate(stopId, busId, arrivalIndex, displayIndex):
	arrivalTime = _getArrivalTimeWithRetries(stopId, busId, arrivalIndex)
	_sendToMailbox(displayIndex, arrivalTime)

def _getArrivalTimeWithRetries(stopId, busId, arrivalIndex):
	arrivalTime = _getArrivalTime(stopId, busId, arrivalIndex)
	if math.isnan(arrivalTime):
		for i in range(10):
			time.sleep(.5)
			arrivalTime = _getArrivalTime(stopId, busId, arrivalIndex)
			if not math.isnan(arrivalTime):
				break
	return arrivalTime

def _getArrivalTime(stopId, busId, arrivalIndex):
	return onebusaway.safeGetNextArrivalInSeconds(onebusaway.getAPIKey(), stopId, busId, arrivalIndex)

def _sendToMailbox(displayIndex, arrivalTime):
	url = "http://localhost/mailbox/%s,%s" % (displayIndex, arrivalTime)
	logger.debug("opening url: %s" % url)
	try:
		handle = urllib2.urlopen(url)
		handle.close()
		logger.info("Posted to mailbox")
	except:
		logger.warning("Error while posting to mailbox")

if __name__ == "__main__":
	if len(sys.argv) < 5:
		print "Usage: %s stop_id bus_id arrival_index display_index" % sys.argv[0]
		sys.exit(-1)

	stopId = sys.argv[1]
	busId = sys.argv[2]
	try:
		arrivalIndex = int(sys.argv[3])
	except:
		sys.exit(-2)
	try:
		displayIndex = int(sys.argv[4])
	except:
		sys.exit(-3)

	getAndSubmitUpdate(stopId, busId, arrivalIndex, displayIndex)
