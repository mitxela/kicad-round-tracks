
<div align = center>

# KiCad Round Tracks

*A subdivision / native arc-based track rounding plugin for* ***KiCad***

<br>

![Showcase]

---

</div>

## Goal

The goal is to algorithmically melt a **PCB** design, <br>
smoothing all tracks in a predictable manner. 

## Teardrop Plugin

For best results possible, consider using it<br>
in conjunction with this **[Teardrop Plugin]**.

#### Note

Currently, the teardrop plugin has not <br>
been ported fully ported to KiCad 6.

I've fixed the behavior with native arcs <br>
on **[My Fork][Mitxela Teardrop]** of it which should hopefully <br>
be merged in soon.

I have written extensively about my KiCad <br>
melting experiments **[Here][Melting A]** and over **[Here][Melting B]**.

## Use

***For the KiCad 5 compatible version, please use the [kicad-5] branch.***

The intended use is to have:

- A source PCB file, which is easy to edit
- A rendered output file, generated by this plugin

After running **DRC** on the output, you <br>
can then go back and adjust the original <br>
file before running the plugin again.

#### Selection

If you select part of the board, only <br>
the selected tracks will get melted.

*If nothing is selected, the whole file will be processed.*

#### `Create A New File`

Does not immediately write anything to disk, <br>
it merely appends `-rounded` to the filename <br>
so that the next time you hit <kbd> Save </kbd> it won't <br>
overwrite the original.

#### `Use Native`

If this option is ticked, the rounded sections are <br>
implemented using KiCad 6's native PCB arcs.

These _can_ be adjusted after the script has run, <br>
but I still recommend keeping the unrounded <br>
source PCB file.

I have tried hard to ensure that the output <br>
PCB is the same, regardless of if native or <br>
subdivision-based arcs are used.

If the option is ticked, the number <br>
of passes parameter is ignored.

Otherwise, the curves are generated<br>
from many small straight sections.

`2` *or* `3` *passes is usually sufficient.*

There is no loading bar, so if the design is <br>
complicated the interface might freeze for <br>
a few seconds while it runs.

You can set the number of passes to be 1, <br>
and run the plugin repeatedly, and it will <br>
give the same results, while letting you <br>
inspect the intermediate stages.


#### `Radius`

This option is the maximum radius <br>
a curve will have on a `90°` bend.

A smaller curve will be used if the <br>
tracks are shorter, or if the angle <br>
between them is sharper.

The resulting curves will always pass through <br>
at least one point of the original tracks.

Thus individual curves can be controlled by <br>
splitting tracks into smaller sections.

If a curve has too large a radius, placing <br>
a small `45°` bend will make it smaller.

Similarly, if a bigger radius is needed for <br>
certain tracks, you can draw an approximate <br>
curve with free-angle tracks to achieve this.

## Installation
Now available from the Plugin and Content manager.

For manual install, clone or unzip this repository in a KiCad plugin folder. You can list the exact paths where KiCad will search for plugins by opening the scripting console in pcbnew and running:
```
import pcbnew
print(pcbnew.GetWizardsSearchPaths())
```

Under Preferences / Preferences / PCB Editor / Action Plugins, you can choose whether to have a button on the toolbar for quick access to the plugin.

## History
This plugin is based on [flexRoundingSuite] by Julian Loiacono and [kicad-round-tracks][KiCad Round Tracks] by Antoine Pintout. My contribution updated the algorithm so that subdivisions are applied equally, resulting in smoother tracks with fewer clearance errors.

Original copyright Miles McCoo, 2017  
Extensively modified by Julian Loiacono, Oct 2018  
Multi-layer support and repacked as action plugin by Antoine Pintout, May 2019  
Updated subdivision algorithm by mitxela, Jan 2021  


<!----------------------------------------------------------------------------->

[Showcase]: https://mitxela.com/img/uploads/sw/kicad/example.png

[Mitxela Teardrop]: https://github.com/mitxela/kicad-teardrops/tree/mitxela/V6.0
[Teardrop Plugin]: https://github.com/NilujePerchut/kicad_scripts

[Melting B]: https://mitxela.com/projects/melting_kicad_2
[Melting A]: https://mitxela.com/projects/melting_kicad

[FlexRoundingSuite]: https://github.com/jcloiacon/flexRoundingSuite
[KiCad Round Tracks]: https://github.com/stimulu/kicad-round-tracks

[kicad-5]: https://github.com/mitxela/kicad-round-tracks/tree/kicad-5
