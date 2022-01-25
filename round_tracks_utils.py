import pcbnew
import math
from math import pi

tolerance = 10 # in nanometres

def cloneWxPoint(wxp):
	return pcbnew.wxPoint(wxp.x, wxp.y)

def reverseTrack(t1):
	#flip the track
	sp = cloneWxPoint(t1.GetStart())
	ep = cloneWxPoint(t1.GetEnd())
	t1.SetStart(ep)
	t1.SetEnd(sp)

def RebuildAllZones(pcb):
	filler = pcbnew.ZONE_FILLER(pcb)
	filler.Fill(pcb.Zones())

# determines whether 2 points are close enough to be considered identical
def similarPoints(p1, p2):
	return (((p1.x > p2.x - tolerance) and (p1.x < p2.x + tolerance)) and ((p1.y > p2.y - tolerance) and (p1.y < p2.y + tolerance)))

# shortens a track by an arbitrary amount, maintaining the angle and the endpoint
def shortenTrack(t1, amountToShorten):
	# return true if amount to shorten exceeds length

	if amountToShorten + tolerance >= t1.GetLength():
		t1.SetStart(cloneWxPoint(t1.GetEnd()))
		return True

	angle = normalizeAngle(getTrackAngle(t1))
	newX = t1.GetStart().x + math.cos(angle)*amountToShorten
	newY = t1.GetStart().y + math.sin(angle)*amountToShorten
	t1.SetStart(pcbnew.wxPoint(newX, newY))
	return False

# normalizes any angle to [-pi, pi)
def normalizeAngle(inputAngle):
	while(inputAngle >= pi):
		inputAngle -= 2*pi;
	while(inputAngle < -pi):
		inputAngle += 2*pi;

	return inputAngle;

# gets the angle of a track (unnormalized)
def getTrackAngle(t1):
	#use atan2 so the correct quadrant is returned
	return math.atan2((t1.GetEnd().y - t1.GetStart().y), (t1.GetEnd().x - t1.GetStart().x))

# Get angle between tracks, assumes both start at their intersection
def getTrackAngleDifference(t1,t2):
	a1 = math.atan2(t1.GetEnd().y - t1.GetStart().y, t1.GetEnd().x - t1.GetStart().x)
	a2 = math.atan2(t2.GetEnd().y - t2.GetStart().y, t2.GetEnd().x - t2.GetStart().x)
	t = a1-a2
	if t > pi:
		t = 2*pi-t
	if t < -pi:
		t = -2*pi-t
	return abs(t)
