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
from GUI.user_interface import GUI, GUIreturn, MenuControls

def main():
    gui = GUI()
    clock = pygame.time.Clock()
    running = True

    while running:
        result = GUIreturn(MenuControls.DONOTHING) #default result, will be overwritten by event handling if an event is detected
        #GUI EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result : GUIreturn = gui.handle_input(event)

        gui.draw_all()
        pygame.display.flip()
        clock.tick(60)
        #END GUI EVENT HANDLING

        #GUI RESULT HANDLING
        type = result.type
        match type:
            #should remove prints eventually, just here for testing purposes
            case MenuControls.NEWGAME:
                gui.set_possible_moves([])
                gui.update_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

                print("New Game")
                #TODO: Add new game code here
            case MenuControls.NEWBOTGAME:
                gui.set_possible_moves([])
                gui.update_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

                print("New Bot Game")
                #TODO: Add new bot game code here
            case MenuControls.RESIGN:
                gui.set_possible_moves([])
                gui.update_board("8/8/8/4k3/3K4/8/8/8 w - - 0 0")

                print("Resign")
                #TODO: Add resign code here
            case MenuControls.MOVESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square_from = result.coords # 0-63 coordinates of piece selected
                square_to = result.move # 0-63 coordinates of move selected

                gui.set_possible_moves([])

                print("Move Select")
                print(f"Piece: {piece}, From: {square_from}, To: {square_to}")
                #TODO: Add move select code here
            case MenuControls.PIECESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square = result.coords # 0-63 coordinates of piece selected

                gui.set_possible_moves([16,17,18,19])

                print("Piece Select")
                print(f"Piece: {piece}, Square: {square}")
                #TODO: Add piece select code here
            case MenuControls.DONOTHING:
                #idk if theres anything we need to do here, this is just the
                #do nothing case which mostly is a safety net in my gui code
                #so this does actually get called a lot, i don't think there's
                #anything we should put in here but it's here if we change our minds
                #print("Do Nothing")
                pass
            case _:
                print("Unknown result")
        #END GUI RESULT HANDLING

    pygame.quit

if __name__ == "__main__":
    main()