import pygame

from tower import Tower
from creep import Creep
from map import Map
from config import config_get_map, config_get_screen_height, config_get_screen_width

#for now, gameboard is both mechanics and graphics
class GameBoard():
    
    def __init__(self): #res = 800*600 as of March 2011
        res = (config_get_screen_width(), config_get_screen_height()) #in pixels
        self.__screen = pygame.display.set_mode(res)
        
        # mechanics (some need to be done before graphics)
        self.__MAP = Map(config_get_map(), res) #load map from config file
        self.__tower_list = []
        self.__creep_list = []
        self.__attack_list = [] #list elements are (u, v, color), where u and v can be towers or creeps, u is attacker, v is defender, and color is the one used to draw the atk lines between u and v
        # graphics of BG
        self.__current_selection = None #stores what the player has selected under her click
        self.__DEFAULT_BG = self._make_bg(self.__screen) # representation of the map with only walkable and non-walkable cells drawn
        self.__bg = self.__DEFAULT_BG.copy() # it is the temp bg always updated during the game loop  
        self.__all_sprites = pygame.sprite.Group()
        return
    
    def _make_bg(self, screen):
        """ create a representation of the map with only walkable and non-walkable cells drawn """
        bg = pygame.Surface(screen.get_size()) 
        bg = bg.convert()
        bg.fill((255, 204, 153))
        for i in range(self.__MAP.get_width()):
            for j in range(self.__MAP.get_height()):
                cell = self.__MAP.cellgrid((i, j))
                if cell.is_walkable():
                    bg.blit(cell.get_surface(), (i * self.__MAP.get_cell_width(), j * self.__MAP.get_cell_height()))
        return bg
    
    
    
    
    
    # ---------------------------
    # UPDATE DURING LOOP
    # ---------------------------
    def update(self):
        """ update the graphics and mechanics of the gameboard """
        # GRAPHICS (needs to be done before towers attack creeps)
        self.__bg = self.__DEFAULT_BG.copy()
        # MECHANICS updates
        for tower in self.__tower_list:
            tower.update()
        for creep in self.__creep_list:
            creep.update()
        self.__all_sprites.empty() #remove all sprites from the __SPRITE set
        for tower in self.__tower_list:
            self.__all_sprites.add(tower.get_sprite())
        for creep in self.__creep_list:
            self.__all_sprites.add(creep.get_sprite())
        #Draw everything
        if self.__current_selection: #if a tower is currently selected
            cells = self.__MAP.get_reachable_cells(self.__current_selection.get_current_cell(), self.__current_selection.get_mvt_range()) 
            for c in cells:#color cells in range in green or red if tower can move or them or not   
                c.indicate_reachable_cells(self.__bg, self.__MAP.get_cell_width(), self.__MAP.get_cell_height())
        self._draw_attacks() #draw the attacks AFTER towers and creeps have moved
        self.__screen.blit(self.__bg, (0, 0))
        self.__all_sprites.draw(self.__screen)
        return




    # ---------------------------
    # USER INPUT
    # ---------------------------
    def do_left_click(self, pos):#pos = position of the click
        """ actions to do when left click -- MOUSEBUTTONUP (dict = pos, button) """
        for tower in self.__tower_list:
            if tower.is_point_inside_area(pos):
                if(tower == self.__current_selection): #if tower was already selected before
                    self.__current_selection = None #unselect it
                    return
                else: #new tower selected
                    self.__current_selection = tower #select the new one
                    return
        # if the function has not returned so far, it's because the user did not click on a tower
        # => either it was a click on a cell with no tower selected
        # or a click to move a tower that had been selected before 
        cell = self.__MAP.get_cell_from_screen_coord(pos) #which cell user clicked in
        if self.__current_selection != None: #if a tower has been selected before 
            reachablecells = self.__MAP.get_reachable_cells(self.__current_selection.get_current_cell(), self.__current_selection.get_mvt_range())                 
            if cell.is_walkable() and cell in reachablecells: # if the destination can receive a tower
                if not cell.has_creeps(): #if there is no creep in the destination
                    self.__current_selection.move_tower(cell) #move tower to destination
                    self.__current_selection = None #unselect tower
                #else: #if click on creep, change nothing
            else: # click in non-walkable zone
                self.__current_selection = None #unselect tower 
        return  
    
    def do_right_click(self, pos):
        """ actions to do when right click - triggered only when button is up """
        self.__current_selection = None #unselect tower 
        return


    # ---------------------------
    # BOARD GAME MECHANICS
    # ---------------------------
    
    def is_game_over(self):
        """ checks if the loss condition is true: there is a creep on entrance cell of dungeon """
        return self.__MAP.cellgrid(self.__MAP.get_entrance_coords()).has_creeps()
    #self.__MAP.cellGrid(self.__MAP.get_entrance_coords()).has_creeps()



    # --------------------------
    # GRAPHICS methods
    # -------------------------
    
    def _draw_attacks(self):
        """ graphics STUB - draws a line when a tower or a creep is attacking a tower or a creep """
        for (atker, defer, color) in self.__attack_list:
            endpos = defer.get_sprite_center_coords()[0] + int(self.__MAP.get_cell_width()*0.1) , defer.get_sprite_center_coords()[1] + int(self.__MAP.get_cell_height()*0.1)
            pygame.draw.line(self.__bg, color, atker.get_sprite_center_coords(), endpos , 5) #5 = thickness
        self.__attack_list[:] = [] #empty the list when it's done     
        return
    
    def draw_atk_animation(self, tower, creep, color):
        """ add a line to be drawn between attacker and defender """
        self.__attack_list.append((tower, creep, color))
        return





         
    # -----------------------------------
    # SERVICES
    # -----------------------------------
    
    # graphics services
    def get_cell_width(self):
        return self.__MAP.get_cell_width()
    
    def get_cell_height(self):
        return self.__MAP.get_cell_height()
    
    #services dealing with towers
     
    def add_tower(self):
        """ add a tower to the game """
        (ex, ey) = self.__MAP.get_entrance_coords() #STUB: add tower on entrance by default
        cell = self.__MAP.get_cell_from_grid((ex, ey))
        tower = Tower(self, (ex * self.__MAP.get_cell_width(), ey * self.__MAP.get_cell_height()), cell)
        cell.add_tower(tower)
        self.__tower_list.append(tower)
        return
    
    def remove_tower(self, tower):
        """ remove specified tower from the game """
        try:
            self.__tower_list.remove(tower)
        except ValueError:
            print("gameboard.remove_tower tried to remove a tower from the game, but this tower was not in game")
        return
    
    
    def get_creep_in_range(self, towercell, range):
        """ returns list of creeps attackable by tower """
        __creep_list = set([])
        for cel in self.__MAP.get_reachable_cells(towercell, range):
            __creep_list = __creep_list.union(cel.get_creeps())
        return __creep_list


    #services dealing with creeps
     
    def add_creep(self):
        """ add a creep to the game - creeps appear in the lair """
        (lx, ly) = self.__MAP.get_lair_coords() #lair coord
        cell = self.__MAP.get_cell_from_grid((lx, ly))
        creep = Creep(self, (lx * self.__MAP.get_cell_width(), ly * self.__MAP.get_cell_height()), cell)
        cell.add_creep(creep)
        self.__creep_list.append(creep)
        return
    
    def remove_creep(self, creep):
        """ removes creep from the game (it probably died) """
        try:
            self.__creep_list.remove(creep)
        except ValueError:
            print("gameboard.remove_creep tried to remove a creep from the game, but this creep was not in game")
        return
    
    
    def get_creep_best_target(self, creep):
        """ STUB - returns the most appropriate tower for the creep to attack; right now, it's the first tower in the list of towers """
        if self.__tower_list: 
            return self.__tower_list[0]
        else:#empty list: no tower in game, so creep can not attack
            return None
    
    def get_next_cell_in_path(self, currentcell): #currentcell is a MapCell
        """ return the destination where a creep should go """
        try:
            assert(currentcell.get_coords() != self.__MAP.get_entrance_coords()) #game should be over
        except AssertionError:
                print("Error in gameboard.get_next_cell_in_path: the creep was on the entrance cell, the game should have been over")            
        return self.__MAP.get_next_cell_in_path(currentcell)
