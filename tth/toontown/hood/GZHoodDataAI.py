# File: G (Python 2.4)

from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.racing import DistributedStartingBlockAI
from pandac.PandaModules import *
from toontown.racing.RaceGlobals import *
from toontown.safezone import DistributedGolfKartAI
import string

class GZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GZHoodDataAI')
    numStreets = 0
    
    def __init__(self, air, zoneId = None):
        hoodId = ToontownGlobals.GolfZone
        if zoneId == None:
            zoneId = hoodId
        
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
