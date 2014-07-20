from collections import OrderedDict

class BaseFile(object):
  dic = OrderedDict()
  __newlines = '\n'

  def __init__(self, newlines='\n'):
    """
    @param sub str file contents
    @param newlines str optional, to retain original line endings
    """
    self.__newlines = newlines

  @classmethod
  def split(cls, lines, sep):
    #logger.debug("split: found %i", lines.count(sep))
    return lines.split(sep)

  def line_at_row(self, pos):
    for i,(k,v) in enumerate(self.dic.iteritems()):
      if pos == i:
        return i,k,v

  def line_at(self, pos, previous_if_none):
    """
    Unit agnostic key comparison (could be frames, could be timedelta)
    """
    closest = None
    for i,(k,v) in enumerate(self.dic.iteritems()):
      if previous_if_none and pos >= k[0]:
        closest = i,k,v
      if pos >= k[0] and pos <= k[1]:
        return i,k,v
    return closest

  def shift(self, delta, row=0, minv=0):
    for i,(k,v) in enumerate(self.dic.items()):
      if i < row: continue
      key = (k[0]+delta, k[1]+delta)
      self.dic[key] = self.dic[k]
      del self.dic[k]
      if key[0] < minv: raise Exception("line at %i was shifted before 0", i)


