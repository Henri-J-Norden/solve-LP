from fractions import Fraction
from equation import Equation, EqElement
from copy import deepcopy

def _div(l, divider, new=False):
    #print(f"dividing {l} by {divider}")
    if new:
        ln = []
    for i in range(len(l)):
        if new:
            ln.append(l[i] / divider)
        else:
            l[i] = l[i] / divider
    if new:
        return ln

def _sub(l, lSub):
    for i in range(len(l)):
        l[i] -= lSub[i]

def remove_bases_from_fn(l, log=False):
    rows = len(l)
    cols = len(l[0])
    for c in range(1, cols):
        values = []
        for r in range(1, rows):
            if l[r][c] != 0:
                values.append((r, c))
        is_base = len(values) == 1 and l[values[0][0]][values[0][1]] == 1

        if not is_base: continue

        r, c = values[0]
        if (l[0][c]) != 0:                
            if log: print("Subtracting row {} from fn (col {})".format(r, c))
            subtract = _div(l[r], l[r][c] / l[0][c], True)
            _sub(l[0], subtract)
            
        if log:
            print(getMatrix(l))
    


def simplex_move(l, el, log=False):
    lead_r, lead_c = el
    for r in range(len(l)):
        if r == lead_r:
            _div(l[r], l[r][lead_c])
            continue
        subtract = _div(l[lead_r], l[lead_r][lead_c] / l[r][lead_c], True)
        #print(f"subtracting {subtract} from row {r}")
        _sub(l[r], subtract)
    if log: print(getMatrix(l))
    

def contains_negative(l):
    global M
    for i in range(len(l)):
        #print(f"{i}: {i+1 not in M} M:({M})")
        if (i+1 not in M) and (not l[i].is_const()):
            return True
    for i in range(len(l)):
        if i+1 in M: continue
        if l[i] < 0: return True
    return False

def get_lead_el(l):
    try:
        lead_col = min([(l[0][col], col) for col in range(1, len(l[0]))], key=lambda x: x[0])[1]
    except ValueError:
        lead_col = min([(l[0][col].elem["M"].multi, col) for col in range(1, len(l[0])) if "M" in l[0][col].elem], key=lambda x: x[0])[1]
    lead_row = max([(l[row][lead_col] / l[row][0] if l[row][lead_col] > 0 else float("-inf"), row)
                    for row in range(1, len(l))], key=lambda x: x[0])[1]
    return (lead_row, lead_col)


def solve_simplex(l, log=False):
    global test
    test = []
    used_cols = set()
    while contains_negative(l[0][1:]):
        if log: print("\nTable does not contain an optimal solution")

        r,c = get_lead_el(l)

        if c in used_cols:
            print(f"Error: solver looped (to col {c}), no solution is possible!")
            return False

        if log: print("\nLead column (min fn value): {}\nLead row (min var and free el div): {}".format(c, r))
        
        simplex_move(l, (r,c), log)
        test.append(deepcopy(l))

        used_cols.add(c)
    if log: print("Optimal solution found!")
    return True
    

def getInput():
    l = []
    col_count = None
    ex = int(input("{}Solver (1:simplex, 2:2-phase, 3:M-method): ".format("" if log else "Silent")))
    #ex = 1
    if ex < 0: return (ex, [], [])

    variables = input("Variable names: (leave empty for x1...xn): ".format()).split(" ")
    
    print("Input simplex table (separate elements with spaces, rows with new line; leave line empty to end input):")
    while True:
        row = []
        try:
            vals = input().strip()
            if vals == "":
                break
            for val in vals.split(" "):
                row.append(Equation(val))
##                if "/" in val:
##                    val = list(map(int, val.split("/")))
##                    row.append(Fraction(*val))
##                else:
##                    row.append(Fraction(float(val)))
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
        #return (0, [], [])

    if variables == ['']:
        variables = ["x{}".format(i) for i in range(1, col_count)]
    print()
    
    return (ex, variables, l)

def _getStrings(l, getMax=False):
    lp = [[] for i in range(len(l))]
    maxLen = 0
    for r in range(len(l)):
        for v in l[r]:
            #lp[r].append((str(v.numerator) if v.denominator == 1 else str(v.numerator) + "/" + str(v.denominator)))
            lp[r].append(str(v))
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
                    v[col] = l[row][0] * l[row][col]
    return v[1:]

