import pygame
from tools import load_image


class Creep():
    
    def __init__(self, gb, sprpos, cell): 
        #static data for game mechanics
        self.gb = gb # pointer to the game board to ask for services such as "get me a tower to attack" 
        self.HP = 88
        self.atk = 1
        self.atkrange = 1 #range at which creep can attack tower
        #dynamic data (status)
        self.atkcooldown = 4 #cooldown before creep can attack again, in frames
        self.atkcooldowntick = self.atkcooldown #unlike towers, at the beginning creeps can not move
        self.atkanimduration = 1 # number of frames dedicated to display the attack animation;
        self.atkanimtick = self.atkanimduration #initialized at animduration and decreased each tick. when == 0, creep actually attacks
        # creep actually inflicts dmg every (atkcooldown + atkanimation) frames
        self.mvtrange = 1 #range at which creep can move (2 means it can potentially jump over a tower) 
        self.mvtcooldown = 6 #cooldown before creep can move again, in frames
        self.mvtcooldowntick = self.mvtcooldown #at beginning, creeps have to wait before moving
        self.currentCell = cell
        self.target = None
        #sprite
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image, self.sprite.rect = load_image("flower.png", (int(self.gb.getCellWidth()*0.8), int(self.gb.getCellHeight()*0.8))) #0.8 = scale img at 80%
        screen = pygame.display.get_surface()
        self.sprite.area = screen.get_rect()
        self.sprite.rect.topleft = int(sprpos[0]+self.gb.getCellWidth()*0.1), int(sprpos[1]+self.gb.getCellHeight()*0.1) #0.1 = 10% of the rect border
        self.atkcolor = (20,20,255) #color of the line between a creep and a tower when a creep attacks it        
        return 

    def update(self):
        if self.gb.nextCellInPath(self.currentCell).hasTower(): #if there is a tower in creep's destination cell
            self.updateAtk() #attack tower or atk cooldown or atk animation
        else:
            self.updateMvt() #walk to following cell in path, or walk cooldown 
        #GRAPHICS
        self.sprite.update(self)
        return

    # handles mechanics and graphics for creep movement
    def updateMvt(self):
        if self.mvtcooldowntick > 0:
            self.mvtcooldowntick -= 1
        else: #creep can move, cooldown is over
            assert(self.mvtcooldowntick == 0)
            nextcell = self.gb.nextCellInPath(self.currentCell)
            self.currentCell.removeCreep(self)
            self.currentCell = nextcell
            nextcell.addCreep(self)
            self.mvtcooldowntick = self.mvtcooldown
            x,y = nextcell.getCoord()
            self.sprite.rect.topleft = int((x+0.1)*self.gb.getCellWidth()), int((y+0.1)*self.gb.getCellHeight()) #0.1 = for 10% margin at left and right of tower img
        return

    # handles mechanics and graphics updates related to creep attacking 
    def updateAtk(self):
        if self.atkcooldowntick != 0: #atk cooldown period
            assert(self.atkcooldowntick > 0)
            self.atkcooldowntick -= 1
        else: #animation period
            if self.target == None: #either the creep didnt have any target before or its target was killed or moved 
                self.target = self.gb.getCreepBestTarget(self) #find optimum target; can return None if no tower in sight
            if self.target == None: #no tower in sight
                self.atkanimduration = 0 #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a target to attack
                self.gb.drawAtkAnimation (self, self.target, self.atkcolor) #display atk graphics in both cases
                if self.atkanimtick == 0: #time to actually inflict dmg to a creep
                    self.target.defend(self.atk)
                    self.target = None
                    self.atkanimtick = self.atkanimduration #no anim to draw anymore
                    self.atkcooldowntick = self.atkcooldown #put in cooldown mode
                else: #tower is doing its atk animation only
                    self.atkanimtick -= 1    
        return 
    
    
    #GRAPHICS
    # return the position of the sprite on the screen
    def getSpriteCenterCoord(self):
        return self.sprite.rect.center
    
    # receive dmg from towers, eventually apply creep def
    def defend(self, dmg):
        self.HP -= dmg
        if self.HP <= 0:
            self.die()
        return

    #creep death
    def die(self):
        self.gb.removeCreep(self)
        return
