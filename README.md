# kicad-round-tracks
A plugin to round tracks in PcbNew

![Screenshot from 2019-05-10 21-15-53](https://user-images.githubusercontent.com/22014799/57551335-068a5480-7369-11e9-8e1b-37698e389c60.png)
[before](https://user-images.githubusercontent.com/22014799/57551336-08ecae80-7369-11e9-86a9-857060306bef.png)

## Installation 
Clone or unzip this repository in a KiCad plugin folder :  

- On linux :
   - `/usr/share/kicad/scripting/plugins/`
   - `~/.kicad/scripting/plugins`
   - `~/.kicad_plugins/`
- On Windows :
   - `%KICAD_INSTALL_PATH%/share/kicad/scripting/plugins`
   - `%APPDATA%/Roaming/kicad/scripting/plugins`
- On macOS :
   - `/Applications/kicad/Kicad/Contents/SharedSupport/scripting/plugins`
   - `~/Library/Application Support/kicad/scripting/plugins`
   
## Usage
In the app menu `Tools > External plugin` click `Round tracks (new file)`.  
This may take some time on large boards.  
A dialog will indicate the end of the process. From this dialog you may open the resulting file in a new windows to verify that nothing is broken and to plot your board.  
The new file has the same as the old except the extension is `.kicad_pcb-rounded`.

## History and licence

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0  
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Original copyright Miles McCoo, 2017  
extensively modified by Julian Loiacono, Oct 2018  
multi-layer support and repacked as action plugin by Antoine Pintout, May 2019
