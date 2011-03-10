import os
from tools import transpose
from cell import Cell

class Map():
    def __init__(self, mapfile, res):
        f = open(os.path.join("maps", mapfile))
        #1st line: entrance
        line = f.readline().strip().split(',') 
        self.__entrancecoord__ = int(line[0]), int(line[1])
        #2nd line: lair
        line = f.readline().strip().split(',') 
        self.__laircoord__ = int(line[0]), int(line[1])
        #other lines = map in itself
        lines = f.readlines() 
        self.__board__ = [] #contains game board
        for j in range(len(lines)): #for all lines in file
            tmprow = []
            line = lines[j].strip().split(',')
            for i in range(len(line)):
                tmprow.append(int(line[i]))
            self.__board__.append(tmprow)
        self.__board__ = transpose(self.__board__)
        assert(len(self.__board__) and len(self.__board__[0]))
        #compute cell width and height to fit the resolution
        self.__cellwidth__ = int(res[0]/self.getWidth()) #800/4=200
        self.__cellheight__ = int(res[1]/self.getHeight()) #600/3=200
        self.__cellgrid__ = [[Cell((i,j), 
                                   self.__cellwidth__, 
                                   self.__cellheight__, 
                                   self.getBoard()[i][j], 
                                   self.getWidth() * self.getHeight()) for j in range(self.getHeight())] for i in range(self.getWidth())] #length * width = so far a distance that it'll be replaced during path making
        self.path = self.makePath() #need cellgrid to be initialized to work 
        # init game objects 
        self.cellGrid(self.getEntranceCoord()).setEntrance()
        self.cellGrid(self.getLairCoord()).setLair()
        return
    #starting from entrance (d=0) assign d+1 recursively to neighbor cells as the cell's distance to entrance
    def makePath(self):  
        def recursiveDistFill(cell, newdist):
            assert(cell.isWalkable()) #if cell is not walkable, it should not be reached by the algorithm
            if(cell.getDistFromEntrance() > newdist):
                cell.setDistFromEntrance(newdist)
                for neighborcell in self.adjacentWalkableCells(cell):
                    recursiveDistFill(neighborcell, newdist+1)
            return
        recursiveDistFill(self.cellGrid(self.getEntranceCoord()), 0)
        return
    
    
    # -----------------------------------
    # ACCESSORS
    # -----------------------------------
    def getBoard(self):
        return self.__board__
    def getLairCoord(self):
        return self.__laircoord__
    def getEntranceCoord(self):
        return self.__entrancecoord__
    def getWidth(self):
        return len(self.__board__)
    def getHeight(self):
        if self.getWidth():
            return len(self.__board__[0])
        else:#if self.board is empty, there's no cell, map is certainly bad
            return 0
    def getCellWidth(self):
        return self.__cellwidth__
    def getCellHeight(self):
        return self.__cellheight__
    # shortcut for cellgrid[x][y]
    def cellGrid(self, coord): 
        return self.__cellgrid__[coord[0]][coord[1]]
    
    
   
    # -----------------------------------
    # CELL and PROXIMITY
    # -----------------------------------

    # made for a square/rectangular grid
    def areAdjacent(self, cell1, cell2):
        return (
                ((abs(cell1.getCoord()[0] - cell2.getCoord()[0]) == 1) and (abs(cell1.getCoord()[1] - cell2.getCoord()[1]) == 0))
                or ((abs(cell1.getCoord()[1] - cell2.getCoord()[1]) == 1) and (abs(cell1.getCoord()[0] - cell2.getCoord()[0]) == 0))
                )
    # returns adjacent walkable cells, made for square cells
    def adjacentWalkableCells(self, currentcell): # can return empty set
        (x,y) = currentcell.getCoord()
        width = self.getWidth()
        height = self.getHeight()
        adjCells = set([])
        # first: get all adjacent cells in the set
        if y == height-1: #bottom line
            if x == width-1: #bottom right
                if width > 1: #board is not a vertical line: there is a cell on the left
                    adjCells.add(self.__cellgrid__[x-1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjCells.add(self.__cellgrid__[x][y-1])
            elif x == 0: #bottom left
                if width > 1: #board is not a vertical line: there is a cell on the right
                    adjCells.add(self.__cellgrid__[x+1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjCells.add(self.__cellgrid__[x][y-1])
            else: #bottom line without corners
                adjCells.add(self.__cellgrid__[x-1][y])
                adjCells.add(self.__cellgrid__[x+1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjCells.add(self.__cellgrid__[x][y-1])
        elif y == 0: #top line
            if x == width-1: #top right
                if width > 1: #board is not a vertical line: there is a cell on the left
                    adjCells.add(self.__cellgrid__[x-1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjCells.add(self.__cellgrid__[x][y+1])
            elif x == 0: #top left
                if width > 1: #board is not a vertical line: there is a cell on the right
                    adjCells.add(self.__cellgrid__[x+1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjCells.add(self.__cellgrid__[x][y+1])
            else: #top line without corners
                adjCells.add(self.__cellgrid__[x-1][y])
                adjCells.add(self.__cellgrid__[x+1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjCells.add(self.__cellgrid__[x][y+1])
        else: #middle lines
            if x == 0: #left column without corners
                adjCells.add(self.__cellgrid__[x][y-1])
                adjCells.add(self.__cellgrid__[x][y+1])
                if width > 1:
                    adjCells.add(self.__cellgrid__[x+1][y])
            elif x == width-1: #right column without corners
                adjCells.add(self.__cellgrid__[x][y-1])
                adjCells.add(self.__cellgrid__[x][y+1])
                if width > 1:
                    adjCells.add(self.__cellgrid__[x-1][y])
            else: #middle middle
                adjCells.add(self.__cellgrid__[x][y+1])
                adjCells.add(self.__cellgrid__[x][y-1])
                adjCells.add(self.__cellgrid__[x-1][y])
                adjCells.add(self.__cellgrid__[x+1][y])
        #second: remove non-walkable cells from the final set
        walkablecells = adjCells.copy() #need a copy because the set is gonna shrink, and if it shrinks, then its not iterable anymore
        for nearbycell in adjCells:
            try:
                assert(self.areAdjacent(currentcell, nearbycell))
            except AssertionError:
                print(str(currentcell.getCoord()) +" -- "+ str(nearbycell.getCoord()))
            if not nearbycell.isWalkable():
                walkablecells.remove(nearbycell)
        return walkablecells
    # return the set of reachable cells at distance "range" from "cell"
    # reachable = walkable at a certain distance, but there can be creeps or other towers in reachable cells
    def reachableCells(self, cell, range):
        result = set([cell]) #add adjacent cells for range>=1
        if range == 0:
            return result
        newcells = set([cell]) #stores the newly added cells at last iteration
        itercells = set([]) #the set of cells obtained at a particular iteration
        i = 1
        while i <= range: #iterate range-1 times
            itercells.clear()
            for c in newcells: #only look at the recently added cells
                itercells = itercells.union(self.adjacentWalkableCells(c))
            newcells = itercells - result #contains ONLY new adjacent cells, ie further from the core cell
            result = result.union(newcells)
            i += 1
        return result
    

    # -----------------------------------
    # PATH
    # -----------------------------------
    
    #c = coord of current cell, return coord of cell after current cell in path 
    def nextInPath(self, currentcell):
        neighbors = self.adjacentWalkableCells(currentcell) #get cells around currentcell
        try:
            bestcelltogoto = neighbors.pop() #if the cell is lost in the middle of nowhere with no neighbor, this function should not be called
        except KeyError:
            print("nextInPath: current cell has no neighbor and should have at least one")
        for c in neighbors:
            if c.getDistFromEntrance() < bestcelltogoto.getDistFromEntrance(): #c is closer to entrance
                bestcelltogoto = c
        return bestcelltogoto
    

    # pos=(x,y)=screen coord, returns the cell in which pos is 
    def getCellFromScreenCoord(self, pos):
        i = int(pos[0]/self.getCellWidth()) #horizontal
        j = int(pos[1]/self.getCellHeight()) #vertical
        assert(i >= 0 and j >= 0 and j < self.getHeight() and i < self.getWidth()) #check that this cell can be found in cellgrid
        return self.cellGrid((i,j))
