    usage: run.py [-h] [-r ROW] [-P] [-R] [-L] [-f FRAMES | -s SECONDS | -d]
                  [filename]

    Tweaks subtitle timings and helps with VLC. Supports .sub and .srt files. VLC
    related functions requires VLC web interface to be enabled.

    optional arguments:
      -h, --help            show this help message and exit
      -r ROW, --row ROW     Number of subtitle to apply the shift on

    vlc:
      -P                    Display subtitle position of VLC
      -R                    Restart VLC while maintaining position
      -L                    Seek position of last subtitle in VLC

    timing related options:
      -f FRAMES, --frames FRAMES
                            Number of frames to shift
      -s SECONDS, --seconds SECONDS
                            Number of seconds to shift, can be negative
      -d, --display         Display the subtitle specified by -r and quit
      filename

