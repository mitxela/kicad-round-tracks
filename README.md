# KiCad Round Tracks
A subdivision-based track rounding plugin for KiCad.

This plugin is based on [flexRoundingSuite](https://github.com/jcloiacon/flexRoundingSuite) by Julian Loiacono and [kicad-round-tracks](https://github.com/stimulu/kicad-round-tracks) by Antoine Pintout. My contribution updates the algorithm so that subdivisions are applied equally, resulting in smoother tracks with fewer clearance errors.

For best results, use in conjunction with this [teardrop plugin](https://github.com/NilujePerchut/kicad_scripts).

![example](https://mitxela.com/img/uploads/sw/kicad/example.png)

Some more info about this plugin is [available here](https://mitxela.com/projects/melting_kicad).

## Use
The curves are generated from many small straight sections, making track modifications difficult after the plugin has been run. The plugin can run in place, but the default is to generate a new file.

After running DRC on the output, you can then go back and adjust the original file before running the plugin again.

"Radius" is the maximum radius curve that would result from a 90° bend. A smaller curve will be used if the tracks are shorter. The resulting curves will always pass through at least one point of the original tracks, so individual curves can be controlled by splitting tracks into smaller sections. If a curve has too large a radius, placing a small 45° bend will make it smaller. Similarly, if a bigger radius is needed for certain tracks, you can draw an approximate curve with free-angle tracks to achieve this.

I am in the process of updating the plugin to work with KiCad 6. A separate branch named kicad-5 marks the last version compatible with KiCad 5.

## Todo
- Limit minimum angle between tracks, to avoid unnecessary subdivisions
- Allow processing only the selection
- Rewrite all or part of this to use the native filleted tracks in KiCad 6

## Installation 
Clone or unzip this repository in a KiCad plugin folder.

- On linux :
   - `/usr/share/kicad/scripting/plugins/`
   - `~/.kicad/scripting/plugins`
   - `~/.kicad_plugins/`
- On macOS :
   - `/Applications/kicad/Kicad/Contents/SharedSupport/scripting/plugins`
   - `~/Library/Application Support/kicad/scripting/plugins`
- On Windows:
   - `C:\Program Files\KiCad\share\kicad\scripting\plugins\`
   - `%UserName%\Documents\KiCad\6.0\scripting\plugins\kicad-round-tracks`

You can list the exact paths where KiCad will search for plugins by opening the scripting console in pcbnew and running:
```
import pcbnew
print(pcbnew.GetWizardsSearchPaths())
```

Under Preferences / Preferences / PCB Editor / Action Plugins, you can choose to add a button to the toolbar for quick access to the plugin.

## History
Original copyright Miles McCoo, 2017  
Extensively modified by Julian Loiacono, Oct 2018  
Multi-layer support and repacked as action plugin by Antoine Pintout, May 2019  
Updated subdivision algorithm by mitxela, Jan 2021  
