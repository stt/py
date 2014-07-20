from ext_base import BaseFile
import re
from datetime import datetime, timedelta

class SrtFile(BaseFile):
  def __init__(self, sub, newlines='\n'):
    self.__newlines = newlines
    tsf = '%H:%M:%S,%f'
    # .srt subs are separated by empty line
    for l in self.split(sub, '\n\n'):
      if not len(l): break
      # 00:00:19,969 --> 00:00:24,289
      matches = re.findall(r"((?:\d\d[:,]){3}\d\d\d)", l)
      key = tuple([datetime.strptime(m, tsf) for m in matches])
      self.dic[key] = '\n'.join(l.split('\n')[2:])

  def __str__(self):
    out = []
    tsf = '%H:%M:%S,%f'
    for i,(k,v) in enumerate(self.dic.iteritems()):
      tss = datetime.strftime(k[0], tsf)[:-3]
      tse = datetime.strftime(k[1], tsf)[:-3]
      out += [str(i+1), "%s --> %s" % (tss,tse), v, '']
    nl = self.__newlines
    # if file had mixed line-endings pick one
    if type(nl) == tuple: nl = nl[0]
    return nl.join(out)

  def shift(self, delta, row=0):
    if type(delta) == int:
      delta = timedelta(seconds=delta)
    super(SrtFile,self).shift(delta, row, datetime.strptime('0','%S'))

