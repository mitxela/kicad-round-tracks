# Copyright [2017] [Miles McCoo]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# this file is some basic examples of doing scripting in pcbnew's python
# interface.

SCALE = 1000000.0	
import pcbnew
import math

def similarPoints(p1, p2):
	return (((p1.x > p2.x - 10) and (p1.x < p2.x + 10)) and ((p1.y > p2.y - 10) and (p1.y < p2.y + 10)));

def projectInward(t1, fromStart, amountToShorten):
	# find the angle of this track
	angle = normalizeAngle(getTrackAngle(t1));
	#print("angle of track: ", angle*180/math.pi)
	#if we need to shorten from the end
	if(fromStart):
		#print("Shortening from Start")
		#otherwise, project amountToShorten as the new endpoint 
		newX = t1.GetStart().x + math.cos(angle)*amountToShorten;
		newY = t1.GetStart().y + math.sin(angle)*amountToShorten;
	else:
		#print("Shortening from End")
		#then project length - amountToShorten as the new endpoint 
		newX = t1.GetEnd().x - math.cos(angle)*amountToShorten;
		newY = t1.GetEnd().y - math.sin(angle)*amountToShorten;

	return pcbnew.wxPoint(newX, newY)

def shortenTrack(t1, fromStart, amountToShorten):
	newPoint = projectInward(t1, fromStart, amountToShorten);

	#if we need to shorten from the end
	if(fromStart):
		t1.SetStart(newPoint)
	else:
		t1.SetEnd(newPoint)

	return newPoint

def normalizeAngle(inputAngle):
	#normalize the angle to [-pi, pi)
	while(inputAngle >= math.pi):
		inputAngle -= 2*math.pi;
	while(inputAngle < -math.pi):
		inputAngle += 2*math.pi;

	return inputAngle;

#gets the angle of a track (unnormalized)
#startReference of True means take angle from startpoint
#otherwise take angle from endpoint (difference of pi)
def getTrackAngle(t1):
	#use atan2 so the correct quadrant is returned
	return math.atan2((t1.GetEnd().y - t1.GetStart().y), (t1.GetEnd().x - t1.GetStart().x));


def angleBetween(t1, t2, ip):

	#find the angle betwenn 2 tracks
	#where start and end point are arranged arbitrarily
	angle1 = getTrackAngle(t1)
	angle2 = getTrackAngle(t2)
	if(similarPoints(t1.GetEnd(), ip)):
		angle1 += math.pi;
	if(similarPoints(t2.GetEnd(), ip)):
		angle2 += math.pi;

	return abs(normalizeAngle(angle1-angle2))

def rounder():

	shortenLength = .75*SCALE # start with intermediate tracks of .75mm length
	for i in range(3):
		addIntermediateTracks(shortenLength)
		shortenLength*=.25

def GetTrackLength(t1):
	return t1.GetLength()

def cloneWxPoint(wxp):
	return pcbnew.wxPoint(wxp.x, wxp.y)

