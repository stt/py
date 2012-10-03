"""
BMS (Binary MultiEx Script) parsing rules
2012, <samuli@tuomola.net>
"""
import re, struct, sys
import ply.yacc as yacc
from bmslex import tokens, formats

class ASTNode:
    def __init__(self, operator, children=[]):
        self.operator = operator
        self.children = children
 
    def __repr__(self):
        return '<%s %s>' % (self.operator, self.children)
 
class ASTEvaluator:
    def evaluate(self, node):
        method = getattr(self,'do_%s' % node.operator, None)
        ret = 0
        if not method:
            print 'unknown', node.operator
        else:
            ret = method(*node.children)
        return ret

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

start = 'program'
 
def p_program(p):
    '''program : statement_list'''
    p[0] = ASTNode('program', p[1].children)

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | empty'''
    if len(p) == 3:
        children = [p[1]]+p[2].children
    else:
        children = []
    p[0] = ASTNode('statement_list', children)

def p_empty(p):
    '''empty :'''
    pass

def p_statement(p):
    '''statement : function
                 | cond
                 | loop'''
    p[0] = p[1]

def p_comparison(p):
    '''comparison : arg LT arg
                  | arg GT arg
                  | arg LE arg
                  | arg GE arg
                  | arg EQ arg
                  | arg NE arg'''
    p[0] = ASTNode('comparison', p[1:])

def p_cond_if(p):
    '''cond : IF comparison THEN statement_list ENDIF
            | IF comparison THEN statement_list elif_list ENDIF
            | IF comparison THEN statement_list elif_list ELSE statement_list ENDIF
            | IF comparison THEN statement_list ELSE statement_list ENDIF'''
    elf = None
    els = None
    if len(p) == 7 or len(p) == 9:
        elf = p[5].children
    if len(p) == 8:
        els = p[6]
    if len(p) == 9:
        els = p[7]

    p[0] = ASTNode(p[1].upper(), [p[2],p[4],elf,els])

def p_cond_elif(p):
    '''elif : ELIF comparison THEN statement_list'''
    p[0] = ASTNode(p[1].upper(), p[2:])

def p_cond_elif_list(p):
    '''elif_list : elif elif_list
                 | empty'''
    if len(p) == 3:
        children = [p[1]]+p[2].children
    else:
        children = []
    p[0] = ASTNode('elif_list', children)

def p_loop_for(p):
    '''loop : FOR ident ASSIGN arg TO arg statement_list NEXT ident'''
    p[0] = ASTNode(p[1].upper(), p[2:3]+p[4:5]+p[6:])


def p_function_get(p):
    '''function : GET ident ident
                | GET ident ident number'''
    num = 0 if len(p) <= 3 else p[4]
    p[0] = ASTNode(p[1].upper(), [p[2], formats[p[3].children[0].upper()], num])

def p_function_goto(p):
    '''function : GOTO arg number number
                | GOTO arg number
                | GOTO arg'''
    num = 0 if len(p) <= 3 else p[3]
    rel = 0 if len(p) <= 4 else p[4]
    p[0] = ASTNode(p[1].upper(), [p[2], num, rel])

def p_function_log(p):
    '''function : LOG arg arg arg
                | LOG arg arg arg number'''
    p[0] = ASTNode(p[1].upper(), p[2:])

def p_function_log2(p):
    '''function : LOG arg arg arg number number'''
    p[0] = ASTNode('LOG2', p[2:])

def p_function_math(p):
    '''function : MATH ident PLUS arg
                | MATH ident MINUS arg
                | MATH ident TIMES arg
                | MATH ident DIVIDE arg'''
    p[0] = ASTNode(p[1].upper(), p[2:])

def p_function_open(p):
    '''function : OPEN string string 
                | OPEN string string number'''
    fnum = 0 if len(p) <= 4 else p[4]
    p[0] = ASTNode(p[1].upper(), p[2:4] + [fnum])

def p_function_savepos(p):
    '''function : SAVEPOS ident
                | SAVEPOS ident number'''
    num = 0 if len(p) <= 3 else p[3]
    p[0] = ASTNode(p[1].upper(), [p[2],num])

def p_function_set(p):
    '''function : SET arg arg
                | SET arg arg arg'''
    #print p[:]
    p[0] = ASTNode(p[1].upper(), [p[2],None,p[3]] if len(p) == 4 else p[2:])

def p_function_strlen(t):
    'function : STRLEN ident ident'
    p[0] = ASTNode(p[1].upper(), p[2:])

def p_function_getvarchr(p):
    '''function : GETVARCHR ident ident number
                | GETVARCHR ident ident number ident'''
    fmt = 'BYTE' if len(p) <= 5 else p[5].children[0].upper()
    p[0] = ASTNode(p[1].upper(), p[2:5]+[formats[fmt]])

def p_function_putvarchr(p):
    '''function : PUTVARCHR ident number ident
                | PUTVARCHR ident number ident ident'''
    fmt = 'BYTE' if len(p) <= 5 else p[5]
    p[0] = ASTNode(p[1].upper(), p[2:5]+[formats[fmt]])

def p_function_print(p):
    'function : PRINT string'
    p[0] = ASTNode(p[1].upper(), p[2:])

def p_arg_uminus(p):
    'arg : MINUS arg %prec UMINUS'
    p[0] = -p[2]

def p_arg(p):
    '''arg : ident
           | number
           | string'''
    p[0] = p[1]

def p_arg_ident(p):
    'ident : NAME'
    p[0] = ASTNode('identifier', [p[1]])

def p_arg_number(p):
    'number : NUMBER'
    p[0] = ASTNode('integer', [p[1]])

def p_arg_string(p):
    'string : STRING'
    p[0] = ASTNode('literal', [p[1]])

#def p_error(p):
#    print p
#    raise Exception("line %i: Syntax error at %s:'%s'" % (p.lineno, p.type, p.value), p)

#p_loop_error = p_error

parser = yacc.yacc()

