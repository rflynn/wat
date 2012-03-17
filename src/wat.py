# -*- encoding: utf-8 -*-

"""
This program is designed to discover relationships between programming
language built-ins such as first-class types (if they exist) and the base cases
of those types.
We abstract all the language-specific stuff in a Lang object along with
a way to run code, then we generate expressions in that language, run them
and read the results.
Currently we generate we generate .dot files intended as input for the
Graphviz graph-generating program.
For Lang(Python) we'd generate py.out.dot, which can be transformed into a graph:

    # run python code and generate py.out.dot
    $ python wat.py 

    # use graphviz to generate a graph
    $ dot -Tpng -o py.out.png py.out.dot

"""

# TODO: eliminate boring string output

# lang in          out
#----- ----------- -----------------------------------------
# js   []+[]       ""
# js   []+{}       [object Object]
# js   {}+[]       0
# php  ~NaN        ��� apparently string bitwise not? why?!
# js   global      {}
# rb   [print]     [nil]
# rb   [end]       [end]
# rb   [break]     [break]
# js   [,]         [] javascript's comma operator is weird
# ruby [1e999][1e-999] Infinity
# php  ~"0"        � unary operators cast numeric strings to ints... except ~
# ruby print //    (?-mix:) WTF?

"""
   3062 1.11e-16-1             php -1                     pl -1                     py -0.9999999999999999    rb -0.9999999999999999
   3286 04294967297            php 34                     py                        rb foo.rb:1: Invalid octal digit
 24228 print"-"               php -1                     py -                      rb -
"""

import os, re
import networkx as nx
import json
from subprocess import Popen, PIPE

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

class Value:
    def __init__(self, type, val):
        self.type = type
        self.val = val
    def __repr__(self):
        return str(self.val)
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return self.val.__hash__()
    def __eq__(self, other):
        if type(other) == type(''):
            return self.val == other
        elif type(other) == type(self):
            return self.type == other.type and self.val == other.val
        return False

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


