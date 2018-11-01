#!/usr/bin/env python

# Teardrops for PCBNEW by svofski, 2014
# http://sensi.org/~svo

# modified slightly by Julian Loiacono 2018

from pcbnew import *
from math import *
from trackUtils import *

ToUnits=ToMM
FromUnits=FromMM


def generate():
	board = GetBoard()
	vias = set()
	
	count = 0;

	# this dumbass way to get all the vias
	# wish I could get them by net like tracks
	for item in board.GetTracks():
		if type(item) == VIA:
			vias.add(item)

	# returns a dictionary netcode:netinfo_item
	netcodes = board.GetNetsByNetcode()

	tracksToAdd = set()	
	tracksToDelete = set() 
	# list off all of the nets in the board.
	for netcode, net in netcodes.items():
		#print("netcode {}, name {}".format(netcode, net.GetNetname()))
		tracks = board.TracksInNet(net.GetNet()) # get all the tracks in this net
		for track in tracks:
			# it seems vias are treated as tracks ???? this should take care of that
			if(track.GetLength() > 0):
				for via in vias:
					if track.IsPointOnEnds(via.GetPosition()):
						#print("track here")
						# ensure that start is at the via/pad end
						if similarPoints(track.GetEnd(), via.GetPosition()):
							reverseTrack(track)

						# get angle of track
						angle = getTrackAngle(track)

						# 2 pependicular angles to find the end points on via side
						angleB = angle + pi/2;
						angleC = angle - pi/2;

						#shorten this track from start by via width*2
						sp = shortenTrack(track, via.GetWidth())

						#if the new track is length 0, slate it for deletion
						if(track.GetLength() == 0):
							tracksToDelete.add(track);

						#determine the radius on which the 2 new endpoints reside
						radius = via.GetWidth() / 2  - track.GetWidth() / 2
					
						# via side points
						pointB = via.GetPosition() + wxPoint(int(math.cos(angleB) * radius), int(math.sin(angleB) * radius))
						pointC = via.GetPosition() + wxPoint(int(math.cos(angleC) * radius), int(math.sin(angleC) * radius))

						# create the teardrop
						tracksToAdd.add((cloneWxPoint(sp), pointB, track.GetWidth(), track.GetLayer(), track.GetNet()))
						tracksToAdd.add((cloneWxPoint(sp), pointC, track.GetWidth(), track.GetLayer(), track.GetNet()))
						tracksToAdd.add((cloneWxPoint(sp), via.GetPosition(), track.GetWidth(), track.GetLayer(), track.GetNet()))
						
						# add extra lines if via/track ratio is high
						if via.GetWidth()/track.GetWidth() > 5.5:
							radius /= 2
							pointB = via[0] + wxPoint(int(vecB[0] * radius), int(vecB[1] * radius))
							pointC = via[0] + wxPoint(int(vecC[0] * radius), int(vecC[1] * radius))
							tracksToAdd.add((cloneWxPoint(sp), pointB, track.GetWidth(), track.GetLayer(), track.GetNet()))
							tracksToAdd.add((cloneWxPoint(sp), pointC, track.GetWidth(), track.GetLayer(), track.GetNet()))


						count = count + 1


	#add all the tracks in post, so as not to cause an infinite loop
	for trackpoints in tracksToAdd:
		(sp, ep, width, layer, net) = trackpoints

		track = pcbnew.TRACK(board)
		track.SetStart(sp)
		track.SetEnd(ep)
		track.SetWidth(width)
		track.SetLayer(layer)
		board.Add(track)
		track.SetNet(net)

	for track in tracksToDelete:
		board.Remove(track)

	print "Teardrops generated for %d vias. To undo, select all drawings in copper layers and delete block" % count
