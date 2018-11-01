

SCALE = 1000000.0	
import pcbnew
import math
from trackUtils import *

def generate():
	# generate a LUT with shape integers to a string
	#padshapes = {
	#	pcbnew.PAD_SHAPE_CIRCLE: "PAD_SHAPE_CIRCLE",
	#	pcbnew.PAD_SHAPE_OVAL: "PAD_SHAPE_OVAL",
	#	pcbnew.PAD_SHAPE_RECT: "PAD_SHAPE_RECT",
	#	pcbnew.PAD_SHAPE_TRAPEZOID: "PAD_SHAPE_TRAPEZOID"
	#}
	## new in the most recent kicad code
	#if hasattr(pcbnew, 'PAD_SHAPE_ROUNDRECT'):
	#	padshapes[pcbnew.PAD_SHAPE_ROUNDRECT] = "PAD_SHAPE_ROUNDRECT"

	board = pcbnew.GetBoard()
	tracksToAdd = set()	
	tracksToDelete = set() 

	# get all "modules", seemingly identical to footprints
	for mod in board.GetModules(): 
		#print(mod.GetReference())
		#get all pads on this module
		for pad in mod.Pads():
			#print("pad {}({}) on {}({}) at {},{} shape {} size {},{}"
			#	.format(pad.GetPadName(),
			#			pad.GetNet().GetNetname(),
			#			mod.GetReference(),
			#			mod.GetValue(),
			#			pad.GetPosition().x, pad.GetPosition().y,
			#			padshapes[pad.GetShape()],
			#			pad.GetSize().x, pad.GetSize().y
			#))

			# for simplicity, only consider the bounding box of the pad
			# future improved versions of the code should account for rotated pads and strange geometries
			boundingBox = pad.GetBoundingBox();
 			# get all the tracks in this net
			tracks = board.TracksInNet(pad.GetNet().GetNet())
			for track in tracks:
				# it seems vias are treated as tracks ???? this should take care of that
				if(track.GetLength() > 0):
					#angle = abs(normalizeAngleHalf(getTrackAngle(track) - pad.GetOrientationRadians())); 
					# keep angle [-pi/2,pi/2] because start and end are placed arbitrarily	
					# because we are using "bounding box", the orientation of the pad is already accounted for
					angle = abs(normalizeAngleHalf(getTrackAngle(track))); 
					# if this track is the same layer, and has an endpoint within the bounding box of the pad, create 3 new traces, one to either side of the bounding box and one in the center

					# reverse this track if the endpoint is on the pad 
					if(pad.HitTest(track.GetEnd())):
						reverseTrack(track)

					# if track and pad are on the same layer, intersect, and are not over stiffener material, make 3 new traces 
					if(track.GetLayer() == pad.GetLayer() and pad.HitTest(track.GetStart()) and not stiffened(board, track.GetStart())):
						#print("intersect at start ", track.GetStart())
						if (angle > math.pi/4):
							# shorten this track by the X-dimension of the pad
							sp = shortenTrack(track, boundingBox.GetHeight()*.7)
							#if the new track is length 0, slate it for deletion
							if(track.GetLength() == 0):
								tracksToDelete.add(track);
							tracksToAdd.add((cloneWxPoint(sp), pcbnew.wxPoint(boundingBox.GetRight() - track.GetWidth()/2,  boundingBox.GetCenter().y), track.GetWidth(), pad.GetLayer(), pad.GetNet()))
							tracksToAdd.add((cloneWxPoint(sp), pcbnew.wxPoint(boundingBox.GetLeft()  + track.GetWidth()/2,  boundingBox.GetCenter().y), track.GetWidth(), pad.GetLayer(), pad.GetNet()))
							tracksToAdd.add((cloneWxPoint(sp), cloneWxPoint(boundingBox.GetCenter()), track.GetWidth(), pad.GetLayer(), pad.GetNet()))
						else:
							# shorten this track by the Y-dimension of the pad
							sp = shortenTrack(track, boundingBox.GetWidth()*.7)
							#if the new track is length 0, slate it for deletion
							if(track.GetLength() == 0):
								tracksToDelete.add(track);
							tracksToAdd.add((cloneWxPoint(sp), pcbnew.wxPoint(boundingBox.GetCenter().x, boundingBox.GetTop() + track.GetWidth()/2),	track.GetWidth(), pad.GetLayer(), pad.GetNet()))
							tracksToAdd.add((cloneWxPoint(sp), pcbnew.wxPoint(boundingBox.GetCenter().x, boundingBox.GetBottom() - track.GetWidth()/2), track.GetWidth(), pad.GetLayer(), pad.GetNet()))
							tracksToAdd.add((cloneWxPoint(sp), cloneWxPoint(boundingBox.GetCenter()), track.GetWidth(), pad.GetLayer(), pad.GetNet()))



	#add all the tracks in post, so as not to cause problems with set iteration
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
