# -*- encoding: utf-8 -*-


# TODO: eliminate boring string output

# lang in          out
#----- ----------- -----------------------------------------
# js   []+[]       ""
# js   []+{}       [object Object]
# js   {}+[]       0
# php  ~NaN        ��� apparently string bitwise not? why?!
# js   global      {}
# php  print str;  happily prints any non-reserved bareword
# py   {type}      set([<type 'type'>])
# rb   [print]     [nil]
# rb   [end]       [end]
# rb   [break]     [break]
# js   [,]         []
# ruby [1e999][1e-999] Infinity
# php  ~"0"        � unary operators cast numeric strings to ints... except ~
# ruby print //    (?-mix:) WTF?

"""
   3062 1.11e-16-1             php -1                     pl -1                     py -0.9999999999999999    rb -0.9999999999999999
   3286 04294967297            php 34                     py                        rb foo.rb:1: Invalid octal digit
 24228 print"-"               php -1                     py -                      rb -
"""

"""
Classic type hierarchy

Null/Nil/None
Bool
Int
    MIN_INT
    MAX_INT
    ...arbitrary precision...
Float
    EPSILON
    MIN_DBL
    MAX_DBL
Tuple
Array
List
Hashtable/Dictionary/Map
Binary
Function
Class
Module
Exception

Operators
    Unary
    Binary
    Ternary

    Equality/Ordinal
    Bitwise
    Arithmetic
    String =~

"""

import os, re

class Lang:
    name = 'FIXME'
    err_substrs = ['Error']
    def run(code): raise Exception('override me!')
    @classmethod
    def is_err(cls, msg):
        for e in cls.err_substrs:
            if e in msg:
                return True
        return False
    def is_nop(self, msg): return msg == ''

class PHP(Lang):
    name = 'php'
    err_substrs = [
        'Parse error',
        'Use of undefined',
        'Unexpected character',
        'PHP Warning:',
        'PHP Notice:',
        'PHP Fatal error:',
    ]
    @staticmethod
    def run(code):
        with open('foo.php', 'w') as f:
            f.write("<?php\necho " + code + ';')
        with os.popen('php -q foo.php 2>&1 | grep -v "PHP Startup:"') as p:
            output = p.readline()
        return output.strip()

class Ruby(Lang):
    name = 'rb'
    err_substrs = [
        'foo.rb:1',
        'syntax error',
        'unterminated regex',
        'uninitialized constant',
        'undefined local',
        'undefined method',
        'no .<digit> floating literal anymore',
        'formal argument cannot be a constant',
        'wrong number of arguments',
    ]
    @staticmethod
    def run(code):
        with open('foo.rb', 'w') as f:
            f.write('print ' + code)
        with os.popen('timeout 1 ruby foo.rb 2>&1') as p:
            output = p.readline().strip()
        return output.strip()

class Perl(Lang):
    name = 'pl'
    err_substrs = [
        'syntax error',
        'Search pattern not terminated',
        'Final $ should be',
        'found where operator expected',
        'Unmatched right square bracket',
        "Can't modify",
        'Missing right curly',
        'Unmatched )',
        'No comma allowed',
        'is no longer supported',
    ]
    @staticmethod
    def run(code):
        with open('foo.pl', 'w') as f:
            f.write('print ' + code)
        with os.popen('timeout 1 perl foo.pl 2>&1') as p:
            output = p.readline()
        return output.strip()

class Javascript(Lang):
    name = 'js'
    @staticmethod
    def run(code):
        with os.popen('timeout 1 js > foo.js.out', 'w') as p:
            p.write(code + '\n')
        with open('foo.js.out') as out:
            output = out.readline()[2:].strip() # toss "> " prompt prefix
        return output.strip()
    @staticmethod
    def is_nop(msg):
        return msg == '' or msg == '>' or msg == '...'

class Types:
    UNKNOWN     = 0 # didn't even try
    UNDECIDED   = 1 # tried, couldn't tell
    ERR_CRASH   = 2 # crash program
    ERR_COMPILE = 3
    ERR_RUN     = 4
    TYPE        = 5
    NULL        = 6
    BOOL        = 7
    INT         = 8
    FLOAT       = 9
    COMPLEX     = 10
    SEQUENCE    = 11
    SET         = 12
    FUNC        = 13
    CLASS       = 14
    OBJ         = 15
    MODULE      = 16

class Value:
    def __init__(self, type, val):
        self.type = type
        self.val = val
    def __repr__(self):
        return str(self.val)
    def __eq__(self, other):
        return self.type == other.type and self.val == other.val

