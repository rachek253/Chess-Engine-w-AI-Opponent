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
from GUI.user_interface import GUI, GUIreturn, MenuControls, GUIStates
from chess_logic.UpdatedGameManager import GameManager, GameState

def main():
    gui = GUI()
    clock = pygame.time.Clock()
    running = True
    GM = None

    while running:
        result = GUIreturn(MenuControls.DONOTHING) #default result, will be overwritten by event handling if an event is detected

        state = GM.get_status() if GM else None
        match state:
            case GameState.WHITEWINS:
                gui.set_state(GUIStates.MENU)
                gui.set_message("White Wins!")
                pass
            case GameState.BLACKWINS:
                gui.set_state(GUIStates.MENU)
                gui.set_message("Black Wins!")
                pass
            case GameState.STALEMATE:
                gui.set_state(GUIStates.MENU)
                gui.set_message("Stalemate!")
                pass
            case GameState.WHITEPROMO:
                gui.set_state(GUIStates.WHITEPROMO)
                gui.set_message("White Promotion")
                pass
            case GameState.BLACKPROMO:
                gui.set_state(GUIStates.BLACKPROMO)
                gui.set_message("Black Promotion")
                pass
            case _:
                pass

        #GUI EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result : GUIreturn = gui.handle_input(event)
        #END GUI EVENT HANDLING

        #GUI DRAWING
        gui.draw_all()
        pygame.display.flip()
        #END GUI DRAWING

        #GUI RESULT HANDLING
        type = result.type
        match type:
            #should remove prints eventually, just here for testing purposes
            case MenuControls.NEWGAME:
                GM = GameManager("pvp")
                gui.set_possible_moves([])
                gui.update_board(GM.get_fen())

                print("New Game")
                #TODO: Add new game code here
            case MenuControls.NEWBOTGAME:
                GM = GameManager("pvb")
                gui.set_possible_moves([])
                gui.update_board(GM.get_fen())

                print("New Bot Game")
                #TODO: Add new bot game code here
            case MenuControls.RESIGN:
                gui.set_possible_moves([])
                GM.resign()

                print("Resign")
                #TODO: Add resign code here
            case MenuControls.MOVESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square_from = result.coords # 0-63 coordinates of piece selected
                square_to = result.move # 0-63 coordinates of move selected

                GM.handle_move_selection(piece, square_from, square_to)
                gui.set_possible_moves([])
                gui.update_board(GM.get_fen())

                print("Move Select")
                print(f"Piece: {piece}, From: {square_from}, To: {square_to}")
                print(f"FEN after move: {GM.get_fen()}")
                #TODO: Add move select code here
            case MenuControls.PIECESELECT:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected
                square = result.coords # 0-63 coordinates of piece selected

                move_list = GM.handle_piece_selection(square)

                gui.set_possible_moves(move_list)
                if not move_list:
                    gui.set_state(GUIStates.PIECE)

                print("Piece Select")
                print(f"Piece: {piece}, Square: {square}")
                #TODO: Add piece select code here
            case MenuControls.PROMOTION:
                #feel free to rename the left hand side variables
                piece = result.piece # FEN name of piece selected for promotion

                GM.promote(piece)
                gui.set_possible_moves([])
                gui.update_board(GM.get_fen())
                gui.set_state(GUIStates.PIECE)

                print("Promotion")
                print(f"Piece: {piece}")
                print(f"FEN after promotion: {GM.get_fen()}")
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

        #leave this at the end, limits game to 60 frames per second, which is plenty
        clock.tick(60)

    pygame.quit

if __name__ == "__main__":
    main()