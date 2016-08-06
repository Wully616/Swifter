'''
Created on 31 Jul 2016
Initializes a bulletWorld
@author: Wully
'''
import sys
import time
from panda3d.bullet import BulletWorld, BulletDebugNode,BulletPlaneShape,BulletRigidBodyNode
from panda3d.bullet import BulletBoxShape, BulletSphereShape, BulletGhostNode
from panda3d.bullet import BulletHelper,  BulletTriangleMesh, BulletTriangleMeshShape
from panda3d.core import Vec3, Vec4, BitMask32, CardMaker, Point3
from direct.task.Task import Task






class bWorld():
    def __init__(self, map):

        # Model
        self.map = map
        # Physics
        self.setup()
        globalClock.setMode(globalClock.MLimited) 
        globalClock.setFrameRate(120.0)
        
        
    def setup(self):
        
        # Setup scene 1: bullet World
        self.worldNP = render.attachNewNode('World')
        
        # Debug bullet nodepath
        self.debugNP = render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.node().showWireframe(True)
        self.debugNP.node().showConstraints(True)
        self.debugNP.node().showBoundingBoxes(False)
        self.debugNP.node().showNormals(True)
        self.debugNP.show()
        
       
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())
        

        
        # Setup scene 2: city
        # Store the visual model in visNP
        visNP = loader.loadModel(self.map)
        visNP.ls()
        #Find all the geom's in the models visual node path;
        #There should only be one so we d ont need to iterate th rough all geoms found
        #This is so we can get the vertex information
        #We want to only find the lowpoly collision mesh geomnodes.
        geomCollect = visNP.findAllMatches('**/=col=1')

        #Create a mesh to store the data.
        mesh = BulletTriangleMesh()
        #loop through all the geoms found and add them to the mesh
        for np in geomCollect:

            ts = np.getTransform(visNP)
            for i in range(np.node().getNumGeoms()):
                geom = np.node().getGeom(i)
                #Add the geom information to the mesh
                #along with transform information from the visual mesh
                mesh.addGeom(geom, True, ts)
        
        #create a physical shape out of the triangle mesh information
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        
        #Create a rigid body node to add the shape too.
        body = BulletRigidBodyNode('City')
        #Attach the city node to the worldNP so its visible
        bodyNP = self.worldNP.attachNewNode(body)
        #Add the shape we created to the node
        bodyNP.node().addShape(shape)
        #bodyNP.node().setMass(0.0)
        bodyNP.setPos(0, 0, 0)
        bodyNP.setCollideMask(BitMask32.allOn())
        #Attach it to the bullet world so its simulated
        self.world.attachRigidBody(bodyNP.node())
        
        #Reparent the visual node to the collision mesh node
        visNPHigh = visNP.find('**/=vis=1')
        visNPHigh.reparentTo(bodyNP)
        
        self.level = bodyNP
        #self.bowlNP.setScale(2)
        
        

        
       
    
    