class Unknown(Value):
    def __init__(self, val):
        Value.__init__(self, Types.UNKNOWN, val)

class Undecided(Value):
    def __init__(self, val):
        Value.__init__(self, Types.UNKNOWN, val)

class Type(Value):
    def __init__(self, val):
        Value.__init__(self, Types.TYPE, val)

class Null(Value):
    def __init__(self, val):
        Value.__init__(self, Types.NULL, val)

class Bool(Value):
    def __init__(self, val):
        Value.__init__(self, Types.BOOL, val)

class Int(Value):
    def __init__(self, val):
        Value.__init__(self, Types.INT, val)

class Float(Value):
    def __init__(self, val):
        Value.__init__(self, Types.FLOAT, val)

class Complex(Value):
    def __init__(self, val):
        Value.__init__(self, Types.COMPLEX, val)

class Sequence(Value):
    def __init__(self, val):
        Value.__init__(self, Types.SEQUENCE, val)

class Set(Value):
    def __init__(self, val):
        Value.__init__(self, Types.SET, val)

class Func(Value):
    def __init__(self, val):
        Value.__init__(self, Types.FUNC, val)

class Class(Value):
    def __init__(self, val):
        Value.__init__(self, Types.CLASS, val)

class Object(Value):
    def __init__(self, val):
        Value.__init__(self, Types.OBJ, val)

class Module(Value):
    def __init__(self, val):
        Value.__init__(self, Types.MODULE, val)


# ref: http://docs.python.org/reference/datamodel.html

class Python(Lang):

    name = 'py'
    prelude = \
        "import sys\n" + \
        "class ClassA: pass\n" + \
        "class ClassB: pass\n"

    def run(self, code):
        with open('tmp.py', 'w') as w:
            w.write(self.prelude)
            w.write('print ' + code + '\n')
        with os.popen('timeout 1 python tmp.py 2>&1', 'r') as r:
            output = r.readline()
        if 'Traceback (most recent call last):' in output:
            output = 'Error'
        return output.strip()

    def parse(self, output):
        if output == 'True' or output == 'False':
            return Bool(output)
        elif output == 'nan' or output == 'inf':
            return Float('float(%s)' % output)
        return Undecided(output)

    def types(self): return [
        Null('None'),
        Type('type'),
        Type('object'),
        Type('NotImplemented'),
        Type('Ellipsis'),
    ]

    def unary(self): return '+ - ~ not * **'.split()
    def binary(self): return [''] + '== != < > <= >= + - * / // << >> ^ & | % is and or , : **'.split()
    def true(self): return Bool('True')
    def false(self): return Bool('False')
    def bools(self): return [ self.true(), self.false() ]

    def int_0(self): return Int('0')
    def int_1(self): return Int('1')
    def int_neg1(self): return Int('-1')
    def int_min(self): return Int('-sys.maxint')
    def int_max(self): return Int('sys.maxint')
    def ints(self): return [
            self.int_0(),
            self.int_1(),
            self.int_neg1(),
            self.int_min(),
            self.int_max(),
            Int('0L'),
            Int('1L'),
            Int('-1L'),
        ]

    def float_0(self): return Float('0.0')
    def float_1(self): return Float('1.0')
    def float_neg1(self): return Float('-1.0')
    def float_min(self): return Float('sys.float_info.min')
    def float_max(self): return Float('sys.float_info.max')
    def float_inf(self): return Float('float("inf")')
    def float_infneg(self): return Float('-float("inf")')
    def float_nan(self): return Float('float("nan")')
    def float_nanneg(self): return Float('-float("nan")')
    def float_epsilon(self): return Float('sys.float_info.epsilon')
    def floats(self): return [
            self.float_0(),
            self.float_1(),
            self.float_neg1(),
            self.float_min(),
            self.float_max(),
            self.float_inf(),
            self.float_infneg(),
            self.float_nan(),
            self.float_nanneg(),
            self.float_epsilon(),
        ]

    def complexs(self): return [
            Int('0j'),
            Int('1j'),
            Int('-1j'),
            Float('1.0j'),
            Float('0.0j'),
            Float('-1.0j'),
        ]

    # http://docs.python.org/library/stdtypes.html#typesseq

    def sequences(self): return [
            Sequence('""'),
            Sequence('unicode()'),
            Sequence('()'),
            Sequence('[]'),
            Sequence('range(0)'),
            Sequence('xrange(0)'),
            Sequence('xrange(sys.maxint)'),
            Sequence('bytearray()'),
        ]
    def sets(self): return [
            Set('{}'),
            Set('set()'),
        ]
    def funcs(self): return [
            Func('help'),
            Func('len'),
            Func('(lambda x:x)'),
        ]
    def classes(self): return [
            Class('Exception'),
            Class('ClassA'),
            Class('ClassB'),
        ]
    def objects(self): return [
            Object('Exception()'),
            Object('ClassA()'),
            Object('ClassB()'),
        ]
    def modules(self): return [
            Module('sys'),
        ]
    def operands(self):
        return \
            self.types() + self.bools() + \
            self.ints() + self.floats() + self.complexs() + \
            self.sequences() + self.sets() + \
            self.funcs() + self.classes() + self.objects() + self.modules()

