'''
Created on 2 Aug 2016
bulletKCC Camera
Used to control a third person mouse controlled camera.
It will rotate the provided bullet kinematic character controller based on mouse movement
@author: Wully
'''
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import CollisionTraverser,CollisionNode,CollisionSegment
from panda3d.core import CollisionHandlerQueue,CollisionRay, BitMask32
from panda3d.core import Point3,Vec3
from direct.task.Task import Task
from panda3d.core import WindowProperties
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

    def __init__(self,bController):
        """Initialise the camera, setting it to follow 'actor'.
        
        Arguments:
        bController -- The bullet character controller that the camera will initially follow.
        
        """
        #Get the node path for the CC
        self.bController = bController
        self.actor = bController.capsuleNP
        self.prevtime = 0
        self.setUpCamera()
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        
    def setUpCamera(self):
        """ puts camera behind the player in third person """
        
        
        # Set up the camera
        # Adding the camera to actor is a simple way to keep the camera locked
        # in behind actor regardless of actor's movement.
        base.camera.reparentTo(self.actor)
        # We don't actually want to point the camera at actors's feet.
        # This value will serve as a vertical offset so we can look over the actor
        self.cameraTargetHeight = 0.5
        # How far should the camera be from the actor
        self.cameraDistance = 10
        # Initialize the pitch of the camera
        self.cameraPitch = 45
        
        # The mouse moves rotates the camera so lets get rid of the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        
        #set up FOV
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        
        # A CollisionRay beginning above the camera and going down toward the
        # ground is used to detect camera collisions and the height of the
        # camera above the ground. A ray may hit the terrain, or it may hit a
        # rock or a tree.  If it hits the terrain, we detect the camera's
        # height.  If it hits anything else, the camera is in an illegal
        # position.
        """
TODO::        This will need to be changed to bullet
        """
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
        
        # We will detect anything obstructing the camera's view of the player

        self.cameraRay = CollisionSegment((0,0,self.cameraTargetHeight),(0,5,5))
        self.cameraCol = CollisionNode('cameraRay')
        self.cameraCol.addSolid(self.cameraRay)
        self.cameraCol.setFromCollideMask(BitMask32.bit(0))
        self.cameraCol.setIntoCollideMask(BitMask32.allOff())
        self.cameraColNp = self.actor.attachNewNode(self.cameraCol)
        self.cameraColHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.cameraColNp, self.cameraColHandler)
        # Uncomment this line to see the collision rays
        #self.groundColNp.show()  
        
         
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        
        elapsed = task.time - self.prevtime
        startpos = self.actor.getPos()
        #get the camera to look at the actor
        #base.camera.lookAt(self.actor)

        #Move the camera left/right
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            
            #turns the actor
            """
            Needs to be changed to move the bullet CC node
            """
            #turns the camera
            self.bController.setH(self.bController.getH() -  (x - base.win.getXSize()/2)*0.1)
            
            #calculate camera pitch
            self.cameraPitch = self.cameraPitch + (y - base.win.getYSize()/2)*0.1
            if (self.cameraPitch < -60): self.cameraPitch = -60
            if (self.cameraPitch >  80): self.cameraPitch =  80
            base.camera.setHpr(0,self.cameraPitch,0)
               
            """
            # set the camera at around actor's middle
            # We should pivot around here instead of the view target which is noticebly higher
            
            """
            #What should the camera pivot around?
            
            base.camera.setPos(0,0,self.cameraTargetHeight) #target head
            #base.camera.setPos(0,0,self.cameraTargetHeight/2) #target body
            
            # back the camera out to its proper distance
            base.camera.setY(base.camera,self.cameraDistance)
            
        # point the camera at the view target
        viewTarget = Point3(0,0,self.cameraTargetHeight)
        base.camera.lookAt(viewTarget)
        # reposition the end of the  camera's obstruction ray trace
        self.cameraRay.setPointB(base.camera.getPos())    

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
            self.actor.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.actor.setPos(startpos)
            
        # We will detect anything obstructing the camera via a ray trace
        # from the view target around the avatar's head, to the desired camera
        # position. If the ray intersects anything, we move the camera to the
        # the first intersection point, This brings the camera in between its
        # ideal position, and any present obstructions.  
        """
TODO::        This will need to be changed to bullet
        """ 
        entries = []
        for i in range(self.cameraColHandler.getNumEntries()):
            entry = self.cameraColHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(-y.getSurfacePoint(self.actor).getY(),
                                     -x.getSurfacePoint(self.actor).getY()))
        if (len(entries)>0):
            collisionPoint =  entries[0].getSurfacePoint(self.actor)
            collisionVec = ( viewTarget - collisionPoint)
            if ( collisionVec.lengthSquared() < self.cameraDistance * self.cameraDistance ):
                base.camera.setPos(collisionPoint)
                if (entries[0].getIntoNode().getName() == "terrain"):
                    base.camera.setZ(base.camera, 0.2)
                base.camera.setY(base.camera, 0.3)
        
        
        return task.cont