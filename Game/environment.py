from panda3d.core import AmbientLight, DirectionalLight, Vec4, Fog
from panda3d.core import Texture, TextureStage
from pandac.PandaModules import CompassEffect
from pandac.PandaModules import VBase4, TransparencyAttrib
from direct.interval.LerpInterval import LerpTexOffsetInterval, LerpPosInterval
 
class GameWorld():
    def __init__(self,size,loader,scenegraph,camera):
        self.worldsize = size
        self.loader = loader
        self.render = scenegraph
        
        self.camera = camera
        self.world = self.loader.loadModel("Game/models/world.bam")
        # the model is 1024 already, so we scale accordingly:
        self.world.setScale(self.worldsize/1024)
        self.world.setPos(0,0,0)
        self.world.reparentTo(self.render)
        self.__createEnvironment()
 
    # private method
    def __createEnvironment(self):
        # Fog
        expfog = Fog("scene-wide-fog")
        expfog.setColor(0.5,0.5,0.5)
        expfog.setExpDensity(0.002)
        self.render.setFog(expfog)
 
        # Our sky
        skysphere = self.loader.loadModel('Game/models/blue-sky-sphere')
        skysphere.setEffect(CompassEffect.make(self.render))
        skysphere.setScale(0.08)
        # NOT render or you'll fly through the sky!:
        skysphere.reparentTo(self.camera) 
 
        # Our lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.6, .6, .6, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))
 
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setColor(VBase4(0.8, 0.8, 0.5, 1))
        dlnp = self.render.attachNewNode(directionalLight)
        dlnp.setPos(0,0,260)
        dlnp.setHpr(225,-60,0)#lookAt(self.player)
        self.render.setLight(dlnp)
 
        """# water
        self.water = self.loader.loadModel('Game/models/square.egg')
        self.water.setSx(self.worldsize* 2)
        self.water.setSy(self.worldsize*2)
        self.water.setPos(self.worldsize/2,self.worldsize/2,10) # sea level
        self.water.setTransparency(TransparencyAttrib.MAlpha) 
        nTS = TextureStage('1')
        self.water.setTexture(nTS,self.loader.loadTexture('Game/models/water.png'))
        self.water.setTexScale(nTS,4)
        self.water.reparentTo(self.render)
        LerpTexOffsetInterval(self.water,200,(1,0),(0,0),textureStage=nTS).loop()
 """
    def setGroundMask(self,mask):
        self.world.setCollideMask(mask)
 
    def setWaterMask(self,mask):
        self.water.setCollideMask(mask)
 
    def getSize(self):
        return self.worldsize