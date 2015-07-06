hoodIdMap = {'ttc': .5, 'dd': 1., 'dg': 1.5, 'mm': 2., 'br': 2.7, 'dl': 3.5, 'ff': 4}

def getemblems(hoodId, diff, memos):
    hoodValue = hoodIdMap[hoodId]
    E = (hoodValue * max(memos, 1) * diff) / 2.5
    return divmod(E, 100)

print getemblems('ttc', 3, 40) # (0.0, 24.0)
print getemblems('dd', 4, 15) # (0.0, 24.0)
print getemblems('dg', 7, 35) # (1.0, 47.0)
print getemblems('mm', 8, 60) # (3.0, 84.0)
print getemblems('br', 10, 55) # (5.0, 94.0)
print getemblems('dl', 13, 45) # (8.0, 19.0)
print getemblems('ff', 13, 40) # (8.0, 32.0)
