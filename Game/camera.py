from pandac.PandaModules import PandaNode,NodePath,Camera,TextNode
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay, BitMask32
from direct.task.Task import Task
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