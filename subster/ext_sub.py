from ext_base import BaseFile
import re

class SubFile(BaseFile):
  __framerate = 0

  def __init__(self, sub, newlines='\n'):
    """
    @param sub str file contents
    @param newlines str optional, to retain original line endings
    """
    self.__newlines = newlines
    # filemode U means all line-endings appear as \n
    for l in self.split(sub, '\n'):
      if not len(l): break
      m = re.findall(r'\{(\d+)\}\{(\d+)\}(.*)', l)[0]
      key = tuple([int(s) for s in m[0:2]])
      if key == (1,1):
        self.__framerate = m[2]
      else:
        self.dic[key] = m[2]

  def __str__(self):
    out = []
    if self.__framerate:
      out.append("{1}{1}%s" % self.__framerate)
    for k,v in self.dic.iteritems():
      out.append("{%i}{%i}%s" % (k+(v,)))
    nl = self.__newlines
    # if file had mixed line-endings pick one
    if type(nl) == tuple: nl = nl[0]
    return nl.join(out)

  def line_at_row(self, pos):
    if self.__framerate: pos -= 1
    return super(SubFile,self).line_at_row(pos)

  def shift(self, delta, row=0):
    if self.__framerate: row -= 1
    super(SubFile,self).shift(delta, row)


