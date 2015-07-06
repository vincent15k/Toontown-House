from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.hood import SkyUtil
from toontown.toon import Toon, ToonDNA, LaffMeter
from toontown.toonbase import TTLocalizer, ToontownGlobals

COLORS = (Vec4(0.917, 0.164, 0.164, 1),
 Vec4(0.152, 0.75, 0.258, 1),
 Vec4(0.598, 0.402, 0.875, 1),
 Vec4(0.133, 0.59, 0.977, 1),
 Vec4(0.895, 0.348, 0.602, 1),
 Vec4(0.977, 0.816, 0.133, 1))
 
PLAY = TTLocalizer.AvatarChoicePlayThisToon.upper().replace('\n', ' ')
MAKE = TTLocalizer.AvatarChoiceMakeAToon.upper().replace('\n', ' ')

class DeleteFrame(DirectLabel):
    def __init__(self, position=0, name="this toon"):
        DirectLabel.__init__(self, image=DGG.getDefaultDialogGeom(), relief=None)
        self.initialiseoptions(DeleteFrame)

        self.position = position
        
        self.blockingFrame = DirectFrame(frameColor=(0, 0, 0, .6),frameSize=(10, -10, 1, -1),
                                         state=DGG.NORMAL, parent=self)

        self.textDict = {"name": name, "confirm": TTLocalizer.AvatarChoiceDeleteConfirmUserTypes}
        _text = TTLocalizer.AvatarChoiceDeleteConfirmText % self.textDict

        self._text = OnscreenText(text=_text, scale=.065, parent=self, wordwrap=.75 / .065, pos = (0, .36))
        self.entry = DirectEntry(parent=self._text, scale=.1, width=8,
                                 numLines=1, focus=1, pos=(-.4, 0, -.215),
                                 relief=DGG.RIDGE, command=self.__ok)

        self.stText = OnscreenText(text="", scale=.4, parent=self.entry, pos=(-.3, -1),
                                   align=TextNode.ALeft, wordwrap=23)

        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okImageList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
        cancelImageList = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
        
        self.okButt = DirectButton(parent=self, geom=okImageList,
                                   command=self.__ok, scale=1.25,
                                   relief=None, pos=(-.1,0,-.41))

        self.cancelButt = DirectButton(parent=self, geom=cancelImageList,
                                       command=self.removeNode, scale=1.25,
                                       relief=None, pos=(.1,0,-.41))

        self.resetFrameSize()
        self.reparentTo(self.getParent())

    def __ok(self, text = None):
        if text is None:
            text = self.entry.get()
            
        if text == TTLocalizer.AvatarChoiceDeleteConfirmUserTypes:
            self.__success()

        else:
            self.stText.setText(TTLocalizer.AvatarChoiceDeleteWrongConfirm % self.textDict)
            self.stText['fg'] = (1, 0, 0, 1)
            self.entry["state"] = DGG.NORMAL

    def __success(self):
        self.removeNode()
        messenger.send(self._ctpScr.doneEvent, [{"mode": "delete"}])

