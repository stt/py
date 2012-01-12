#!/usr/bin/env python
"""
struct naming was copied from
http://www.sweetscape.com/010editor/templates/files/ZIPTemplate.bt
"""

import mmap, os, sys
from cpystruct import *
from binascii import hexlify
from datetime import date, time
from struct import unpack

class COMPTYPE(CpyStruct('short c')):
  val = ['Stored','Shrunk','Red1','Red1','Red1','Red1','Imploded','Token',
  'Deflate','Defl64','PkImpl','BZip2','LZMA','Terse','Lz77','Jpeg','WavPack',
  'PPMd','WzAES']

  @classmethod
  def fromval(cls, d):
    return cls(c=d)

  def __str__(self):
    return self.val[self.c]

class DOSDATE(CpyStruct('ushort d')):
  @classmethod
  def fromval(cls, d):
    return cls(d = date((d>>9)+1980, (d>>5)&0xF, d&0x1F))

class DOSTIME(CpyStruct('ushort t')):
  @classmethod
  def fromval(cls, t):
    return cls(t = time(t>>11, (t>>5)&0x3F, (t&0x1F) * 2))

class ZIPFILERECORD(CpyStruct('''
  ushort   frVersion;
  ushort   frFlags;
  COMPTYPE frCompression;
  DOSTIME  frFileTime;
  DOSDATE  frFileDate;
  uint     frCrc;
  uint     frCompressedSize;
  uint     frUncompressedSize;
  ushort   frFileNameLength;
  ushort   frExtraFieldLength;
  ''')):
  def unpack(self, dat):
    super(ZIPFILERECORD, self).unpack(dat)
    l = self.frFileNameLength
    self.frFileName = unpack('%is' % l, dat.read(l))
    l = self.frExtraFieldLength
    self.frExtraField = unpack('%is' % l, dat.read(l))
    l = self.frCompressedSize 
    self.frData = unpack('%is' % l, dat.read(l))
  def compRate(self):
    if rec.frUncompressedSize==0:
      return 0
    else:
      return round(100-float(rec.frCompressedSize)/rec.frUncompressedSize*100)

class ZIPDIRENTRY(CpyStruct('''
  ushort   deVersionMadeBy;
  ushort   deVersionToExtract;
  ushort   deFlags;
  COMPTYPE deCompression;
  DOSTIME  deFileTime;
  DOSDATE  deFileDate;
  uint     deCrc;
  uint     deCompressedSize;
  uint     deUncompressedSize;
  ushort   deFileNameLength;
  ushort   deExtraFieldLength;
  ushort   deFileCommentLength;
  ushort   deDiskNumberStart;
  ushort   deInternalAttributes;
  uint     deExternalAttributes;
  uint     deHeaderOffset;
  ''')):
  def unpack(self, dat):
    super(ZIPDIRENTRY, self).unpack(dat)
    l = self.deFileNameLength
    self.deFileName = unpack('%is' % l, dat.read(l))
    l = self.deExtraFieldLength
    self.deExtraField = unpack('%is' % l, dat.read(l))
    l = self.deFileCommentLength
    self.deFileComment = unpack('%is' % l, dat.read(l))
	
class ZIPDIGITALSIG(CpyStruct('ushort dsDataLength;')):
  def unpack(self, dat):
    super(ZIPDIGITALSIG, self).unpack(dat)
    if self.dsDataLength > 0:
      (d,) = unpack('H', dat.read(self.dsDataLength))

class ZIPDATADESCR(CpyStruct('''
  uint ddCRC ;
  uint ddCompressedSize;
  uint ddUncompressedSize;
  ''')): pass

class ZIPENDLOCATOR(CpyStruct('''
  ushort   elDiskNumber;
  ushort   elStartDiskNumber;
  ushort   elEntriesOnDisk;
  ushort   elEntriesInDirectory;
  uint     elDirectorySize;
  uint     elDirectoryOffset;
  ushort   elCommentLength;
  ''')):
  def unpack(self, dat):
    super(ZIPENDLOCATOR, self).unpack(dat)
    if self.elCommentLength > 0:
      (d,) = unpack('H', dat.read(self.elCommentLength))


sigdict = {
0x04034b50:ZIPFILERECORD,
0x02014b50:ZIPDIRENTRY,
0x05054b50:ZIPDIGITALSIG,
0x08074b50:ZIPDATADESCR,
0x06054b50:ZIPENDLOCATOR
}


if __name__ == "__main__":
  if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
    print 'Syntax: %s filename' % sys.argv[0]
    sys.exit(-1)

  cols = (
    ' Length ',' Method ','  Size ','Cmpr',
    '   Date   ','  Time  ','  CRC-32  ','Name'
    )
  print '  '.join(cols)
  print '  '.join(['-' * len(f) for f in cols])

  with open(sys.argv[1], 'r+b') as fh:

    map = mmap.mmap(fh.fileno(), 0)
    t = map.read(4)
    totals = {'len':0,'siz':0,'cmp':[]}

    while t != None:
      sig = unpack('I', t)[0]
      if not sigdict.has_key(sig): print 'No such key',hex(sig)

      rec = sigdict[sig]()
      #print rec.fstr,rec.__slots__,rec().unpack_from(map, map.tell())
      rec.unpack(map)
      #print rec,len(rec)

      if sig == 0x04034b50:
        r = (
          rec.frUncompressedSize, rec.frCompression,
          rec.frCompressedSize, rec.compRate(),
          rec.frFileDate.d, rec.frFileTime.t,
          hex(rec.frCrc), rec.frFileName[0])
        print '  '.join(
          [str(f).rjust(len(cols[i])) for i,f in enumerate(r)]
          )

        totals['len'] += rec.frUncompressedSize
        totals['siz'] += rec.frCompressedSize
        totals['cmp'].append(rec.compRate())

      if map.size() == map.tell(): break
      t = map.read(4)

    tt = (
      totals['len'], None, totals['siz'], sum(totals['cmp'])/len(totals['cmp']),
      None, None, None, len(totals['cmp'])
      )
    print '  '.join(
      [(' ' if f is None else '-') * len(cols[i]) for i,f in enumerate(tt)]
      )
    print '  '.join(
      [' '*len(cols[i]) if f is None else str(f).rjust(len(cols[i])) for i,f in enumerate(tt)]
      ),'files'

    map.close()

