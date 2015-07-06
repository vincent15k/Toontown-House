from direct.distributed.DistributedObjectAI import *
from direct.distributed.PyDatagram import *
import cPickle

class ControlMessageAI(DistributedObjectAI):
    """
    This is a special message that State Servers can use to communicate (like NetMessenger).
    Because there's no default UD -> AIs messaging mechanism, this was created.
    Currently, you must specify explicit target channel. To do: channel 12 (see Astron issue #294)
    """
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.origin = 0
        self.targets = []
        self.eventName = "controlMessage"
        self.data = []
        
    def setOrigin(self, origin):
        self.origin = origin
        
    def getOrigin(self):
        return self.origin
        
    def setTargets(self, channels):
        self.targets = channels
    
    def getTargets(self):
        return self.targets
        
    def setEventName(self, eventName):
        self.eventName = eventName
        
    def getEventName(self):
        return self.eventName
        
    def setData(self, data):
        self.data = cPickle.loads(data)
        
    def getData(self):
        return cPickle.dumps(self.data)
        
    def setRawData(self, data):
        self.data = data
        
    def getRawData(self):
        return self.data
        
    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        
        forUs = False
        if self.air.ourChannel in self.targets:
            forUs = True
            
        elif self.air.serverId in self.targets:
            forUs = True
            
        elif 12 in self.targets:
            forUs = True
            
        if forUs:
            print 'ControlMessageAI for us from', self.getOrigin(), self.eventName, self.data
            messenger.send(self.eventName, [self, self.data])
            
    def doSend(self, targets, origin=None):
        if origin is None:
            origin = self.air.ourChannel
            
        self.setOrigin(origin)
        self.setTargets(targets)
        
        for target in targets:
            dg = self.dclass.aiFormatGenerate(self, self.air.allocateChannel(), 0, 0, target, self.air.serverId, [])
            self.air.send(PyDatagram(dg.getMessage()[17:]))
        