"""Roamers is a simple demo consisting of:

   * A 3D environment
   * A keyboard-controlled animated player character (class Character)
   * A 3rd-person camera that follows the player (class Camera)
   * And some non-player characters with their own animated avatars 
     (class Agent)

   The main class that initialises everything is the Game class.
   
   Roamers is based on Panda3D's Tut-Roaming-Ralph.py by Ryan Myers and uses
   models and animations from Panda3D's collection.
   
   Classes:
   Camera -- A 3rd-person floating camera that follows an actor around.
   Character -- An animated, 3D character that moves in response to control
                settings. These control settings can be used by a deriving
                class to create non-playe character behaviours (as in class
                Agent_ or can be hooked up to keyboard keys to create a
                player character (see Game.__init__()).
   Agent -- A computer-controlled extension of Character.
   Game -- The game world: environment, characters, camera, onscreen text and
           keyboard controls.
   """

import direct.directbase.DirectStart
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import Filename
from pandac.PandaModules import PandaNode,NodePath,Camera,TextNode
from pandac.PandaModules import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math

# Figure out what directory this program is in.
MYDIR=os.path.abspath(sys.path[0])
MYDIR=Filename.fromOsSpecific(MYDIR).getFullpath()

class Camera:
    
    """A floating 3rd person camera that follows an actor around, and can be
    turned left or right around the actor.

    Public fields:
    self.controlMap -- The camera's movement controls.
    actor -- The Actor object that the camera will follow.
    
    Public functions:
    init(actor) -- Initialise the camera.
    move(task) -- Move the camera each frame, following the assigned actor.
                  This task is called every frame to update the camera.
    setControl -- Set the camera's turn left or turn right control on or off.
    
    """

    def __init__(self,actor):
        """Initialise the camera, setting it to follow 'actor'.
        
        Arguments:
        actor -- The Actor that the camera will initially follow.
        
        """
        
        self.actor = actor
        self.prevtime = 0

        # The camera's controls:
        # "left" = move the camera left, 0 = off, 1 = on
        # "right" = move the camera right, 0 = off, 1 = on
        self.controlMap = {"left":0, "right":0}

        taskMgr.add(self.move,"cameraMoveTask")

        # Create a "floater" object. It is used to orient the camera above the
        # target actor's head.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)        

        # Set up the camera.

        base.disableMouse()
        base.camera.setPos(self.actor.getX(),self.actor.getY()+10,2)

        # A CollisionRay beginning above the camera and going down toward the
        # ground is used to detect camera collisions and the height of the
        # camera above the ground. A ray may hit the terrain, or it may hit a
        # rock or a tree.  If it hits the terrain, we detect the camera's
        # height.  If it hits anything else, the camera is in an illegal
        # position.

        self.cTrav = CollisionTraverser()
        self.groundRay = CollisionRay()
        self.groundRay.setOrigin(0,0,1000)
        self.groundRay.setDirection(0,0,-1)
        self.groundCol = CollisionNode('camRay')
        self.groundCol.addSolid(self.groundRay)
        self.groundCol.setFromCollideMask(BitMask32.bit(1))
        self.groundCol.setIntoCollideMask(BitMask32.allOff())
        self.groundColNp = base.camera.attachNewNode(self.groundCol)
        self.groundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.groundColNp, self.groundHandler)

        # Uncomment this line to see the collision rays
        #self.groundColNp.show()
      
    def move(self,task):
        """Update the camera's position before rendering the next frame.
        
        This is a task function and is called each frame by Panda3D. The
        camera follows self.actor, and tries to remain above the actor and
        above the ground (whichever is highest) while looking at a point
        slightly above the actor's head.
        
        Arguments:
        task -- A direct.task.Task object passed to this function by Panda3D.
        
        Return:
        Task.cont -- To tell Panda3D to call this task function again next
                     frame.
        
        """

        # FIXME: There is a bug with the camera -- if the actor runs up a
        # hill and then down again, the camera's Z position follows the actor
        # up the hill but does not come down again when the actor goes down
        # the hill.

        elapsed = task.time - self.prevtime

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.
         
        base.camera.lookAt(self.actor)
        camright = base.camera.getNetTransform().getMat().getRow3(0)
        camright.normalize()
        if (self.controlMap["left"]!=0):
            base.camera.setPos(base.camera.getPos() - camright*(elapsed*20))
        if (self.controlMap["right"]!=0):
            base.camera.setPos(base.camera.getPos() + camright*(elapsed*20))

        # If the camera is too far from the actor, move it closer.
        # If the camera is too close to the actor, move it farther.

        camvec = self.actor.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Keep the camera at one foot above the terrain,
        # or two feet above the actor, whichever is greater.
        
        entries = []
        for i in range(self.groundHandler.getNumEntries()):
            entry = self.groundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.actor.getZ() + 2.0):
            base.camera.setZ(self.actor.getZ() + 2.0)
            
        # The camera should look in the player's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above the player's head.
        
        self.floater.setPos(self.actor.getPos())
        self.floater.setZ(self.actor.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        # Store the task time and continue.
        self.prevtime = task.time
        return Task.cont

    def setControl(self, control, value):
        """Set the state of one of the camera's movement controls.
        
        Arguments:
        See self.controlMap in __init__.
        control -- The control to be set, must be a string matching one of
                   the strings in self.controlMap.
        value -- The value to set the control to.
        
        """

        # FIXME: this function is duplicated in Camera and Character, and
        # keyboard control settings are spread throughout the code. Maybe
        # add a Controllable class?
        
        self.controlMap[control] = value

class Character:
    
    """A character with an animated avatar that moves left, right or forward
       according to the controls turned on or off in self.controlMap.
    
    Public fields:
    self.controlMap -- The character's movement controls
    self.actor -- The character's Actor (3D animated model)
    
    
    Public functions:
    __init__ -- Initialise the character
    move -- Move and animate the character for one frame. This is a task
            function that is called every frame by Panda3D.
    setControl -- Set one of the character's controls on or off.
    
    """

    def __init__(self, model, run, walk, startPos, scale):        
        """Initialise the character.
        
        Arguments:
        model -- The path to the character's model file (string)
           run : The path to the model's run animation (string)
           walk : The path to the model's walk animation (string)
           startPos : Where in the world the character will begin (pos)
           scale : The amount by which the size of the model will be scaled 
                   (float)
                   
           """

        self.controlMap = {"left":0, "right":0, "forward":0}

        self.actor = Actor(MYDIR+model,
                                 {"run":MYDIR+run,
                                  "walk":MYDIR+walk})        
        self.actor.reparentTo(render)
        self.actor.setScale(scale)
        self.actor.setPos(startPos)

        taskMgr.add(self.move,"moveTask") # Note: deriving classes DO NOT need
                                          # to add their own move tasks to the
                                          # task manager. If they override
                                          # self.move, then their own self.move
                                          # function will get called by the
                                          # task manager (they must then
                                          # explicitly call Character.move in
                                          # that function if they want it).
        self.prevtime = 0
        self.isMoving = False

        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.groundRay = CollisionRay()
        self.groundRay.setOrigin(0,0,1000)
        self.groundRay.setDirection(0,0,-1)
        self.groundCol = CollisionNode('ralphRay')
        self.groundCol.addSolid(self.groundRay)
        self.groundCol.setFromCollideMask(BitMask32.bit(1))
        self.groundCol.setIntoCollideMask(BitMask32.allOff())
        self.groundColNp = self.actor.attachNewNode(self.groundCol)
        self.groundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.groundColNp, self.groundHandler)

        # Uncomment this line to see the collision rays
        # self.groundColNp.show()

        #Uncomment this line to show a visual representation of the 
        #collisions occuring
         self.cTrav.showCollisions(render)

    def move(self, task):
        """Move and animate the character for one frame.
        
        This is a task function that is called every frame by Panda3D.
        The character is moved according to which of it's movement controls
        are set, and the function keeps the character's feet on the ground
        and stops the character from moving if a collision is detected.
        This function also handles playing the characters movement
        animations.

        Arguments:
        task -- A direct.task.Task object passed to this function by Panda3D.
        
        Return:
        Task.cont -- To tell Panda3D to call this task function again next
                     frame.
        """
        
        elapsed = task.time - self.prevtime

        # save the character's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.actor.getPos()

        # move the character if any of the move controls are activated.

        if (self.controlMap["left"]!=0):
            self.actor.setH(self.actor.getH() + elapsed*300)
        if (self.controlMap["right"]!=0):
            self.actor.setH(self.actor.getH() - elapsed*300)
        if (self.controlMap["forward"]!=0):
            backward = self.actor.getNetTransform().getMat().getRow3(1)
            backward.setZ(0)
            backward.normalize()
            self.actor.setPos(self.actor.getPos() - backward*(elapsed*5))

        # If the character is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.controlMap["forward"]!=0) or (self.controlMap["left"]!=0) or (self.controlMap["right"]!=0):
           
            if self.isMoving is False:
                self.actor.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.actor.stop()
                self.actor.pose("walk",5)
                self.isMoving = False

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust the character's Z coordinate.  If the character's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.groundHandler.getNumEntries()):
            entry = self.groundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.actor.setPos(startpos)

        # Store the task time and continue.
        self.prevtime = task.time
        return Task.cont

    def setControl(self, control, value):
        """Set the state of one of the character's movement controls.
        
        Arguments:
        See self.controlMap in __init__.
        control -- The control to be set, must be a string matching one of
                   the strings in self.controlMap.
        value -- The value to set the control to.
        
        """

        # FIXME: this function is duplicated in Camera and Character, and
        # keyboard control settings are spread throughout the code. Maybe
        # add a Controllable class?
        
        self.controlMap[control] = value

