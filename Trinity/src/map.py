import os
from tools import matrix_transpose
from cell import Cell

class Map():
    def __init__(self, mapfile, res):
        f = open(os.path.join("maps", mapfile))
        #other lines = map in itself
        lines = f.readlines() #might be optimized: for line in open("file.txt"):
        self.__BOARD = [] #contains game board
        for j in range(len(lines)): #for all lines in file
            tmprow = []
            line = lines[j].strip().split(',')
            for i in range(len(line)):
                cellvalue = line[i];
                if cellvalue == 'E':
                    self.__entrance_coords = i,j
                    tmprow.append(1) #entrance is walkable
                elif cellvalue == 'L':
                    self.__lair_coords = i,j
                    tmprow.append(1) #lair is walkable
                else:
                    tmprow.append(int(line[i]))
            self.__BOARD.append(tmprow)
        self.__BOARD = matrix_transpose(self.__BOARD)
        # TODO: instead of assert, catch error and print explanatory message 
        assert(self.__BOARD and self.__BOARD[0]) # map has no row or no column
        #compute cell width and height to fit the resolution
        self.__CELL_WIDTH = int(res[0] / self.get_width()) #800/4=200
        self.__CELL_HEIGHT = int(res[1] / self.get_height()) #600/3=200
        self.__CELLGRID = [[Cell((i, j),
                                   self.__CELL_WIDTH,
                                   self.__CELL_HEIGHT,
                                   self._get_board()[i][j],
                                   self.get_width() * self.get_height()) for j in range(self.get_height())] for i in range(self.get_width())] #length * width = so far a distance that it'll be replaced during path making
        self.path = self._makePath() #need __CELLGRID to be initialized to work 
        # init game objects 
        self.cellgrid(self.get_entrance_coords()).set_entrance()
        self.cellgrid(self.get_lair_coords()).set_lair()
        return
    
    def _makePath(self):  
        """ starting from entrance (d=0) assign d+1 recursively to neighbor cells as the cell's distance to entrance """
        def recursive_dist_fill(cell, newdist):
            assert(cell.is_walkable()) #if cell is not walkable, it should not be reached by the algorithm
            if(cell.get_dist_from_entrance() > newdist):
                cell.set_dist_from_entrance(newdist)
                for neighborcell in self._get_adjacent_walkable_cells(cell):
                    recursive_dist_fill(neighborcell, newdist + 1)
            return
        recursive_dist_fill(self.cellgrid(self.get_entrance_coords()), 0)
        return
    
    
    # -----------------------------------
    # ACCESSORS
    # -----------------------------------
    def _get_board(self):
        return self.__BOARD
    
    def get_lair_coords(self):
        return self.__lair_coords
    
    def get_entrance_coords(self):
        return self.__entrance_coords
    
    def get_width(self):
        return len(self.__BOARD)
    
    def get_height(self):
        if self.get_width():
            return len(self.__BOARD[0])
        else:#if self.board is empty, there's no cell, map is certainly bad
            return 0
        
    def get_cell_width(self):
        return self.__CELL_WIDTH
    
    def get_cell_height(self):
        return self.__CELL_HEIGHT
    
    
    def cellgrid(self, coord): 
        """ shortcut for cellgrid[x][y] """
        return self.__CELLGRID[coord[0]][coord[1]]
    
    def get_cell_from_grid(self, coords):
        """ return the cell located at coords """
        return self.cellgrid(coords)
    
    # -----------------------------------
    # CELL and PROXIMITY
    # -----------------------------------

    def are_adjacent(self, cell1, cell2):
        """ made for a square/rectangular grid - diagonal moves forbidden """
        return (
                ((abs(cell1.get_coords()[0] - cell2.get_coords()[0]) == 1) and
                 (abs(cell1.get_coords()[1] - cell2.get_coords()[1]) == 0))
                or 
                ((abs(cell1.get_coords()[1] - cell2.get_coords()[1]) == 1) and 
                 (abs(cell1.get_coords()[0] - cell2.get_coords()[0]) == 0))
                )
    
    def _get_adjacent_walkable_cells(self, currentcell): # can return empty set
        """ returns adjacent walkable cells, made for square cells in non-diagonal movement """
        (x, y) = currentcell.get_coords()
        width = self.get_width()
        height = self.get_height()
        adjcells = set([])
        # first: get all adjacent cells in the set
        if y == height - 1: #bottom line
            if x == width - 1: #bottom right
                if width > 1: #board is not a vertical line: there is a cell on the left
                    adjcells.add(self.__CELLGRID[x - 1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjcells.add(self.__CELLGRID[x][y - 1])
            elif x == 0: #bottom left
                if width > 1: #board is not a vertical line: there is a cell on the right
                    adjcells.add(self.__CELLGRID[x + 1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjcells.add(self.__CELLGRID[x][y - 1])
            else: #bottom line without corners
                adjcells.add(self.__CELLGRID[x - 1][y])
                adjcells.add(self.__CELLGRID[x + 1][y])
                if height > 1: #board is not a horizontal line: there is a cell on top
                    adjcells.add(self.__CELLGRID[x][y - 1])
        elif y == 0: #top line
            if x == width - 1: #top right
                if width > 1: #board is not a vertical line: there is a cell on the left
                    adjcells.add(self.__CELLGRID[x - 1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjcells.add(self.__CELLGRID[x][y + 1])
            elif x == 0: #top left
                if width > 1: #board is not a vertical line: there is a cell on the right
                    adjcells.add(self.__CELLGRID[x + 1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjcells.add(self.__CELLGRID[x][y + 1])
            else: #top line without corners
                adjcells.add(self.__CELLGRID[x - 1][y])
                adjcells.add(self.__CELLGRID[x + 1][y])
                if height > 1: #board is not a horizontal line: there is a cell at bottom
                    adjcells.add(self.__CELLGRID[x][y + 1])
        else: #middle lines
            if x == 0: #left column without corners
                adjcells.add(self.__CELLGRID[x][y - 1])
                adjcells.add(self.__CELLGRID[x][y + 1])
                if width > 1:
                    adjcells.add(self.__CELLGRID[x + 1][y])
            elif x == width - 1: #right column without corners
                adjcells.add(self.__CELLGRID[x][y - 1])
                adjcells.add(self.__CELLGRID[x][y + 1])
                if width > 1:
                    adjcells.add(self.__CELLGRID[x - 1][y])
            else: #middle middle
                adjcells.add(self.__CELLGRID[x][y + 1])
                adjcells.add(self.__CELLGRID[x][y - 1])
                adjcells.add(self.__CELLGRID[x - 1][y])
                adjcells.add(self.__CELLGRID[x + 1][y])
        #second: remove non-walkable cells from the final set
        walkablecells = adjcells.copy() #need a copy because the set is gonna shrink, and if it shrinks, then its not iterable anymore
        for adjcell in adjcells:
            try:
                assert(self.are_adjacent(currentcell, adjcell))
            except AssertionError:
                print("Error in map._get_adjacent_walkable_cells: ")
                print(str(currentcell.get_coords()) + " -- " + str(adjcell.get_coords()))
            if not adjcell.is_walkable():
                walkablecells.remove(adjcell)
        return walkablecells
    

    def get_reachable_cells(self, cell, range):
        """ return the set of walkable cells in range - there could be a tower or creeps in some or all of these """
        result = set([cell]) #add adjacent cells for range>=1
        if range == 0:
            return result
        newcells = set([cell]) #stores the newly added cells at last iteration
        itercells = set([]) #the set of cells obtained at a particular iteration
        i = 1
        while i <= range: #iterate range-1 times
            itercells.clear()
            for c in newcells: #only look at the recently added cells
                itercells = itercells.union(self._get_adjacent_walkable_cells(c))
            newcells = itercells - result #contains ONLY new adjacent cells, ie further from the core cell
            result = result.union(newcells)
            i += 1
        return result
    

    # -----------------------------------
    # PATH
    # -----------------------------------
    
     
    def get_next_cell_in_path(self, currentcell):
        """ c = coord of current cell, return coord of cell after current cell in path """
        neighbors = self._get_adjacent_walkable_cells(currentcell) #get cells around currentcell
        try:
            bestcelltogoto = neighbors.pop() #if the cell is lost in the middle of nowhere with no neighbor, this function should not be called
        except KeyError:
            print("get_next_cell_in_path: current cell has no neighbor and should have at least one")
        for c in neighbors:
            if c.get_dist_from_entrance() < bestcelltogoto.get_dist_from_entrance(): #c is closer to entrance
                bestcelltogoto = c
        return bestcelltogoto
    

    # pos=(x,y)=screen coord, returns the cell in which pos is 
    def get_cell_from_screen_coord(self, pos):
        i = int(pos[0] / self.get_cell_width()) #horizontal
        j = int(pos[1] / self.get_cell_height()) #vertical
        try:
            assert(i >= 0 and j >= 0 and j < self.get_height() and i < self.get_width()) 
        except AssertionError:
            print("Error in map.get_next_cell_in_path: the cell could not be found in cellgrid")            
        return self.cellgrid((i, j))

