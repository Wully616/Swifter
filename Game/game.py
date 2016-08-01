'''
Created on 3 Jul 2016
Game class which sets up the stickman fight game
@author: Wully
'''
import sys
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionHandlerQueue, CollisionRay
from panda3d.core import BitMask32, TextNode
from panda3d.core import NodePath, PandaNode
from panda3d.core import loadPrcFileData
from panda3d.core import Vec3, Vec4, ModifierButtons, Point3, VBase3
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText

from Game.environment import GameWorld
from Game.camera3 import Camera
from Game.player import Swifter
from Game.bulletWorld import bWorld
from Game.bulletController import PandaBulletCharacterController


loadPrcFileData('','win-size 1280 720')
class StickFightGame(ShowBase):
    def __init__(self):
        
        self.renderPipeline = True
        
        if(self.renderPipeline is True):
            # Notice that you must not call ShowBase.__init__ (or super), the render
            # pipeline does that for you.
    
            # Insert the pipeline path to the system path, this is required to be
            # able to import the pipeline classes. In case you placed the render
            # pipeline in a subfolder of your project, you have to adjust this.
           
            sys.path.insert(0, "Game/render_pipeline")
            #sys.path.insert(0, "../../RenderPipeline")
            
            # Import render pipeline classes
            from rpcore import RenderPipeline, SpotLight
    
            # Construct and create the pipeline
            self.render_pipeline = RenderPipeline()
            self.render_pipeline.create(self)
    
            # Done! You can start setting up your application stuff as regular now.
        else:
            ShowBase.__init__(self)
        

                    
        
        #Debug stuff
        self.debug = True
        if(self.debug is True):
            base.setFrameRateMeter(True)
            render.analyze()
            
        #Disable modifiers Shift+Something/Alt+Something/Ctrl+Something
        base.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
        base.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())
        

        #Create bullet world
        self.bWorld = bWorld()
                    
        #Add task to process physics
        taskMgr.add(self.update, 'updateWorld')

        
        #Set up the player
        self.Bcharacter = PandaBulletCharacterController(self.bWorld.world, self.bWorld.worldNP, 1.75, 1.3, 0.5, 0.4)
        self.Bcharacter.setPos(render, Point3(0, 0, 10))
        
        # Parent the player model to the bullet character
        
        player = Swifter("Game/models/swifter",
                         "Game/models/swifter-Run",
                         "Game/models/swifter-Walk",
                         "Game/models/swifter-Idle",
                         "Game/models/swifter-Jump",
                         "Game/models/swifter-IdleCrouch",
                         "Game/models/swifter-WalkCrouch",
                         Vec3(0,0,0),
                         .1)
                         #environ.find("**/start_point").getPos(),.2)
        
        player.actor.clearModelNodes()
        #Reparent the visual actor node path to the bullet collision node path
        #this is so when we move the bullet sphere node path, our actor will move
        
        player.actor.reparentTo(self.Bcharacter.capsuleNP)
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

    #For processing physic updates

    def update(self, task):
        dt = globalClock.getDt()
        
        """ processes character movement    
        self.processInput(dt)
        """
        #Get the characters old position, comes from the bullet Char controller
        oldCharPos = self.Bcharacter.getPos(render)
        
        #Used for the camera in this demo, not needed
        #self.character.setH(base.camera.getH(render))
        
        #Runs the update function in the bullet Char controller
        #It will apply physics and movement and check states
        self.Bcharacter.update() # WIP
        
        newCharPos = self.Bcharacter.getPos(render)
        delta = newCharPos - oldCharPos
        
        self.bWorld.world.doPhysics(dt, 4, 1./120.)
    
        """ processes camera    
        ml.orbitCenter = self.character.getPos(render)
        base.camera.setPos(base.camera.getPos(render) + delta)
        """    
        return task.cont        
          
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


