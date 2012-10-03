"""
BMS (Binary MultiEx Script) lexer
2012, <samuli@tuomola.net>
"""
import re, struct, sys
import ply.lex as lex

reserved = [
  'PUTVARCHR', 'LOG', 'FOR', 'NEXT', 'TO', 'PRINT', 'MATH', 'DO',
  'STRING', 'GET', 'FINDLOC', 'SAVEPOS', 'IDSTRING', 'GETDSTRING', 'CLOG', 'GOTO',
  'WHILE', 'CLEANEXIT', 'IMPTYPE', 'SET', 'OPEN', 'GETVARCHR', 'STRLEN',
  'IF','THEN','ELIF','ELSE','ENDIF'
  ]
tokens = [
  'ID', 'NAME','NUMBER','COMMENT',
  'PLUS','MINUS','TIMES','DIVIDE','ASSIGN',
  'LT','GT','LE','GE','EQ','NE',
  'MOD','OR','AND','NOT','XOR','LSHIFT','RSHIFT'
  ] + reserved

formats = {
  'STRING':'s','BYTE':'b','SHORT':'h','THREEBYTE':'3b','LONG':'i',	#long=4B
  'LONGLONG':'q','FLOAT':'f','DOUBLE':'d','LONGDOUBLE':'d'
  }

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = t.value.upper() if t.value.upper() in reserved else 'NAME'
    #t.value = (t.value, '') #symbol_lookup(t.value))
    return t

t_PLUS    = r'\+[=]?'
t_MINUS   = r'-[=]?'
t_TIMES   = r'\*[=]?'
t_DIVIDE  = r'/[=]?'
t_ASSIGN  = r'='
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_MOD     = r'%'
t_OR      = r'\|'
t_AND     = r'&'
t_NOT     = r'~'
t_XOR     = r'\^'
t_LSHIFT  = r'<<'
t_RSHIFT  = r'>>'
t_LT      = r'<'
t_GT      = r'>'
t_LE      = r'<='
t_GE      = r'>='
t_EQ      = r'=='
t_NE      = r'!='


def t_COMMENT(t):
    r'(\#|//|/\*).*'
    pass

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value.replace('"','')
    return t

t_ignore = "; \t\r"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    # could raise ValueError
    print("Illegal character at line %i: '%s'" % (t.lexer.lineno, t.value[0]))
    t.lexer.skip(1)

lexer = lex.lex(reflags = re.IGNORECASE)