class NewPickAToon:
    def __init__(self, avList, parentFSM, doneEvent):
        self.toonsList = {i: (i in [x.position for x in avList]) for i in xrange(6)}
        self.avList = avList
        
        self.currentSlot = 0
        self.doneEvent = doneEvent

    def load(self, isPaid=1):
        self.patNode = render.attachNewNode('patNode')
        self.pat2dNode = aspect2d.attachNewNode('pat2dNode')
        
        self.background = loader.loadModel('phase_3/models/newpat/terrain.bam')
        self.background.reparentTo(self.patNode)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')

        self.infoText = OnscreenText(font=ToontownGlobals.getSignFont(), text=TTLocalizer.AvatarChooserPickAToon,
                                     scale=TTLocalizer.ACtitle, fg=COLORS[self.currentSlot], pos=(0, .855),
                                     parent=self.pat2dNode)
                                     
        arrow = loader.loadModel("phase_3/models/props/arrow.bam")
        self.arrowRight = DirectButton(geom=arrow, relief=None, command=self.__right)
        self.arrowRight.reparentTo(self.pat2dNode)
        self.arrowRight.setPos(.6, 0, -.2)
        self.arrowRight.setScale(.255)
        self.arrowRight.setColor(1, 1, 0, 1)
        
        self.arrowLeft = DirectButton(geom=arrow, relief=None, command=self.__left)
        self.arrowLeft.reparentTo(self.pat2dNode)
        self.arrowLeft.setPos(-.6, 0, -.2)
        self.arrowLeft.setR(180)
        self.arrowLeft.setScale(.255)
        self.arrowLeft.setColor(1, 0, 0, 1)

        self.origin = self.patNode.attachNewNode('toon-origin')
        self.origin.reparentTo(self.patNode)
        self.origin.setPos(-50,-11,3.5)
        self.origin.setHpr(180, 0, 0)
        self.origin.setScale(1.5)
        
        self.matText = OnscreenText(pos=(0, -.155), text=TTLocalizer.AvatarChoiceMakeAToon,
                                    font=ToontownGlobals.getMinnieFont(), fg=(1, 1, 0, 1),
                                    parent=self.pat2dNode, scale=.135, shadow=(0,0,0,1))
                                    
        bdes = loader.loadModel('phase_3/models/gui/quit_button.bam')
        self.play = DirectButton(relief=None, geom=(bdes.find("**/QuitBtn_UP"), bdes.find("**/QuitBtn_DN"),
                                                    bdes.find("**/QuitBtn_RLVR"),bdes.find("**/QuitBtn_UP")),
                                 text=PLAY, text_scale=.050, text_pos=(0, -0.013), scale=1.3,
                                 pos=(.8, 0, -.6), command=self.startGame, parent=self.pat2dNode)
        
        self.name = OnscreenText(pos=(0, -.5), scale=.1, fg=COLORS[self.currentSlot], parent=self.pat2dNode,
                                 shadow=(0,0,0,1), font=ToontownGlobals.getToonFont())
        self.area = OnscreenText(parent=self.pat2dNode, font=ToontownGlobals.getToonFont(),
                                 pos=(-.7, -.855), scale=.075, text="", shadow=(0,0,0,1), fg=COLORS[self.currentSlot])

        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui.bam')
        self.deleteButton = DirectButton(parent=self.pat2dNode, geom=(trashcanGui.find('**/TrashCan_CLSD'),
                                                                      trashcanGui.find('**/TrashCan_OPEN'),
                                                                      trashcanGui.find('**/TrashCan_RLVR')),
                                        text=('',TTLocalizer.AvatarChoiceDelete,TTLocalizer.AvatarChoiceDelete,''), text_scale=.150, text_pos=(0,-0.3), relief=None, scale=0.45,
                                        command=self.__handleDelete, pos=(1, 0, -.735))
                                        
        self.toon = Toon.Toon()
        self.toon.reparentTo(self.origin)
        self.toon.setDNAString(ToonDNA.ToonDNA().makeNetString()) # initialize with garbage
        self.toon.hide()
        
        self.statusText = OnscreenText(pos=(0, -.8), text="", font=ToontownGlobals.getToonFont(),
                                       fg=(0, 0, 0, 1), parent=self.pat2dNode, scale=.075)
                                       
        self.nameYourToonButton = DirectButton(relief=None, geom=(bdes.find("**/QuitBtn_UP"), bdes.find("**/QuitBtn_DN"),
                                                                  bdes.find("**/QuitBtn_RLVR"),bdes.find("**/QuitBtn_UP")),
                                               text=TTLocalizer.AvatarChoiceNameYourToon.upper().replace('\n', ' '),
                                               text_scale=.045, text_pos=(0, -0.013), scale=1.3, pos=(.8, 0, -.47), command=self.__nameIt,
                                               parent=self.pat2dNode)
    
    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)
    
    def enter(self):
        base.cam.setPos(-50,-27,6.5)
        base.cam.setHpr(0,4,0)
 
        SkyUtil.startCloudSky(self)
        
        self.patNode.unstash()
        self.pat2dNode.unstash()
        
        self.__updateMainButton()
        self.__updateFunction()
        
    def exit(self):
        base.cam.iPosHpr()
 
        taskMgr.remove('skyTrack')
        self.sky.reparentTo(hidden)
        
        self.patNode.stash()
        self.pat2dNode.stash()
        
    def unload(self):
        self.patNode.removeNode()
        self.pat2dNode.removeNode()
        
        del self.patNode
        del self.pat2dNode
        
    def __left(self):
        self.currentSlot -= 1
        
        if self.currentSlot == 0:
            self.arrowLeft.setColor(1, 0, 0, 1)
            
        elif self.currentSlot < 0:
            self.currentSlot = 0
            
        else:
            self.arrowRight.setColor(1, 1, 0, 1)
            self.arrowLeft.setColor(1, 1, 0, 1)
            
        self.__updateFunction()
            
    def __right(self):
        self.currentSlot += 1
        
        if self.currentSlot == 5:
            self.arrowRight.setColor(1, 0, 0, 1)
            
        elif self.currentSlot > 5:
            self.currentSlot = 5
            
        else:
            self.arrowLeft.setColor(1, 1, 0, 1)
            self.arrowRight.setColor(1, 1, 0, 1)
            
        self.__updateFunction()
    
    def __updateFunction(self):
        self.infoText['fg'] = COLORS[self.currentSlot]
        self.name['fg'] = COLORS[self.currentSlot]
        self.area['fg'] = COLORS[self.currentSlot]
                
        if hasattr(self, 'laffmeter'):
            self.laffmeter.destroy()
            del self.laffmeter
            
        hasToon = self.toonsList[self.currentSlot]
        if hasToon:
            self.matText.hide()
            self.showToon()
            self.deleteButton.show()
            
        else:
            self.name['text'] = ''
            self.area['text'] = ''
            self.deleteButton.hide()
            self.matText.show()
            self.toon.hide()
            self.nameYourToonButton.hide()
            self.statusText['text'] = ''
            
        self.__updateMainButton()
    
    def showToon(self):        
        av = [x for x in self.avList if x.position == self.currentSlot][0]
        dna = av.dna
        
        if av.wantName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameReview
        
        elif av.approvedName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameApproved
        
        elif av.rejectedName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameRejected
        
        elif av.allowedName == 1:
            self.nameYourToonButton.show()
            self.statusText['text'] = ''
                
        else:
            self.nameYourToonButton.hide()
            self.statusText['text'] = ''
               
        self.toon.setDNAString(dna)
        self.toon.loop('neutral')
        self.toon.show()
            
        self.laffmeter = LaffMeter.LaffMeter(ToonDNA.ToonDNA(dna), av.hp, av.maxHp)
        self.laffmeter.setPos(-.7, 0, -.655)
        self.laffmeter.setScale(self.laffmeter, .8)
        self.laffmeter.start()
        self.laffmeter.reparentTo(self.pat2dNode)
        
        self.name.setText(av.name.decode("latin-1"))

        lastAreaName = ToontownGlobals.hoodNameMap.get(av.lastHood, [""])[-1]
        self.area.setText(lastAreaName)
        
    def __updateMainButton(self):
        if self.toonsList[self.currentSlot]:
            self.play['text'] = PLAY
            self.play['command'] = self.startGame
            
        else:
            self.play['text'] =  MAKE
            self.play['command'] = self.startMAT
    
    def startGame(self):
        doneStatus = {"mode": "chose", "choice": self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])

    def startMAT(self):
        doneStatus = {"mode": "create", "choice": self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])
        
    def getStatus(self):
        return self.doneStatus
        
    def __handleDelete(self):
        av = [x for x in self.avList if x.position == self.currentSlot][0]
        DeleteFrame(position=self.currentSlot, name=av.name)._ctpScr = self
        
    def __nameIt(self):
        doneStatus = {"mode": "nameIt", "choice": self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])
        
    def getChoice(self):
        return self.currentSlot
        