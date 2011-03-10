import pygame


class Cell():
    
    def __init__(self, coord, width, height, walkable, maxdist):
        self.surface = pygame.Surface((width, height))
        self.tower = None #tower currently occupying the cell
        self.creeps = set([]) # list of creeps in the cell
        self.coord = coord #
        self.WALKABLECOLOR = 222,222,222 #gray; color of the walkable cells
        self.NONWALKABLECOLOR = 255,204,153 #orange/salmon; color of the non-walkable cells
        if walkable:
            self.walkable = True
            self.dist = maxdist #how far is the cell from the entrance; default = boardheight*boardwidth
            self.surface.fill(self.WALKABLECOLOR)
        else: #non walkable
            self.walkable = False
            self.dist = -1 #how far is the cell from the entrance; default = boardheight*boardwidth
            self.surface.fill(self.NONWALKABLECOLOR)
        return
    
    
    # Accessor
    def getDistFromEntrance(self):
        return self.dist
    def setDistFromEntrance(self, d):
        self.dist = d
        return 
    #---- map generation ----
    #returns true if cell could receive tower or creeps at some point in the game
    def isWalkable(self):
        return self.walkable;
    # colors the cell to show it's an entrance
    def setEntrance(self):
        self.surface.fill((0,0,255)) #blue
        return
    # colors the cell to show it's a lair
    def setLair(self):
        self.surface.fill((255,0,0)) #red
        return
    def getSurface(self):
        return self.surface
    
    # ---- during game ---
    def addTower(self, tower):
        self.tower = tower;
        return 
    def getTower(self):
        return self.tower
    def hasTower(self):
        return self.getTower() != None
    def removeTower(self):
        self.tower = None
        return

    #a creep moves to the cell
    def addCreep(self, creep):
        self.creeps.add(creep)
        return    
    #a creep moved to another cell or died
    def removeCreep(self, creep):
        try:
            self.creeps.remove(creep)
        except KeyError:
            print("cell could not remove creep because creep was not in cell")
        return
    # return list of creeps on the cell
    def getCreeps(self):
        #print("cell " + str(self.coord) + " has " + str(len(self.creeps)) + " creep")
        return self.creeps
    def hasCreeps(self):
        return len(self.getCreeps())!=0
    
    # return coordinates in the board grid; top left = 0,0 and bottom left = BOARDHEIGHT,0
    def getCoord(self):
        return self.coord

    def overlayReachable(self, bg, width, height):
        surfoverlay = pygame.Surface((width, height)) #will contain red or green overlay
        surfoverlay.set_alpha(100) #set transparency (higher = less transparent)
        if self.hasTower() or self.hasCreeps():
            surfoverlay.fill((255,0,0)) #fills the overlay in red 
        else:
            surfoverlay.fill((0,255,0)) #fills the overlay in green
        bg.blit(surfoverlay, (self.coord[0]*width, self.coord[1]*height)) #add the overlay to the main bg