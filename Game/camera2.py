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
        self.setUpCamera()
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        
    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.actor) 
           
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
            self.actor.setH(self.actor.getH() -  (x - base.win.getXSize()/2)*0.1)
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
        return task.cont