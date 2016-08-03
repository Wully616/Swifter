'''
Created on 18 Jul 2016

@author: Wully
'''

from direct.fsm.FSM import FSM
 
class ActorFSM(FSM):
    
    def __init__(self, actor, bController):
        FSM.__init__(self, 'Character')
        #get the actor that we want to move.
        self.bController = bController
        self.actor = actor
        self.defaultTransitions = {
            'Walk' : ['Walk', 'Run', 'Jump', 'Idle', 'IdleCrouch', 'WalkCrouch'],
            'WalkCrouch' : [ 'Run', 'Jump', 'Idle', 'IdleCrouch', 'Walk'],
            'Run' : [ 'Walk', 'Jump', 'Idle', 'IdleCrouch', 'WalkCrouch' ],
            'Idle' : [ 'Walk', 'Run', 'Jump', 'IdleCrouch', 'WalkCrouch'],
            'IdleCrouch' : [ 'Idle', 'Run', 'Jump', 'Walk', 'WalkCrouch'],
            'Jump' : [ 'Idle', 'Run', 'IdleCrouch', 'Walk'],           
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
        
    def enterWalkCrouch(self, animSpeed):
        self.bController.startCrouch()
        self.actor.setPlayRate(animSpeed, 'walk_crouch')
        self.actor.loop('walk_crouch')
        #footstepsSound.play()
        
    def exitWalkCrouch(self):
        self.bController.stopCrouch()
        self.actor.stop()
        #footstepsSound.stop()  
        
    def enterIdleCrouch(self, animSpeed):
        self.bController.startCrouch()
        self.actor.setPlayRate(animSpeed, 'idleCrouch')
        self.actor.loop('idleCrouch')
        #footstepsSound.play()
        
    def exitIdleCrouch(self):
        self.bController.stopCrouch()
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
        self.bController.startJump(10)
        self.actor.setPlayRate(animSpeed, 'jump')
        self.actor.play('jump')
        #footstepsSound.play()
        
    def exitJump(self):
        self.actor.stop()
        
def storeLastPose(self):
        self.lastPose=self.state