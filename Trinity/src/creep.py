import pygame
import config
from tools import load_image
from config import config_get_creep_hp, config_get_creep_atk,\
    config_get_creep_atk_range, config_get_creep_atk_cooldown,\
    config_get_creep_atk_anim_duration, config_get_creep_mvt_range,\
    config_get_creep_mvt_cooldown, config_get_creep_sprite,\
    config_get_creep_sprite_scale, config_get_creep_atk_color


class Creep():
    
    def __init__(self, gb, sprpos, cell): 
        #static data for game mechanics
        self.__GAMEBOARD = gb # pointer to the game board to ask for services such as "get me a tower to attack" 
        self.__MAXHP = config_get_creep_hp()
        self.__ATK = config_get_creep_atk()
        self.__ATK_RANGE = config_get_creep_atk_range() #range at which creep can attack tower
        self.__MVT_RANGE =  config_get_creep_mvt_range() #range at which creep can move (2 means it can potentially jump over a tower) 
        self.__MVT_COOLDOWN = config_get_creep_mvt_cooldown() #cooldown before creep can move again, in frames
        #dynamic data (status)
        self.__hp = self.__MAXHP
        self.__atk_cooldown_tick = config_get_creep_atk_cooldown() #at the beginning creeps can not attack
        self.__atk_anim_tick = config_get_creep_atk_anim_duration() #initialized at animduration and decreased each tick. when == 0, creep actually attacks
        # creep actually inflicts dmg every (atkcooldown + atkanimation) frames
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN #at beginning, creeps have to wait before moving
        self.__current_cell = cell
        self.__target = None
        #__SPRITE
        self.__SPRITE = pygame.sprite.Sprite()
        self.__SPRITE.image, self.__SPRITE.rect = load_image(config_get_creep_sprite(), 
                                                             (int(self.__GAMEBOARD.get_cell_width()*config_get_creep_sprite_scale()),
                                                             int(self.__GAMEBOARD.get_cell_height()*config_get_creep_sprite_scale()))
                                                             )
        self.__SPRITE.area = pygame.display.get_surface().get_rect()
        self.__padding = (1 - config_get_creep_sprite_scale()) / 2
        self.__SPRITE.rect.topleft = int(sprpos[0] + self.__GAMEBOARD.get_cell_width()*self.__padding), int(sprpos[1] + self.__GAMEBOARD.get_cell_height()*self.__padding) 
        #if spritescale = 0.8, then padding should be (1-0.8)/2 = 0.1 on top and bottom, and 0.1 on left and right 
        #so that the spr is centered in the middle of the cell
        return 

    def update(self):
        destinationcell = self.__GAMEBOARD.get_next_cell_in_path(self.__current_cell)
        if destinationcell.has_tower(): #if there is a tower in creep's destination cell
            self.update_atk() #attack tower or atk cooldown or atk animation
        else:
            self.update_mvt() #walk to following cell in path, or walk cooldown 
        #GRAPHICS
        self.__SPRITE.update(self)
        return

    
    def update_mvt(self):
        """ handles mechanics and graphics for creep movement """
        if self.__mvt_cooldown_tick > 0:
            self.__mvt_cooldown_tick -= 1
        else: #creep can move, cooldown is over
            try:
                assert(self.__mvt_cooldown_tick <= 0)
            except AssertionError:
                print("Error in creep.update_mvt: creep still has to wait before being able to move.")
            nextcell = self.__GAMEBOARD.get_next_cell_in_path(self.__current_cell)
            self.__current_cell.remove_creep(self)
            self.__current_cell = nextcell
            nextcell.add_creep(self)
            self.__mvt_cooldown_tick = self.__MVT_COOLDOWN
            x, y = nextcell.get_coords()
            self.__SPRITE.rect.topleft = int((x + self.__padding) * self.__GAMEBOARD.get_cell_width()), int((y + self.__padding) * self.__GAMEBOARD.get_cell_height()) 
            #0.1 = for 10% margin at left and right of tower img
        return

     
    def update_atk(self):
        """ handles mechanics and graphics updates related to creep attacking """
        if self.__atk_cooldown_tick != 0: #atk cooldown period
            assert(self.__atk_cooldown_tick > 0)
            self.__atk_cooldown_tick -= 1
        else: #animation period
            if self.__target == None: #either the creep didnt have any target before or its target was killed or moved 
                self.__target = self.__GAMEBOARD.get_creep_best_target(self) #find optimum target; can return None if no tower in sight
            if self.__target == None: #no tower in sight
                self.__atk_anim_tick = config_get_creep_atk_anim_duration() #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a target to attack
                self.__GAMEBOARD.draw_atk_animation(self, self.__target, config_get_creep_atk_color()) #display atk graphics in both cases
                if self.__atk_anim_tick == 0: #it is the moment to actually inflict dmg to a tower
                    self.__target.defend(self.__ATK)
                    self.__target = None
                    self.__atk_anim_tick = config_get_creep_atk_anim_duration() #no anim to draw anymore
                    self.__atk_cooldown_tick = config_get_creep_atk_cooldown() #put in cooldown mode
                else: #creep is doing its atk animation only
                    self.__atk_anim_tick -= 1    
        return 
    
    
    #GRAPHICS
    # return the position of the __SPRITE on the screen
    def get_sprite_center_coords(self):
        return self.__SPRITE.rect.center
    
    def get_sprite(self):
        return self.__SPRITE
    
    # receive dmg from towers, eventually apply creep def
    def defend(self, dmg):
        self.__hp -= dmg
        if self.__hp <= 0:
            self.die()
        return

    #creep death
    def die(self):
        self.__GAMEBOARD.remove_creep(self)
        return
