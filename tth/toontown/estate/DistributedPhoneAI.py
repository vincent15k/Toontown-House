from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from toontown.estate.DistributedFurnitureItemAI import DistributedFurnitureItemAI
from PhoneGlobals import *

from toontown.toonbase import ToontownGlobals
from toontown.catalog import CatalogItem, CatalogInvalidItem
from toontown.catalog.CatalogItemList import CatalogItemList

import time

MAX_MAILBOX = 10
MAX_ON_ORDER = 10

def isItemForbidden(item):
    blacklist = ["CatalogGardenStarterItem"]
    if not config.GetBool('want-cannon-rental', True):
        blacklist.append("CatalogRentalItem")
        
    return item.__class__.__name__ in blacklist

class DistributedPhoneAI(DistributedFurnitureItemAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPhoneAI")
    
    def __init__(self, air, furnitureMgr, catalogItem):
        DistributedFurnitureItemAI.__init__(self, air, furnitureMgr, catalogItem)
        self.initialScale = (1, 1, 1)
        self.inUse = False
        self.currAvId = 0
    
    def calcHouseItems(self, avatar):
        houseId = avatar.houseId
        
        if not houseId:
            self.notify.warning('Avatar %s has no houseId associated.' % avatar.doId)
            return 0
            
        house = simbase.air.doId2do.get(houseId)
        if not house:
            self.notify.warning('House %s (for avatar %s) not instantiated.' % (houseId, avatar.doId))
            return 0
            
        mgr = house.interior.furnitureManager
        attic = (mgr.atticItems, mgr.atticWallpaper, mgr.atticWindows)
        numHouseItems = len(CatalogItemList(house.getInteriorItems(), store=CatalogItem.Customization | CatalogItem.Location))
        numAtticItems = sum(len(x) for x in attic)
        
        return numHouseItems + numAtticItems
        
    def setInitialScale(self, scale):
        self.initialScale = scale
    
    def getInitialScale(self):
        return self.initialScale

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if self.inUse:
            self.ejectAvatar(avId)
            return
            
        av = self.air.doId2do.get(avId)
        if av:
            self.setInUse(avId)
            self.sendUpdateToAvatarId(avId, 'setLimits', [self.calcHouseItems(av)])
            self.d_setMovie(PHONE_MOVIE_PICKUP, avId)
            av.b_setCatalogNotify(0, av.mailboxNotify)
            
    def avatarExit(self):
        if not self.inUse:
            self.notify.warning('Requested avatarExit but phone isn\'t in use!')
            return
        avId = self.air.getAvatarIdFromSender()
        if avId != self.currAvId:
            self.notify.warning('Requested avatarExit from unknown avatar %s' %avId)
            return
        self.d_setMovie(PHONE_MOVIE_HANGUP, avId)
        taskMgr.doMethodLater(1, self.resetMovie, self.taskName('resetMovie'))
        self.setFree()
        
    def setFree(self):
        self.inUse = False
        self.currAvId = 0
            
    def setInUse(self, avId):
        self.inUse = True
        self.currAvId = avId
        
    def d_setMovie(self, movie, avId):
        self.sendUpdate('setMovie', [movie, avId, globalClockDelta.getRealNetworkTime()])
            
    def ejectAvatar(self, avId):
        self.sendUpdateToAvatarId(avId, 'freeAvatar', [])
        
    def requestPurchaseMessage(self, context, blob, optional, payMethod):        
        avId = self.air.getAvatarIdFromSender()
        if avId != self.currAvId:
            self.air.writeServerEvent('suspicious', avId, 'tried purchasing item, but not using phone')
            self.notify.warning('%d tried purchasing item, but not using phone' % avId)
            return
            
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId, 'tried purchasing item, but not on shard')
            self.notify.warning('%d tried purchasing item, but not on shard' % avId)
            return
            
        item = CatalogItem.getItem(blob, CatalogItem.Customization)
        if isinstance(item, CatalogInvalidItem.CatalogInvalidItem):
            self.air.writeServerEvent('suspicious', avId, 'tried purchasing invalid item')
            self.notify.warning('%d tried purchasing invalid item' % avId)
            self.sendUpdateToAvatarId(avId, 'requestPurchaseResponse', [context, ToontownGlobals.P_NotInCatalog])
            return
            
        if item in av.backCatalog:
            priceType = CatalogItem.CatalogTypeBackorder
            
        elif item in av.weeklyCatalog or item in av.monthlyCatalog:
            priceType = 0
            
        else:
            self.air.writeServerEvent('suspicious', avId, 'tried purchasing non-existing item')
            self.notify.warning('%d tried purchasing non-existing item' % avId)
            self.sendUpdateToAvatarId(avId, 'requestPurchaseResponse', [context, ToontownGlobals.P_NotInCatalog])
            return
                        
        def _getEmblemPrices():
            if config.GetBool('catalog-emblems-OR', False):
                ep = list(item.getEmblemPrices())
                if len(ep) != 2:
                    return []
                
                if all(ep):
                    ep[payMethod] = 0
                    
            else:
                ep = item.getEmblemPrices()
                
            return ep
            
        def charge():
            ep = _getEmblemPrices()
            if ep:
                av.subtractEmblems(ep)
                
            av.takeMoney(item.getPrice(priceType))
            
        if item in av.onOrder:
            retcode = ToontownGlobals.P_ReachedPurchaseLimit
            
        elif len(av.onOrder) >= MAX_ON_ORDER:
            retcode = ToontownGlobals.P_ReachedPurchaseLimit
            
        elif item.reachedPurchaseLimit(av):
            retcode = ToontownGlobals.P_ReachedPurchaseLimit
            
        elif len(av.mailboxContents) >= MAX_MAILBOX:
            retcode = ToontownGlobals.P_MailboxFull
            
        elif item.getPrice(0) >= av.getTotalMoney():
            retcode = ToontownGlobals.P_NotEnoughMoney
            
        elif not av.isEnoughEmblemsToBuy(_getEmblemPrices()):
            retcode = ToontownGlobals.P_NotEnoughMoney
            
        elif isItemForbidden(item):
            retcode = ToontownGlobals.P_ReachedPurchaseLimit
            
        elif item.__class__.__name__ in ("CatalogChatItem", "CatalogHouseItem") or not item.getDeliveryTime():
            # no mailbox, deliver it already
            retcode = item.recordPurchase(av, optional)
            if retcode == ToontownGlobals.P_ItemAvailable:
                charge()
            
        else:
            retcode = ToontownGlobals.P_ItemOnOrder
            charge()
        
            deliveryTime = item.getDeliveryTime()
            if config.GetBool('want-instant-delivery', False):
                deliveryTime = 0
                
            item.deliveryDate = int(time.time() / 60. + deliveryTime + .5)
            av.onOrder.append(item)
            av.b_setDeliverySchedule(av.onOrder)
        
        self.sendUpdateToAvatarId(avId, 'requestPurchaseResponse', [context, retcode])

    def requestGiftPurchase(self, context, targetDoID, blob, optional):
        # not implemented
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'requestGiftPurchaseResponse', [context, ToontownGlobals.P_NoPurchaseMethod])

    def resetMovie(self, task):
        self.d_setMovie(PHONE_MOVIE_CLEAR, 0)
        return task.done
        