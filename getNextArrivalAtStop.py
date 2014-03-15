#!/usr/bin/env python

import urllib2
import sys
import json
import datetime

def getNextArrivalInMinutes(apiKey, stopId, busId=None):
	url = "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_%s.json?minutesBefore=0&minutesAfter=99&key=%s" % (stopId, apiKey)
	responseHandle = urllib2.urlopen(url)
	response = json.loads(responseHandle.read())

	currentTime = response["currentTime"]
	arrivals = response["data"]["arrivalsAndDepartures"]

	if len(arrivals) <= 0:
		raise Exception("No upcoming arrivals at stop %s" % stopId)
	
	soonestTime = None
	for arrival in arrivals:
		name = arrival["routeShortName"]
		if None != busId and name != busId:
			continue
	
		predicted = arrival["predictedArrivalTime"]
		scheduled = arrival["scheduledArrivalTime"]
		if scheduled > currentTime and (scheduled < soonestTime or soonestTime == None):
			soonestTime = scheduled
		if predicted > currentTime and (predicted < soonestTime or soonestTime == None):
			soonestTime = predicted

	if not soonestTime:
		raise Exception("No upcoming arrivals of bus %s at stop %s" % (busId, stopId))

	current = datetime.datetime.fromtimestamp(currentTime / 1000) #convert ms to s
	soonest = datetime.datetime.fromtimestamp(soonestTime / 1000) #convert ms to s

	return int((soonest - current).total_seconds() / 60) #convert sec to min

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "--"
		sys.exit(-1)

	stopId = sys.argv[1]
	busId = None
	if len(sys.argv) > 2:
		busId = sys.argv[2]

	apiKey = "TEST"
	try:
		nextArrival = getNextArrivalInMinutes(apiKey, stopId, busId)
		print nextArrival
		sys.exit(nextArrival)
	except Exception as e:
		print "--"
		sys.exit(255)
