
### CreepyStruct

This is a helper class for dealing with structured binaries in python.
It's main features are mapping from C datatypes struct.pack format and recursive structs.
(It also sees the classes defined in callers namespace through some trickery.)

### Short demo

    [stt@engn ~]$ identify test.gif 
    test.gif GIF 20x22 20x22+0+0 8-bit PseudoClass 8c 229B 0.000u 0:00.000
    
    [stt@engn ~]$ python
    Python 2.7.2 (default, Jun 29 2011, 11:10:00) 
    [GCC 4.6.1] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from cp import *
    >>> class gif(CpyStruct('char sig[3]; char ver[3]; ushort w; ushort h;')): pass
    ... 
    >>> print gif.__fstr
    <3s3sHH
    >>> g=gif()
    >>> with open('test.gif') as fh:
    ...     g.unpack(fh.read(len(g)))
    ... 
    >>> print g
    {'ver': '89a', 'sig': 'GIF', 'w': 20, 'h': 22}
    >>> 

For more worked example, have a look at `test1-zip.py`

### Install

Typical distutils magic: `python setup.py install`

