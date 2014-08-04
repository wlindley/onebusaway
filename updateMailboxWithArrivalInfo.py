#!/usr/bin/env python

import sys
import urllib2
import math
import time
import onebusaway

logger = onebusaway.getLogger()

def getArrivalTime(stopId, busId, arrivalIndex):
	return onebusaway.safeGetNextArrivalInSeconds(onebusaway.getAPIKey(), stopId, busId, arrivalIndex)

def getArrivalTimeWithRetries(stopId, busId, arrivalIndex):
	arrivalTime = getArrivalTime(stopId, busId, arrivalIndex)
	if math.isnan(arrivalTime):
		for i in range(10):
			time.sleep(.5)
			arrivalTime = getArrivalTime(stopId, busId, arrivalIndex)
			if not math.isnan(arrivalTime):
				break
	return arrivalTime

def sendToMailbox(stopId, busId, arrivalIndex, arrivalTime):
	url = "http://localhost/mailbox/%s,%s,%s,%s" % (stopId, busId, arrivalIndex, arrivalTime)
	logger.debug("opening url: %s" % url)
	try:
		handle = urllib2.urlopen(url)
		handle.close()
		logger.info("Posted to mailbox")
	except:
		logger.warning("Error while posting to mailbox")

if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Usage: %s stop_id bus_id arrival_index" % sys.argv[0]
		sys.exit(-1)

	stopId = sys.argv[1]
	busId = sys.argv[2]
	try:
		arrivalIndex = int(sys.argv[3])
	except:
		sys.exit(-2)

	arrivalTime = getArrivalTimeWithRetries(stopId, busId, arrivalIndex)

	if not math.isnan(arrivalTime):
		sendToMailbox(stopId, busId, arrivalIndex, arrivalTime)
