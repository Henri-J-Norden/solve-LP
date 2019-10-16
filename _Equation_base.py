from numbers import Number
from fractions import Fraction
from copy import deepcopy, copy
import operator as op
import re

class EqElement:
    def get_identifier(var_p):
        return " ".join(["{}{}".format(v, "^"+str(var_p[v]) if (var_p[v] != 1 and not (v == "" and var_p[v] == 0)) else "") for v in sorted(var_p.keys()) if v != ""])
        

    def _update(self, identity_update=True):
        for v in list(self.vars):
            if self.vars[v] == 0:
                self.vars.pop(v)
        if self.multi == 0: self.vars = {}
        if len(self.vars) == 0: self.vars[""] = 1

        if identity_update:
            self.ident = f"{EqElement.get_identifier(self.vars)}"
    
    def __init__(self, multiplier:int, var):
        if type(var) is dict:
            var_p = var
        elif type(var) is str:
            var = re.subn(r"  ", " ", var.strip())[0]
            #print(f"'{var}'")
            var_p = {v[0]: int(v[1]) if len(v) > 1 else 1  for v in (vp.replace("**", "^").replace(" ", "").replace("*", "").split("^") for vp in var.split(" "))}
        self.multi = multiplier
        self.vars = var_p # {"x": <power>}
        self._update()
        

    def is_const(self):
        return len(self.vars) == 1 and list(self.vars.keys())[0] == ""

    def is_zero(self):
        return self.multi == 0

    def value(self, abs_val=False, op=" "):
        show_val = abs(self.multi) != 1 or self.is_const()
        return (f"{abs(self.multi) if abs_val else self.multi}" if show_val else "")  +  (op if self.ident != "" and show_val else "")  +  f"{self.ident}"

    def __repr__(self):
        return self.value()
        

    def __imul__(a, b):
##        if isinstance(b, EquationBase):
##            return NotImplemented
        if isinstance(b, Number):
            a.multi *= b
        elif type(b) is EqElement: 
            a.multi *= b.multi
            for var_b in b.vars:
                if var_b == "": continue
                a.vars[var_b] = a.vars.get(var_b, 0) + b.vars[var_b]
        else:
            raise TypeError(f"Can only multiply with a Number or EqElement (not {type(b)})!")
        a._update()
        return a

    def __mul__(a, b):
##        if isinstance(b, EquationBase):
##            return NotImplemented
        e = deepcopy(a)
        e *= b
        return e

    def __rmul__(a, b):
        return a * b

    def __iadd__(a, b):
        if type(b) is not EqElement:
            raise TypeError(f"Can only add EqElement (not {type(b)})!")
        if a.ident != b.ident:
            raise TypeError(f"Cannot add var '{b.ident}' to '{a.ident}'! Variables must be equal")
        a.multi += b.multi
        a._update()
        return a

    def __add__(a, b):
        e = deepcopy(a)
        e += b
        return e

    def __radd__(a, b):
        if not isinstance(b, Number):
            raise TypeError()
        if b != 0:
            raise ValueError()
        return a

    def __ipow__(a, b):
        if not isinstance(b, Number):
            raise TypeError()
        if b == -1: # special case for exact division
            a.multi = Fraction(1, a.multi)
        else:
            a.multi **= b
            
        for v in a.vars:
            if v == "": continue
            a.vars[v] *= b
        a._update()
        return a

    def __pow__(a, b):
        e = deepcopy(a)
        e **= b
        return e

    def __neg__(a):
        e = deepcopy(a)
        e.multi = -e.multi
        return e

    def __eq__(a, b):
        if isinstance(b, Number):
            if a.is_const():
                return a.multi == b
            else:
                return False
            #raise ValueError("Non-numerical EqElement can't be compared to a number!")
        elif isinstance(b, EqElement):
            return a.ident == b.ident and a.multi == b.multi
        else:
            raise TypeError(f"Can't compare {type(b)} to EqElement")
        return True


