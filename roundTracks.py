# Original example Copyright [2017] [Miles McCoo]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#	 http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# extensively modified by Julian Loiacono, Oct 2018


# This script will round PCBNEW traces by shortening traces at intersections, 
# and filling new traces between. This process is repeated thrice. 

# usage: 
# import round
# round.rounder()

SCALE = 1000000.0	
import pcbnew
import math
from trackUtils import *


#the main function, adds intermediate tracks 3 times
def rounder():
	for i in range(2):
		addIntermediateTracks()


def addIntermediateTracks():

	# most queries start with a board
	board = pcbnew.GetBoard()

	# returns a dictionary netcode:netinfo_item
	netcodes = board.GetNetsByNetcode()

	# list off all of the nets in the board.
	for netcode, net in netcodes.items():
		#print("netcode {}, name {}".format(netcode, net.GetNetname()))
		tracks = board.TracksInNet(net.GetNet()) # get all the tracks in this net


		#add all the possible intersections to a unique set, for iterating over later
		intersections = set();	
		for t1 in range(len(tracks)):
			for t2 in range(t1+1, len(tracks)):
				#check if these two tracks share an endpoint
				# reduce it to a 2-part tuple so there are not multiple objects of the same point in the set
				if(tracks[t1].IsPointOnEnds(tracks[t2].GetStart())): 
					intersections.add((tracks[t2].GetStart().x, tracks[t2].GetStart().y))
				if(tracks[t1].IsPointOnEnds(tracks[t2].GetEnd())):
					intersections.add((tracks[t2].GetEnd().x, tracks[t2].GetEnd().y))

		ipsToRemove = set()

		# remove all of the intersections which occur over an ECO1 (stiffener) zone
		# we are not worried about rounding these traces. 
		for ip in intersections:
			(newX, newY) = ip;
			if stiffened(board, pcbnew.wxPoint(newX, newY)):
				ipsToRemove.add(ip)
		for ip in ipsToRemove:
			#print("removing", ip)
			intersections.remove(ip)



		#for each remaining intersection, shorten each track by the same amount, and place a track between.
		tracksToAdd = set()
		tracksToShorten = set()
		for ip in intersections:
			(newX, newY) = ip;
			intersection = pcbnew.wxPoint(newX, newY)
			tracksHere = [];
			for t1 in tracks:
				# it seems vias are treated as tracks ???? this should take care of that
				if(t1.GetLength() > 0):
					if similarPoints(t1.GetStart(), intersection):
						tracksHere.append(t1)
					if similarPoints(t1.GetEnd(), intersection):
						#flip track such that all tracks start at the IP
						reverseTrack(t1)
						tracksHere.append(t1)


			# sometimes tracksHere is empty ???
			if len(tracksHere) == 0:
				continue

			#sort tracks by length, just to find the shortest
			tracksHere.sort(key = GetTrackLength)
			#shorten all tracks by the same length, which is a function of existing shortest path length
			# maximum path length is set arbitrarily to .25mm, and progressive shortening is 35%
			shortenLength = min(tracksHere[0].GetLength() * .35, .35*SCALE)

			#sort these tracks by angle, so new tracks can be drawn between them
			tracksHere.sort(key = getTrackAngle)
			#shorten all these tracks
			for t1 in range(len(tracksHere)):
				shortenTrack(tracksHere[t1], shortenLength)
			#connect the new startpoints in a circle around the old center point
			for t1 in range(len(tracksHere)):
				#dont add 2 new tracks in the 2 track case
				if not (len(tracksHere) == 2 and t1 == 1):
					newPoint1 = cloneWxPoint(tracksHere[t1].GetStart())
					newPoint2 = cloneWxPoint(tracksHere[(t1+1)%len(tracksHere)].GetStart())
					tracksToAdd.add((newPoint1, newPoint2, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNet()))

		#add all the new tracks in post, so as not to cause problems with set iteration
		for trackpoints in tracksToAdd:
			(sp, ep, width, layer, net) = trackpoints

			track = pcbnew.TRACK(board)
			track.SetStart(sp)
			track.SetEnd(ep)
			track.SetWidth(width)
			track.SetLayer(layer)
			board.Add(track)
			track.SetNet(net)

		# the following really fucks with the vias:
		# remove all tracks of length 0
		#for track in tracks:
		#	if track.GetLength() == 0:
		#		board.Remove(track)
