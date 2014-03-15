#!/usr/bin/env python

import urllib2
import sys
import json
import datetime

if len(sys.argv) < 2:
	print "--"
	sys.exit(1)

stopId = sys.argv[1]
busId = None
if len(sys.argv) > 2:
	busId = sys.argv[2]

url = "http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_%s.json?minutesBefore=0&minutesAfter=99&key=TEST" % stopId
responseHandle = urllib2.urlopen(url)
response = json.loads(responseHandle.read())

currentTime = response["currentTime"]
arrivals = response["data"]["arrivalsAndDepartures"]

if len(arrivals) <= 0:
	print "--"
	sys.exit(0)
	
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
	print "--"
	sys.exit(0)

current = datetime.datetime.fromtimestamp(currentTime / 1000) #convert ms to s
soonest = datetime.datetime.fromtimestamp(soonestTime / 1000) #convert ms to s

print int((soonest - current).total_seconds() / 60) #convert sec to min

#print "Current time:"
#print currentTime
#print currentTime / 1000
#print current.isoformat()
#print "Next arrival:"
#print soonestTime
#print soonestTime / 1000
#print soonest.isoformat()

#print "Data:"
#print json.dumps(response["data"]["arrivalsAndDepartures"], indent=1)
