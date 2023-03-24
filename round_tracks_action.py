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
import time
from .round_tracks_utils import *
from .round_tracks_gui import RoundTracksDialog

RADIUS_DEFAULT = 2.0
PASSES_DEFAULT = 3

class RoundTracks(RoundTracksDialog):

    def __init__(self, board, action):
        super(RoundTracks, self).__init__(None)
        self.board = board
        self.basefilename = os.path.splitext(board.GetFileName())[0]
        if self.basefilename.endswith('-rounded'):
            self.basefilename = self.basefilename[:-len('-rounded')]
        self.configfilepath = self.basefilename+".round-tracks-config"
        self.action = action
        self.config = {}
        self.netClassCount = 1
        self.load_config()
        if 'checkboxes' not in self.config:
            self.config['checkboxes'] = {'new_file':False, 'native':True, 'avoid_junctions':False}
        self.do_create.SetValue( self.config['checkboxes']['new_file'])
        self.use_native.SetValue( self.config['checkboxes']['native'])
        self.avoid_junctions.SetValue( self.config['checkboxes']['avoid_junctions'])

        c = self.config['classes']
        if "Default" not in c:
            self.netclasslist.AppendItem( ["Default", True, str(RADIUS_DEFAULT), str(PASSES_DEFAULT)])
        else:
            self.netclasslist.AppendItem( ["Default", c['Default']['do_round'],  str(c['Default']['scaling']),  str(c['Default']['passes'])])
        for class_id in self.board.GetNetClasses():
            classname = str(class_id)
            self.netClassCount += 1
            if classname not in c:
                self.netclasslist.AppendItem( [classname, True, str(RADIUS_DEFAULT), str(PASSES_DEFAULT)])
            else:
                self.netclasslist.AppendItem( [classname, c[classname]['do_round'],  str(c[classname]['scaling']),  str(c[classname]['passes'])])
        self.validate_all_data()


    def run( self, event ):
        start = time.time()
        self.apply.SetLabel("Working...")
        self.validate_all_data()
        self.save_config()

        self.prog = wx.ProgressDialog("Processing", "Starting...", 100, self, wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME)

        if self.do_create.IsChecked():
            new_name = self.basefilename+"-rounded.kicad_pcb"
            self.board.SetFileName(new_name)

        anySelected = False
        for t in self.board.GetTracks():
            if t.IsSelected():
                anySelected = True
                break

        avoid = self.avoid_junctions.IsChecked()
        classes = self.config['classes']
        for classname in classes:
            if classes[classname]['do_round']:
                if self.use_native.IsChecked():
                    self.addIntermediateTracks(scaling = classes[classname]['scaling'], netclass = classname, native = True, onlySelection = anySelected, avoid_junctions = avoid)
                else:
                    for i in range(classes[classname]['passes']):
                        self.addIntermediateTracks(scaling = classes[classname]['scaling'], netclass = classname, native = False, onlySelection = anySelected, avoid_junctions = avoid, msg=f", pass {i+1}")

        # Track selection apparently de-syncs if we've modified it
        if anySelected:
            for t in self.board.GetTracks():
                t.ClearSelected()

        # if m_AutoRefillZones is set, we should skip here, but PCBNEW_SETTINGS is not exposed to swig
        # ZONE_FILLER has SetProgressReporter, but PROGRESS_REPORTER is also not available, so we can't use it
        # even zone.SetNeedRefill(False) doesn't prevent it running twice
        self.prog.Pulse("Rebuilding zones...")
        wx.Yield()
        filler = pcbnew.ZONE_FILLER(self.board)
        filler.Fill(self.board.Zones())

        if bool(self.prog):
            self.prog.Destroy()
            wx.Yield()
        dt = time.time()-start
        if dt>0.1:
            wx.MessageBox("Done, took {:.3f} seconds".format(time.time()-start), parent=self)
        self.EndModal(wx.ID_OK)

    def on_close( self, event ):
        self.EndModal(wx.ID_OK)

    def on_item_editing( self, event ):
        if bool(self.netclasslist):
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
                        try:
                            new_config_line['new_file'] = params[0] == "True"
                            new_config_line['native'] = params[1] == "True"
                            new_config_line['avoid_junctions'] = params[2] == "True"
                            self.config['checkboxes'] = new_config_line
                        except Exception as e:
                            pass
        self.config['classes'] = new_config

    def save_config(self):
        classes = self.config['classes']
        try:
            with open(self.configfilepath, "w") as configfile:
                for classname in classes:
                    configfile.write('%s\t%s\t%s\t%s\n' % (classname, str(classes[classname]['do_round']), str(classes[classname]['scaling']), str(classes[classname]['passes'])))
                configfile.write('%s\t%s\t%s\n' % (str(self.config['checkboxes']['new_file']), str(self.config['checkboxes']['native']), str(self.config['checkboxes']['avoid_junctions'])))
        except PermissionError:
            pass

    def validate_all_data (self):
        new_config = {}
        for i in range(self.netClassCount):
            for j in range(5):
                if j == 2:
                    # param should be between 0 and 1
                    try:
                        tested_val = float(self.netclasslist.GetTextValue(i, j))
                        if tested_val < 0:
                            self.netclasslist.SetTextValue(str(RADIUS_DEFAULT), i, j)
                    except Exception as e:
                        self.netclasslist.SetTextValue(str(RADIUS_DEFAULT), i, j)
                if j == 3:
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
        self.config['checkboxes'] = {'new_file':self.do_create.IsChecked(), 'native':self.use_native.IsChecked(), 'avoid_junctions':self.avoid_junctions.IsChecked()}

    def addIntermediateTracks( self, scaling = RADIUS_DEFAULT, netclass = None, native = False, onlySelection = False, avoid_junctions = False, msg=""):

        # A 90 degree bend will get a maximum radius of this amount
        RADIUS = pcbnew.FromMM(scaling /(math.sin( math.pi/4 )+1))

        board = self.board
        netcodes = board.GetNetsByNetcode()
        allTracks = board.GetTracks()
        allPads = board.GetPads()

        tracksToRemove = []

        for netcode, net in netcodes.items():

            if netclass is not None and netclass == net.GetNetClassName():

                # BOARD::TracksInNet casts everything to a PCB_TRACK, even PCB_VIA and PCB_ARC
                # tracksInNet = board.TracksInNet(net.GetNetCode())
                tracksInNet = []
                viasInNet = []
                for t in allTracks:
                    if t.GetNetCode() == netcode and (not onlySelection or t.IsSelected()):
                        if t.GetClass() == 'PCB_VIA':
                            viasInNet.append(t)
                        else:
                            tracksInNet.append(t)

                tracksPerLayer = {}
                # separate track by layer
                for t in tracksInNet:
                    layer = t.GetLayer()
                    if layer not in tracksPerLayer:
                        tracksPerLayer[layer] = []
                    tracksPerLayer[layer].append(t)

                for v in viasInNet:
                    # a buried/blind via will report only layers affected
                    # a through via will return all 32 possible layers
                    layerSet = v.GetLayerSet().CuStack()
                    for layer in tracksPerLayer:
                        if layer in layerSet:
                            tracksPerLayer[layer].append(v)

                # TH pads cover all layers
                # SMD/CONN pads only touch F.Cu and B.Cu (layers 0 and 31)
                # Due to glitch in KiCad, pad.GetLayer() always returns 0. Need to use GetLayerSet().Contains() to actually check

                padsInNet = []
                FCuPadsInNet = []
                BCuPadsInNet = []

                for p in allPads:
                    if p.GetNetCode() == netcode and (not onlySelection or t.IsSelected()):
                        attr = p.GetAttribute()
                        if attr == pcbnew.PAD_ATTRIB_NPTH or attr == pcbnew.PAD_ATTRIB_PTH:
                            padsInNet.append(p)
                        else:
                            if p.GetLayerSet().Contains(31):
                                BCuPadsInNet.append(p)
                            else:
                                FCuPadsInNet.append(p)

                for layer in tracksPerLayer:
                    tracks = tracksPerLayer[layer]

                    # add all the possible intersections to a unique set, for iterating over later
                    intersections = set();  
                    for t1 in range(len(tracks)):
                        for t2 in range(t1+1, len(tracks)):
                            # check if these two tracks share an endpoint
                            # reduce it to a 2-part tuple so there are not multiple objects of the same point in the set
                            if(tracks[t1].IsPointOnEnds(tracks[t2].GetStart())): 
                                intersections.add((tracks[t2].GetStart().x, tracks[t2].GetStart().y))
                            if(tracks[t1].IsPointOnEnds(tracks[t2].GetEnd())):
                                intersections.add((tracks[t2].GetEnd().x, tracks[t2].GetEnd().y))

                    # for each remaining intersection, shorten each track by the same amount, and place a track between.
                    tracksToAdd = []
                    arcsToAdd = []
                    trackLengths = {}
                    for ip in intersections:
                        (newX, newY) = ip;
                        intersection = pcbnew.VECTOR2I(newX, newY)
                        tracksHere = [];
                        for t1 in tracks:
                            if similarPoints(t1.GetStart(), intersection):
                                tracksHere.append(t1)
                            elif similarPoints(t1.GetEnd(), intersection):
                                # flip track such that all tracks start at the IP
                                reverseTrack(t1)
                                tracksHere.append(t1)

                        if len(tracksHere) == 0 or (avoid_junctions and len(tracksHere)>2):
                            continue

                        # if there are any arcs or vias present, skip the intersection entirely
                        skip = False
                        for t1 in tracksHere:
                            if t1.GetClass() != 'PCB_TRACK':
                                skip = True
                                break

                        # If the intersection is within a pad, but none of the tracks end within the pad, skip
                        for p in padsInNet:
                            if withinPad(p, intersection, tracksHere):
                                skip = True
                                break

                        if layer == 0:
                            for p in FCuPadsInNet:
                                if withinPad(p, intersection, tracksHere):
                                    skip = True
                                    break
                        elif layer == 31:
                            for p in BCuPadsInNet:
                                if withinPad(p, intersection, tracksHere):
                                    skip = True
                                    break

                        if skip:
                            continue

                        shortest=-1
                        for t1 in tracksHere:
                            if id(t1) not in trackLengths:
                                trackLengths[id(t1)] = t1.GetLength()
                            if shortest == -1 or trackLengths[id(t1)]<trackLengths[id(shortest)]:
                                shortest = t1

                        #sort these tracks by angle, so new tracks can be drawn between them
                        tracksHere.sort(key = getTrackAngle)

                        if native:
                            halfTrackAngle = {} # cache this, because after shortening the length may end up zero
                            for t1 in range(len(tracksHere)):
                                halfTrackAngle[t1] = getTrackAngleDifference( tracksHere[t1], tracksHere[(t1+1)%len(tracksHere)] )/2

                            for t1 in range(len(tracksHere)):
                                f = math.sin( halfTrackAngle[t1] )+1
                                if shortenTrack(tracksHere[t1], min(trackLengths[id(shortest)] *0.5, RADIUS *f )):
                                    tracksToRemove.append(tracksHere[t1])

                            for t1 in range(len(tracksHere)):
                                if not (len(tracksHere) == 2 and t1 == 1):
                                    theta = math.pi/2 - halfTrackAngle[t1]
                                    f = 1/(2*math.cos(theta) +2)

                                    sp = cloneVECTOR2I(tracksHere[t1].GetStart())
                                    ep = cloneVECTOR2I(tracksHere[(t1+1)%len(tracksHere)].GetStart())
                                    if halfTrackAngle[t1]> math.pi/2 -0.001:
                                        tracksToAdd.append((sp, ep, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNetCode()))
                                    else:
                                        mp = pcbnew.VECTOR2I(int(newX*(1-f*2)+sp.x*f+ep.x*f), int(newY*(1-f*2)+sp.y*f+ep.y*f))
                                        arcsToAdd.append((sp, ep, mp, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNetCode()))

                        else:
                            #shorten all these tracks
                            for t1 in range(len(tracksHere)):
                                theta = math.pi/2 - getTrackAngleDifference( tracksHere[t1], tracksHere[(t1+1)%len(tracksHere)] )/2
                                f = 1/(2*math.cos(theta) +2)
                                shortenTrack(tracksHere[t1], min(trackLengths[id(shortest)] * f, RADIUS ))

                            #connect the new startpoints in a circle around the old center point
                            for t1 in range(len(tracksHere)):
                                #dont add 2 new tracks in the 2 track case
                                if not (len(tracksHere) == 2 and t1 == 1):
                                    newPoint1 = cloneVECTOR2I(tracksHere[t1].GetStart())
                                    newPoint2 = cloneVECTOR2I(tracksHere[(t1+1)%len(tracksHere)].GetStart())
                                    tracksToAdd.append((newPoint1, newPoint2, tracksHere[t1].GetWidth(), tracksHere[t1].GetLayer(), tracksHere[t1].GetNetCode()))

                    #add all the new tracks in post, so as not to cause problems with set iteration
                    for trackpoints in tracksToAdd:
                        (sp, ep, width, layer, net) = trackpoints

                        track = pcbnew.PCB_TRACK(board)
                        track.SetStart(sp)
                        track.SetEnd(ep)
                        track.SetWidth(width)
                        track.SetLayer(layer)
                        board.Add(track)
                        track.SetNetCode(net)
                        if onlySelection:
                            track.SetSelected()

                    for trackpoints in arcsToAdd:
                        (sp, ep, mp, width, layer, net) = trackpoints

                        arc = pcbnew.PCB_ARC(board)
                        arc.SetStart(sp)
                        arc.SetMid(mp)
                        arc.SetEnd(ep)
                        arc.SetWidth(width)
                        arc.SetLayer(layer)
                        board.Add(arc)
                        arc.SetNetCode(net)
                        if onlySelection:
                            arc.SetSelected()

            self.prog.Pulse(f"Netclass: {netclass}, {netcode+1} of {len(netcodes)}{msg}")

        for t in tracksToRemove:
            board.Remove(t)

class ActionRoundTracks( pcbnew.ActionPlugin ):
 
    def defaults( self ):
        self.name = "Round tracks"
        self.category = "Modify PCB"
        self.description = "Subdivision-based track rounding"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./round_tracks.png")

    def Run( self ):
        if pcbnew.GetBuildVersion()=='(7.0.0)':
            wx.MessageBox("Sorry, this plugin is not compatible with KiCad 7.0.0\n\nIt should work with 7.0.1, if that's not out yet you can try KiCad nightly.")
            return
        board = pcbnew.GetBoard()
        rt = RoundTracks(board, self)
        rt.ShowModal()
        rt.Destroy()

        # this shouldn't be needed, but without it, arcs are sometimes not acknowledged as tangential until they've been moved or the file re-opened
        # as of kicad 6.0.0, doing pcbnew.Refresh() here causes the arcs to glitch out and create duplicate shapes that can't be deleted
        pcbnew.UpdateUserInterface()
