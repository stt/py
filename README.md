
### Introduction

How many times a day do you pipe something to less(1) only to copypaste a path to use elsewhere?

Most graphical terminals can detect URLs and provide them as links, wouldn't it be nice if you could do that to any filesystem path in the terminal? How about selecting sets of those paths and dragging them into a new directory or into a zip file?

Here's `legs` to try and ease some of that pain of living double life between the CLI and the GUI.

### Some example use cases:

Browse docs without cd'ing or touching the mouse
`ls -d /usr/share/doc/*/examples | legs`

Collect links to a window and continue to use the terminal while utilizing the links at your leisure
`lynx -dump -listonly http://slashdot.org | grep -o "http.*" | legs &`

Get a list of open network connections for a process of your choosing without having to care about PIDs
`ps x | legs -c 'lsof -ni -ap' -r '\d*'`

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

