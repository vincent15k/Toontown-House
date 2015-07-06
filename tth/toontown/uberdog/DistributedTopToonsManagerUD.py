from direct.distributed.DistributedObjectUD import *
import TopToonsGlobals
import time, cPickle, os, random

class DistributedTopToonsManagerUD(DistributedObjectUD):
    cacheFile = config.GetString('top-toons-cache-file', 'databases/air_cache/toptoons.dat')
    
    def __init__(self, air):
        DistributedObjectUD.__init__(self, air)
        
        if os.path.isfile(self.cacheFile):
            with open(self.cacheFile, "rb") as f:
                data = f.read()
                if data:
                    data = cPickle.loads(data)
                    
                else:
                    data = {}

        else:
            data = {}
            
        self.currentSeed = data.get('currentSeed', int(time.time()))
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        
        defaultRanking = []
        defaultHistory = []
        
        if config.GetBool('top-toons-fake-toons', False):
            for i in xrange(20):
                avId = 0
                name = "Fake Toon %d" % (i + 1)
                score = int(self.currentChallenge.getAmount() * random.random())
                defaultRanking.append([avId, name, score])
                
            defaultRanking.sort(key=lambda x: x[2])
            
            for i in xrange(20):
                name = "Fake History Toon %d" % (i + 1)
                tim = random.randint(600, 180000)
                seed = int(i + time.time())
                defaultHistory.append([name, tim, seed])
        
        self.history = data.get('history', defaultHistory)
        self.ranking = data.get('ranking', defaultRanking)
        self.ranking.sort(key=lambda x: x[2])
        self.__startTime = data.get('startTime', time.time())
        self.save()
        
        self.aiChannels = set()
        
    def announceGenerate(self):
        DistributedObjectUD.announceGenerate(self)
        self.d_updateData()
        
    def newChallenge(self, winnerName):
        self.history.append([winnerName, int(time.time() - self.__startTime), self.currentSeed])
        
        self.currentSeed = int(time.time())
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        self.ranking = []
        self.__startTime = time.time()
        
    def save(self):
        data = {}
        data['currentSeed'] = self.currentSeed
        data['history'] = self.history
        data['ranking'] = self.ranking
        data['startTime'] = self.__startTime
        data = cPickle.dumps(data)
        
        with open(self.cacheFile, "wb") as f:
            f.write(data)
        
    def requestData(self):
        channel = self.air.getMsgSender()
        if channel < 500000000:
            # Bad way to test if it's an AI
            self.aiChannels.add(channel)
            
        # print 'requestData', channel
        self.d_updateData(channel)
        
    def d_updateData(self, channel=None):
        if channel is None:
            channel = 10
            
        self.sendUpdateToChannel(channel, "setData", [self.currentSeed, self.ranking, self.history, self.__startTime])
        if channel == 10:
            # Need to update the AIs
            
            for ch in self.aiChannels:
                self.d_updateData(ch)
        
    def score(self, challengeSeed, avId, score, name):
        self.aiChannels.add(self.air.getMsgSender())
        
        if challengeSeed != self.currentSeed:
            self.d_updateData(self.air.getMsgSender())
            return
            
        if avId == 0:
            return
            
        for i, (_avId, _, _score) in enumerate(self.ranking):
            if _avId == avId:
                _score += score
                break
                
        else:
            self.ranking.append(None)
            _score = score
            i = -1
            
        self.ranking[i] = [avId, name, _score]
            
        # print 'SCORE', avId, score, _score, self.currentChallenge, self.currentChallenge.getAmount()
            
        if _score >= self.currentChallenge.getAmount():
            self.d_notifyWinner(avId, name)
            self.sendUpdateToChannel(self.air.getMsgSender(), 'applyReward', [avId, self.getReward()])
            self.newChallenge(name)
            
        else:
            # sort ranking                
            self.ranking.sort(key=lambda x: x[2])
                
        self.d_updateData()
        self.save()
        
    def d_notifyWinner(self, doId, name):
        self.sendUpdateToChannel(10, "notifyWinner", [name, doId])
        
    def __getName(self, avId):
        return self.air.friendsManager.getToonName(avId)

    def getReward(self):
        return self.currentChallenge.reward
        