from fractions import Fraction
from numbers import Number
import re
from copy import deepcopy
from numpy import roots

from _Equation_base import *
#from eqelement import EqElement


NUMERAL_REGEX = r"(?P<numeral>(?P<sign>([\+\-])) *((?P<fraction>(?P<num>\d+) *\/ *(?P<den>\d+))|(?P<decimal>(?P<int>\d+)[.,](?P<frac>\d+))|(?P<integer>\d+))|(?P<valueless>([\+\-])))"
_EQUATION_REGEX = re.compile(f"{NUMERAL_REGEX} *(?P<identity>[^\+\-]*) *")
#_IDENT_REGEX = re.compile(f"{NUMERAL_REGEX}?(?P<identity>.*)")

def _parse_num_match(match):
    if match.group("numeral") is None: return 1
    num = match.group("sign")
    if match.group("fraction") is not None:
        num += match.group("num")
        num = int(num)
        den = int(match.group("den"))
    elif match.group("decimal") is not None:
        num += match.group("frac")
        num = int(num)
        den = 10**len(match.group("frac"))
        num += (den * int(match.group("int"))) * ((-1) if match.group("sign") == "-" else 1)
    elif match.group("integer") is not None:
        den = 1
        num += match.group("integer")
        num = int(num)
    elif match.group("valueless") is not None:
        num = -1 if match.group("valueless") == "-" else 1
        den = 1
    else:
        raise ValueError("Numerical value not found in \"{}\"".format(str(match)))
    return Fraction(num, den)



class Equation(EquationBase):
    
    def _parsePart(self, match):
        val = _parse_num_match(match)
        ident = match.group("identity")

        self += EqElement(val, ident)

    def __init__(self, s:str=None):
        self.elem = {}
        if s is None: return
        s = s.lstrip()
        if s[0] != "+" and s[0] != "-": s = "+"+s
        
        match = _EQUATION_REGEX.search(s)
        end = 0
        while match is not None and match.start() != match.end():
            #print(f"{match.start()}:{match.end()}")
            if match.start() != end:
                print(match.start())
                print(end)
                raise ValueError("Failed to parse \"{}\" (did not match the regex)!".format(s[end:match.start()]))
            self._parsePart(match)
            end = match.end()
            match = _EQUATION_REGEX.search(s, end)

    def __repr__(self, op=" "):
        s = [[("+" if el.multi >= 0 else "-"), el.value(abs_val=True, op=op)] for el in sorted(self.elem.values(), key=str, reverse=True)]
        if len(s) == 0:
            s.append(["0"])
        elif s[0][0] == "+":
            s[0].pop(0)

        if self.is_const(): return "".join(s[0])
        return (" ".join(map(lambda x: " ".join(x), s)))

    def calc(self, vals={}, get_print_out=False):
        if get_print_out:
            out_str = self.__repr__("*")
            for k in sorted(vals, key=len, reverse=True):
                out_str = out_str.replace(k, f"{vals[k]}")
        
        s = 0
        vals[""] = 1
        for el in self.elem.values():
            if len(el.vars) == 1 and list(el.vars.keys())[0] == "":
                s += el.multi ** el.vars[""]
                continue

            prod = el.multi
            for var in el.vars:
                if var not in vals:
                    raise KeyError(f"Value for {var} not given!")
                prod *= vals[var] ** el.vars[var]
            s += prod

        if get_print_out:
            return (s, out_str)
        else:
            return s

    def calculate(self, *arg, **kwarg):
        return self.calc(*arg, **kwarg)

    def replace(self, x, y):
        if type(y) == str:
            y = Equation(y)
        eq = Equation()
        #new_eqs = []
        for el in self.elem.values():
            el = deepcopy(el)
            if x in el.vars:
                newvar = y ** el.vars.pop(x)
                #new_eqs.append(newvar * el)
                eq += newvar * el
            else:
                eq += el
            #eq.elem[el.ident] = eq.elem.get(el.ident, 0) + el
        return eq

    def is_const(self):
        return len(self.elem) == 1 and list(self.elem.keys())[0] == ""

    def get_variables(self):
        v_l = [""]
        for el in self.elem.values():
            v = list(el.vars)[0]
            if v not in v_l:
                v_l.append(v)
        return v_l

    def roots(self):
        var = self.get_variables()
        if len(var) != 2:
            raise ValueError(f"Expected 1 variable (+ empty variable), but got: {var}")

        v = var[1]
        # [(power, polynomial factor), ...]
        values = sorted(((el.vars[v] if not el.is_const() else 0, el.multi) for el in self.elem.values()), key=lambda x: x[0], reverse=True) 

        p = [v[1] for v in values]
        return list(roots(p))
        
