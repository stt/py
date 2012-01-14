import unittest, StringIO
from base64 import b64decode
from examples.zipper import *

class Test1(unittest.TestCase):
  def setUp(self):
    """ test data created by dd if=/dev/zero of=store.dat count=64;
    touch test.txt; zip test.zip store.dat test.txt; base64 test.zip """
    self.zip = ZipFile(StringIO.StringIO(b64decode("""
      UEsDBBQAAAAIAKUKLUCm/B8BLgAAAACAAAAJABwAc3RvcmUuZGF0VVQJAAPlag9P5WoPT3V4CwAB
      BOgDAAAEZAAAAO3BAQEAAACAkP6v7ggKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhQ
      SwMECgAAAAAAqwotQAAAAAAAAAAAAAAAAAgAHAB0ZXN0LnR4dFVUCQAD8WoPT/FqD091eAsAAQTo
      AwAABGQAAABQSwECHgMUAAAACAClCi1ApvwfAS4AAAAAgAAACQAYAAAAAAAAAAAApIEAAAAAc3Rv
      cmUuZGF0VVQFAAPlag9PdXgLAAEE6AMAAARkAAAAUEsBAh4DCgAAAAAAqwotQAAAAAAAAAAAAAAA
      AAgAGAAAAAAAAAAAAKSBcQAAAHRlc3QudHh0VVQFAAPxag9PdXgLAAEE6AMAAARkAAAAUEsFBgAA
      AAACAAIAnQAAALMAAAAAAA==
      """)))

  def test_pack(self):
    buf = ''
    for s in sigdict:
      if not self.zip.records.has_key(s): continue
      for b in self.zip.records[s]:
        buf += b.pack()
    print 'Testing packing of %i records' % len(self.zip.records)
    self.assertTrue(self.zip.cksum, md5(buf).hexdigest())

  def test_unpack(self):
    files = []
    for d in self.zip.records[ZIPFILERECORD.sig]:
      files.append(d.frFileName)
    print 'Testing unpacking of',files
    self.assertTrue('store.dat' in files and 'test.txt' in files)


if __name__ == "__main__":
  unittest.main()

