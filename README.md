# flexRoundingSuite
## Introduction

This repository contains three important functions for preparing a high density board for flexpcb production:
1) **VIA teardrops**;  usage: import teardrop; teardrop.generate()
2) **PAD teardrops**;  usage: import padTeardrop; padTeardrop.generate()
3) **Track rounding**; usage: import roundTracks; roundTracks.rounder()

VIA teardrops script is adapted from the one here:
https://github.com/svofski/kicad-teardrops

I am most proud of the track rounding function, which iteratively places intermediate tracks at every intersection where the track angle difference is sufficiently large. 

This script may also be useful in RF applications ???

Make sure you run DRC after running these scripts!!! You may need to edit tracks in pre to make sure there is room for the curves. 

Enjoy!
jcloiacon

## Examples:

### LED Footprints

#### LED footprints before any script:

![LED footprints before any script](https://imgur.com/brsHhDN.png)

#### LED footprints after pad teardrops:

![LED footprints after pad teardrops](https://imgur.com/rDwSO6a.png)

#### LED footprints after pad teardrops and rounding:

![LED footprints after pad teardrops and rounding](https://imgur.com/GCDScS4.png)

### VIAs

#### VIAs before any script

![VIAs before any script](https://imgur.com/S8dzbRL.png)

#### VIAs after teardrops and padTeardrops

![VIAs after teardrops and padTeardrops](https://imgur.com/QMF7foi.png)

#### VIAs after teardrops and padTeardrops and rounding

![VIAs after teardrops and padTeardrops and rounding](https://imgur.com/etUYDx7.png)
