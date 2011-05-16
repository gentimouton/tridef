from config import config_get_tower_hp, config_get_tower_atk, \
    config_get_tower_atk_range, config_get_tower_mvt_range, \
    config_get_tower_mvt_cooldown, config_get_tower_atk_cooldown, \
    config_get_tower_atk_anim_duration, config_get_tower_sprite, \
    config_get_tower_sprite_scale, config_get_tower_atk_color
from tools import load_image
import pygame


class Tower():
    
    def __init__(self, gb, sprpos, cell):
        #static data for game mechanics
        self.__GAMEBOARD = gb # pointer to the game board to ask for services such as "find me a creep to attack" 
        self.__MAXHP = config_get_tower_hp()
        self.__ATK = config_get_tower_atk()
        self.__ATK_RANGE = config_get_tower_atk_range() #range at which tower can attack creep
        self.__MVT_RANGE =  config_get_tower_mvt_range() #range at which tower can move (2 means it can potentially jump over a creep) 
        self.__MVT_COOLDOWN = config_get_tower_mvt_cooldown() #cooldown before tower can move again, in frames
        #dynamic data (status)
        self.__hp = self.__MAXHP
        self.__atk_cooldown_tick = config_get_tower_atk_cooldown() #at the beginning it can not attack
        self.__atk_anim_tick = config_get_tower_atk_anim_duration() #initialized at animduration and decreased each tick. when == 0, tower actually attacks
        # towers actually inflicts dmg every (atkcooldown + atkanimation) frames
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN #when towers are created, player has to wait before towers can be moved
        self.__current_cell = cell
        self.__target = None
        #__SPRITE
        self.__SPRITE = pygame.sprite.Sprite()   
        self.__SPRITE.image, self.__SPRITE.rect = load_image(config_get_tower_sprite(), 
                                                             (int(self.__GAMEBOARD.get_cell_width()*config_get_tower_sprite_scale()),
                                                             int(self.__GAMEBOARD.get_cell_height()*config_get_tower_sprite_scale()))
                                                             )
        self.__padding = (1 - config_get_tower_sprite_scale()) / 2
        self.__SPRITE.rect.topleft = int(sprpos[0] + self.__GAMEBOARD.get_cell_width()*self.__padding), int(sprpos[1] + self.__GAMEBOARD.get_cell_height()*self.__padding) 
        #if spritescale = 0.8, then padding should be (1-0.8)/2 = 0.1 on top and bottom, and 0.1 on left and right 
        #so that the spr is centered in the middle of the cell
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
                assert(self.__atk_cooldown_tick <= 0)
            except AssertionError:
                print("Error in tower._update_atk: tower should not be in cooldown period if it's in animation period")
            if self.__target == None: #either the tower didnt have any __target before or its __target was killed by another tower 
                creeplist = self.__GAMEBOARD.get_creep_in_range(self.__current_cell, self.__ATK_RANGE) #get the list of creeps in range of __current_cell
                if creeplist:
                    self.__target = creeplist.pop() #get a random creep in range
            if self.__target == None: #all creeps in sight have been killed before tower could actually attack 
                self.__atk_anim_tick = config_get_tower_atk_anim_duration() #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a __target to attack
                self.__GAMEBOARD.draw_atk_animation(self, self.__target, config_get_tower_atk_color()) #ask gameboard to display __ATK graphics in both cases
                if self.__atk_anim_tick == 0: #time to actually inflict dmg to a creep
                    self.__target.defend(self.__ATK)
                    self.__target = None
                    self.__atk_anim_tick = config_get_tower_atk_anim_duration() #no anim to draw anymore
                    self.__atk_cooldown_tick = config_get_tower_atk_cooldown() #put in cooldown mode
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
        self.__hp -= dmg
        if self.__hp <= 0:
            self.die()
        #print("tower __hp: "+str(self.__hp))
        return
    
    
    def move_tower(self, destcell):
        """ move a tower's __SPRITE to destination cell """
        self.__current_cell.remove_tower()
        self.__current_cell = destcell
        destcell.add_tower(self)
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN
        x,y = destcell.get_coords() # x = row, starting from top; y = column, starting from left
        self.__SPRITE.rect.topleft = int((x+self.__padding)*self.__GAMEBOARD.get_cell_width()), int((y+self.__padding)*self.__GAMEBOARD.get_cell_height()) #0.1 = for 10% margin at left and right of tower img
        return
    
    

    def die(self):
        """ tower death """
        self.__GAMEBOARD.remove_tower(self)
        #print("tower dead")
        return