def getValueDict(l):
    global var
    val = getValues(l)
    vd = {}
    for i in range(len(var)):
        if var[i] != "":
            vd[var[i]] = val[i]
    return vd
        

def getValueStrings(l, var):
    global fn
    v = getValues(l)
    #s = [getZ(l[0], v)[0]]
    fn_val = fn.calc(getValueDict(l), True)
    s = [f"fn = {fn_val[0]} = {fn_val[1]} = {fn}"]
    for i in range(len(var)):
        if (var[i] != ""):
            s.append("{} = {}".format(var[i], v[i]))
    return s


def exec_solve_simplex(l, log):
    remove_bases_from_fn(l, log)
    return solve_simplex(l, log)

def get_fn(l, var):
    eq = Equation()
    var = [""] + var
    for i in range(len(var)):
        if var[i] == "" and i != 0:
            continue
        eq += EqElement(-l[i].calc(), {var[i]: 1})
    return eq


def solver(ex, l, log):
    global var, M
    if ex != 0 and log:
        print("\n\tGOT INPUT:")
        print(getMatrix(l), end="\n\n")

    for i in range(len(l[0])):
        if not l[0][i].is_const():
            M.add(i)
    if len(M) != 0: print("M-table detected")
    
    if ex == 1:
        return exec_solve_simplex(l, log)

    elif ex == 2:
        fn_ = l[0]
        var_ = var
        rows = len(l)
        cols = len(fn_)

        var = var + ["y"+str(i) for i in range(1, rows)]

        # identity matrix
        l[0] = ([Equation("0")]*cols) + ([Equation("1")]*(rows-1))
        for r in range(1,rows):
            l[r] = l[r] + ([Equation("0")]*(r-1)) + [Equation("1")] + ([Equation("0")]*(rows-r-1))

        
        if log: print("\tPhase 1\n{}".format(getMatrix(l)))
        if not exec_solve_simplex(l, log): return

        p1_fn = get_fn(l[0], var)
        if p1_fn.calc(getValueDict(l)) != 0:
            print("\nError: unable to solve (fn = {0} = {1} = {2})!".format(*p1_fn.calc(getValueDict(l), True), str(p1_fn)))
            return False

        l[0] = fn_
        var = var_
        for r in range(1, rows):
            l[r] = l[r][:-rows+1]

        
        if log: print("\n\n\tPhase 2\n{}".format(getMatrix(l)))

        return exec_solve_simplex(l, log)

    elif ex == 3:
        fn_ = l[0]
        rows = len(l)
        
        # identity M-matrix
        l[0] += ([Equation("M")]*(rows-1))
        for r in range(1,rows):
            l[r] = l[r] + ([Equation("0")]*(r-1)) + [Equation("1")] + ([Equation("0")]*(rows-r-1))

        if log: print("\tM-table: \n{}".format(getMatrix(l)))

        v = exec_solve_simplex(l, log)
        l[0] = fn_
        return v
        
        
    else:
        print("Error: Unknown solver {}!".format(ex))
        return False
    
    

log = True
#manual_mode = 0
while True:
    l = [[]]
    var = []
    ex = 0
    M = set()
    fn = None

    # calculate
    while ex == 0:
        try:
            ex, var, l = getInput()
        except Exception as e:
            print("Input parsing failed!")
            print(e)
            ex = 0

    print()
    if ex == -1:
        log = not log
        continue

    fn = get_fn(l[0], var)
    solved = solver(ex, l, log)
        
    
    """
    if manual_mode < 2:
        if log: print("Ensuring simplex compatibility...")
        remove_bases_from_fn(l, log)
    if manual_mode < 1:
        if log: print("\n\nSolving...")
        solved = solve_simplex(l, log)
    if manual_mode:
        while True:
            c,r = map(int, input("\nLead element coords (<col> <row>): ").strip().split(" "))
            simplex_move(l, (r,c), True)
    """

    if solved: # print values
        print("\nRaw data:")
        print("\n".join([" ".join(map(str, row)) for row in l]))
        print()
        print("\n".join(getValueStrings(l, var)))
        
    print("\n")
    l = [[]]