def addIntermediateTracks(trackLength):

	# most queries start with a board
	board = pcbnew.GetBoard()

	######
	# NETS
	######

	# want to know all of the nets in your board?
	# nets can be looked up in two ways:
	#  by name
	#  by netcode - a unique integer identifier for your net.

	# returns a dictionary netcode:netinfo_item
	netcodes = board.GetNetsByNetcode()

	# list off all of the nets in the board.
	for netcode, net in netcodes.items():
		#print("netcode {}, name {}".format(netcode, net.GetNetname()))
		tracks = board.TracksInNet(net.GetNet()) # get all the tracks in this net


		intersections = set();	
		#count up the amount of intersections at each start and endpoint
		for t1 in range(len(tracks)):
			for t2 in range(t1+1, len(tracks)):
				#check if these two tracks share an endpoint
				if(tracks[t1].GetLayer() == tracks[t2].GetLayer()):
					if (similarPoints(tracks[t1].GetStart(), tracks[t2].GetStart())):
						intersections.add((tracks[t1].GetStart().x, tracks[t1].GetStart().y))
					if (similarPoints(tracks[t1].GetEnd(),   tracks[t2].GetStart())):
						intersections.add((tracks[t1].GetEnd().x, tracks[t1].GetEnd().y))
					if (similarPoints(tracks[t1].GetStart(), tracks[t2].GetEnd()  )):
						intersections.add((tracks[t1].GetStart().x, tracks[t1].GetStart().y))
					if (similarPoints(tracks[t1].GetEnd(),   tracks[t2].GetEnd()  )):
						intersections.add((tracks[t1].GetEnd().x, tracks[t1].GetEnd().y))


		tracksToAdd = set()
		tracksToShorten = set()
		#for each intersection, shorten each track by the same amount, and place a track between.
		for ip in intersections:
			(newX, newY) = ip;
			intersection = pcbnew.wxPoint(newX, newY)
			#print("intersection at ", intersection)
			tracksHere = [];
			for t1 in tracks:
				if similarPoints(t1.GetStart(), intersection):
					tracksHere.append(t1)
				if similarPoints(t1.GetEnd(), intersection):
					#flip track such that all tracks start at the IP
					sp = cloneWxPoint(t1.GetStart())
					ep = cloneWxPoint(t1.GetEnd())
					t1.SetStart(ep)
					t1.SetEnd(sp)
					tracksHere.append(t1)

			#print(len(tracksHere))
			tracksHere.sort(key = GetTrackLength)
			#shorten all tracks by the same length, which is a function of existing path lengths
			shortenLength = min(tracksHere[0].GetLength() * .3, .4*SCALE)
			#print(shortenLength)
			#sort these tracks by angle
			tracksHere.sort(key = getTrackAngle)
			#shorten all these tracks, and make a new track between it and the next
			for t1 in range(len(tracksHere)):
				shortenTrack(tracksHere[t1], True, shortenLength)

			#connect the new startpoints
			for t1 in range(len(tracksHere)):
				#dont add 2 new tracks in the 2 track case
				if not (len(tracksHere) == 2 and t1 == 1):
					newPoint1 = cloneWxPoint(tracksHere[t1].GetStart())
					newPoint2 = cloneWxPoint(tracksHere[(t1+1)%len(tracksHere)].GetStart())
					tracksToAdd.add((newPoint1, newPoint2, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNet()))

		#add and shorten all the tracks in post, so as not to cause an infinite loop
		for trackpoints in tracksToAdd:
			(sp, endp, width, layer, net) = trackpoints
			track = pcbnew.TRACK(board)
			track.SetStart(sp)
			track.SetEnd(endp)
			track.SetWidth(width)
			track.SetLayer(layer)
			board.Add(track)
			track.SetNet(net)


	#raw_input("Press Enter to continue...")
	# here's another way of doing the same thing.
	#print("here's the other way to do it")
	#nets = board.GetNetsByName()
	#for netname, net in nets.items():
	#    print("method2 netcode {}, name{}".format(net.GetNet(), netname))


	# maybe you just want a single net
	# the find method returns an iterator to all matching nets.
	# the value of an iterator is a tuple: name, netinfo
	#neti = nets.find("/clk")
	#if (neti != nets.end()):
	#  clknet = neti.value()[1]
	#  clkclass = clknet.GetNetClass()
	#
	#  print("net {} is on netclass {}".format(clknet.GetNetname(),
	#                                          clkclass))
	  
	  ########
	  # tracks
	  ########

	  # clk net was defined above as was SCALE      
	#else:
	#  print("you don't have a net call clk. change the find('clk') to look for a net you do have")

	  
	#####################
	# physical dimensions
	#####################

	# coordinate space of kicad_pcb is in mm. At the beginning of
	# https://en.wikibooks.org/wiki/Kicad/file_formats#Board_File_Format
	# "All physical units are in mils (1/1000th inch) unless otherwise noted."
	# then later in historical notes, it says,
	# As of 2013, the PCBnew application creates ".kicad_pcb" files that begin with
	# "(kicad_pcb (version 3)". All distances are in millimeters. 

	# the internal coorinate space of pcbnew is 10E-6 mm. (a millionth of a mm)
	# the coordinate 121550000 corresponds to 121.550000 


	#boardbbox = board.ComputeBoundingBox()
	#boardxl = boardbbox.GetX()
	#boardyl = boardbbox.GetY()
	#boardwidth = boardbbox.GetWidth()
	#boardheight = boardbbox.GetHeight()

	#print("this board is at position {},{} {} wide and {} high".format(boardxl,
	#                                                                   boardyl,
	#                                                                   boardwidth,
	#                                                                   boardheight))

	# each of your placed modules can be found with its reference name
	# the module connection points are pad, of course.


	#padshapes = {
	##    pcbnew.PAD_SHAPE_CIRCLE:  "PAD_SHAPE_CIRCLE",
	#    pcbnew.PAD_SHAPE_OVAL:    "PAD_SHAPE_OVAL",
	#    pcbnew.PAD_SHAPE_RECT:    "PAD_SHAPE_RECT",
	#    pcbnew.PAD_SHAPE_TRAPEZOID: "PAD_SHAPE_TRAPEZOID"    
	#}
	# new in the most recent kicad code
	#if hasattr(pcbnew, 'PAD_SHAPE_ROUNDRECT'):
	#    padshapes[pcbnew.PAD_SHAPE_ROUNDRECT] = "PAD_SHAPE_ROUNDRECT",


	#modref = "U1"
	#mod = board.FindModuleByReference(modref)
	#if (mod == None):
	##    print("you don't have a module named U1 which this script assumes is there.")
	#   print("search for U1 in the script and change it to something you do have")
	    
	#for pad in mod.Pads():
	#    print("pad {}({}) on {}({}) at {},{} shape {} size {},{}"
	#          .format(pad.GetPadName(),
	#                  pad.GetNet().GetNetname(),
	#                  mod.GetReference(),
	#                  mod.GetValue(),
	##                  pad.GetPosition().x, pad.GetPosition().y,
	#                 padshapes[pad.GetShape()],
	#                 pad.GetSize().x, pad.GetSize().y
	#         ))
	#eturn;



	    
	 
