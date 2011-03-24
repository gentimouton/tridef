import pygame
from tools import load_image


class Tower():
    
    def __init__(self, gb, sprpos, cell):
        #mechanics
        self.__GAMEBOARD = gb #used to ask the gameboard for services such as "get me a creep to attack"
        self.__HP = 80
        self.__ATK = 1
        self.__ATK_RANGE = 3 #DPS can attack creeps located 3 cells from them
        self.__ATK_COOLDOWN = 5 #cooldown before unit can attack again, in frames
        self.__atk_cooldown_tick = 0
        self.__ATK_ANIM_DURATION = 2 # number of frames dedicated to display the attack animation;
        self.__atk_anim_tick = self.__ATK_ANIM_DURATION #initialized at animduration and decreased each tick. when == 0, tower actually attacks
        # towers actually inflict dmg to creeps every (__ATK_COOLDOWN + atkanimation) frames
        self.__MVT_RANGE = 3 #DPS can move 3 cells from them  
        self.__MVT_COOLDOWN = 3 #cooldown before tower can be moved again, in frames
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN #when towers are created, player has to wait before towers can be moved
        self.__current_cell = cell
        self.target = None 
        #GRAPHICS
        self.__SPRITE = pygame.sprite.Sprite()
        self.__SPRITE.image, self.__SPRITE.rect = load_image("star.png", (int(self.__GAMEBOARD.get_cell_width()*0.8), int(self.__GAMEBOARD.get_cell_height()*0.8))) #0.8 = scale img at 80%
        self.__SPRITE.area = pygame.display.get_surface().get_rect()
        self.__SPRITE.rect.topleft = int(sprpos[0]+self.__GAMEBOARD.get_cell_width()*0.1), int(sprpos[1]+self.__GAMEBOARD.get_cell_height()*0.1) #0.1 = 10% of the rect border
        self.__ATK_COLOR = (255,20,20) #color of the line between a tower and a creep when the tower attacks it
        return 

    def update(self):
        self._update_atk() #attack creep or __ATK cooldown or __ATK animation 
        #GRAPHICS
        self.__SPRITE.update(self)
        return

        
     
    def _update_atk(self):
        """ handles mechanics and graphics updates related to tower attacking """
        if self.__atk_cooldown_tick > 0: #__ATK cooldown period
            self.__atk_cooldown_tick -= 1
        else: #animation period
            try:
                assert(self.__atk_cooldown_tick == 0)
            except AssertionError:
                print("Error in tower._update_atk: tower should not be in cooldown period if it's in animation period")
            if self.target == None: #either the tower didnt have any target before or its target was killed by another tower 
                creeplist = self.__GAMEBOARD.get_creep_in_range(self.__current_cell, self.__ATK_RANGE) #get the list of creeps in range of __current_cell
                if creeplist:
                    self.target = creeplist.pop() #get a random creep in range
            if self.target == None: #all creeps in sight have been killed before tower could actually attack 
                self.__ATK_ANIM_DURATION = 0 #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a target to attack
                self.__GAMEBOARD.draw_atk_animation(self, self.target, self.__ATK_COLOR) #ask gameboard to display __ATK graphics in both cases
                if self.__atk_anim_tick == 0: #time to actually inflict dmg to a creep
                    self.target.defend(self.__ATK)
                    self.target = None
                    self.__atk_anim_tick = self.__ATK_ANIM_DURATION #no anim to draw anymore
                    self.__atk_cooldown_tick = self.__ATK_COOLDOWN #put in cooldown mode
                else: #tower is doing its atk animation only
                    self.__atk_anim_tick -= 1    
        return 
            
    
    # GRAPHICS
    def get_sprite(self):
        return self.__SPRITE
    def get_sprite_center_coords(self):
        """ return the position of the __SPRITE on the screen """
        return self.__SPRITE.rect.center

    def is_point_inside_area(self, coord):
        """ whether coord is inside the rectangle of the __SPRITE """
        return self.__SPRITE.rect.collidepoint(coord)
    
    def get_current_cell(self):
        return self.__current_cell
    
    def get_mvt_range(self):
        return self.__MVT_RANGE
    
    
    def defend(self, dmg):
        """ receive dmg from creeps, eventually apply tower def """
        self.__HP -= dmg
        if self.__HP <= 0:
            self.die()
        #print("tower __HP: "+str(self.__HP))
        return
    
    
    def move_tower(self, destcell):
        """ move a tower's __SPRITE to destination cell """
        self.__current_cell.remove_tower()
        self.__current_cell = destcell
        destcell.add_tower(self)
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN
        x,y = destcell.get_coords() # x = row, starting from top; y = column, starting from left
        self.__SPRITE.rect.topleft = int((x+0.1)*self.__GAMEBOARD.get_cell_width()), int((y+0.1)*self.__GAMEBOARD.get_cell_height()) #0.1 = for 10% margin at left and right of tower img
        return
    
    

    def die(self):
        """ tower death """
        self.__GAMEBOARD.remove_tower(self)
        #print("tower dead")
        return