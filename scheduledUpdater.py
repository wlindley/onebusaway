#!/usr/bin/env python

import sys
import time
import traceback
import onebusaway
import updateMailboxWithArrivalInfo as obaupdate

logger = onebusaway.getLogger()

def findAndUpdateRequestedBuses():
	logger.info("----Running Scheduled Update----")
	requestedData = _getRequestedData()
	for data in requestedData:
		_submitUpdate(data[0], data[1], data[2])

def _getRequestedData():
	handle = _getFile()
	lines = handle.readlines()
	handle.close()
	return _convertLinesToData(lines)

def _getFile():
	return open(onebusaway.getRequestedBusesPath(), "r")

def _convertLinesToData(lines):
	data = [[x for x in line.split(",")] for line in lines]
	for datum in data:
		try:
			datum[2] = int(datum[2])
		except Exception as e:
			logger.exception(str(e) + "\n" + traceback.format_exc())
	return data

def _submitUpdate(stopId, busId, arrivalIndex):
	logger.debug("Updating stop %s, bus %s, arrival index %s" % (stopId, busId, arrivalIndex))
	obaupdate.getAndSubmitUpdate(stopId, busId, arrivalIndex)

if __name__ == "__main__":
	for i in range(10):
		try:
			findAndUpdateRequestedBuses()
			break
		except Exception as e:
			logger.exception(str(e) + "\n" + traceback.format_exc())
			time.sleep(.1)