class Agent(Character, DirectObject):
    """A computer-controlled non-player character.
    
    This class derives from Character.
    
    New public fields:
    None.
    
    New public functions:
    None.
    
    Functions extended from Character:
    __init__ -- Initialise some private fields.
    move -- Make the character run around randomly.
    
    """
    
    def __init__(self,model,run,walk,startPoint,scale):
        """Initialise the character.
        
        Initialises private fields used to control the character's behaviour.
        Also see Character.__init__().
        
        Arguments:
        See Character.__init__().
        
        """
        
        Character.__init__(self, model, run, walk, startPoint, scale)
        self.prevTurnTime = 0
        self.setControl('forward',1)
    
    def move(self,task):
        """Update the character for one frame.
        
        Pick a new direction for the character to turn in every second.
        Also see Character.move().
        
        Arguments:
        See Character.move().
        
        Return:
        See Character.move().
        
        """
        
        if task.time - self.prevTurnTime >= 1:
            import random
            direction = random.randint(1,3)
            if direction == 1:
                self.setControl('left',1)
                self.setControl('right',0)
            elif direction == 2:
                self.setControl('left',0)
                self.setControl('right',1)
            elif direction == 3:
                self.setControl('left',0)
                self.setControl('right',0)
            self.prevTurnTime = task.time
        return Character.move(self,task)

