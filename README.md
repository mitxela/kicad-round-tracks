# kicad-round-tracks
A plugin to round tracks in PcbNew.

This plugin works by approximating arcs with many small segments, making track modifications difficult after the plugin has been run. You can choose to make the modification in place or in a duplicate file (default).

## Installation 
Clone or unzip this repository in a KiCad plugin folder :  

- On linux :
   - `/usr/share/kicad/scripting/plugins/`
   - `~/.kicad/scripting/plugins`
   - `~/.kicad_plugins/`
- On macOS :
   - `/Applications/kicad/Kicad/Contents/SharedSupport/scripting/plugins`
   - `~/Library/Application Support/kicad/scripting/plugins`
- On Windows:
   - C:\Program Files\KiCad\share\kicad\scripting\plugins\

## History
Original copyright Miles McCoo, 2017  
Extensively modified by Julian Loiacono, Oct 2018  
Multi-layer support and repacked as action plugin by Antoine Pintout, May 2019  
Updated subdivision algorithm by mitxela, Jan 2021  
