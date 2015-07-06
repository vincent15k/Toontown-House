from direct.distributed.DistributedObjectUD import DistributedObjectUD
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify import DirectNotifyGlobal
import urllib2

class BanManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerUD')
    BanUrl = simbase.config.GetString('ban-base-url', 'https://api.toontownhouse.net/api_ban.php')
    DoActualBan = simbase.config.GetBool('ban-do-ban', False)
            
    def banUD(self, banner, accountId, time, banReason):
        self.air.csm.getUsername(accountId, lambda username: self.__ban(username, accountId, banner, time, banReason))
        
    def __ban(self, username, accountId, banner, time, banReason):     
        headers = {'User-Agent' : 'TTHBanManager'}
        
        bannerLevel = self.air.friendsManager.getToonAccess(banner)
        bannerName = self.air.friendsManager.getToonName(banner)
        
        if bannerLevel == 0:
            # Toon attempted to ban himself
            return
        
        data = "target=%s" % username
        data += "&time=%s" % time
        data += "&banner=%s (%s): %s" % (bannerName, banner, bannerLevel)
        data += "&reason=%s" % banReason
        data += "&anticacheagent=%s" % id(username)        
        
        if self.DoActualBan:
            try:
                data += "&key=%s" % self.air.getApiKey()
                req = urllib2.Request(self.BanUrl, data, headers)
                res = urllib2.urlopen(req).read()
                print res
            
            except:
                raise
                self.notify.warning('Failed to ban %s!' % username)
                return

        self.notify.info("%s (%d/%d) banned %s for %s hours: %s" % (bannerName, banner, bannerLevel, username, time, banReason))
                
        for doId, access in self.air.friendsManager.toonAccess.items():
            if access >= bannerLevel:
                self.sendToAv(self.GetPuppetConnectionChannel(doId),
                              '%s (%d): %d' % (bannerName, banner, bannerLevel),
                              username, time, banReason)
                                
    def _makeAvMsg(self, values, recipient):
        msg = "%s banned %s for %s hours: %s" % values
        
        msgDg = PyDatagram()
        msgDg.addUint16(6)
        msgDg.addString(msg)

        dg = PyDatagram()
        dg.addServerHeader(recipient, self.air.ourChannel, CLIENTAGENT_SEND_DATAGRAM)
        dg.addString(msgDg.getMessage())
        return dg

    def sendToAv(self, avId, *values):
        dg = self._makeAvMsg(values, avId)
        self.air.send(dg)
