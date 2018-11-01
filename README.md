# pcbnewCornerRounder

This repository contains three important functions for preparing a high density board for flexpcb production:
1) VIA teardrops;  usage: import teardrop; teardrop.generate()
2) PAD teardrops;  usage: import padTeardrop; padTeardrop.generate()
3) Track rounding; usage: import roundTracks; roundTracks.rounder()

VIA teardrops script is adapted from the one here:
https://github.com/svofski/kicad-teardrops

I am most proud of the track rounding function, which iteratively places intermediate tracks at every intersection where the track angle difference is sufficiently large. 

Make sure you run DRC after running these scripts!!! You may need to edit tracks in pre to make sure there is room for the curves. 

Enjoy!
jcloiacon

Here are some pictorial examples of the scripts in progress:
