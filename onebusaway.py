from __future__ import division
import urllib2
import sys
import os
import json
import datetime
import traceback
import logging
import logging.handlers
import inspect

def getLogger():
	return logging.getLogger("onebusaway")

def _buildLogger():
	scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	logger = getLogger()
	logger.setLevel(logging.DEBUG)
	logger.addHandler(logging.handlers.RotatingFileHandler(os.path.join(scriptDir, "onebusaway.log"), maxBytes=1024*1024, backupCount=5))
	return logger
logger = _buildLogger()

def getAPIKey(filename="api.key"):
	try:
		f = open(filename)
		contents = f.read()
		f.close()
		return contents.replace("\n", "")
	except:
		return "TEST"

def getNextArrivalInSeconds(apiKey, stopId, busId=None, arrivalIndex=0):
	logger.info("\n------------------------------------------------------------------------------------")
	logger.info("Getting info for stop: %s, bus: %s, arrival index: %s" % (stopId, busId, arrivalIndex))
	response = _getResponse(apiKey, stopId)
	_validateResponse(response)
	currentTime = _getCurrentTime(response)
	arrivals = _getArrivalPayload(response)
	return _getTimeUntilSpecifiedArrival(currentTime, arrivals, busId, arrivalIndex)

def safeGetNextArrivalInSeconds(apiKey, stopId, busId=None, arrivalIndex=0):
	try:
		return getNextArrivalInSeconds(apiKey, stopId, busId, arrivalIndex)
	except Exception as e:
		logger.exception(str(e) + "\n" + traceback.format_exc())
		logger.error("Next arrival: %s" % float("NaN"))
		return float("NaN")

def _getResponse(apiKey, stopId):
	url = "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_%s.json?minutesBefore=0&minutesAfter=99&key=%s" % (stopId, apiKey)
	logger.debug("calling url: %s" % url)
	responseHandle = urllib2.urlopen(url)
	rawResponse = responseHandle.read()
	response = json.loads(rawResponse)
	logger.debug("API response:\n" + rawResponse + "\n")
	responseHandle.close()
	return response

def _validateResponse(response):
	if response["code"] < 400:
		return
	logger.error("Server returned error code %s: %s" % (response["code"], response["text"]))
	raise Exception("Error code %s: %s" % (response["code"], response["text"]))

def _getCurrentTime(response):
	return response["currentTime"]

def _getArrivalPayload(response):
	payload = response["data"]
	if not payload:
		raise Exception("No payload in response")
	if not "arrivalsAndDepartures" in payload:
		payload = payload["entry"]
	if not payload:
		raise Exception("Malformed payload in response")
	if not "arrivalsAndDepartures" in payload:
		raise Exception("No arrival info in payload")
	arrivals = payload["arrivalsAndDepartures"]

	logger.info("Upcoming arrivals at stop:\n" + str(arrivals) + "\n")

	if len(arrivals) <= 0:
		raise Exception("No upcoming arrivals at stop %s" % stopId)

	return arrivals

def _getTimeUntilSpecifiedArrival(currentTime, arrivals, busId, arrivalIndex):
	soonestTimes = _getSortedSoonestArrivals(arrivals, busId, currentTime)

	if 0 == len(soonestTimes):
		raise Exception("No upcoming arrivals of bus %s at stop %s" % (busId, stopId))
	if arrivalIndex >= len(soonestTimes):
		raise Exception("Stop %s only has %s upcoming arrivals for bus %s, but arrival index %s was requested" % (stopId, busId, len(soonestTimes), arrivalIndex))

	soonestTime = soonestTimes[arrivalIndex]

	logger.info("Current time (raw): " + str(currentTime))
	logger.info("Arrival time (raw): " + str(soonestTime))

	current = datetime.datetime.fromtimestamp(currentTime / 1000) #convert ms to s
	soonest = datetime.datetime.fromtimestamp(soonestTime / 1000) #convert ms to s

	secondsUntilArrival = (soonest - current).total_seconds()
	logger.info("Seconds until arrival: %s" % secondsUntilArrival)
	return secondsUntilArrival

def _getSortedSoonestArrivals(arrivals, busId, currentTime):
	soonestTimes = []
	for arrival in arrivals:
		name = arrival["routeShortName"]
		if None != busId and name != busId:
			continue
	
		curArrival = arrival["scheduledArrivalTime"]
		predicted = arrival["predictedArrivalTime"]
		if predicted < curArrival and 0 < predicted:
			curArrival = predicted
		if curArrival >= currentTime:
			soonestTimes.append(curArrival)

	soonestTimes.sort()
	logger.info("Sorted and filtered upcoming arrivals: " + str(soonestTimes))
	return soonestTimes
