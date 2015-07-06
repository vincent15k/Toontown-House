from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.PyDatagram import PyDatagram

class BanManager(DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManager')

