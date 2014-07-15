#!/usr/bin/env python

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

scriptDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
logger = logging.getLogger("onebusaway")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.handlers.RotatingFileHandler(os.path.join(scriptDir, "onebusaway.log"), maxBytes=1024*1024, backupCount=5))

def getAPIKey(filename):
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
	response = getResponse(apiKey, stopId)
	validateResponse(response)
	currentTime = getCurrentTime(response)
	arrivals = getArrivalPayload(response)
	return getTimeUntilSpecifiedArrival(currentTime, arrivals, busId, arrivalIndex)

def getResponse(apiKey, stopId):
	url = "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_%s.json?minutesBefore=0&minutesAfter=99&key=%s" % (stopId, apiKey)
	responseHandle = urllib2.urlopen(url)
	rawResponse = responseHandle.read()
	response = json.loads(rawResponse)
	logger.debug("API response:\n" + rawResponse + "\n")
	return response

def validateResponse(response):
	if response["code"] < 400:
		return
	logger.error("Server returned error code %s: %s" % (response["code"], response["text"]))
	raise Exception("Error code %s: %s" % (response["code"], response["text"]))

def getCurrentTime(response):
	return response["currentTime"]

def getArrivalPayload(response):
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

def getTimeUntilSpecifiedArrival(currentTime, arrivals, busId, arrivalIndex):
	soonestTimes = getSortedSoonestArrivals(arrivals, busId, currentTime)

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

def getSortedSoonestArrivals(arrivals, busId, currentTime):
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

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print float("NaN")
		sys.exit(2)

	stopId = sys.argv[1]
	busId = None
	if len(sys.argv) > 2:
		busId = sys.argv[2]
	arrivalIndex = 0
	if len(sys.argv) > 3:
		try:
			arrivalIndex = int(sys.argv[3])
		except Exception as e:
			print float("NaN")
			sys.exit(3)

	apiKey = getAPIKey("api.key")
	try:
		nextArrival = getNextArrivalInSeconds(apiKey, stopId, busId, arrivalIndex)
		logger.info("Next arrival: %s" % nextArrival)
		print nextArrival
		sys.exit(0)
	except Exception as e:
		print float("NaN")
		logger.exception(str(e) + "\n" + traceback.format_exc())
		logger.error("Next arrival: %s" % float("NaN"))
		sys.exit(1)
