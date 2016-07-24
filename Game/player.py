'''
Created on 3 Jul 2016
Defines the different player types we have in Swifter
@author: Wully
'''
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3,Vec4,BitMask32
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from direct.task.Task import Task
from controller import ActorFSM

class Swifter:
    def __init__(self, model, run, walk, idle, jump, crouch, crouchWalk, startPos, scale):
         #(self, model, run, walk, startPos, scale):
        """Initialise the character.
        
        Arguments:
        model -- The path to the character's model file (string)
           run : The path to the model's run animation (string)
           walk : The path to the model's walk animation (string)
           startPos : Where in the world the character will begin (pos)
           scale : The amount by which the size of the model will be scaled 
                   (float)
                   
           """
        
        #Define movement map and speeds
        self.speedSprint = 20
        self.speedWalk = 7
        self.speedCrouch = 5
        self.speed = self.speedWalk
        #Capture control status
        self.isMoving = False
        self.isJumping = False
        self.isIdle = False
        self.isCrouching = False
        
        self.movementMap = {"forward":Vec3(0,-self.speed,0), "back":Vec3(0,self.speed,0), \
                            "left":Vec3(self.speed,0,0), "right":Vec3(-self.speed,0,0), \
                            "crouch":0, "sprint":0, "jump":1, "punch":0, "kick":0, "stop":Vec3(0), "changeView":0}
        
        #Set up key state variables
        self.strafe_left = self.movementMap["stop"]
        self.strafe_right = self.movementMap["stop"]
        self.forward = self.movementMap["stop"]
        self.back = self.movementMap["stop"]
        self.jump = False
        self.sprint = False
        self.crouch = False
        
        #Stop player by default
        self.walk = self.movementMap["stop"]
        self.strafe = self.movementMap["stop"]
           
        #Define the actor and his animations
        self.actor = Actor(model,
                           {"run":run,
                            "walk":walk,
                            "idle":idle,
                            "jump":jump,
                            "crouch":crouch,
                            "crouchWalk":crouchWalk})
        
        
        #self.actor.enableBlend()
       
        self.actor.setBlend(frameBlend = True)#Enable interpolation
        self.actor.reparentTo(render)
        self.actor.setScale(scale)
        self.actor.setPos(startPos)
        
        #Set up FSM controller
        self.FSM = ActorFSM(self.actor)
        
        
        
        taskMgr.add(self.move,"moveTask") # Note: deriving classes DO NOT need
                                          # to add their own move tasks to the
                                          # task manager. If they override
                                          # self.move, then their own self.move
                                          # function will get called by the
                                          # task manager (they must then
                                          # explicitly call Character.move in
                                          # that function if they want it).
    
        self.prevtime = 0
        
        

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
        self.groundCol = CollisionNode('actorRay')
        self.groundCol.addSolid(self.groundRay)
        self.groundCol.setFromCollideMask(BitMask32.bit(1))
        self.groundCol.setIntoCollideMask(BitMask32.allOff())
        self.groundColNp = self.actor.attachNewNode(self.groundCol)
        self.groundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.groundColNp, self.groundHandler)

        # Uncomment this line to see the collision rays
        self.groundColNp.show()

        #Uncomment this line to show a visual representation of the 
        #collisions occuring
        self.cTrav.showCollisions(render)
    """    
    def jumpUpdate(self,task):
        # this task simulates gravity and makes the player jump 
        # get the highest Z from the down casting ray
        
        highestZ = -100
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(self.render).getZ()
            if z > highestZ and entry.getIntoNode().getName() == "Cube":
                highestZ = z
        # gravity effects and jumps
        self.node.setZ(self.node.getZ()+self.jump*globalClock.getDt())
        self.jump -= 1*self.globalClock.getDt()
        if highestZ > self.node.getZ()-.3:
            self.jump = 0
            self.node.setZ(highestZ+.3)
            if self.readyToJump:
                self.jump = 1
        return task.cont    
    """
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
 

        #Calculate stateful movement
        
        self.walk = self.forward + self.back
        self.strafe = self.strafe_left + self.strafe_right

        
        # move the character if any of the move controls are activated.
        self.actor.setPos(self.actor,self.walk*globalClock.getDt()*self.speed)
        self.actor.setPos(self.actor,self.strafe*globalClock.getDt()*self.speed)
        
        #If strafing rotate the model -90 / 90 degrees to go in the direction specified
        #if going backwards rotate model 180 degrees

        # If the character is moving, loop the run animation.
        # If he is standing still, stop the animation.
        
        ##CALLL CONTROLLER CLASS AND CALL FSM's INSTEAD OF DOING IT HERE
        
        #Decide what type of movement anim to use
        
        if(self.sprint is True):
            #If we are sprinting..
            self.walkAnim = 'Run'
            self.speed = self.speedSprint
        elif(self.crouch is True): # Can't sprint while crouching ;)
            #If we are crouching..
            print "Crouching!"
            self.walkAnim = "CrouchWalk"
            self.idleAnim = "Crouch"
            self.speed = self.speedCrouch
        else:
            #Otherwise were walking..
            self.walkAnim = 'Walk'
            self.idleAnim = 'Idle'
            self.speed = self.speedWalk
            
            
        #Idling
        if(self.isJumping is False and self.isMoving is False and self.isIdle is True and self.FSM.state != self.idleAnim):
            #If were not moving and not jumping and were supposed to be idle, play the idle anim if we aren't already
            self.FSM.request(self.idleAnim,1)
            
            #We are idle, feel free to do something else, setting isIdle = False.
            print "We are Idle but ready to do something: isIdle = False"
            
        elif(self.isJumping is False and self.isMoving is False and self.isIdle is False):
            #If were not moving or jumping, were not  doing anything, we should probably be idle if we aren't already          
            self.isIdle = True

        
        #locomotion           
        #TODO: Separate out into animations for forward, back and side stepping
        if( (self.walk != self.movementMap["stop"] or self.strafe != self.movementMap["stop"]) and self.isJumping is False):
            #Check if actor is walking forward/back
            if(self.walk != self.movementMap["stop"]):
                if(self.isMoving is False or self.FSM.state != self.walkAnim):
                    self.isMoving = True # were now moving
                    self.isIdle = False # were not idle right now 
                    self.FSM.request(self.walkAnim,1)
                    print "Started running or walking"
            #Check if actor is strafing
            if(self.strafe != self.movementMap["stop"]):
                if(self.isMoving is False or self.FSM.state != self.walkAnim):
                    #MAKE THE NODE ROTATE SO THE LEGS POINT THE DIRECTION MOVING
                    #myLegRotate = actor.controlJoint(None,"modelRoot",)
                    #http://www.panda3d.org/manual/index.php/Controlling_a_Joint_Procedurally
                    self.isMoving = True # were now moving
                    self.isIdle = False # were not idle right now 
                    self.FSM.request(self.walkAnim,1)
                    print "Started running or walking"    
        elif(self.isMoving is True and self.isIdle is False):
            #Only switch of isMoving if we were moving and not idle
            self.isMoving = False
            print "Finished walking"
            
                  
            #if were moving, set isMoving = 1 and call walking FSM
        
            
        '''
        Jumping
        
        Check if the user is jumping, if they currently aren't jumping:
        make them not idle and mark them as jumping and request the Jump FSM.
        
        If the jump anim isn't playing but we were jumping, mark actor as not jumping.
        
        '''     
        if(self.jump is True):
            #if user pressed jump and were not already jumping, jump
            if(self.isJumping is False and self.FSM.state != 'Jump'):
                self.isJumping = True # were jumping 
                self.isIdle = False # were not idle right now
                self.FSM.request('Jump',1)
                print "Started jumping"
        
        #if we are jumping, check the anim has finished and stop jumping
        self.JumpQuery = self.actor.getAnimControl('jump')
        if(self.isJumping is True and self.JumpQuery.isPlaying() is False):
            self.isJumping = False # finished jumping
            print "Finished Jumping"
        
                

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
            
    def setMove(self, key, moveType):
        """ Used by keyboard setup 
            This gets the input from keyBoardSetup and will capture inputs
        """
        if (moveType == "strafe_left"):
            self.strafe_left = self.movementMap[key]
        if (moveType == "strafe_right"):
            self.strafe_right = self.movementMap[key]
        if (moveType == "forward"):
            self.forward = self.movementMap[key]
        if (moveType == "back"):
            self.back = self.movementMap[key]
        if (moveType == "sprint"):
            self.sprint = key
        if (moveType == "jump"):
            self.jump = key
        if (moveType == "crouch"):
            self.crouch = key