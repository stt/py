
### Introduction

How many times a day do you pipe something to less(1) only to copypaste a path to use elsewhere?

Most graphical terminals can detect URLs and provide them as links, wouldn't it be nice if you could do that to any filesystem path in the terminal?

Here's `lgss` to try and ease some of that pain of living double life between the CLI and the GUI.

### Some example use cases:

Browse docs without cd'ing or touching the mouse

    ls -d /usr/share/doc/pyt*/examples | lgss

Collect links to a window and continue to use the terminal while utilizing the links at your leisure

    lynx -dump -listonly http://slashdot.org | grep -o "http.*" | lgss &

Get a list of open network connections for a process of your choosing without having to care about PIDs

    ps x | lgss -c 'lsof -ni -ap' -r '\d*'

Shell function to calculate line numbers for selected files in tar package (silly I know)

    function browsearc { tar ztf "$1" | lgss -fc 'tar Ozvxf '"$1"' {} | wc -l'; }
    browsearc ~/*.tar.gz

etc. ad infinitum, send in your own cool commands and improvements.

### Status:
Early development phase (YMMV)

### Features:
 * Double click or enter key prompts for opening the selected item by default with xdg-open
 * There's a button for autodetecting filesystem entries and listing some details for sorting
 * Esc closes the window
 * There are no window decorations but moving can be done by alt+mouse1 and resizing by alt+middle mouse btn
 * Custom command can be given for running the selected items, if {} is present in command it's replaced by the selected item, otherwise selected item is appended at the end of the command
 * Regex can be given to match a part of the line for passing to the open command
 * Drag and drop items into applications that support text/uri-list types (e.g. gedit)
 
### Requirements

A relatively modern version of python (currently developed and tested with 2.6) and python-gtk2 (should already be installed in most desktop environments).

### Installation

Just drop the executable into a directory in your PATH, distribution packages will be made available later.

