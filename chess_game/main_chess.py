"""
File name: main_chess.py

Author(s):

Purpose: Main file to execute chess engine.
All necessary librarys will be loaded here.

Please add code as we get it! I will work on
creating the libraries for each of the main
classes for the chess engine as we make files for them! - Rachel
"""
# insert main file code here
import pygame
from chess_game.GUI.user_interface import UserInterface, GUIreturn, MenuControls

def main():
    gui = UserInterface()
    clock = pygame.time.Clock()
    running = True

    while running:
        #GUI EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = gui.handle_event(event)
                if result is not None:
                    print(result)

        gui.draw_all()
        pygame.display.flip()
        clock.tick(60)
        #END GUI EVENT HANDLING

        #GUI RESULT HANDLING
        match result:
            #should remove prints eventually, just here for testing purposes
            case MenuControls.NEWGAME:
                print("New Game")
                #TODO: Add new game code here
            case MenuControls.RESIGN:
                print("Resign")
                #TODO: Add resign code here
            case MenuControls.MOVESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square_from = result.coords # 0-63 coordinates of piece selected
                square_to = result.move # 0-63 coordinates of move selected

                print("Move Select")
                #TODO: Add move select code here
            case MenuControls.PIECESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square = result.coords # 0-63 coordinates of piece selected

                print("Piece Select")
                #TODO: Add piece select code here
            case MenuControls.DONOTHING:
                #idk if theres anything we need to do here, this is just the
                #do nothing case which mostly is a safety net in my gui code
                print("Do Nothing")
        #END GUI RESULT HANDLING

    pygame.quit