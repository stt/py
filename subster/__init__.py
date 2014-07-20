from ext_srt import SrtFile
from ext_sub import SubFile
import logging

logger = logging.getLogger()


def ident_fileformat(args):
  if args.filename.endswith('.srt'):
    if args.frames > 0:
      print "Can't shift .sub with frames, don't know the framerate"
      sys.exit(1)
    return SrtFile, args.seconds

  elif args.filename.endswith('.sub'):
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
          logger.debug("at %f fps, %i sec == %i",
                      fps, int(args.seconds), delta)
          return delta

    return SubFile, find_delta(args)

  else:
    raise Exception("Unknown file format")

