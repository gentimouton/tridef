from config import config_get_walkablecolor, config_get_entrancecolor, \
    config_get_laircolor, config_get_nonwalkableoverlay, config_get_walkableoverlay, \
    config_get_nonwalkablecolor
import pygame


class Cell():
    
    def __init__(self, coord, width, height, walkable, maxdist):
        self.__surface = pygame.Surface((width, height))
        self.__tower = None #tower currently occupying the cell
        self.__creeps = set([]) # list of creeps in the cell
        self.__coords = coord #coord of the cell in the board 
        if walkable:
            self.__is_walkable = True
            self.__dist_from_entrance = maxdist #how far is the cell from the entrance; default = boardheight*boardwidth
            self.__surface.fill(config_get_walkablecolor())
        else: #non walkable
            self.__is_walkable = False
            self.__dist_from_entrance = -1 #just in case
            self.__surface.fill(config_get_nonwalkablecolor())
        return
    
    
    # Accessor
    def get_dist_from_entrance(self):
        return self.__dist_from_entrance
   
    def set_dist_from_entrance(self, d):
        self.__dist_from_entrance = d
        return 
    
    #---- map generation ----
    
    def get_surface(self):
        """accessor to the graphical element surface of the cell """
        return self.__surface
    
    def is_walkable(self):
        """ returns true if cell could receive tower or creeps at some point in the game"""
        return self.__is_walkable;
    
    def set_entrance(self):
        """colors the cell to show it's an entrance """
        self.__surface.fill(config_get_entrancecolor()) #blue
        return

    def set_lair(self):
        """ colors the cell to show it's a lair """
        self.__surface.fill(config_get_laircolor()) #red
        return

    
    # ---- during game ---
    def add_tower(self, tower):
        """ add a tower on this cell """
        self.__tower = tower;
        return 

    def has_tower(self):
        return self.__tower != None

    def get_tower(self):
        return self.__tower
        
    def remove_tower(self):
        self.__tower = None
        return

    def add_creep(self, creep):
        """ a creep moves to the cell """
        self.__creeps.add(creep)
        return
    
    def remove_creep(self, creep):
        """ a creep moved to another cell or died """
        try:
            self.__creeps.remove(creep)
        except KeyError:
            print("Cell could not remove the creep because the creep was not in the cell")
        return

    def get_creeps(self):
        """  return list of creeps on the cell """
        #print("cell " + str(self.__coords) + " has " + str(len(self.__creeps)) + " creep")
        return self.__creeps
    
    def has_creeps(self):
        return self.get_creeps()
       
    def get_coords(self):
        """ return coordinates in the board grid; top left = 0,0 and bottom left = BOARDHEIGHT,0 """
        return self.__coords

    def indicate_reachable_cells(self, bg, width, height):
        """ Displays a green overlay on top of cells where a tower can go to, and red where it can not. Only display an overlay at walking distance."""
        surfoverlay = pygame.Surface((width, height))
        surfoverlay.set_alpha(100) #set transparency (higher = less transparent)
        if self.has_tower() or self.has_creeps():
            surfoverlay.fill(config_get_nonwalkableoverlay()) #fills the overlay in red 
        else:
            surfoverlay.fill(config_get_walkableoverlay()) #fills the overlay in green
        bg.blit(surfoverlay, (self.__coords[0] * width, self.__coords[1] * height)) #add the overlay to the main bg

