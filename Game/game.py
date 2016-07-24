'''
Created on 3 Jul 2016
Game class which sets up the stickman fight game
@author: Wully
'''

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import CollisionTraverser, CollisionNode, CollisionHandlerPusher
from pandac.PandaModules import CollisionSphere, CollisionHandlerQueue, CollisionRay
from panda3d.core import BitMask32, TextNode
from panda3d.core import NodePath, PandaNode
from panda3d.core import loadPrcFileData
from panda3d.core import Vec3, Vec4, ModifierButtons
from direct.actor.Actor import Actor
from pandac.PandaModules import VBase3
from direct.gui.OnscreenText import OnscreenText
import sys
from environment import GameWorld
from camera3 import Camera
from player import Swifter


loadPrcFileData('','win-size 1024 768')
class StickFightGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Notice that you must not call ShowBase.__init__ (or super), the render
        # pipeline does that for you.

        # Insert the pipeline path to the system path, this is required to be
        # able to import the pipeline classes. In case you placed the render
        # pipeline in a subfolder of your project, you have to adjust this.
        """
        sys.path.insert(0, "./Game/render_pipeline")
        #sys.path.insert(0, "../../RenderPipeline")

        # Import render pipeline classes
        from rpcore import RenderPipeline, SpotLight

        # Construct and create the pipeline
        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)

        # Done! You can start setting up your application stuff as regular now.
        """   
        #Disable modifiers Shift+Something/Alt+Something/Ctrl+Something
        base.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        base.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())
        

        
        base.win.setClearColor(Vec4(0,0,0,1))
        environ = self.loader.loadModel("Game/models/world")      
        environ.reparentTo(self.render)
        environ.setPos(0,0,0)    
        environ.setCollideMask(BitMask32.bit(1))
        
        player = Swifter("Game/models/swifter",
                         "Game/models/swifter-Run",
                         "Game/models/swifter-Walk",
                         "Game/models/swifter-Idle",
                         "Game/models/swifter-Jump",
                         "Game/models/swifter-IdleCrouch",
                         "Game/models/swifter-WalkCrouch",
                         environ.find("**/start_point").getPos(),.2)
        
        self.keyboardSetup(player)
        
        # Create a camera to follow the player.
        #base.oobe()  
        camera = Camera(player.actor)
    
        # Accept some keys to move the camera.
        """
        self.accept("g-up", camera.setControl, ["left",0])
        self.accept("h-up", camera.setControl, ["right",0])
        self.accept("g", camera.setControl, ["left",1])
        self.accept("h", camera.setControl, ["right",1])
        """
        # Accept the Esc key to quit the game.
    
        self.accept("escape", sys.exit)   
          
        
        

    """      
    def mouseUpdate(self,task):
       
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, self.win.getXSize()/2, self.win.getYSize()/2):
            self.node.setH(self.node.getH() -  (x - self.win.getXSize()/2)*0.1)
            self.camera.setP(self.camera.getP() - (y - self.win.getYSize()/2)*0.1)
        return task.cont
    

    
    
    """    

        
          
    def keyboardSetup(self,player):
        #Turn of shift/ctl/alt modifiers

        #setup keyboard inputs
        self.accept("escape", sys.exit)
        
        #movement
        self.accept("a", player.setMove, ["left","strafe_left"])
        self.accept("a-up", player.setMove, ["stop","strafe_left"])
        self.accept("d", player.setMove, ["right","strafe_right"])
        self.accept("d-up", player.setMove, ["stop","strafe_right"])
        self.accept("w", player.setMove, ["forward","forward"])
        self.accept("w-up", player.setMove, ["stop","forward"])
        self.accept("s", player.setMove, ["back","back"])
        self.accept("s-up", player.setMove, ["stop","back"])
    
        #modifyers / jumping
        self.accept("lcontrol", player.setMove, [True,"crouch"])
        self.accept("lcontrol-up", player.setMove, [False,"crouch"])
        self.accept("lshift", player.setMove, [True,"sprint"])
        self.accept("lshift-up", player.setMove, [False,"sprint"])
        self.accept("space", player.setMove, [True,"jump"])
        self.accept("space-up", player.setMove, [False,"jump"])
        
        #Set up mouse controls
        
        self.accept("mouse1", player.setMove, [True,"punch"])
        self.accept("mouse1-up", player.setMove, [False,"punch"])
        self.accept("mouse2", player.setMove, [True,"kick"])
        self.accept("mouse2-up", player.setMove, [False,"kick"])        


