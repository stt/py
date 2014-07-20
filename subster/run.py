#!/usr/bin/env python
"""
(c)2014, <samuli@tuomola.net>
"""

import sys, re
from os.path import isfile
from datetime import datetime, timedelta

from vlc import VlcRemote
from ext_srt import SrtFile
from ext_sub import SubFile
import logging

logger = logging.getLogger()


if __name__ == '__main__':
  logging.basicConfig()
  logger.setLevel(logging.DEBUG)
  import argparse
  from os.path import basename

  def positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
      raise argparse.ArgumentTypeError("Not a positive integer: %s" % value)
    # users: one-based, code: zero-based
    return ivalue - 1

  parser = argparse.ArgumentParser(description="""
  Tweaks subtitle timings and helps with VLC.
  Supports .sub and .srt files.
  VLC related functions requires VLC web interface to be enabled.
  """)

  parser.add_argument('-r', '--row', dest='row', default=0, type=positive_int,
                     help='Number of subtitle to apply the shift on')

  group_vlc = parser.add_argument_group('vlc')
  group_vlc.add_argument('-P', dest='vlc_position', action='store_true',
                    help='Display subtitle position of VLC')
  group_vlc.add_argument('-R', dest='vlc_restart', action='store_true',
                    help='Restart VLC while maintaining position')
  group_vlc.add_argument('-L', dest='vlc_last', action='store_true',
                    help='Seek position of last subtitle in VLC')

  group = parser.add_argument_group('timing related options')
  groupx = group.add_mutually_exclusive_group()#required=True)
  groupx.add_argument('-f', '--frames', dest='frames', default=0, type=int,
                    help='Number of frames to shift')
  groupx.add_argument('-s', '--seconds', dest='seconds', default=0, type=int,
                    help='Number of seconds to shift, can be negative')
  groupx.add_argument('-d', '--display', dest='display', action='store_true',
                    help='Display the subtitle specified by -r and quit')

  group.add_argument('filename', nargs='?')

  args = parser.parse_args()

  if args.vlc_restart and args.filename is None:
    VlcRemote().restart()
    sys.exit(1)

  if not args.filename or not isfile(args.filename):
    #parser.print_help()
    parser.error("Not a file")

  delta = 0

  if args.filename.endswith('.srt'):
    if args.frames > 0:
      print "Can't shift .sub with frames, don't know the framerate"
      sys.exit(1)
    cls = SrtFile
    delta = args.seconds

  elif args.filename.endswith('.sub'):
    cls = SubFile

    def find_delta(args):
      if not args.seconds: return args.frames
      with open(args.filename) as fh:
        m = re.match(r'(?:\{1\}){2}\s*(\d+.\d+)', fh.readline())
        if not m:
          print "Framerate not in the file, can't shift by seconds"
          sys.exit(1)
        else:
          fps = float(m.group(1))
          delta = int(args.seconds * fps)
          logger.debug("at %f fps, %i sec == %i", fps, int(args.seconds), delta)
          return delta

    delta = find_delta(args)

  else:
    print "Unknown file format"
    sys.exit(1)

  with open(args.filename, 'r+U') as fh:
    contents = fh.read()
    f = cls(contents, fh.newlines)
    logger.debug("read %i lines", len(cls.dic))

    if args.display:
      (row,times,line) = f.line_at_row(args.row)
      print times,line

    if args.vlc_position:
      r = VlcRemote()
      try:
        fps = r.framerate()
        pos = timedelta(seconds=r.position())
        logger.debug('Find line at %i*%f=%i', pos.seconds,fps,pos.seconds*fps)
        (row,times,line) = f.line_at(pos.seconds * fps, True)
        print "row",row,times, line
      except Exception as e:
        print e

    if delta == 0:
      sys.exit(1)

    f.shift(delta, args.row)
    fh.seek(0)
    fh.write(str(f))
    fh.truncate()
    logger.debug('Shifted by %i, file written', delta)

  if args.vlc_restart:
    VlcRemote().restart()

