'''
Created on 18 Jul 2016

@author: Wully
'''

from direct.fsm.FSM import FSM
 
class ActorFSM(FSM):
    
    def __init__(self, actor):
        FSM.__init__(self, 'Character')
        #get the actor that we want to move.
        self.actor = actor
        self.defaultTransitions = {
            'Walk' : [ 'Run', 'Jump', 'Idle', 'Crouch', 'CrouchWalk'],
            'CrouchWalk' : [ 'Run', 'Jump', 'Idle', 'Crouch', 'Walk'],
            'Run' : [ 'Walk', 'Jump', 'Idle', 'Crouch', 'CrouchWalk' ],
            'Idle' : [ 'Walk', 'Run', 'Jump', 'Crouch', 'CrouchWalk'],
            'Crouch' : [ 'Idle', 'Run', 'Jump', 'Walk', 'CrouchWalk'],
            'Jump' : [ 'Idle', 'Run', 'Crouch', 'Walk'],           
            }
        """
        self.defaultTransitions = {
            'Walk' : [ 'WalkToRun', 'WalkToJump', 'WalkToIdle', 'WalkToCrouch'],
            'WalkToRun' : [ 'Run' ],
            'WalkToJump' : [ 'Jump' ],
            'WalkToIdle' : [ 'Idle' ],
            'WalkToCrouch' : [ 'Crouch' ],
            'Run' : [ 'RunToWalk', 'RunToJump', 'RunToIdle', 'RunToCrouch' ],
            'RunToWalk' : [ 'Walk' ],
            'RunToJump' : [ 'Jump' ],
            'RunToCouch' : [ 'Crouch' ],
            'Idle' : [ 'IdleToWalk', 'IdleToRun', 'IdleToJump', 'IdleToCrouch'],
            'IdleToWalk' : [ 'Walk' ],
            'IdleToRun' : [ 'Run' ],
            'IdleToJump' : [ 'Jump' ],
            'Crouch' : [ 'CrouchToIdle', 'CrouchToRun', 'CrouchToJump', 'CrouchToWalk'],
            'CrouchToIdle' : ['Run'],
            'CrouchToIdle' : ['Jump'],
            'CrouchToIdle' : ['Walk'],
            'Jump' : [ 'JumpToIdle', 'JumpToRun', 'JumpToCrouch', 'JumpToWalk'],
            }
        """
    def enterWalk(self, animSpeed):
        self.actor.setPlayRate(animSpeed, 'walk')
        self.actor.loop('walk')
        #footstepsSound.play()
        
    def exitWalk(self):
        self.actor.stop()
        #footstepsSound.stop()
        
    def enterCrouchWalk(self, animSpeed):
        self.actor.setPlayRate(animSpeed, 'crouchWalk')
        self.actor.loop('crouchWalk')
        #footstepsSound.play()
        
    def exitCrouchWalk(self):
        self.actor.stop()
        #footstepsSound.stop()  
        
    def enterCrouch(self, animSpeed):
        self.actor.setPlayRate(animSpeed, 'crouch')
        self.actor.loop('crouch')
        #footstepsSound.play()
        
    def exitCrouch(self):
        self.actor.stop()
        #footstepsSound.stop()        
                
    def enterRun(self,animSpeed):
        self.actor.setPlayRate(animSpeed, 'run')
        self.actor.loop('run')
        #footstepsSound.play()       
    def exitRun(self):
        self.actor.stop()
        #footstepsSound.stop()
        
    def enterIdle(self,animSpeed):
        self.actor.setPlayRate(animSpeed, 'idle')
        self.actor.loop('idle')
        #footstepsSound.play()
        
    def exitIdle(self):
        self.actor.stop()
        #footstepsSound.stop()
    def enterJump(self, animSpeed):
        self.actor.setPlayRate(animSpeed, 'jump')
        self.actor.play('jump')
        #footstepsSound.play()
        
    def exitJump(self):
        self.actor.stop()
        
def storeLastPose(self):
        self.lastPose=self.state