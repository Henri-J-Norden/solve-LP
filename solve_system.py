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

# performs the transformation in place
def gauss(l, col=0, log=False):
    print("Column " + str(col+1))
    for r in range(len(l)):
        print("Row " + str(r+1))
        if len(l) <= col or l[col][col] == 0 or l[r][col] == 0:
            continue
        if r == col:
            _div(l[r], l[r][col])
            print(getMatrix(l))
            continue
        subtract = _div(l[col], Fraction(l[col][col], l[r][col]), True)
        _sub(l[r], subtract)
        print(getMatrix(l))
    if len(l[0]) > col+2:
        gauss(l, col+1)

def isComplete(l):
    for r in range(len(l)):
        for c in range(len(l)):
            if r == c:
                if l[r][c] != 1:
                    return False
                continue
            if l[r][c] != 0:
                return False
    return True

def getInput():
    size = [int(input("Matrix rows: "))]
    cols = input("Matrix columns (leave empty for " + str(size[0]+1) + "): ")
    if len(cols) == 0:
        size.append(size[0] + 1)
    else:
        size.append(int(cols))
    l = [[] for i in range(size[0])]
    if size[0] < 2 or size[1] <= size[0]:
        print("<rows> must be larger than 2 and <cols> must be larger <rows> + 1!")
        return l
    for i in range(size[0]):
        while True:
            l[i] = []
            try:
                vals = input("Row " + str(i+1) + ": ")
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
    return l

def _getStrings(l, getMax=False):
    lp = [[] for i in range(len(l))]
    maxLen = 0
    for r in range(len(l)):
        for v in l[r]:
            lp[r].append((str(v.numerator) if v.denominator == 1 else str(v.numerator) + "/" + str(v.denominator)))
            maxLen = max(maxLen, len(lp[r][-1]))
    return lp if not getMax else (lp, maxLen)

def getMatrix(l):
    lp, maxLen = _getStrings(l, True)
    ls = []
    formatStr = "{: >" + str(maxLen) + "}  "
    print(len(lp))
    print(len(lp[0]))
    s = formatStr * (len(lp[0]) - 1) + "| " + formatStr
    for r in range(len(l)):
        ls.append(s.format(*lp[r]))
    return "\n".join(ls)


l = [[]]
while True:
    # calculate
    while len(l[0]) == 0:
        try:
            l = getInput()
        except:
            print("Input parsing failed!")
    gauss(l)
    if not isComplete(l):
        l1 = l.copy()
        gauss(l)
        while l1 != l:
            l1 = l.copy()
            gauss(l)

    # print values
    print()
    if isComplete(l):
        lp = _getStrings(l)
        for i in range(len(l)):
            print("Value col " + str(i+1) + ": " + " ".join(lp[i][len(lp):]))
    else:
        print("Complete transmutation failed!")
        print(getMatrix(l))
    l = [[]]
    print("\n")
        
        
    
    

        
     
