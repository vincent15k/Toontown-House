from panda3d.core import *
loadPrcFileData('', 'window-type none')
import direct.directbase.DirectStart

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

import random

winnerByTieBreak = 2**28 + 5

trophiesList = []
holeBestList = []
courseBestList = []
cupList = []

rankings = [1, 0, 1, -1]

aimTimesList = [1.53, 356.33, 14003.63214, 666.1134]

for i in xrange(4):
    x = [0]*16 + [1]*16
    random.shuffle(x)
    trophiesList.append(x)
    
for i in xrange(4):
    x = [0]*16 + [1]*16
    random.shuffle(x)
    holeBestList.append(x)
    
for i in xrange(4):
    x = [0]*16 + [1]*16
    random.shuffle(x)
    courseBestList.append(x)
    
for i in xrange(4):
    x = [0]*16 + [1]*16
    random.shuffle(x)
    cupList.append(x)

dg = PyDatagram()
for list in trophiesList:
    dg.addUint8(len(list))
    for item in list:
        dg.addUint8(item)

dg.addUint8(len(rankings))
for item in rankings:
    dg.addInt8(item)
        
for list in holeBestList:
    dg.addUint8(len(list))
    for item in list:
        dg.addUint8(item)
        
for list in courseBestList:
    dg.addUint8(len(list))
    for item in list:
        dg.addUint8(item)

for list in cupList:
    dg.addUint8(len(list))
    for item in list:
        dg.addUint8(item)
        
dg.addUint32(winnerByTieBreak)
for at in aimTimesList:
    dg.addUint32(int(at * 100))
    
dgi = PyDatagramIterator(dg)
print dgi

def _unpackList(method, numItems=4):
    list = []
    
    for i in xrange(numItems):
        size = dgi.getUint8()
        if not size:
            list.append([])
            continue
        
        x = []
        for i in xrange(size):
            x.append(method())
            
        list.append(x)
        
    return list

assert _unpackList(dgi.getUint8) == trophiesList
assert _unpackList(dgi.getInt8, 1)[0] == rankings
assert _unpackList(dgi.getUint8) == holeBestList
assert _unpackList(dgi.getUint8) == courseBestList
assert _unpackList(dgi.getUint8) == cupList
assert dgi.getUint32() == winnerByTieBreak
print [dgi.getUint32() / 100.0 for _ in xrange(4)], aimTimesList
