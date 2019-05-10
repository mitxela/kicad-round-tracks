# Original example Copyright [2017] [Miles McCoo]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# extensively modified by Julian Loiacono, Oct 2018
# updated and repacked as action plugin by Antoine Pintout, May 2019

# This script will round PCBNEW traces by shortening traces at intersections, 
# and filling new traces between. This process is repeated four times.
# The resulting board is saved in a new file. 

import pcbnew
import math
import os
from subprocess import Popen
import wx
from .track_utils import *
from pprint import pprint

class flex_round( pcbnew.ActionPlugin ):
 
    def defaults( self ):

        self.name = "Round the tracks (new file)"
        self.category = "Modify PCB"
        self.description = "Will round all tracks on the PCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./round_tracks.png")

    def Run( self ):
        # save a copy of the board
        
        board = pcbnew.GetBoard()
        new_name = board.GetFileName()+"-rounded"
        board.Save(new_name)
        board = pcbnew.LoadBoard(new_name, pcbnew.IO_MGR.KICAD_SEXP)

        for i in range(4):
            self.addIntermediateTracks(board)

        board.Save(new_name)
        d = wx.MessageDialog(None, 'The new file with rounded tracks has been saved as :\n\''+new_name.split("/")[-1]+'\'\nDo you want to open it in a new window ?', 'Tracks rounding',
            wx.YES_NO | wx.NO_DEFAULT)
        result = d.ShowModal()
        if result == wx.ID_YES:
            Popen(['pcbnew', new_name])

    
    def addIntermediateTracks( self, board):

        # maximum path length is set to .2mm, and progressive shortening is 25% 
        MAXLENGTH = 0.5 # % of length of track used for the arc
        SCALING   = 0.5  # radius
        SCALE = 1000000.0  

        # returns a dictionary netcode:netinfo_item
        netcodes = board.GetNetsByNetcode()

        # list off all of the nets in the board.
        for netcode, net in netcodes.items():
            #print("netcode {}, name {}".format(netcode, net.GetNetname()))
            allTracks = board.TracksInNet(net.GetNet()) # get all the tracks in this net

            tracksPerLayer = {}
            # separate track by layer
            for t in allTracks:
                layer = t.GetLayer()
                if t.GetStart() != t.GetEnd(): # ignore vias
                    if layer not in tracksPerLayer:
                        tracksPerLayer[layer] = []
                    tracksPerLayer[layer].append(t)

            for layer in tracksPerLayer:
                tracks = tracksPerLayer[layer]

                #add all the possible intersections to a unique set, for iterating over later
                intersections = set();  
                endings = set();
                for t1 in range(len(tracks)):
                    for t2 in range(t1+1, len(tracks)):
                        #check if these two tracks share an endpoint
                        # reduce it to a 2-part tuple so there are not multiple objects of the same point in the set
                        if(tracks[t1].GetLayer() == tracks[t2].GetLayer()):
                            if(tracks[t1].IsPointOnEnds(tracks[t2].GetStart())): 
                                intersections.add((tracks[t2].GetStart().x, tracks[t2].GetStart().y))
                            if(tracks[t1].IsPointOnEnds(tracks[t2].GetEnd())):
                                intersections.add((tracks[t2].GetEnd().x, tracks[t2].GetEnd().y))

                #for each remaining intersection, shorten each track by the same amount, and place a track between.
                tracksToAdd = []
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
                    shortenLength = min(tracksHere[0].GetLength() * MAXLENGTH, SCALING*SCALE)

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
                            tracksToAdd.append((newPoint1, newPoint2, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNet()))

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
