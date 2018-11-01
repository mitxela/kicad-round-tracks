
SCALE = 1000000.0	
import pcbnew
import math

def test():

	# most queries start with a board
	board = pcbnew.GetBoard()
	# returns a dictionary netcode:netinfo_item
	netcodes = board.GetNetsByNetcode()


	# list off all of the nets in the board.
	for netcode, net in netcodes.items():
		#print("netcode {}, name {}".format(netcode, net.GetNetname()))
		tracks = board.TracksInNet(net.GetNet()) # get all the tracks in this net
		for track in tracks:
			try:
				print(track.GetDrill())
			except:
				print("an exception occurred")