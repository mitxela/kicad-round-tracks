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
import wx
from subprocess import Popen
from .round_tracks_utils import *
from .round_tracks_gui import RoundTracksDialog

RADIUS_DEFAULT = 0.5
PASSES_DEFAULT = 3

class RoundTracks(RoundTracksDialog):

    def __init__(self, board, action):
        super(RoundTracks, self).__init__(None)
        self.board = board
        self.configfilepath = ".".join(self.board.GetFileName().split('.')[:-1])+".round-tracks-config"
        self.action = action
        self.config = {}
        self.netClassCount = 1
        self.load_config()
        c = self.config['classes']
        if "Default" not in c:
            self.netclasslist.AppendItem( ["Default", True, str(RADIUS_DEFAULT), str(PASSES_DEFAULT)])
        else:
            self.netclasslist.AppendItem( ["Default", c['Default']['do_round'],  str(c['Default']['scaling']),  str(c['Default']['passes'])])
        for class_id in self.board.GetNetClasses().NetClasses():
            classname = str(class_id)
            self.netClassCount += 1
            if classname not in c:
                self.netclasslist.AppendItem( [classname, True, str(RADIUS_DEFAULT), str(PASSES_DEFAULT)])
            else:
                self.netclasslist.AppendItem( [classname, c[classname]['do_round'],  str(c[classname]['scaling']),  str(c[classname]['passes'])])
        self.validate_all_data()


    def run( self, event ):
        # save a copy of the board

        self.validate_all_data()
        self.save_config()
        self.Destroy()
        if self.do_create.IsChecked() :
            new_name = self.board.GetFileName()+"-rounded"
            self.board.Save(new_name)
            self.board = pcbnew.LoadBoard(new_name, pcbnew.IO_MGR.KICAD_SEXP)

        classes = self.config['classes']
        for classname in classes:
            if classes[classname]['do_round']:
                for i in range(classes[classname]['passes']):
                    self.addIntermediateTracks(self.board, scaling = classes[classname]['scaling'], netclass = classname)

        RebuildAllZones(self.board)

        if self.do_create.IsChecked():
            self.board.Save(new_name)
        if self.do_create.IsChecked() and self.do_open.IsChecked():
            Popen(['pcbnew', new_name])

    def on_toggle_create( self, event ):
        self.do_open.Enable(self.do_create.IsChecked())

    def on_close( self, event ):
        self.Destroy()

    def on_item_editing( self, event ):
        self.validate_all_data()

    def load_config(self):
        new_config = {}
        if os.path.isfile(self.configfilepath):
            with open(self.configfilepath, "r") as configfile:
                for line in configfile.readlines():
                    params = line[:-1].split("\t")
                    new_config_line = {}
                    try:
                        new_config_line['do_round'] = params[1] == "True"
                        new_config_line['scaling'] = float(params[2])
                        new_config_line['passes'] = int(params[3])
                        new_config[params[0]] = new_config_line
                    except Exception as e:
                        pass
        self.config['classes'] = new_config

    def save_config(self):
        classes = self.config['classes']
        with open(self.configfilepath, "w") as configfile:
            for classname in classes:
                configfile.write('%s\t%s\t%s\t%s\n' % (classname, str(classes[classname]['do_round']), str(classes[classname]['scaling']), str(classes[classname]['passes'])))
        pass

    def validate_all_data (self):
        new_config = {}
        for i in range(self.netClassCount):
            for j in range(5):
                if j is 2:
                    # param should be between 0 and 1
                    try:
                        tested_val = float(self.netclasslist.GetTextValue(i, j))
                        if tested_val < 0:
                            self.netclasslist.SetTextValue(str(RADIUS_DEFAULT), i, j)
                    except Exception as e:
                        self.netclasslist.SetTextValue(str(RADIUS_DEFAULT), i, j)
                if j is 3:
                    # param should be between int 1 and 5
                    try:
                        tested_val = int(self.netclasslist.GetTextValue(i, j))
                        if tested_val < 0 or tested_val > 5:
                            self.netclasslist.SetTextValue(str(PASSES_DEFAULT), i, j)
                    except Exception as e:
                        self.netclasslist.SetTextValue(str(PASSES_DEFAULT), i, j)
            new_config[self.netclasslist.GetTextValue(i, 0)] = {
                'do_round' : self.netclasslist.GetToggleValue(i, 1),
                'scaling' : float(self.netclasslist.GetTextValue(i, 2)),
                'passes' : int(self.netclasslist.GetTextValue(i, 3))
            }
        self.config['classes'] = new_config
   
    def addIntermediateTracks( self, board, scaling = RADIUS_DEFAULT, netclass = None):

        # A 90 degree bend will get a maximum radius of this amount
        RADIUS = pcbnew.FromMM(scaling /1.707)

        # returns a dictionary netcode:netinfo_item
        netcodes = board.GetNetsByNetcode()

        # list off all of the nets in the board.
        for netcode, net in netcodes.items():

            # print(net.GetName(), net.GetClassName())

            if netclass is not None and netclass == net.GetClassName():

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
                    trackLengths = {}
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

                        shortest=-1
                        for t1 in tracksHere:
                            if id(t1) not in trackLengths:
                                trackLengths[id(t1)] = t1.GetLength()
                            if shortest == -1 or trackLengths[id(t1)]<trackLengths[id(shortest)]:
                                shortest = t1

                        #sort these tracks by angle, so new tracks can be drawn between them
                        tracksHere.sort(key = getTrackAngle)
                        #shorten all these tracks
                        for t1 in range(len(tracksHere)):
                            theta = math.pi/2 - getTrackAngleDifference( tracksHere[t1], tracksHere[(t1+1)%len(tracksHere)] )/2
                            f = 1/(2*math.cos(theta) +2)
                            shortenTrack(tracksHere[t1], min(trackLengths[id(shortest)] * f, RADIUS))

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


class ActionRoundTracks( pcbnew.ActionPlugin ):
 
    def defaults( self ):
        self.name = "Round the tracks (new file)"
        self.category = "Modify PCB"
        self.description = "Will round all tracks on the PCB"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./round_tracks.png")

    def Run( self ):
        board = pcbnew.GetBoard()
        rt = RoundTracks(board, self)
        rt.ShowModal()