class Game(DirectObject):
    """The game world -- environment, characters, camera, onscreen  text and
    keyboard controls.
    
    Public functions:
    _init__ -- Initialise the game environment, characters, camera, onscreen
               text and keyboard controls.
    
    """
    
    def __init__(self):
        """Initialise the game environment and characters."""
    
        # Post some onscreen instructions.

        title = addTitle("Panda3D Tutorial: Roaming Ralph (Walking on Uneven Terrain)")
        inst1 = addInstructions(0.95, "[ESC]: Quit")
        inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        inst4 = addInstructions(0.80, "[Up Arrow]: Run Ralph Forward")
        inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")

        # Initialise the environment.

        base.win.setClearColor(Vec4(0,0,0,1))
        environ = loader.loadModel(MYDIR+"/models/world/world")      
        environ.reparentTo(render)
        environ.setPos(0,0,0)    
        environ.setCollideMask(BitMask32.bit(1))

        # Create a character for the player.

        player = Character("/models/ralph/ralph",
                        "/models/ralph/ralph-run",
                        "/models/ralph/ralph-walk",
                        environ.find("**/start_point").getPos(),
                        .2)
                        
        # Hook up some control keys to the character
        
        self.accept("arrow_left", player.setControl, ["left",1])
        self.accept("arrow_right", player.setControl, ["right",1])
        self.accept("arrow_up", player.setControl, ["forward",1])
        self.accept("arrow_left-up", player.setControl, ["left",0])
        self.accept("arrow_right-up", player.setControl, ["right",0])
        self.accept("arrow_up-up", player.setControl, ["forward",0])

        # Create a camera to follow the player.

        camera = Camera(player.actor)
    
        # Accept some keys to move the camera.

        self.accept("a-up", camera.setControl, ["left",0])
        self.accept("s-up", camera.setControl, ["right",0])
        self.accept("a", camera.setControl, ["left",1])
        self.accept("s", camera.setControl, ["right",1])
                        
        # Create some non-player characters.
        
        rex = Agent("/models/trex/trex",
                        "/models/trex/trex-run",
                        "/models/trex/trex-run",
                        environ.find("**/start_point").getPos(),
                        .2)

        eve = Agent("/models/eve/eve",
                        "/models/eve/eve-walk",
                        "/models/eve/eve-run",
                        environ.find("**/start_point").getPos(),
                        .2)    
    
        # Accept the Esc key to quit the game.
    
        self.accept("escape", sys.exit)

def addInstructions(pos, msg):
    """Put 'msg' on the screen at position 'pos'."""
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
            pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

def addTitle(text):
    """Put 'text' on the screen as the title."""
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
        
if __name__ == "__main__":        
    
    game = Game()
    run()