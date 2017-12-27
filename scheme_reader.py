"""This module implements the built-in data types of the Scheme language, along
with a parser for Scheme expressions."""

from ucb import main, trace, interact
from scheme_tokens import tokenize_lines, DELIMITERS
from buffer import Buffer, InputReader, LineReader

# Pairs and Scheme lists

class Pair:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __repr__(self):
        return 'Pair({0}, {1})'.format(repr(self.first), repr(self.second))

    def __str__(self):
        s = '(' + str(self.first)
        second = self.second
        while isinstance(second, Pair):
            s += ' ' + str(second.first)
            second = second.second
        if second is not nil:
            s += ' . ' + str(second)
        return s + ')'
        return s

    def __len__(self):
        n, second = 1, self.second
        while isinstance(second, Pair):
            n += 1
            second = second.second
        if second is not nil:
            raise TypeError('length attempted on improper list')
        return n

    def __eq__(self, p):
        if not isinstance(p, Pair):
            return False
        return self.first == p.first and self.second == p.second

    def map(self, fn):
        """Return a Scheme list after mapping Python function FN to SELF."""
        mapped = fn(self.first)
        if self.second is nil or isinstance(self.second, Pair):
            return Pair(mapped, self.second.map(fn))
        else:
            raise TypeError('ill-formed list')

class nil:
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __str__(self):
        return '()'

    def __len__(self):
        return 0

    def map(self, fn):
        return self

nil = nil() #hides nil class. Only 1 instance

# Scheme list parser
def scheme_read(src):
    """Read the next expression from SRC, a Buffer of tokens."""


    if src.current() is None:
        raise EOFError
    val = src.remove_front() # Get the first token
    if val == 'nil':
        return nil
    elif val == '(':
        return read_tail(src)
    elif val == "'":
        return Pair('quote',Pair(scheme_read(src),nil))
    elif val not in DELIMITERS:
        return val
    else:
        raise SyntaxError('unexpected token: {0}'.format(val))

def read_tail(src):
    """Return the remainder of a list in SRC, starting before an element or )."""
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        elif src.current() == ')':
            src.remove_front()
            return nil
        elif src.current() == '.':
            src.remove_front()
            curr = scheme_read(src)
            if (read_tail(src) is nil):
                return curr
            else:
                raise SyntaxError
        else:
            return Pair(scheme_read(src), read_tail(src))
    except EOFError:
        raise SyntaxError('unexpected end of file')

def buffer_input(prompt='scm> '):
    return Buffer(tokenize_lines(InputReader(prompt)))

def buffer_lines(lines, prompt='scm> ', show_prompt=False):
    if show_prompt:
        input_lines = lines
    else:
        input_lines = LineReader(lines, prompt)
    return Buffer(tokenize_lines(input_lines))

def read_line(line):
    return scheme_read(Buffer(tokenize_lines([line])))

# Interactive loop
@main
def read_print_loop():
    """Run a read-print loop for Scheme expressions."""
    while True:
        try:
            src = buffer_input('read> ')
            while src.more_on_line:
                expression = scheme_read(src)
                print('str :', expression)
                print('repr:', repr(expression))
        except (SyntaxError, ValueError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print()
            return