import sys
import itertools

cmds = set()
langs = [
    Python(),
    #Ruby,
    #PHP,
    #Perl, # boring... everthing is a fucking variable and weird behavior is not interesting
    #Javascript, # nodejs is slow to start, it's not really designed to boot up quickly...
]

def operations(lang):
    # return all possible operations using operators and operands
    return itertools.imap(
        lambda x: ' '.join([str(y) for y in x]),
        itertools.chain(
            itertools.product(lang.unary(), lang.operands()),
            itertools.product(
                lang.operands(),
                lang.binary(),
                lang.operands())))

def get_results(lang, code):
    output = lang.run(code)
    if lang.is_err(output):
        output = 'error'
    elif lang.is_nop(output):
        output = ''
    return output

EmptySet = set()
BoringResults = set(['', 'error'])

def is_interesting(results):
    vals = set(results.values())
    return vals & BoringResults == EmptySet

# partition l into sublists based on callback(x,y) of consecutive list items
def partition(l, callback):
    parts = [l[:1]]
    for i in xrange(1, len(l)):
        if callback(l[i-1], l[i]):
            parts[-1].append(l[i])
        else:
            print 'invalid: %s %s' % (l[i-1], l[i])
            parts.append(l[i:i+1])
    return parts

# calculate total language built-in ordinality
# python is weird
def ordinality(lang):
    def do_run_op(x, op, y):
        code = '%s %s %s' % (x, op, y)
        result = lang.run(code)
        return result
    def cmp_gte_run(x, y):
        if x.type == Types.NULL:
            return 1
        if y.type == Types.NULL:
            return -1
        res = do_run_op(x, '>', y)
        return -1 if res == 'True' else 0 if res == 'False' else 1
    def cmp_gte_valid(x, y):
        gte = do_run_op(x, '>', y)
        lte = do_run_op(x, '<', y)
        return lte in ['True', 'False'] and gte in ['True', 'False'] and (lte != gte or do_run_op(x, '==', y) == 'True')
    vals = list(lang.operands())
    """
    # print table: exhaustive, but too hard to read; too little data-density
    maxlen = max([len(str(v)) for v in vals])
    print '%-*s %-*s' % (maxlen, '', max(5, vals[0]), vals[0],),
    for v in vals[1:]:
        sv = str(v)
        print '%-*s' % (max(5, len(sv)), sv),
    print
    for x in vals:
        print '%-*s' % (maxlen, x,),
        for y in vals:
            sy = str(y)
            print '%-*s' % (max(5, len(sy)), do_run_op(x, '>=', y)[:1]),
        print
    """
    vals2 = sorted(vals, cmp=cmp_gte_run)
    print vals2
    order = partition(vals2, cmp_gte_valid)
    print order
    orderl = [sorted(x, cmp=cmp_gte_run) for x in order]
    print orderl
    for l in orderl:
        for x,y in zip(l, l[1:]):
            print x, '>' if do_run_op(x, '>', y) == 'True' else '==',
        print l[-1]

ordinality(Python())
exit(1)

for lang in langs:
    results = {}
    for code in operations(lang):
        results[lang.name] = get_results(lang, code)
        if is_interesting(results):
            print '%-30s' % (code),
            for k,v in sorted(results.items()):
                print ': %s' % (v,),
            print

exit(1)

for i in xrange(50000000):
    # generate the nth permutation of code
    code = nth(i)
    # only run unique snippets, time is precious
    if code not in cmds:
        cmds.add(code)
        results = {}
        # run it in each language
        for l in langs:
            results[l.name] = get_results(l)
        if is_interesting(results):
            print '%6u %-22s' % (i, code),
            for k,v in sorted(results.items()):
                print '%s %-22s' % (k,v),
            print

