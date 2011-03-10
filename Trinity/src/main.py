import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONUP
from gameboard import GameBoard



def main():
    #init
    FPS = 2
    SCREENCAPTION = "Trinity 0.0"
    pygame.init()
    resolution = (800,600)
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption(SCREENCAPTION)
    pygame.mouse.set_visible(1) #1 == visible, 0==invisible
    clock = pygame.time.Clock()
    gameBoard = GameBoard(screen, resolution, "testmap.txt") #gameBoard is supposed to be a self-controlled singleton, it is just perturbed by main()
  
    
    #game testing
    gameBoard.addTower()
    gameBoard.addCreep()
    
    #Main Loop
    while 1:
        print("tick")
        clock.tick(FPS)
        pygame.display.set_caption(SCREENCAPTION + " --- FPS: " + str(clock.get_fps()))
        gameBoard.update()
        if gameBoard.isGameOver():
            print("game over!")
            return
        pygame.display.flip() #reveal the scene - this is the last thing to do in the loop
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type is MOUSEBUTTONUP:
                if event.dict['button'] == 1: #'button' == 1:left click, 2 == middle, 3 == right ; 'pos' == (x,y) == position of click
                    gameBoard.leftClick(event.dict['pos'])
                elif event.dict['button'] == 3: #right click
                    gameBoard.rightClick(event.dict['pos'])


if __name__ == '__main__': main()
