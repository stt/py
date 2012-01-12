"""
  CreepyStruct - Convenience class for (un)packing structured binaries
  (c)2011, <samuli@tuomola.net>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re, sys, struct

# skip C or python style comments to the end of line
RECMT = r'\s*(?:#.*|//.*)?'
# struct.pack format characters prefixed by :
REFMT = r':[@!<>=]?[0-9xcbBhHiIlLqQfdspP]+'
# whole line with attribute name and possible array definition
REPCK = r'(%s|[\s\w]+)\s+(\w+)(?:\[(\w+)\])?[,;]?%s' % (REFMT, RECMT)

fdict = {
'char':'c',
'signed char':'b', 'SBYTE':'b',
'unsigned char':'B', 'BYTE':'B',
'uchar':'B',
'_Bool':'?',
'short':'h', 'SWORD':'h',
'unsigned short':'H', 'ushort':'H', 'UWORD':'H',
'int':'i',
'unsigned int':'I', 'uint':'I', 'WORD':'I',
'long':'l',
'unsigned long':'L', 'DWORD':'L',
'ulong':'L',
'long long':'q',
'unsigned long long':'Q',
'float':'f',
'd':'double'
}

def init(self, **kws):
  """ Becomes __init__ of the constructed class.
  Takes keyword arguments to initialize attributes """
  struct.Struct.__init__(self, self.__fstr)
  if kws != None:
    for k in kws: setattr(self, k, kws[k])

def unpack(self, buf):
  """ Is bound to the constructed CpyStruct.
  buf can be a buffer or mmap instance """

  if type(buf).__name__ == 'mmap':
    buf = buf.read(len(self))

  unpacked = struct.Struct.unpack(self, buf)

  for i,v in enumerate(unpacked):
    f = self.formats[i][0]

    if type(f) == type(struct.Struct):
      if f.__dict__.has_key('fromval'):
        setattr(self, self.__slots__[i], f.fromval(v))
      else:
        raise Exception('please define %s.fromval classmethod' % self)
    else:
      setattr(self, self.__slots__[i], v)

def CpyStruct(s):
  """ Call with a string specifying
  C-like struct to get a Struct class """
  d = {}
  fmt = [(f.strip(),n,a) for f,n,a in re.findall(REPCK, s)]
  fstr = ''
  callscope = sys._getframe(1)

  try:
    for i,(f,n,a) in enumerate(fmt):
      if a.isdigit():
        fstr += a

      if fdict.has_key(f):
        if a.isdigit() and fdict[f] != 'c':
          raise Exception('only chararray tested atm')
        elif a.isdigit():
          fstr += 's'
        else:
          # C type
          fstr += fdict[f]
      elif f[0] == ':':
        # struct format
        fstr += f[1:]
        fmt[i] = (f[1:],n,a)
      elif callscope.f_globals.has_key(f):
        # resolve references to other CpyStructs
        fmt[i] = (callscope.f_globals[f],n,a)
        fstr += re.sub('<?','',fmt[i][0].__fstr)
      else:
        raise Exception('Unknown format: '+f)
  finally:
    del callscope

  #print fmt,fstr
  d['__fstr'] = '<'+fstr
  d['__init__'] = init
  d['__slots__'] = [n for f,n,a in fmt]
  d['formats'] = fmt
  d['unpack'] = unpack
  d['__str__'] = lambda s: str(dict([(a,getattr(s, a)) for a in s.__slots__]))
  d['__len__'] = lambda s: struct.calcsize(s.__fstr)

  return type('', (struct.Struct,), d)

