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
    size = [int(input("Simplex table rows: "))]
    cols = input("Simplex table columns (leave empty for " + str(size[0]+1) + "): ")
    if len(cols) == 0:
        size.append(size[0] + 1)
    else:
        size.append(int(cols))

    variables = input("Variable names: (leave empty for x1...x{}): ".format(size[1]-1)).split(" ")
    if variables == ['']:
        variables = ["x{}".format(i) for i in range(1, size[1]-1)]
        
    l = [[] for i in range(size[0])]
    if size[0] < 2 or size[1] <= size[0]:
        print("<rows> must be larger than 2 and <cols> must be larger <rows> + 1!")
        return l
    for i in range(size[0]):
        while True:
            l[i] = []
            try:
                vals = input("Row " + str(i) + ": ")
                j = 0
                for val in vals.split(" "):
                    if "/" in val:
                        val = list(map(int, val.split("/")))
                        l[i].append(Fraction(*val))
                    else:
                        l[i].append(Fraction(float(val)))
                    j += 1
                if len(l[i]) != size[1]:
                    print("Input does not match column count! (use spaces as separators between numbers)")
                    continue
                break
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    print("Input cancelled!\n")
                    raise KeyboardInterrupt()
                print("Input parsing failed!")
                print(e)
    print()
    return (variables, l)

def _getStrings(l, getMax=False):
    lp = [[] for i in range(len(l))]
    maxLen = 0
    for r in range(len(l)):
        for v in l[r]:
            lp[r].append((str(v.numerator) if v.denominator == 1 else str(v.numerator) + "/" + str(v.denominator)))
            maxLen = max(maxLen, len(lp[r][-1]))
    return lp if not getMax else (lp, maxLen)

def getMatrix(l):
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
while True:
    # calculate
    while len(l[0]) == 0:
        try:
            var, l = getInput()
        except Exception as e:
            print("Input parsing failed!")
            print(e)
    solved = solve_simplex(l, True)
    
    if solved: # print values
        print()
        print("\n".join(getValueStrings(l, var)))
        
    print("\n")
    l = [[]]
