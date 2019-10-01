from fractions import Fraction

def _div(l, divider, new=False):
    if new:
        ln = []
    for i in range(len(l)):
        if new:
            ln.append(Fraction(l[i], divider))
        else:
            l[i] = Fraction(l[i], divider)
    if new:
        return ln

def _sub(l, lSub):
    for i in range(len(l)):
        l[i] -= lSub[i]

def check_el_diag(l, log=False):
    rows = len(l)-1
    for c in range(-1, -rows-1, -1):
        if l[0][c] != 0:
            for r in range(1, rows+1):
                if l[r][c] != 0:
                    if log: print("Subtracting row {} from 0 at col {}".format(r, c))
                    subtract = _div(l[r], Fraction(l[r][c], l[0][c]), True)
                    _sub(l[0], subtract)
                    break
    if log:
        print(getMatrix(l))

def remove_lead_elements(l, log=False, removed=None):
    rows = len(l)
    cols = len(l[0])
    if removed is None: removed = set()
    newly_removed = set()
    for c in range(1, cols):
        nonzero = []
        for r in range(1, rows):
            if l[r][c] != 0:
                nonzero.append((r,c))
        if len(nonzero) == 1 and nonzero[0] not in removed:
            r, c = nonzero[0]
            if (l[0][c]) != 0:                
                if log: print("Subtracting row {} from 0 at col {}".format(r, c))
                subtract = _div(l[r], Fraction(l[r][c], l[0][c]), True)
                _sub(l[0], subtract)
                newly_removed.add(nonzero[0])
    if log:
        print(getMatrix(l))
    return newly_removed

def simplex_move(l, col, log=False):
    lead_row = max([(l[row][col] / l[row][0], row) for row in range(1, len(l))], key=lambda x: x[0])[1]
    if log: print("Minimal el and free val div on row: {}".format(lead_row))
    
    for r in range(len(l)):
        if r == lead_row:
            _div(l[r], l[r][col])
            continue
        subtract = _div(l[lead_row], Fraction(l[lead_row][col], l[r][col]), True)
        _sub(l[r], subtract)
    if log: print(getMatrix(l))
    

def contains_negative(l):
    for el in l:
        if el < 0: return True
    return False
    

def solve_simplex(l, log=False):
    used_cols = set()
    while contains_negative(l[0][1:]):
        if log: print("\nTable does not contain an optimal solution")

        lead_col = min([(l[0][col], col) for col in range(1, len(l[0]))], key=lambda x: x[0])[1]
        if lead_col in used_cols:
            print("Error: solver looped, no solution is possible!")
            return False
        
        if log: print("\nChosen variable/column: {}".format(lead_col))
        simplex_move(l, lead_col, log)

        used_cols.add(lead_col)
    print("Optimal solution found!")
    return True
    

def getInput():
    l = []
    col_count = None
    ex = int(input("Solver (1-simplex, 2-diag): "))
    print("Input simplex table (separate elements with spaces, rows with new line; leave line empty to end input):")
    while True:
        row = []
        try:
            vals = input()
            if vals == "":
                break
            for val in vals.split(" "):
                if "/" in val:
                    val = list(map(int, val.split("/")))
                    row.append(Fraction(*val))
                else:
                    row.append(Fraction(float(val)))
            if col_count is None:
                col_count = len(row)
            elif len(row) != col_count:
                print("Input does not match column count! (use a single space as the separator between numbers)")
                continue
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                print("Input cancelled!\n")
                raise KeyboardInterrupt()
            print("Input parsing failed!")
            print(e)
        l.append(row)

    row_count = len(l)
    if row_count < 2 or col_count <= row_count:
        print("<rows> must be larger than 2 (got {}) and <cols> must be larger <rows> + 1 (got {})!".format(row_count, col_count))
        return (0, [], [])

    variables = input("Variable names: (leave empty for x1...x{}): ".format(col_count-1)).split(" ")
    if variables == ['']:
        variables = ["x{}".format(i) for i in range(1, col_count)]
    print()
    
    return (ex, variables, l)

def _getStrings(l, getMax=False):
    lp = [[] for i in range(len(l))]
    maxLen = 0
    for r in range(len(l)):
        for v in l[r]:
            lp[r].append((str(v.numerator) if v.denominator == 1 else str(v.numerator) + "/" + str(v.denominator)))
            maxLen = max(maxLen, len(lp[r][-1]))
    return lp if not getMax else (lp, maxLen)

def getMatrix(l, highlight=None):
    global var
    lp, maxLen = _getStrings(l, True)
    ls = []
    formatStr = "{: >" + str(maxLen) + "}  "
    s = formatStr + "| " + formatStr * (len(lp[0]) - 1)
    if var is not None:
        ls.append(s.format("", *var, *([""] * (len(lp[0]) - len(var) - 1))))
        ls.append("-" * len(ls[0]))
    for r in range(len(l)):
        ls.append(s.format(*lp[r]))
        if r == 0: ls.append("-" * len(ls[0]))
    return "\n".join(ls)

def getValues(l):
    v = [0]*(len(l[0]))
    for col in range(1, len(l[0])):
        valExists = False
        for row in range(1, len(l)):
            if l[row][col] != 0:
                if valExists:
                    v[col] = 0
                else:
                    valExists = True
                    v[col] = l[row][0]
    return v[1:]

def getZ(l, v):
    s = ""
    z = 0
    for i in range(len(l)):
        if i == 0:
            m = 1
        else:
            m = v[i - 1]

        s += "+{}*{} ".format(l[i], m)
        z += l[i]*m
    s = "z = {} = ".format(z) + s
    return (s, z)
        

def getValueStrings(l, var):
    v = getValues(l)
    s = [getZ(l[0], v)[0]]
    for i in range(len(var)):
        if (var[i] != ""):
            s.append("{} = {}".format(var[i], v[i]))
    return s
        


l = [[]]
var = []
ex = 0
while True:
    # calculate
    while len(l[0]) == 0:
        try:
            ex, var, l = getInput()
        except Exception as e:
            print("Input parsing failed!")
            print(e)
            ex = 0
    if ex == 0:
        l = [[]]
        continue
    if ex == 2:
        check_el_diag(l, True)
    removed_els = set((-1, -1))
    while len(removed_els) != 0:
        removed_els = remove_lead_elements(l, True, removed_els)
    solved = solve_simplex(l, True)
    
    if solved: # print values
        print()
        print("\n".join(getValueStrings(l, var)))
        
    print("\n")
    l = [[]]
