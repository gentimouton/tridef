import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONUP

from gameboard import GameBoard
from config import load_config, config_get_fps, config_get_screencaption


def main():
    #init
    load_config()
    pygame.init()
    pygame.display.set_caption(config_get_screencaption())
    pygame.mouse.set_visible(1) #1 == visible, 0==invisible
    clock = pygame.time.Clock()
    gameBoard = GameBoard() #gameBoard is supposed to be a self-controlled singleton, it is just perturbed by main()
  
    
    #game testing
    gameBoard.add_tower()
    gameBoard.add_creep()


    #Main Loop
    while 1:
        print("tick")
        clock.tick(config_get_fps()) #number of frames per second
        pygame.display.set_caption(config_get_screencaption() + " --- FPS: " + str(clock.get_fps()))
        gameBoard.update()
        if gameBoard.is_game_over():
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
                    gameBoard.do_left_click(event.dict['pos'])
                elif event.dict['button'] == 3: #right click
                    gameBoard.do_right_click(event.dict['pos'])


if __name__ == '__main__': main()