class Python(Lang):
    # ref: http://docs.python.org/reference/datamodel.html

    name = 'py'
    longname = 'Python'
    version = ''
    prelude = \
        "import sys\n" + \
        "class ClassA: pass\n" + \
        "class ClassB: pass\n"

    def __init__(self):
        self.version = os.popen('python --version 2>&1 | cut -d" " -f2').readline().strip()

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
            Sequence('u""'),
            Sequence('str()'),
            Sequence('unicode()'),
            Sequence('()'),
            Sequence('[]'),
            Sequence('range(0)'),
            Sequence('xrange(0)'),
            #Sequence('xrange(sys.maxint)'),
            Sequence('bytearray()'),
        ]

    def sets(self): return [
            Set('{}'),
            Set('set()'),
        ]

    def funcs(self): return [
            Func('help'),
            Func('len'),
            Func('id'),
            Func('(lambda x:x)'),
        ]

    def classes(self): return [
            Class('Exception'),
            #Class('ClassA'),
            #Class('ClassB'),
        ]

    def objects(self): return [
            #Object('Exception()'),
            #Object('ClassA()'),
            #Object('ClassB()'),
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


class Javascript(Lang):
    # ref: Standard ECMA-262 ECMAScript Language Specification Edition 5.1 (June 2011)
    # http://www.ecma-international.org/publications/files/ECMA-ST/Ecma-262.pdf

    # node.js v0.4.9

    name = 'js'
    longname = 'Javascript'
    version = ''
    proc = None

    def __init__(self):
        self.version = 'node.js ' + os.popen('js --version').readline().strip()
        self.proc = Popen('js', shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)

    def run(self, code):
        print >> self.proc.stdin, code + '\n'
        output = self.proc.stdout.readline()[2:].strip() # toss "> " prompt prefix
        return output.strip()

        """
        with os.popen('timeout 1 js > tmp.js.out', 'w') as p:
            p.write(code + '\n')
        with open('tmp.js.out') as out:
            output = out.readline()[2:].strip() # toss "> " prompt prefix
        return output.strip()
        """

    def parse(self, output):
        if output == 'true' or output == 'false':
            return Bool(output)
        elif output == 'NaN' or output == 'Infinity':
            return Float(output)
        return Undecided(output)

    def types(self): return [
        Null('undefined'),
        Null('null'),
    ]

    def sequences(self): return [
            Sequence('""'),
            Sequence('[]'),
        ]

    def unary(self): return '+ - ! ~ !!'.split()
    def binary(self): return [''] + '== != < > <= >= + - * / << >> ^ & | % ,'.split()
    def true(self): return Bool('true')
    def false(self): return Bool('false')
    def bools(self): return [ self.true(), self.false() ]

    def int_0(self): return Int('0')
    def int_neg0(self): return Int('-0')
    def int_1(self): return Int('1')
    def int_neg1(self): return Int('-1')
    # http://ecma262-5.com/ELS5_HTML.htm#Section_8.5
    def int_min(self): return Int('-9007199254740992')
    def int_max(self): return Int('9007199254740992')
    def ints(self): return [
            self.int_0(),
            self.int_neg0(),
            self.int_1(),
            self.int_neg1(),
            self.int_min(),
            self.int_max(),
            Int('9007199254740993'), # int_max+1
            Int('-9007199254740993'), # int_min-1
        ]

    def float_0(self): return Float('0.0')
    def float_1(self): return Float('1.0')
    def float_neg1(self): return Float('-1.0')
    #def float_min(self): return self.int_min()
    #def float_max(self): return self.int_max()
    def float_inf(self): return Float('Infinity')
    def float_infneg(self): return Float('-Infinity')
    def float_nan(self): return Float('NaN')
    def float_nanneg(self): return Float('-NaN')
    #def float_epsilon(self): return Float('5e-324') # epsilon is not well-defined
    def floats(self): return [
            self.float_0(),
            self.float_1(),
            self.float_neg1(),
            #self.float_min(),
            #self.float_max(),
            self.float_inf(),
            self.float_infneg(),
            self.float_nan(),
            self.float_nanneg(),
            #self.float_epsilon(),
        ]

    def sets(self): return [
            Set('{}'),
        ]

    def funcs(self): return [
            Func('clearInterval'),
            Func('clearTimeout'),
            #Func('console'), # non-standard, though common
            Func('eval'),
            Func('(function(){})'),
            Func('(function(){})()'),
            Func('global'),
            Func('isFinite'),
            Func('isNaN'),
            #Func('module'), # non-standard(?) node.js
            Func('parseFloat'),
            Func('parseInt'),
            #Func('process'), # non-standard(?) node.js
            #Func('require'), # non-standard(?) node.js
            Func('setInterval'),
            Func('setTimeout'),
        ]

    def objects(self): return [
            Class('Array'),
            Class('Boolean'),
            Class('Date'),
            Class('Error'),
            Class('Function'),
            Class('JSON'),
            Class('Math'),
            Class('Number'),
            Class('Object'),
            Class('RangeError'),
            Class('ReferenceError'),
            Class('RegExp'),
            Class('String'),
            Class('SyntaxError'),
            Class('TypeError'),
            Class('URIError'),
        ]

    def objects(self): return [
        ]

    def operands(self):
        return \
            self.types() + self.bools() + \
            self.ints() + self.floats() + \
            self.sequences() + self.sets() + \
            self.funcs() + self.objects()

import sys
import itertools

cmds = set()
langs = [
    Python(),
    Javascript(), # nodejs is slow to start, it's not really designed to boot up quickly...
    #Ruby,
    #PHP,
    #Perl, # boring... everthing is a fucking variable and weird behavior is not interesting
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

def esc(s):
    return str(s).replace('"', '\\"')

def graphviz(lang, vals, cmps):

    G = nx.DiGraph()

    # reduce the number of links by way of transitivity;
    # that is, if AxB and BxC then we don't need AxC
    # TODO: UNLESS the relationship is unintuitive/broken
    link = {}
    # graphviz-friendly key names
    key = dict((str(k),"\"%s\"" % esc(k)) for k in vals)
    for a, op, b in cmps:
        G.add_node(a)
        G.add_node(b)
        G.add_edge(a, b)
        try:
            # FIXME: use networkx edge attributes instead of this out-of-band crap
            link[a][b] = op
        except KeyError:
            link[a] = {b:op}

    #nodes_in_cycles = set(sum(nx.simple_cycles(G), []))
    #print 'nodes_in_cycles:', nodes_in_cycles

    # remove redundant edges
    # TODO: ultimately, it would be faster to NOT run redundant tests
    for x, y in G.edges():
        # if any of x's successors has a path to y then I don't need a direct path
        # favor more, "shorter" paths that outline the total ordinality than
        # "long" paths that clutter our graph
        existing = [
            s for s in G.successors(x)
                if s != x and s != y and nx.has_path(G, s, y) ]
        if existing:
            print 'remove_edge(%s, %s) because of %s' % (x, y, existing)
            G.remove_edge(x, y)
            if not nx.has_path(G, x, y):
                # we thought we could remove an edge and still have a path x->y,
                # but that was an illusion due to a cycle in our directional
                # graph; put the edge back in to preserve the path
                G.add_edge(x, y)

    print key.items()

    #print 'nodes:', G.nodes()
    #print 'edges:', G.edges()
    #print 'link:', link
    with open(lang.name + ".ord.dot", "w") as dot:
        dot.write('digraph {\n')
        dot.write('label="%s (%s)\\n%s\\n"\n' % (
            lang.longname, lang.version, 'Built-in Ordinality'))
        dot.write('labelloc="t";\n')
        # a clean style never hurt anyone
        dot.write('graph [fontsize=24]\n')
        dot.write('edge [fontsize=18, penwidth=0.5, color="#999999"]\n')
        dot.write('node [fontsize=12, shape=box, penwidth=0.5, style="filled", fillcolor="#ffffcc", color="#ff9900"]\n')

        # ensure that anything that isn't connected still gets a visual node
        for x in vals:
            dot.write("%s\n" % key[x])
        for x, y in G.edges():
            if link[x].has_key(y):
                op = link[x][y]
            else:
                op = link[y][x]
                x,y = y,x
            dot.write('%s -> %s [label="%s"]\n' % (key[str(x)], key[str(y)], esc(op)))
        dot.write('}\n')

# calculate total language built-in ordinality
# python is weird
def ordinality(lang):
    def do_run_op(x, op, y):
        code = '%s %s %s' % (x, op, y)
        result = lang.run(code)
        return result
    vals = list(lang.operands())
    cmp_true = []
    if os.path.exists(lang.name + '.cmps'):
        with open(lang.name + '.cmps') as f:
            cmp_true = json.loads(f.read())
    else:
        # try every order-insensitive combination
        for x,y in itertools.combinations(vals, 2):
            for op in ['>', '==', '<']:
                if lang.true() == do_run_op(x, op, y):
                    if op == '<':
                        x,y,op = y,x,'>'
                    print '"%s" -> "%s" [label="%s"]' % (esc(x), esc(y), esc(op))
                    cmp_true.append((str(x), op, str(y)))
                    break
        with open(lang.name + '.cmps', 'w') as f:
            f.write(json.dumps(cmp_true))
    graphviz(lang, vals, cmp_true)

ordinality(Javascript())
ordinality(Python())

