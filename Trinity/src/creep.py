import pygame

from tools import load_image


class Creep():
    
    def __init__(self, gb, sprpos, cell): 
        #static data for game mechanics
        self.__GAMEBOARD = gb # pointer to the game board to ask for services such as "get me a tower to attack" 
        self.__HP = 88
        self.__ATK = 1
        self.__ATK_RANGE = 1 #range at which creep can attack tower
        #dynamic data (status)
        self.__ATK_COOLDOWN = 4 #cooldown before creep can attack again, in frames
        self.__atk_cooldown_tick = self.__ATK_COOLDOWN #unlike towers, at the beginning creeps can not move
        self.__ATK_ANIM_DURATION = 1 # number of frames dedicated to display the attack animation;
        self.__atk_anim_tick = self.__ATK_ANIM_DURATION #initialized at animduration and decreased each tick. when == 0, creep actually attacks
        # creep actually inflicts dmg every (atkcooldown + atkanimation) frames
        self.__MVT_RANGE = 1 #range at which creep can move (2 means it can potentially jump over a tower) 
        self.__MVT_COOLDOWN = 6 #cooldown before creep can move again, in frames
        self.__mvt_cooldown_tick = self.__MVT_COOLDOWN #at beginning, creeps have to wait before moving
        self.__current_cell = cell
        self.__target = None
        #__SPRITE
        self.__SPRITE = pygame.sprite.Sprite()
        self.__SPRITE.image, self.__SPRITE.rect = load_image("disk.png", (int(self.__GAMEBOARD.get_cell_width()*0.8), int(self.__GAMEBOARD.get_cell_height()*0.8))) #0.8 = scale img at 80% of the cell size
        self.__SPRITE.area = pygame.display.get_surface().get_rect()
        self.__SPRITE.rect.topleft = int(sprpos[0] + self.__GAMEBOARD.get_cell_width()*0.1), int(sprpos[1] + self.__GAMEBOARD.get_cell_height()*0.1) #0.1 = 10% of the rect border, centers the spr in midle of the cell
        self.__ATK_COLOR = (20, 20, 255) #color of the line between a creep and a tower when a creep attacks it        
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
            assert(self.__mvt_cooldown_tick == 0)
            nextcell = self.__GAMEBOARD.get_next_cell_in_path(self.__current_cell)
            self.__current_cell.remove_creep(self)
            self.__current_cell = nextcell
            nextcell.add_creep(self)
            self.__mvt_cooldown_tick = self.__MVT_COOLDOWN
            x, y = nextcell.get_coords()
            self.__SPRITE.rect.topleft = int((x + 0.1) * self.__GAMEBOARD.get_cell_width()), int((y + 0.1) * self.__GAMEBOARD.get_cell_height()) #0.1 = for 10% margin at left and right of tower img
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
                self.__ATK_ANIM_DURATION = 0 #come back or stay in default position (ie anim=0 and cooldown=0)
            else: #tower has a target to attack
                self.__GAMEBOARD.draw_atk_animation(self, self.__target, self.__ATK_COLOR) #display atk graphics in both cases
                if self.__atk_anim_tick == 0: #it is the moment to actually inflict dmg to a tower
                    self.__target.defend(self.__ATK)
                    self.__target = None
                    self.__atk_anim_tick = self.__ATK_ANIM_DURATION #no anim to draw anymore
                    self.__atk_cooldown_tick = self.__ATK_COOLDOWN #put in cooldown mode
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
        self.__HP -= dmg
        if self.__HP <= 0:
            self.die()
        return

    #creep death
    def die(self):
        self.__GAMEBOARD.remove_creep(self)
        return
