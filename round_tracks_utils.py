import pcbnew
import math
from math import pi

tolerance = 10 # in nanometres

def cloneVECTOR2I(vec):
    return pcbnew.VECTOR2I(vec.x, vec.y)

def reverseTrack(t1):
    #flip the track
    sp = cloneVECTOR2I(t1.GetStart())
    ep = cloneVECTOR2I(t1.GetEnd())
    t1.SetStart(ep)
    t1.SetEnd(sp)

# determines whether 2 points are close enough to be considered identical
def similarPoints(p1, p2):
    return (((p1.x > p2.x - tolerance) and (p1.x < p2.x + tolerance)) and ((p1.y > p2.y - tolerance) and (p1.y < p2.y + tolerance)))

# test if an intersection is within the bounds of a pad
def withinPad(pad, a, tracks):
    # Bounding box is probably sufficient, unless we had a giant L-shaped pad or something
    box = pad.GetBoundingBox()
    if not box.Contains(a):
        return False

    # If the intersection is within the pad, return true
    # But if one of the connected tracks is *entirely* within the pad, return false, since rounding won't break connectivity
    inside = True
    for t in tracks:
        if box.Contains(t.GetEnd()):
            inside = False
    return inside


# shortens a track by an arbitrary amount, maintaining the angle and the endpoint
def shortenTrack(t1, amountToShorten):
    # return true if amount to shorten exceeds length

    if amountToShorten + tolerance >= t1.GetLength():
        t1.SetStart(cloneVECTOR2I(t1.GetEnd()))
        return True

    angle = normalizeAngle(getTrackAngle(t1))
    newX = t1.GetStart().x + math.cos(angle)*amountToShorten
    newY = t1.GetStart().y + math.sin(angle)*amountToShorten
    t1.SetStart(pcbnew.VECTOR2I(int(newX), int(newY)))
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
