from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify import DirectNotifyGlobal
import urllib2

class BanManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerAI')
        
    def ban(self, banner, target, time, reason):
        dg = PyDatagram()
        dg.addServerHeader(target.GetPuppetConnectionChannel(target.doId), self.air.ourChannel, CLIENTAGENT_EJECT)
        dg.addUint16(152)
        dg.addString('You were banned by a moderator!')
        self.air.send(dg)
        self.sendUpdateToChannel(100000, "banUD", [banner, target.DISLid, time, reason])
        