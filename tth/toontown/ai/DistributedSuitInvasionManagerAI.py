from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify import DirectNotifyGlobal

from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA

import random

class DistributedSuitInvasionManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedSuitInvasionManagerAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        
        self.skel = False
        self.curInvading = None
        
        self.startTime = 0
        self.duration = 0
        
    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        
        if not self.air.wantMegaInvasions:
            return
        
        def testInvasion(holidayId, suitIndex):
            if self.air.holidayManager.isHolidayRunning(holidayId):
                suitName = SuitDNA.suitHeadTypes[suitIndex]
                self.notify.info('Starting mega invasion of %s' % suitName)
                self.startInvasion(suitName, skel=self.air.holidayManager.isHolidayRunning(ToontownGlobals.SKELECOG_INVASION), mega=True)
                return 1
            
        if testInvasion(ToontownGlobals.MR_HOLLYWOOD_INVASION, 31):
            return

        if testInvasion(ToontownGlobals.YES_MAN_INVASION, 2):
            return
        
        if testInvasion(ToontownGlobals.TIGHTWAD_INVASION, 18):
            return

        if testInvasion(ToontownGlobals.TELEMARKETER_INVASION, 25):
            return

        if testInvasion(ToontownGlobals.HEADHUNTER_INVASION, 5):
            return

        if testInvasion(ToontownGlobals.SPINDOCTOR_INVASION, 13):
            return

        if testInvasion(ToontownGlobals.MONEYBAGS_INVASION, 21):
            return

        if testInvasion(ToontownGlobals.TWOFACES_INVASION, 29):
            return

        if testInvasion(ToontownGlobals.MINGLER_INVASION, 30):
            return

        if testInvasion(ToontownGlobals.LOANSHARK_INVASION, 22):
            return

        if testInvasion(ToontownGlobals.CORPORATE_RAIDER_INVASION, 6):
            return

        if testInvasion(ToontownGlobals.ROBBER_BARON_INVASION, 23):
            return

        if testInvasion(ToontownGlobals.LEGAL_EAGLE_INVASION, 14):
            return
        
        if testInvasion(ToontownGlobals.BIG_WIG_INVASION, 15):
            return
        
        if testInvasion(ToontownGlobals.BIG_CHEESE_INVASION, 7):
            return
        
        if testInvasion(ToontownGlobals.DOWN_SIZER_INVASION, 4):
            return
        
        if testInvasion(ToontownGlobals.MOVER_AND_SHAKER_INVASION, 28):
            return
        
        if testInvasion(ToontownGlobals.DOUBLETALKER_INVASION, 10):
            return
        
        if testInvasion(ToontownGlobals.PENNY_PINCHER_INVASION, 17):
            return
        
        if testInvasion(ToontownGlobals.NAME_DROPPER_INVASION, 26):
            return
        
        if testInvasion(ToontownGlobals.AMBULANCE_CHASER_INVASION, 11):
            return
        
        if testInvasion(ToontownGlobals.MICROMANAGER_INVASION, 3):
            return
        
        if testInvasion(ToontownGlobals.NUMBER_CRUNCHER_INVASION, 20):
            return
            
        if testInvasion(ToontownGlobals.BLOODSUCKER_INVASION, 9):
            return
        
    def getCurrentInvasion(self):
        name = self.curInvading or ""
        return (name, self.skel, False, self.startTime, self.duration)
        
    def getInvadingCog(self):
        return (self.curInvading, self.skel)
        
    def hasInvading(self):
        return self.skel or (self.curInvading != None)
        
    def startInvasion(self, suitName=None, skel=False, mega=False):
        self.withdrawAllCogs()
        
        skel = bool(skel)
        mega = bool(mega)
        
        self.skel = skel
        self.curInvading = suitName if suitName != "" else None
        
        self.startTime = globalClockDelta.localToNetworkTime(globalClock.getRealTime(), bits = 32)
        
        if not mega:
            self.duration = int(random.random() * 600 + 300) # 5 - 15 mins
            taskMgr.doMethodLater(self.duration, self.__stop, self.taskName('end-invasion'))
            
        else:
            self.duration = 1
        
        self.sendUpdate("startInvasion", [suitName or "", skel, 0, self.startTime, self.duration])
        self.sendUpdate("setCurrentInvasion", self.getCurrentInvasion())
        
        self.notify.info("Invasion started: %s (%s); duration = %s secs" % (suitName, skel, self.duration))
        messenger.send("startInvasion")
        
    def __stop(self, task = None):
        self.withdrawAllCogs()
        
        self.skel = False
        self.curInvading = None
        self.startTime = self.duration = 0
        
        self.sendUpdate("invasionOver", [])
        self.sendUpdate("setCurrentInvasion", self.getCurrentInvasion())
        
        messenger.send("endInvasion")
        
        if task:
            self.notify.info("Invasion is over")
            return task.done
            
    def withdrawAllCogs(self):
        for planner in self.air.suitPlanners.values():
            planner.flySuits()
            
    def abort(self):
        self.notify.info("Invasion aborted")
        taskMgr.remove(self.taskName('end-invasion'))
        self.__stop(None)
        
    def isMega(self):
        return self.hasInvading() and self.duration == 1
            
from otp.ai.MagicWordGlobal import *
@magicWord(types = [int], access = 400)
def invasion(index = -1):
    av = spellbook.getInvoker()
    dsi = av.air.suitInvasionManager
    
    if not -1 <= index <= 31:
        return "Invalid value! Must be between -1 (stop inv) and 31!"
        
    if index == -1:
        if not dsi.hasInvading():
            return "No invasion in progress!"
            
        elif dsi.isMega():
            return "Current invasion is mega. Use ~megainv controls!"
            
        else:
            dsi.abort()
    
    else:
        if dsi.hasInvading():
            return "An invasion is already progress! Use ~invasion -1 to stop it!"
            
        else:
            dsi.startInvasion(SuitDNA.suitHeadTypes[index])

@magicWord(access = 500)
def invasionext():
    dsi = simbase.air.suitInvasionManager
        
    if dsi.hasInvading():
        return "An invasion is already progress! Use ~invasion -1 to stop it!"
            
    dsi.startInvasion(suitName = None, skel = True)
   
@magicWord(access = 1000, types=[int])   
def megainv(index = -1):
    av = spellbook.getInvoker()
    dsi = av.air.suitInvasionManager
    
    if not -1 <= index <= 31:
        return "Invalid value! Must be between -1 (stop inv) and 31!"
        
    if index == -1:
        if not dsi.isMega():
            return "Cannot stop current invasion (if any): not mega! Use ~invasion controls!"
            
        dsi.abort()
        
    else:
        if dsi.hasInvading():
            return "An invasion is already progress! Use ~invasion -1 to stop it!"
            
        dsi.startInvasion(SuitDNA.suitHeadTypes[index], mega=True)
        return "Successfully started mega invasion!"
        