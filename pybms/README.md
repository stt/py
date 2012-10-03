
### pybms is a work in progress BMS (MexScript) parser/interpreter

Although still missing lots of syntax and features known in other implementations, it
can already run some scripts, like [this one](http://aluigi.altervista.org/papers/bms/xentax_cs/The_Lost_Vikings_DAT.bms):

    $ cd ~/games/lostvikings/
    $ du -b DATA.DAT
    1570444 DATA.DAT
    $ mkdir pybmsout
    $ cd pybmsout
    $ bms.py ../The_Lost_Vikings_DAT.bms ../DATA.DAT
    ...(debug output)
    $ for f in $(ls 00000*dat|head); do du -b $f; hexdump -C $f|head -1; done
    22018   00000002lOPEUD.dat
    00000000  80 15 01 01 01 01 01 01  01 01 01 01 01 01 01 01  |................|
    1448    00000003OipWXc.dat
    00000000  7f 16 30 ee ff 11 f0 23  f0 35 f0 f0 01 49 00 3b  |..0....#.5...I.;|
    51      00000004nU985o.dat
    00000000  2f 00 fe ff 3f 3e 3e 3e  2c 00 00 16 ff 16 16 00  |/...?>>>,.......|
    412     00000005Q37U_U.dat
    00000000  ff 02 59 01 00 f0 12 e0  02 02 1e 40 0c 12 20 bb  |..Y........@.. .|
    456     00000006F8494W.dat
    00000000  ff 02 a9 01 00 f0 05 10  0c 05 40 02 18 70 0c b9  |..........@..p..|
    492     00000007hNbszZ.dat
    00000000  ff 02 e9 01 00 f0 09 50  06 09 40 0b 0a 04 7d 0c  |.......P..@...}.|
    361     00000008Lz7zVu.dat
    00000000  ff 02 79 01 00 f0 10 c0  04 01 0c 04 10 10 d7 0c  |..y.............|
    385     00000009ICiFo6.dat
    00000000  ff 02 69 01 00 f0 0a 60  02 17 40 0c 01 23 10 93  |..i....`..@..#..|
    401     0000000aDZwAqS.dat
    00000000  ff 02 6d 01 00 f0 01 02  02 30 0c 04 02 20 7b 04  |..m......0... {.|
    296     0000000b72bLiL.dat
    00000000  ff 02 d1 01 00 f0 12 f0  19 30 0c 25 40 02 04 ae  |.........0.%@...|

    $ cat *dat | md5sum
    df0275708f2aa6a95cf71e7295c74a05  -

In comparison this is what quickbms does running same script:

    $ mkdir ../qbmsout
    $ cd ../qbmsout
    $ quickbms ../The_Lost_Vikings_DAT.bms ../DATA.DAT
      0000085c 32         00000000.dat
      0000087c 22018      00000001.dat
      00005e7e 1448       00000002.dat
      00006426 51         00000003.dat
      00006459 412        00000004.data
      ...(530 files)
      0017f689 4          00000216.dat

    Error: incomplete input file number 0, can't read 1 bytes.

    $ for f in $(ls 00000*dat|head); do du -b $f; hexdump -C $f|head -1; done
    22018   00000001.dat
    00000000  80 15 01 01 01 01 01 01  01 01 01 01 01 01 01 01  |................|
    1448    00000002.dat
    00000000  7f 16 30 ee ff 11 f0 23  f0 35 f0 f0 01 49 00 3b  |..0....#.5...I.;|
    51      00000003.dat
    00000000  2f 00 fe ff 3f 3e 3e 3e  2c 00 00 16 ff 16 16 00  |/...?>>>,.......|
    412     00000004.dat
    00000000  ff 02 59 01 00 f0 12 e0  02 02 1e 40 0c 12 20 bb  |..Y........@.. .|
    456     00000005.dat
    00000000  ff 02 a9 01 00 f0 05 10  0c 05 40 02 18 70 0c b9  |..........@..p..|
    492     00000006.dat
    00000000  ff 02 e9 01 00 f0 09 50  06 09 40 0b 0a 04 7d 0c  |.......P..@...}.|
    361     00000007.dat
    00000000  ff 02 79 01 00 f0 10 c0  04 01 0c 04 10 10 d7 0c  |..y.............|
    385     00000008.dat
    00000000  ff 02 69 01 00 f0 0a 60  02 17 40 0c 01 23 10 93  |..i....`..@..#..|
    401     00000009.dat
    00000000  ff 02 6d 01 00 f0 01 02  02 30 0c 04 02 20 7b 04  |..m......0... {.|
    296     0000000a.dat
    00000000  ff 02 d1 01 00 f0 12 f0  19 30 0c 25 40 02 04 ae  |.........0.%@...|

    $ cat *dat | md5sum
    df0275708f2aa6a95cf71e7295c74a05  -
    
(The comparison was without first and last blocks which are different due to implementation.)

Also, pybms includes a rudimentary REPL (doesn't yet support multiline statements):

    $ rlwrap python bms.py 
    > for i = 1 to 5   print "%i%"  next i
    1234> set s "asdai9psjdp"
    > strlen len s
    > print "%len%\n"
    11
    > help
    Available functions (try "HELP func"): 
    FOR GET GETVARCHR GOTO IF LOG LOG2 MATH OPEN PRINT PUTVARCHR SAVEPOS SET STRLEN
    > help GET
    Help on method do_GET in module __main__:
    
    do_GET(self, var, fmt, num) method of __main__.BMSEvaluator instance
        Get VarName Type File
    
    None
    > 
    

