#!/usr/bin/env python3
import asyncio
import websockets
import xml.etree.ElementTree as ET
from datetime import datetime
from time import sleep
import sys

tree = ET.parse(sys.argv[1])
root = tree.getroot()
xmlNS = root.tag.replace("gpx", "")
trk = root.find(xmlNS + "trk")
trkseg = trk.find(xmlNS + "trkseg")

def parseTs(inStr):
	return datetime.strptime(inStr.replace("Z","+0000"), "%Y-%m-%dT%H:%M:%S%z")

def delayTo(gpxTime):
	realSeconds = (datetime.now() - startRealTs).total_seconds()
	gpxSeconds = (gpxTime - startGpxTs).total_seconds()
	sleepVal = gpxSeconds - realSeconds
#	print(sleepVal)
	if(sleepVal <= 0):
		return
	sleep(sleepVal)

startRealTs = datetime.now()
startGpxTs =  parseTs(trkseg.find(xmlNS + "trkpt").find(xmlNS + "time").text)

async def wsLoop():
	async with websockets.connect('ws://localhost:8765') as websocket:
		await websocket.send('{"type": "debug", "msg": "Python GPX-Replay Connected"}')
		print("Connected")
		for trkpt in trkseg.findall(xmlNS + "trkpt"):
			print(trkpt.find(xmlNS + "time").text)
			gpxTime = parseTs(trkpt.find(xmlNS + "time").text)
			delayTo(gpxTime)
			print("> " + trkpt.get('lat') + ","  + trkpt.get('lon'))
			await websocket.send('{{"type": "position", "lat": {0}, "lon": {1}, "head": 0}}'.format(trkpt.get('lat'), trkpt.get('lon')))
		
asyncio.get_event_loop().run_until_complete(wsLoop())
