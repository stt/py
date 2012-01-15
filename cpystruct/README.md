
### CreepyStruct

This is a helper class for dealing with structured binaries in python.
It's main features are mapping from C datatypes to struct.pack format, structs within structs, variable-length arrays (with a caveat that they are the last elements in a struct).
It also sees the classes defined in callers' namespace through some trickery.

### Short demo

    [stt@engn ~]$ identify test.gif 
    test.gif GIF 20x22 20x22+0+0 8-bit PseudoClass 8c 229B 0.000u 0:00.000
    
    [stt@engn ~]$ python
    Python 2.7.2 (default, Jun 29 2011, 11:10:00) 
    [GCC 4.6.1] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from cpystruct import *
    >>> class gif(CpyStruct('char sig[6]; ushort sz[2];')): pass
    ... 
    >>> print gif.__fstr
    <6s2H
    >>> g=gif()
    >>> g.unpack(open('test.gif'))
    'GIF89a\x14\x00\x16\x00'
    >>> print g
    gif[sig=GIF89a,sz=[20, 22]]
    >>> 

For more worked example, have a look at `examples/zipper.py`, here's how it compares to unzip:

    [stt@engn ~]$ unzip -v test.zip 
    Archive:  test.zip
     Length   Method    Size  Cmpr    Date    Time   CRC-32   Name
    --------  ------  ------- ---- ---------- ----- --------  ----
       32768  Defl:N       46 100% 2012-01-13 01:21 011ffca6  store.dat
           0  Stored        0   0% 2012-01-13 01:21 00000000  test.txt
    --------          -------  ---                            -------
       32768               46 100%                            2 files
    
    [stt@engn ~]$ examples/zipper.py test.zip 
     Length   Method    Size   Cmpr     Date      Time     CRC-32   Name
    -------- -------- ------- ------ ---------- -------- ---------- ----
       32768  Deflate      46  100.0 2012-01-13 01:21:10  0x11ffca6 store.dat
           0   Stored       0      0 2012-01-13 01:21:22        0x0 test.txt
    --------          ------- ------                                ----
       32768               46   50.0                                   2 files


### To-do

  * Perhaps bitfiels à la 010 editor

### Install

Typical distutils magic: `python setup.py install`

