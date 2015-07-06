# File: G (Python 2.4)

from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
import ZoneUtil
from toontown.classicchars import DistributedGoofySpeedwayAI
from toontown.classicchars import DistributedSuperGoofyAI
from toontown.toonbase import ToontownGlobals
from toontown.racing import DistributedStartingBlockAI
from pandac.PandaModules import *
from toontown.racing.RaceGlobals import *
if __debug__:
    import pdb


class GSHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GSHoodDataAI')
    numStreets = 0
    cycleDuration = 10
    
    def __init__(self, air, zoneId = None):
        hoodId = ToontownGlobals.GoofySpeedway
        if zoneId == None:
            zoneId = hoodId
        self.classicChar = None
        
        HoodDataAI.HoodDataAI.__init__(self, air, zoneId, hoodId)
    
    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        # self.createLeaderBoards()
        self.__cycleLeaderBoards()
        if simbase.config.GetBool('want-goofy', True):
            self.createClassicChar()
    
    def cleanup(self):
        self.notify.debug('cleaning up GSHoodDataAI: %s' % self.zoneId)
        taskMgr.removeTasksMatching(str(self) + '_leaderBoardSwitch')
        for board in self.leaderBoards:
            board.delete()
        
        del self.leaderBoards
    
    def createLeaderBoards(self):
        self.leaderBoards = []
        dnaStore = DNAStorage()
        dnaData = simbase.air.loadDNAFileAI(dnaStore, simbase.air.lookupDNAFileName('goofy_speedway_sz.dna'))
        if isinstance(dnaData, DNAData):
            self.leaderBoards = self.air.findLeaderBoards(dnaData, self.zoneId)
        
        for distObj in self.leaderBoards:
            if distObj:
                if distObj.getName().count('city'):
                    type = 'city'
                elif distObj.getName().count('stadium'):
                    type = 'stadium'
                elif distObj.getName().count('country'):
                    type = 'country'
                
                for subscription in LBSubscription[type]:
                    distObj.subscribeTo(subscription)
                
                self.addDistObj(distObj)
                continue
    
    def __cycleLeaderBoards(self, task = None):
        messenger.send('GS_LeaderBoardSwap' + str(self.zoneId))
        taskMgr.doMethodLater(self.cycleDuration, self.__cycleLeaderBoards, str(self) + '_leaderBoardSwitch')
    
    def createClassicChar(self):
        if ToontownGlobals.HALLOWEEN_COSTUMES in self.air.holidayManager.currentHolidays:
            self.classicChar = DistributedSuperGoofyAI.DistributedSuperGoofyAI(self.air)
            self.classicChar.generateWithRequired(self.zoneId)
            self.classicChar.start()
        else:
            self.classicChar = DistributedGoofySpeedwayAI.DistributedGoofySpeedwayAI(self.air)
            self.classicChar.generateWithRequired(self.zoneId)
            self.classicChar.start()