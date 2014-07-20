from urllib2 import urlopen, URLError
from xml.etree import ElementTree

class VlcRemote(object):

  def __init__(self, url='http://localhost:8080/requests/status.xml'):
    self.staturl = url

  def wait_for(self, state, maxi=10):
    import time
    for i in range(maxi):
      c = urlopen(self.staturl)
      if self.is_state(ElementTree.parse(c), state):
        return True
      logger.debug('waiting for state: %s, %i', state,i)
      time.sleep(1)
    return False

  def is_state(self, x, state):
    return x.find('state').text == state

  def command(self, cmd=''):
    url = self.staturl
    if len(cmd): url += '?command=' + cmd
    try:
      return ElementTree.parse(urlopen(url))
    except URLError as e:
      raise Exception(str(e) + " VLC is not running?")

  def framerate(self):
    """
    has to do some guessing as stream info is localized
    and it's something they apparently are not going to fix
    https://trac.videolan.org/vlc/ticket/8039
    """
    x = self.command()
    for e in x.find('information').findall('category'):
      # Stream 0, localized
      if e.get('name').endswith('0'):
        for i in e.findall('info'):
          try:
            # framerate is atm the only codec info field
            # parseable as a float
            return float(i.text)
          except:
            pass

  def position(self):
    x = self.command()
    return int(x.find('time').text)

  def restart(self):
    x = self.command()
    if self.is_state(x, 'stopped'):
      raise Exception("Already stopped, can't recall position")
    ot = x.find('time').text

    # restart for vlc to reload subs
    if not self.is_state(self.command('pl_stop'), 'stopped'):
      self.wait_for('stopped')
    if not self.is_state(self.command('pl_play'), 'playing'):
      self.wait_for('playing')

    # restore pos
    c = self.command('seek&val=' + ot)
    logger.debug('seeked %s, %s', ot, c.find('state').text)
    c = self.command('pl_pause')

