# some utility functions for dealing with tracks
# Julian Loiacono 2018

import pcbnew
import math

def reverseTrack(t1):
	#flip the track
	sp = cloneWxPoint(t1.GetStart())
	ep = cloneWxPoint(t1.GetEnd())
	t1.SetStart(ep)
	t1.SetEnd(sp)

#determine if there is a stiffener zone on Eco1 which this point lies above
def stiffened(board, point):
	# remove all of the intersections which occur over an ECO1 (stiffener) zone
	# we are not worried about rounding these traces. 
	for zone in board.Zones():
		if "Eco1" in board.GetLayerName(zone.GetLayer()):
			if zone.HitTestInsideZone(point):
				return True
	return False;
	

# normalizes any angle to between pi/2 and -pi/2
def normalizeAngleHalf(inputAngle):
	#normalize the angle to [-pi, pi)
	while(inputAngle >= math.pi/2):
		inputAngle -= math.pi;
	while(inputAngle < -math.pi/2):
		inputAngle += math.pi;

	return inputAngle;

#determines whether 2 points are close enough to be considered identical
def similarPoints(p1, p2):
	#return (((p1.x > p2.x - 10) and (p1.x < p2.x + 10)) and ((p1.y > p2.y - 10) and (p1.y < p2.y + 10)));
	return ((p1.x == p2.x) and (p1.y == p2.y));

# the math for shorten track
def projectInward(t1, amountToShorten):

	#reduce to 0 length if amount to shorten exceeds length

	# find the angle of this track
	angle = normalizeAngle(getTrackAngle(t1));
	#print("angle of track: ", angle*180/math.pi)
		#print("Shortening from Start")	
	if amountToShorten >= t1.GetLength():
		newX = t1.GetEnd().x;
		newY = t1.GetEnd().y;

	else:
		#project amountToShorten as the new startpoint 
		newX = t1.GetStart().x + math.cos(angle)*amountToShorten;
		newY = t1.GetStart().y + math.sin(angle)*amountToShorten;

	return pcbnew.wxPoint(newX, newY)

# shortens a track by an arbitrary amount, maintaning the angle and the endpoint
def shortenTrack(t1, amountToShorten):
	newPoint = projectInward(t1, amountToShorten);

	#always shorten from start
	t1.SetStart(newPoint)	

	return newPoint

# normalizes any angle to between pi and -pi
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


#finds the angle difference between t1 and t2 at intersection ip
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
	
#utility function for sorting tracks by length
def GetTrackLength(t1):
	return t1.GetLength()

#utility function to return a new point object with the same coordinates
def cloneWxPoint(wxp):
	return pcbnew.wxPoint(wxp.x, wxp.y)