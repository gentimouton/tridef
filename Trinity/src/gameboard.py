import pygame
from tower import Tower
from creep import Creep
from map import Map


#for now, gameboard is both mechanics and graphics
class GameBoard():
    
    def __init__(self, screen, res, mapfile): #res = 800*600
        self.screen = screen
        # MECHANICS (some need to be done before GRAPHICS)
        self.map = Map(mapfile, res) #load map from file
        self.TOWERLIST = []
        self.CREEPLIST = []
        self.ATTACKSLIST = [] #elements are (u, v, color), where u and v can be towers or creeps, u is attacking v, and color is the one used to draw the atk lines between them
        # graphics of BG
        self.currentSelection = None #stores what the player has selected under her click
        self.defaultbg = self.makeBg(screen) # representation of the map with only walkable and non-walkable cells drawn
        self.bg = self.defaultbg.copy() # it is the temp bg always updated during the game loop  
        self.allsprites = pygame.sprite.Group()
        return
    # create a representation of the map with only walkable and non-walkable cells drawn
    def makeBg(self, screen):
        defaultbg = pygame.Surface(screen.get_size()) 
        defaultbg = defaultbg.convert()
        defaultbg.fill((255,204,153))
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                cell = self.map.cellGrid((i,j))
                if cell.isWalkable():
                    defaultbg.blit(cell.getSurface(), (i*self.map.getCellWidth(), j*self.map.getCellHeight()))
        return defaultbg
    
    
    
    
    
    # ---------------------------
    # UPDATE DURING LOOP
    # ---------------------------
    def update(self):
        # GRAPHICS (needs to be done before towers attack creeps)
        self.bg = self.defaultbg.copy()
        # MECHANICS updates
        for tower in self.TOWERLIST:
            tower.update()
        for creep in self.CREEPLIST:
            creep.update()            
        self.allsprites.empty() #remove all sprites from the sprite set
        for tower in self.TOWERLIST:
            self.allsprites.add(tower.sprite)
        for creep in self.CREEPLIST:
            self.allsprites.add(creep.sprite)
        #Draw everything
        if self.currentSelection: #if a tower is currently selected
            cells = self.map.reachableCells(self.currentSelection.getCurrentCell(), self.currentSelection.getMvtrange()) 
            for c in cells:#color cells in range in green or red if tower can move or them or not   
                c.overlayReachable(self.bg, self.map.getCellWidth(), self.map.getCellHeight())
        self.drawAttacks() #draw the attacks AFTER towers and creeps have moved
        self.screen.blit(self.bg, (0,0))
        self.allsprites.draw(self.screen)
        return




    # ---------------------------
    # USER INPUT
    # ---------------------------
    # actions to do when MOUSEBUTTONUP (dict = pos, button)
    def leftClick(self, pos):#pos = position of the click
        for tower in self.TOWERLIST:
            if tower.getSpriteRect().collidepoint(pos):
                if(tower == self.currentSelection): #if tower was already selected before
                    self.currentSelection = None #unselect it
                    return
                else: #new tower selected
                    self.currentSelection = tower #select the new one
                    return
        # if the function has not returned so far, it's because the user did not click on a tower
        # => either click on cell with no tower selected
        # or click to move a tower that had been selected before 
        cell = self.map.getCellFromScreenCoord(pos) #which cell user clicked in
        if self.currentSelection != None: #if a tower has been selected before 
            reachablecells = self.map.reachableCells(self.currentSelection.getCurrentCell(), self.currentSelection.getMvtrange())                 
            if cell.isWalkable() and cell in reachablecells: # if the destination can receive a tower
                if not cell.hasCreeps(): #if there is no creep in the destination
                    self.currentSelection.moveTower(cell) #move tower to destination
                    self.currentSelection = None #unselect tower
                #else: #if click on creep, change nothing
            else: # click in non-walkable zone
                self.currentSelection = None #unselect tower 
        return  
    def rightClick(self, pos):
        self.currentSelection = None #unselect tower 
        return


    # ---------------------------
    # BOARD GAME MECHANICS
    # ---------------------------
    # checks if the loss condition is true: there is a creep on entrance cell of dungeon
    def isGameOver(self):
        return self.map.cellGrid(self.map.getEntranceCoord()).hasCreeps()



    # --------------------------
    # GRAPHICS methods
    # -------------------------
    #graphics STUB - draws a line when a tower or a creep is attacking a tower or a creep
    def drawAttacks(self):
        for (atker, defer, color) in self.ATTACKSLIST:
            endpos = defer.getSpriteCenterCoord()[0] + int(self.map.getCellWidth()*0.1) , defer.getSpriteCenterCoord()[1] + int(self.map.getCellHeight()*0.1)
            pygame.draw.line(self.bg, color, atker.getSpriteCenterCoord(), endpos , 5) #5 = thickness
        self.ATTACKSLIST[:] = [] #empty the list when it's done     
        return
    # add a line to be drawn between attacker and defender
    def drawAtkAnimation(self, tower, creep, color):
        self.ATTACKSLIST.append((tower, creep, color))
        return





         
    # -----------------------------------
    # SERVICES
    # -----------------------------------
    
    # graphics services
    def getCellWidth(self):
        return self.map.getCellWidth()
    def getCellHeight(self):
        return self.map.getCellHeight()
    
    #services dealing with towers
    #add a tower to the game 
    def addTower(self):
        (ex, ey) = self.map.getEntranceCoord() #STUB: add tower on entrance by default
        cell = self.map.cellGrid((ex,ey))
        tower = Tower(self, (ex*self.map.getCellWidth(), ey*self.map.getCellHeight()), cell)
        cell.addTower(tower)
        self.TOWERLIST.append(tower)
        return
    def removeTower(self, tower):
        try:
            self.TOWERLIST.remove(tower)
        except ValueError:
            print("removeTower tried to remove a tower from the game, but this tower was not in TOWERLIST")
        return
    #returns list of creeps attackable by tower
    def getCreepInRange(self, towercell, range):
        creeplist = set([])
        for cel in self.map.reachableCells(towercell, range):
            creeplist = creeplist.union(cel.getCreeps())
        return creeplist


    #services dealing with creeps
    #add a creep to the game    
    def addCreep(self):
        (lx, ly) = self.map.getLairCoord() #lair coord
        cell = self.map.cellGrid((lx,ly))
        creep = Creep(self, (lx*self.map.getCellWidth(), ly*self.map.getCellHeight()), cell)
        cell.addCreep(creep)
        self.CREEPLIST.append(creep)
        return
    #removes creep from the game (it probably died)
    def removeCreep(self, creep):
        try:
            self.CREEPLIST.remove(creep)
        except ValueError:
            print("removeCreep tried to remove a creep from the game, but this creep was not in CREEPLIST")
        return
    #STUB - returns the most appropriate tower for the creep to attack
    def getCreepBestTarget(self, creep):
        if self.TOWERLIST: 
            return self.TOWERLIST[0]
        else:#empty list: no tower in game, so creep can not attack
            return None
    #return the cell where creep should go after current cell
    def nextCellInPath(self, currentcell): #currentcell is a MapCell
        assert(currentcell.getCoord() != self.map.getEntranceCoord()) #game should be over
        return self.map.nextInPath(currentcell)