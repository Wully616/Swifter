'''
Created on 3 Jul 2016
Creates the Actor along with the animations.
@author: Wully
'''
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3,Vec4,BitMask32
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from direct.task.Task import Task
from Game.playerFSM import ActorFSM

class Player:
    def __init__(self, bController, model, scale):
         #(self, model, run, walk, startPos, scale):
        """Initialise the character.
        
        Arguments:
        bController -- The bullet character controller assigned to this player
        model -- The path to the character's model file (string)
                  
        """
        self.bController = bController
        #Define movement map and speeds
        self.speedSprint = 20
        self.speedWalk = 5
        self.speedCrouch = 5
        self.speed = self.speedWalk
        #Capture control status
        """
        Handled by bulletController?
        """
        self.isMoving = False
        self.isJumping = False
        self.isIdle = False
        self.isCrouching = False
        
        self.movementMap = {"forward":Vec3(0,-self.speed,0), 
                            "back":Vec3(0,self.speed,0),
                            "left":Vec3(self.speed,0,0),
                            "right":Vec3(-self.speed,0,0),
                            "crouch":0, 
                            "sprint":0, 
                            "jump":1, 
                            "punch":0, 
                            "kick":0, 
                            "stop":Vec3(0), 
                            "changeView":0
                            }
        
        #Set up key state variables
        self.strafe_left = self.movementMap["stop"]
        self.strafe_right = self.movementMap["stop"]
        self.forward = self.movementMap["stop"]
        self.back = self.movementMap["stop"]
        self.jump = False
        self.sprint = False
        self.crouch = False
        
        #Stop player by default
        self.move = self.movementMap["stop"]

           
        #Define the actor and his animations
        self.actor = Actor(model,
                           {"run":model + "-Run",
                            "walk":model + "-Walk",
                            "idle":model + "-Idle",
                            "jump":model + "-Jump",
                            "idleCrouch":model + "-IdleCrouch",
                            "walkCrouch":model + "-WalkCrouch"})
        
        
        #self.actor.enableBlend()
        
        self.actor.clearModelNodes()
        #Reparent the visual actor node path to the bullet collision node path
        #this is so when we move the bullet sphere node path, our actor will move
        
        self.actor.reparentTo(self.bController.capsuleNP)
        
        self.actor.setBlend(frameBlend = True)#Enable interpolation
        #self.actor.reparentTo(render)
        self.actor.setScale(scale)
        
        #Set up FSM controller
        self.FSM = ActorFSM(self.actor, self.bController)
        
        
        
        taskMgr.add(self.processInput,"processInput") 

    def processInput(self, task):

        #Calculate movement & do animations and stuff
        
        self.move = self.forward + self.back + self.strafe_right + self.strafe_left 
        
        # move the character if any of the move controls are activated.
        self.bController.setLinearMovement(self.move, True)
        
        
        
        """
#############################################################################        
        CALL CONTROLLER CLASS AND CALL FSM's INSTEAD OF DOING IT HERE
#############################################################################  
        """
        
        #Decide what type of movement anim to use
        
        if(self.sprint is True):
            #If we are sprinting..
            self.walkAnim = 'Run'
            self.speed = self.speedSprint
        elif(self.crouch is True): # Can't sprint while crouching ;)
            #If we are crouching..
            print ("Crouching!")
            self.walkAnim = "WalkCrouch"
            self.idleAnim = "IdleCrouch"
            self.speed = self.speedCrouch
        else:
            #Otherwise were walking..
            self.walkAnim = 'Walk'
            self.idleAnim = 'Idle'
            self.speed = self.speedWalk
            
        """ 
        Idling
        """
        if(self.isJumping is False and self.isMoving is False and self.isIdle is True and self.FSM.state != self.idleAnim):
            #If were not moving and not jumping and were supposed to be idle, play the idle anim if we aren't already
            self.FSM.request(self.idleAnim,1)
            
            #We are idle, feel free to do something else, setting isIdle = False.
            print ("We are Idle but ready to do something: isIdle = False")
            
        elif(self.isJumping is False and self.isMoving is False and self.isIdle is False):
            #If were not moving or jumping, were not  doing anything, we should probably be idle if we aren't already          
            self.isIdle = True
        
        """
        Locomotion
        """      
        #TODO: Separate out into animations for forward, back and side stepping
        if(self.move != self.movementMap["stop"] and self.isJumping is False):
            #Check if actor is walking forward/back
            if(self.move != self.movementMap["stop"]):
                if(self.isMoving is False or self.FSM.state != self.walkAnim):
                    self.isMoving = True # were now moving
                    self.isIdle = False # were not idle right now 
                    self.FSM.request(self.walkAnim,1)
                    print ("Started running or walking")
        elif(self.isMoving is True and self.isIdle is False):
            #Only switch of isMoving if we were moving and not idle
            self.isMoving = False
            print ("Finished walking")
            
                  
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
                print ("Started jumping")
        
        #if we are jumping, check the anim has finished and stop jumping
        self.JumpQuery = self.actor.getAnimControl('jump')
        if(self.isJumping is True and self.JumpQuery.isPlaying() is False):
            self.isJumping = False # finished jumping
            print ("Finished Jumping")

        """
#############################################################################        
        CALL CONTROLLER CLASS AND CALL FSM's INSTEAD OF DOING IT HERE
#############################################################################  
        """        
        
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