class EquationBase:
    
    def __iadd__(a, b):
        if isinstance(b, Number):
            a += EqElement(b, {"": 1})
            
        elif isinstance(b, EqElement):
            if b.ident in a.elem:
                e = a.elem.pop(b.ident) + b
                a.elem[e.ident] = e
                
            else:
                a.elem[b.ident] = b
                
            if "" in a.elem and len(a.elem) != 1 and a.elem[""].is_zero():
                a.elem.pop("")
                
        elif isinstance(b, EquationBase):
            for e in b.elem.values():
                a += e
            
        else:
            raise TypeError("Only multiplication with numbers and other Equation objects is allowed (but \"{}\" was given)!".format(str(type(b))))
        return a

    def __add__(a, b):
        e = deepcopy(a)
        e += b
        return e

    def __radd__(self, b):
        return self.__add__(b)

    def __sub__(self, b):
        e = deepcopy(self)
        return e + (-b)

    def __rsub__(self, b):
        return self.__sub__(b)

    def __neg__(a):
        e = copy(a)
        e.elem = {_el.ident: _el for _el in (-el for el in a.elem.values())}
        return e

    def __imul__(a, b):
        if isinstance(b, Number):
            for el in a.elem.values():
                el *= b
        elif isinstance(b, EqElement):
            for el in a.elem.values():
                el *= b
        elif isinstance(b, EquationBase):
            new_elem = {}
            for elem_b in b.elem.values():
                for elem_a in a.elem.values():
                    new_el = elem_a * elem_b
                    new_elem[new_el.ident] = new_elem.get(new_el.ident, 0) + new_el
            a.elem = new_elem
        else:
            raise TypeError("Only multiplication with numbers and other Equation objects is allowed (but \"{}\" was given)!".format(str(type(b))))
        return a

    def __mul__(a, b):
        e = deepcopy(a)
        e *= b
        return e
        

    def __rmul__(a, b):
        return a * b

    def __truediv__(a, b):
        if isinstance(b, EquationBase):
            c = deepcopy(b)
            for el in c.elem.values(): el **= -1
            return a * c
        elif isinstance(b, Number):            
            return a * (1 / b)
        else:
            TypeError(f"Can't divide equation with {type(b)}")

    def __pow__(a, b):
        if isinstance(b, int):
            prod = 1
            for _ in range(b):
                prod *= a
            for _ in range(0, b, -1):
                prod /= a
            return prod
        elif isinstance(b, Number):
            raise NotImplemented(f"Can currently only pow with int (got {type(b)}).")
        else:
            raise TypeError()
        

    def __eq__(a, b):
        if isinstance(b, Number):
            if a.is_const():
                return a.calculate() == b
            else:
                return False
            #raise ValueError("Non-numerical equation can't be compared to a number!")
        elif isinstance(b, EquationBase):
            if len(a.elem) != len(b.elem):
                return False
                #raise ValueError(f"Equations have a different number of terms {len(a.elem)} for '{a}' and {len(b.elem)} for '{b}'")
            for ident in a.elem:
                if ident not in b.elem:
                    return False
                if a.elem[ident] != b.elem[ident]:
                    return False
        else:
            raise TypeError(f"Can't compare {type(b)} to Equation.")
        return True

    def __ne__(a, b):
        return not a == b

    def __numeric_comparer(fn, a, b):
        if isinstance(b, Number):
            if a.is_const():
                return fn(a.calculate(), b)
            raise ValueError("Non-numerical equation can't be compared to a number!")
        elif isinstance(b, EquationBase):
            if not (a.is_const() and b.is_const()):
                raise ValueError("Cannot compare non-numerical equations")
            return fn(a.calculate(), b.calculate())
        else:
            raise TypeError(f"Can't compare {type(b)} to Equation.")
        
    def __lt__(a, b): return EquationBase.__numeric_comparer(op.lt, a, b)
    def __le__(a, b): return EquationBase.__numeric_comparer(op.le, a, b)
    def __gt__(a, b): return EquationBase.__numeric_comparer(op.gt, a, b)
    def __ge__(a, b): return EquationBase.__numeric_comparer(op.ge, a, b)
    
