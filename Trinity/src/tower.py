import pygame
from tools import load_image


class Tower():
    
    def __init__(self, gb, sprpos, cell):
        #mechanics
        self.gb = gb #used to ask the gameboard for services such as "get me a creep to attack"
        self.HP = 80
        self.atk = 1
        self.atkrange = 3 #DPS can attack creeps located 3 cells from them
        self.atkcooldown = 5 #cooldown before unit can attack again, in frames
        self.atkcooldowntick = 0
        self.atkanimduration = 2 # number of frames dedicated to display the attack animation;
        self.atkanimtick = self.atkanimduration #initialized at animduration and decreased each tick. when == 0, tower actually attacks
        # towers actually inflict dmg to creeps every (atkcooldown + atkanimation) frames
        self.mvtrange = 3 #DPS can move 3 cells from them  
        self.mvtcooldown = 3 #cooldown before tower can be moved again, in frames
        self.mvtcooldowntick = self.mvtcooldown #when towers are created, player has to wait before towers can be moved
        self.currentCell = cell
        self.target = None 
        #GRAPHICS
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image, self.sprite.rect = load_image("star.png", (int(self.gb.getCellWidth()*0.8), int(self.gb.getCellHeight()*0.8))) #0.8 = scale img at 80%
        screen = pygame.display.get_surface()
        self.sprite.area = screen.get_rect()
        self.sprite.rect.topleft = int(sprpos[0]+self.gb.getCellWidth()*0.1), int(sprpos[1]+self.gb.getCellHeight()*0.1) #0.1 = 10% of the rect border
        self.atkcolor = (255,20,20) #color of the line between a tower and a creep when the tower attacks it
        return 

    def update(self):
        self.updateAtk() #attack creep or atk cooldown or atk animation 
        #GRAPHICS
        self.sprite.update(self)
        return

        
    # handles mechanics and graphics updates related to tower attacking 
    def updateAtk(self):
        if self.atkcooldowntick != 0: #atk cooldown period
            assert(self.atkcooldowntick > 0)
            self.atkcooldowntick -= 1
        else: #animation period
            assert(self.atkcooldowntick == 0) #tower should not be in cooldown period if it's in animation period
            if self.target == None: #either the tower didnt have any target before or its target was killed by another tower 
                creeplist = self.gb.getCreepInRange(self.currentCell, self.atkrange) #get the list of creeps in range of currentCell
                if len(creeplist)!=0:
                    self.target = creeplist.pop() #get a random creep in range
            if self.target == None: #all creeps in sight have been killed before tower could actually attack 
                self.atkanimduration = 0 #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a target to attack
                self.gb.drawAtkAnimation(self, self.target, self.atkcolor) #ask gameboard to display atk graphics in both cases
                if self.atkanimtick == 0: #time to actually inflict dmg to a creep
                    self.target.defend(self.atk)
                    self.target = None
                    self.atkanimtick = self.atkanimduration #no anim to draw anymore
                    self.atkcooldowntick = self.atkcooldown #put in cooldown mode
                else: #tower is doing its atk animation only
                    self.atkanimtick -= 1    
        return 
            
    
    # GRAPHICS
    # return the position of the sprite on the screen
    def getSpriteCenterCoord(self):
        return self.sprite.rect.center
    def getSpriteRect(self):
        return self.sprite.rect
    def getCurrentCell(self):
        return self.currentCell
    def getMvtrange(self):
        return self.mvtrange
    
    # receive dmg from creeps, eventually apply tower def
    def defend(self, dmg):
        self.HP -= dmg
        if self.HP <= 0:
            self.die()
        #print("tower HP: "+str(self.HP))
        return
    # move a tower's sprite to destination cell
    def moveTower(self, destcell):
        self.currentCell.removeTower()
        self.currentCell = destcell
        destcell.addTower(self)
        self.mvtcooldowntick = self.mvtcooldown
        x,y = destcell.getCoord() # x = row, starting from top; y = column, starting from left
        self.sprite.rect.topleft = int((x+0.1)*self.gb.getCellWidth()), int((y+0.1)*self.gb.getCellHeight()) #0.1 = for 10% margin at left and right of tower img
        return
    #tower death
    def die(self):
        self.gb.removeTower(self)
        #print("tower dead")
        return