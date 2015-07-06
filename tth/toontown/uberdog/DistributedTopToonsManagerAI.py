from direct.distributed.DistributedObjectAI import *
import TopToonsGlobals

class DistributedTopToonsManagerAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
                
        self.currentSeed = 0
        self.currentChallenge = None
        self.accept("topToonsManager-UD-newChallenge", lambda x, y: self.setData(*y))   
        
    def sendUpdate(self, *args):
        self.sendUpdateToChannel(100000, *args)
    
    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.sendUpdate("requestData", [])
        taskMgr.doMethodLater(10, self.__sendNullScore, self.taskName("sendNullScore"))
        
    def setData(self, challengeSeed, ranking, history, startTime):
        self.notify.debug('DistributedTopToonsManagerAI: setData %d' % challengeSeed)
        self.currentSeed = challengeSeed
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        self.ranking = ranking
        
    def d_score(self, avId, score):
        av = self.air.doId2do.get(avId)
        if not av:
            return
            
        self.sendUpdate("score", [self.currentSeed, avId, score, av.getName()])
        
    def applyReward(self, avId, amount):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        
        av.addMoney(amount)

    def toonKilledCogs(self, av, suits):
        score = sum(1 for suit in suits if self.currentChallenge.doesCogCount(suit))
        if score:
            self.d_score(av.doId, score)
        
    def toonKilledBldg(self, av, track, height):
        bldg = {'track': track, 'height': height}
        if self.currentChallenge.doesBuildingCount(bldg):
            self.d_score(av.doId, 1)
            
    def toonKilledOffice(self, av, track):
        if self.currentChallenge.doesOfficeCount(track):
            self.d_score(av.doId, 1)
            
    def toonKilledFactory(self, av, factory):
        if self.currentChallenge.doesFactoryCount(factory):
            self.d_score(av.doId, 1)
            
    def toonKilledBoss(self, av, boss):
        if self.currentChallenge.doesBossCount(boss):
            self.d_score(av.doId, 1)
            
    def __sendNullScore(self, task):
        """
        Sends a null score every 10 seconds to the UD.
        This forces sync.
        """
        
        self.sendUpdate("score", [self.currentSeed, 0, 0, "none"])
        return task.cont
            
from otp.ai.MagicWordGlobal import *
@magicWord(access=1000, types=[int])
def chs(score):
    av = spellbook.getTarget()
    mgr = av.air.topToonsMgr
    if not mgr:
        return "No manager!"
        
    mgr.d_score(av.doId, score)
    