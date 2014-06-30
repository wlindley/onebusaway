#!/usr/bin/env python

from __future__ import division
import urllib2
import sys
import json
import datetime

def getAPIKey(filename):
	try:
		f = open(filename)
		contents = f.read()
		f.close()
		return contents.replace("\n", "")
	except:
		return "TEST"

def getNextArrivalInSeconds(apiKey, stopId, busId=None, arrivalIndex=0):
	url = "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_%s.json?minutesBefore=0&minutesAfter=99&key=%s" % (stopId, apiKey)
	responseHandle = urllib2.urlopen(url)
	response = json.loads(responseHandle.read())

	currentTime = response["currentTime"]
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

	if len(arrivals) <= 0:
		raise Exception("No upcoming arrivals at stop %s" % stopId)
	
	soonestTimes = []
	for arrival in arrivals:
		name = arrival["routeShortName"]
		if None != busId and name != busId:
			continue
	
		curArrival = arrival["scheduledArrivalTime"]
		predicted = arrival["predictedArrivalTime"]
		if predicted < curArrival:
			curArrival = predicted
		soonestTimes.append(curArrival)

	soonestTimes.sort()

	if 0 == len(soonestTimes):
		raise Exception("No upcoming arrivals of bus %s at stop %s" % (busId, stopId))
	if arrivalIndex >= len(soonestTimes):
		raise Exception("Stop %s only has %s upcoming arrivals for bus %s, but arrival index %s was requested" % (stopId, busId, len(soonestTimes), arrivalIndex))

	soonestTime = soonestTimes[arrivalIndex]

	current = datetime.datetime.fromtimestamp(currentTime / 1000) #convert ms to s
	soonest = datetime.datetime.fromtimestamp(soonestTime / 1000) #convert ms to s

	return (soonest - current).total_seconds()

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
		print nextArrival
		sys.exit(0)
	except Exception as e:
		print float("NaN")
		sys.exit(1)
