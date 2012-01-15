#!/usr/bin/env python
"""
structs were copied from
http://www.sweetscape.com/010editor/templates/files/ZIPTemplate.bt
"""

import mmap, os, sys
from cpystruct import *
from datetime import date, time
from struct import pack, unpack
from hashlib import md5

class ZipFile():
  def __init__(self, data):
    self.records = {}
    self.data = data
    if data.__class__.__name__ == 'mmap':
      self.cksum = md5(data.read(data.size())).hexdigest()
      data.seek(0)
      self.size = data.size()
    elif data.__class__.__name__ == 'StringIO':
      self.cksum = md5(data.getvalue()).hexdigest()
      self.size = len(data.getvalue())
    else:
      raise Exception('unknown data source: '+data.__class__.__name__)
    """
    sig = unpack('I', peek(self.data, 4))[0]
    t=peek(self.data, 26)
    print 'bah',unpack('<HHhHHIIIHH',t),md5(t).hexdigest()
    self.data.seek(0)
    """
    self.readrecords()

  def __str__(self):
    return str([ (k,len(self.records[k])) for k in self.records.keys() ])

  def addrecord(self, sig, rec):
    """ keep a dict of sig:[records] pairs """
    if self.records.has_key(sig):
      self.records[sig].append(rec)
    else:
      self.records[sig] = [rec]

  def readrecords(self):
    while 1:
      if self.data.tell() >= self.size: break  # eof
      sig = unpack('I', peek(self.data, 4))[0]
      if not sigdict.has_key(sig):
        print 'No such key',hex(sig)
        break

      rec = sigdict[sig]()
      rec.unpack(self.data) #.read(len(rec)))
      self.addrecord(sig, rec)

class COMPTYPE(CpyStruct('short c')):
  "Types of compression enum"
  val = [
    'Stored','Shrunk','Red1','Red2','Red3','Red4','Imploded','Token','Deflate',
    'Defl64','PkImpl','BZip2','LZMA','Terse','Lz77','Jpeg','WavPack','PPMd','WzAES'
  ]
  @classmethod
  def fromval(cls, d):
    return cls(c=d)

  def __str__(self):
    return self.val[self.c]

class DOSDATE(CpyStruct('ushort d')):
  @classmethod
  def fromval(cls, d):
    return cls(d = date((d>>9)+1980, (d>>5)&0xF, d&0x1F))
  def pack(self):
    return pack("H", (self.d.year - 1980) << 9 | self.d.month << 5 | self.d.day)

class DOSTIME(CpyStruct('ushort t')):
  @classmethod
  def fromval(cls, t):
    return cls(t = time(t>>11, (t>>5)&0x3F, (t&0x1F) * 2))
  def pack(self):
    return pack("H", self.t.hour << 11 | self.t.minute << 5 | (self.t.second // 2))

class ZIPFILERECORD(CpyStruct('''
  uint     sig = 0x04034b50;
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
  char     frFileName[frFileNameLength];
  char     frExtraField[frExtraFieldLength];
  char     frData[frCompressedSize];
  ''')):
  def compRate(self):
    if rec.frUncompressedSize==0:
      return 0
    else:
      return round(100-float(rec.frCompressedSize)/rec.frUncompressedSize*100)

class ZIPDIRENTRY(CpyStruct('''
  uint     sig = 0x02014b50;
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
  char     deFileName[deFileNameLength];
  char     deExtraField[deExtraFieldLength];
  char     deFileComment[deFileCommentLength];
  ''')): pass
	
class ZIPDIGITALSIG(CpyStruct('''
  uint sig = 0x05054b50;
  ushort dsDataLength;
  ushort dsData[dsDataLength];
  ''')): pass

class ZIPDATADESCR(CpyStruct('''
  uint sig = 0x08074b50;
  uint ddCRC;
  uint ddCompressedSize;
  uint ddUncompressedSize;
  ''')): pass

class ZIPENDLOCATOR(CpyStruct('''
  uint     sig = 0x06054b50;
  ushort   elDiskNumber;
  ushort   elStartDiskNumber;
  ushort   elEntriesOnDisk;
  ushort   elEntriesInDirectory;
  uint     elDirectorySize;
  uint     elDirectoryOffset;
  ushort   elCommentLength;
  char     elComment[elCommentLength];
  ''')): pass

class ZipPprint():
  " Pretty-print, generates ascii table "
  cols = (' Length ',' Method ','  Size ',' Cmpr ',
    '   Date   ','  Time  ','  CRC-32  ','Name')
  def head(self):
    return ' '.join(self.cols) +'\n'+ ' '.join(
      ['-' * len(f) for f in self.cols]
    )
  def file(self, r):
    return ' '.join(
      [str(f).rjust(len(self.cols[i])) for i,f in enumerate(r)]
      )
  def condpad(self, f, pad, txt=None):
    txt = str(f).rjust(pad) if txt is None else txt*pad
    return ' '*pad if f is None else txt
  def foot(self, tt):
    return ' '.join(
        [self.condpad(f, len(self.cols[i]), '-') for i,f in enumerate(tt)]
      ) +'\n'+' '.join(
        [self.condpad(f, len(self.cols[i])) for i,f in enumerate(tt)]
      ) + ' files'

sigdict = dict([(s.sig,s) for s in [
  ZIPFILERECORD, ZIPDIRENTRY, ZIPDIGITALSIG, ZIPDATADESCR, ZIPENDLOCATOR
  ]])

if __name__ == "__main__":
  if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
    print 'Syntax: %s filename' % sys.argv[0]
    sys.exit(-1)

  with open(sys.argv[1], 'r+b') as fh:
    totals = {'len':0,'siz':0,'cmp':[]}
    pp = ZipPprint()
    print pp.head()

    map = mmap.mmap(fh.fileno(), 0)
    zip = ZipFile(map)

    for rec in zip.records[ZIPFILERECORD.sig]:
      r = (
        rec.frUncompressedSize, rec.frCompression,
        rec.frCompressedSize, rec.compRate(),
        rec.frFileDate.d, rec.frFileTime.t,
        hex(rec.frCrc), rec.frFileName)

      print pp.file(r)

      totals['len'] += rec.frUncompressedSize
      totals['siz'] += rec.frCompressedSize
      totals['cmp'].append(rec.compRate())

    tt = (
      totals['len'], None, totals['siz'], sum(totals['cmp'])/len(totals['cmp']),
      None, None, None, len(totals['cmp'])
      )
    print pp.foot(tt)

    map.close()

