[![Build Status](https://travis-ci.org/ladybug-tools/ladybug-blender.svg?branch=master)](https://travis-ci.org/ladybug-tools/ladybug-blender)

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

# ladybug-blender

:beetle: :orange_book: Ladybug plugin for [Blender](https://www.blender.org/) using the
[Sverchok](https://github.com/nortikin/sverchok) visual scripting interface for Blender.

This package contains the interface between Blender and the Ladybug Tools core
libraries as well as the Blender Sverchok nodes for the Ladybug plugin.
Note that, in order to run the plugin, the core libraries must be installed
in a way that they can be found by Blender (see dependencies).

## Dependencies

The ladybug-blender plugin has the following dependencies:

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)

## Installation

**Warning: We're slowly releasing an incomplete, alpha state version of the Blender port of Ladybug Tools for environmental analysis. If you're really awesome, please check it out, and when you inevitably come across a bug (like, actual bugs, not ladybugs), please let us know so we can fix it. Don't say we didn't warn you.**

 1. Install Sverchok (scroll down on https://blenderbim.org/download.html - download zip and install like any other add-on)
 2. Install Ladybug Tools (scroll down on https://blenderbim.org/download.html - download zip and install like any other add-on)
 3. Want to display coloured points? Yes you do. [Install it](https://github.com/uhlik/bpy/blob/master/space_view3d_point_cloud_visualizer.py).
 4. Restart Blender

If you are upgrading, uninstall the old Ladybug Tools, and restart Blender, then
install the new version.

Things to be aware of:

 1. [Look in the console when an error occurs](https://blender.stackexchange.com/questions/23147/how-do-i-get-the-console-on-windows) for errors. If you see `WARNING: geometry <...> not yet supported in Sverchok` please ignore. However, if you see `WARNING: geometry <...> not yet supported in Blender`, please report as a high priority. You may safely ignore `TODO: interpolate this line` messages.
 2. These nodes may _not_ be the same nodes you will find in Grasshopper. Most users of the Ladybug Tools on Grasshopper are using the older Ladybug Legacy nodes. Ladybug Tools have since rewritten all their nodes from scratch, and this includes node renaming and restructuring of inputs and outputs. If you are using the Ladybug Tools [+] Plus version, then you will be familiar with these nodes. If not, be prepared for a few new things.
 3. These nodes are _only_ Ladybug for now. You will not find Honeybee, Dragonfly, or Butterfly. This is a work in progress.
 4. Use the `LB Out` node to bake Ladybug Geometry, or to extract unbaked verts, edges, and faces for further Sverchok progressing. Right now, it bakes directly to the scene collection with no garbage collection, so it can make your scene a bit messy, but was the simplest implementation to show that things work for now.
 5. Grid size will be ignored in analysis. Blender is a good mesh modeling package, and so I recommend simply using a subdivision modifier (you don't need to apply it) to set the resolution of your analysis.
 6. Too many menus? Use `Alt-Space` to search.
 7. Objects coming from the scene need to be nested to be used in Ladybug nodes. Use the List join node with the wrap option enabled as shown in [this screenshot](https://user-images.githubusercontent.com/88302/94118359-c9a4fc00-fe90-11ea-8fea-735dc9e1326d.png)

If you'd like to get a feel for it, watch [this demo video](https://www.youtube.com/watch?v=rMCuSwsF2aM).

## Developing
```bash
sudo apt install git build-essentials 2to3 imagemagick
git clone https://github.com/ladybug-tools/ladybug-blender.git
cd ladybug-blender
make dist
```