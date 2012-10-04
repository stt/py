"""
BMS (Binary MultiEx Script) interpreter
2012, <samuli@tuomola.net>

http://aluigi.altervista.org/papers/quickbms.txt
http://wiki.xentax.com/index.php/MexScript

TODO:
- extend different BMS dialects from common baseclass?
"""
from bmslex import lexer
from bmsparse import parser, ASTEvaluator
import os, re, struct, sys, tempfile

class BMSEvaluator(ASTEvaluator):
    """Evaluates the AST provided by bmsparse

    Perhaps some operations should be callbacks to interpreter, like
    exit?"""

    def __init__(self):
        self.files = []
        self.outfileidx = 0
        self.vars = {}

    def do_statement_list(self, *stms):
        for stm in stms:
            self.evaluate(stm)
 
    do_program = do_statement_list

    def do_comparison(self, l, op, r):
        ret = False
        l = self.evaluate(l)
        r = self.evaluate(r)
        if   op == '<' : ret = l <  r
        elif op == '!=': ret = l != r
        elif op == '==': ret = l == r
        elif op == '>' : ret = l >  r
        elif op == '<=': ret = l <= r
        elif op == '>=': ret = l >= r
        return ret

    def do_integer(self, n):
        return n

    def do_identifier(self, name):
        return self.vars.get(name,0)

    def do_literal(self, lit):
        return lit

    def do_IF(self, cond, stm, elf, els):
        if self.evaluate(cond):
            self.evaluate(stm)
        else:
            done = False
            if elf:
                for e in elf:
                    if self.evaluate(e.children[0]):
                        self.evaluate(e.children[2])
                        done = True
                        break
            if not done and els:
                self.evaluate(els)

    def do_FOR(self, idx, start, stop, stm, *rest):
        start = self.evaluate(start)
        stop = self.evaluate(stop)
        idx = idx.children[0]
        #print start,stop
        #if stop > 100: stop=3

        for self.vars[idx] in range(start, stop):
            self.evaluate(stm)

    def do_GET(self, var, fmt, num):
        """Get VarName Type File"""
        fsz = struct.calcsize(fmt)
        num = self.evaluate(num)
        self.vars[var.children[0]] = struct.unpack(fmt, self.files[num].read(fsz))[0]

    def do_GETVARCHR(self, var, src, pos, fmt):
        sz = struct.calcsize(fmt)
        pos = self.evaluate(pos)
        # should do pack+unpack in desired fmt?
        self.vars[var.children[0]] = self.vars[src.children[0]][pos:pos+sz] # struct.unpack(fmt, src[pos:pos+sz])[0]

    def do_GOTO(self, pos, var, rel):
        """Get pos file [whence]"""
        pos = self.evaluate(pos)
        var = self.evaluate(var)
        self.files[var].seek(pos, rel)

    def do_LOG(self, var, pos, sz, fnum=0):
        var = self.evaluate(var)
        pos = self.evaluate(pos)
        print var,pos,sz,fnum
        # TODO: sort this out, quickbms Log only takes 3 args,
        # xentax wiki says MexScript takes 5
        if var == "":
            self.outfileidx += 1
            fh = os.fdopen(tempfile.mkstemp('.dat', '%08x' % self.outfileidx, '.')[0], 'wb')
        else:
            fh = open(var, 'wb')
        with fh:
            oldpos = self.files[fnum].tell()
            self.files[fnum].seek(pos)
            fh.write(self.files[fnum].read(sz))
            self.files[fnum].seek(oldpos)

    def do_LOG2(self, var, pos, sz, ptroffset, szoffset):
        var = self.evaluate(var)
        pos = self.evaluate(pos)
        sz = self.evaluate(sz)
        print var,pos,sz,ptroffset
        if var == "":
            self.outfileidx += 1
            fh = os.fdopen(tempfile.mkstemp('.dat', '%08x' % self.outfileidx, '.')[0], 'wb')
        else:
            fh = open(var, 'wb')
        fnum = 0
        with fh:
            oldpos = self.files[fnum].tell()
            self.files[fnum].seek(pos)
            fh.write(self.files[fnum].read(sz))
            self.files[fnum].seek(oldpos)

    def do_MATH(self, var, op, exp):
        var = var.children[0]
        exp = self.evaluate(exp)
        op = op[0]  # assignment implied
        if not var in self.vars:
            self.vars[var] = 0
        if   op == '+': self.vars[var] += exp
        elif op == '-': self.vars[var] -= exp
        elif op == '*': self.vars[var] *= exp
        elif op == '/': self.vars[var] /= exp

    def do_OPEN(self, path, filename, fnum):
        filepath = self.evaluate(path) + '/' + self.evaluate(filename)
        fnum = self.evaluate(fnum)
        try:
            self.files.insert(fnum, open(filepath))
        except AttributeError:
            self.files = [None]*fnum + [open(filepath)]
        print self.files

    def do_PRINT(self, val):
        def varref(v):
            return str(self.vars[v.group(0).replace('%','')])

        val = self.evaluate(val)
        try:
            sys.stdout.write(re.sub('(%[^%]*%)', varref, val).decode("string-escape"))
        except KeyError as e:
            print "No such variable:", e

    def do_PUTVARCHR(self, var, pos, src, fmt):
        sz = struct.calcsize(fmt)
        pos = self.evaluate(pos)
        # should do pack+unpack?
        self.vars[var.children[0]] = self.vars[src.children[0]][pos:pos+sz] # struct.unpack(fmt, src[pos:pos+sz])[0]

    def do_SAVEPOS(self, var, num):
        num = self.evaluate(num)
        self.vars[var.children[0]] = self.files[num].tell()

    def do_SET(self, var, t, val):
        # TODO: handle type
        self.vars[var.children[0]] = self.evaluate(val)

    def do_STRLEN(self, var, val):
        self.vars[var.children[0]] = len(self.evaluate(val))



class BMSInterpreter:
    def __init__(self, infile=None, datfile=None):
        self.infile = infile
        self.datfile = datfile
 
    def run(self):
        #import rpdb2; rpdb2.start_embedded_debugger('asd')
        ev = BMSEvaluator()

        if not self.infile:
            while True:
                try:
                    s = raw_input('> ')
                except (KeyboardInterrupt, EOFError):
                    break
                if not s: continue

                if s.upper().strip() == 'HELP':
                    funcs = [f.replace('do_','') for f in dir(ev) if re.match('do_[A-Z]',f)]
                    print 'Available functions (try "HELP func"): \n' + ' '.join(funcs)
                elif s.upper().startswith('HELP'):
                    fname = s.upper().replace('HELP','').strip()
                    print help( getattr(ev, 'do_%s' % fname, None) )
                else:
                    result = parser.parse(s, lexer=lexer)
                    ev.evaluate(result)

        else:
            input = open(self.infile).read()
            result = parser.parse(input, lexer=lexer)
            if self.datfile:
                ev.files.insert(0, open(self.datfile))
            ev.evaluate(result)

    #def cb(self, *kw): print kw


if __name__ == '__main__':
    app = BMSInterpreter(*sys.argv[1:])
    app.run()

