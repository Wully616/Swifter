'''
Created on 3 Jul 2016
Invokes the game class and runs the game
@author: Wully
'''

from Game.game import StickFightGame

#base.messenger.toggleVerbose()
app = StickFightGame()
app.run()