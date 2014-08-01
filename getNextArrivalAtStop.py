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
import onebusaway

if __name__ == "__main__":
	logger = onebusaway.getLogger()
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

	apiKey = onebusaway.getAPIKey("api.key")
	try:
		nextArrival = onebusaway.getNextArrivalInSeconds(apiKey, stopId, busId, arrivalIndex)
		logger.info("Next arrival: %s" % nextArrival)
		print nextArrival
		sys.exit(0)
	except Exception as e:
		print float("NaN")
		logger.exception(str(e) + "\n" + traceback.format_exc())
		logger.error("Next arrival: %s" % float("NaN"))
		sys.exit(1)
