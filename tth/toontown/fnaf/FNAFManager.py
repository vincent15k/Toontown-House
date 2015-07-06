from toontown.toonbase import ToontownGlobals
from direct.showbase.DirectObject import *

class FNAFManager(DirectObject):    
    def __init__(self):
        self._isPlaying = False
        
    def enterMinigame(self):        
        place = base.cr.playGame.getPlace()
        
        if not hasattr(place, 'debugStartMinigame'):
            base.cr.doFind("DistributedSuitInvasionManager").displayMsgs(["ERROR: Redeem this code at a playground!"])
            return
        
        self._isPlaying = True
        
        localAvatar.b_setParent(ToontownGlobals.SPHidden)
        self.__hoodId = place.loader.hood.id        
        place.debugStartMinigame(1, 1234)
        
        localAvatar.laffMeter.obscure(1)
        localAvatar.chatMgr.fsm.request('otherDialog')
        
        base.camera.reparentTo(render)
        base.camera.iPosHprScale()
        
        self.accept("FNAF-gameComplete", self.__handleGameDone)
        base.startGame()
        
    def __handleGameDone(self):
        # XXX to do: reward??
        self.leaveMinigame()
        
    def leaveMinigame(self):
        base.leaveGame()
        self.ignore("FNAF-gameComplete")
        
        self._isPlaying = False
        
        base.cam.iPosHprScale()
        
        localAvatar.laffMeter.obscure(0)
        localAvatar.chatMgr.fsm.request('mainMenu')
        base.cr.playGame.enter(self.__hoodId, self.__hoodId, 0)
        
    def isPlaying(self):
        return self._isPlaying
        