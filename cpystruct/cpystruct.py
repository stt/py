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

# struct.pack format characters prefixed by :
REFMT = r':[@!<>=]?[0-9xcbBhHiIlLqQfdspP]+'
# possible array definition or value assignment
REARR = r'(?:\[(\w+)\])?(?:\s*=\s*([0-9a-fx]+))?'
# skip C or python style comments to the end of line
RECMT = r'\s*(?:#.*|//.*)?'
# whole line with at least format/struct ref and attribute name
REPCK = r'(%s|[\s\w]+)\s+(\w+)%s%s[,;]?%s' % (REFMT, RECMT, REARR, RECMT)

fdict = {
'char':'c',
'signed char':'b', 'SBYTE':'b',
'unsigned char':'B', 'uchar':'B', 'BYTE':'B',
'_Bool':'?',
'short':'h', 'SWORD':'h',
'unsigned short':'H', 'ushort':'H', 'UWORD':'H',
'int':'i',
'unsigned int':'I', 'uint':'I', 'WORD':'I',
'long':'l',
'unsigned long':'L', 'ulong':'L', 'DWORD':'L',
'long long':'q',
'unsigned long long':'Q',
'float':'f',
'd':'double'
}

class CpySkeleton(struct.Struct):
  """ Not to be used directly, use CpyStruct() to build a class """

  def __init__(self, **kws):
    """ Takes keyword arguments to initialize attributes """
    struct.Struct.__init__(self, getattr(self, '__fstr'))
    if kws != None:
      for k in kws: setattr(self, k, kws[k])

  def pack(self):
    ret = ''
    rf = re.sub('<?','',getattr(self, '__fstr'))
    for i,(f,n,a,v) in enumerate(self.formats):
      v = getattr(self, n)
      if issubclass(v.__class__, CpySkeleton):
        ret += v.pack()
      else:
        ret += struct.pack(rf[i], v)
    #if type(self).__name__ == 'ZIPFILERECORD': print 'packed',len(ret), md5(ret).hexdigest()
    return ret

  def unpack(self, buf):
    """ buf can be a string, mmap or StringIO instance
    atm returns read binary for testing purposes """
    if buf.__class__.__name__ in ('mmap', 'StringIO'):
      buf = buf.read(len(self))

    unpacked = struct.Struct.unpack(self, buf)
 
    for i,v in enumerate(unpacked):
      f = self.formats[i][0]
 
      if type(f) == type(struct.Struct):
        if f.__dict__.has_key('fromval'):
          setattr(self, self.__slots__[i], f.fromval(v))
          #assert v == struct.unpack('H', getattr(self, self.__slots__[i]).pack() )[0]
        else:
          raise Exception('please define %s.fromval classmethod' % self)
      else:
        setattr(self, self.__slots__[i], v)
    return buf

  def __str__(self):
    ret = self.__class__.__name__+'['
    for f,n,a,v in self.formats:
      ret += '%s=%s,' % (n,getattr(self, n))
    return ret+']'


def peek(s, n):
  p = s.tell()
  r = s.read(n)
  s.seek(p)
  return r

def parseformat(fmt, callscope=None):
  fstr = ''
  for i,(f,n,a,v) in enumerate(fmt):
    if a.isdigit():
      fstr += a
    elif a != '':
      print '!!',a
      fstr += ''

    if fdict.has_key(f):
      if a.isdigit() and fdict[f] != 'c':
        raise Exception('only chararray tested atm')
      elif a.isdigit():
        fstr += 's'
      else:
        # C type
        fstr += fdict[f]
    elif f[0] == ':':
      # struct format uses colon as prefix for explicitness
      fstr += f[1:]
      fmt[i] = (f[1:],n,a,v)
    elif callscope.f_globals.has_key(f):
      # resolve references to other CpyStructs
      fmt[i] = (callscope.f_globals[f],n,a,v)
      fstr += re.sub('<?','',fmt[i][0].__fstr)
    else:
      raise Exception('Unknown format: '+f)
  return (fmt, fstr)

def CpyStruct(s, bigendian=False):
  """ Call with a string specifying
  C-like struct to get a Struct class """
  d = {}
  # f=format, n=name, a=array
  fmt = [(f.strip(),n,a,v) for f,n,a,v in re.findall(REPCK, s)]

  # peek into caller's namespace in case they refer to custom classes
  callscope = sys._getframe(1)
  try:
    (fmt,fstr) = parseformat(fmt, callscope)
  finally:
    del callscope

  #print fmt,fstr
  d['__fstr'] = ('>' if bigendian else '<') + fstr
  d['__slots__'] = [n for f,n,a,v in fmt]
  d['formats'] = fmt
  d['__len__'] = lambda s: struct.calcsize(s.__fstr)
  for f,n,a,v in fmt:
    if v != '': d[n] = int(v,0)

  return type('', (CpySkeleton,), d)

