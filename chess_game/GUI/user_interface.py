"""
File Name: user_interface.py

Author(s): William Tinker

Purpose: This file contains code reponsible for running the user interface
for the chess application.

This configuration module is responsible for:
1. Properly initializing pygame
2. Properly displaying the board & menu
3. Properly handling user input
4. Properly closing pygame
"""
import os
from tkinter import font
import pygame
from enum import Enum

class GUIStates(Enum):
    MENU = 1
    PIECE = 2
    MOVE = 3

class MenuControls(Enum):
    NEWGAME = 1
    RESIGN = 2
    PIECESELECT = 3
    MOVESELECT = 4
    DONOTHING = 5

class GUIreturn:
    """Container for a GUI action result sent back to the game controller."""

    def __init__(self, type:MenuControls, piece:str = None, coords:int = None, move:int = None):
        self.type = type  # MenuControls command type
        self.piece = piece  # Piece code in FEN-style notation
        self.coords = coords  # Source square index 0-63
        self.move = move  # Destination square index 0-63

class MenuButton:
    """Represents a clickable menu button in the side panel."""

    def __init__(self, label, rect, type):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.type = type
    
    def use_button(self, pos):
        """Return a GUIreturn if the provided mouse position is inside the button."""
        if self.rect.collidepoint(pos):
            return GUIreturn(self.type)
        else:
            return None
        
    def draw_button(self, screen, font):
        pygame.draw.rect(screen, (80, 80, 80), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        text_surface = font.render(self.label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class GUI:
    """Main graphical user interface for displaying the board and menu controls."""

    x_size = 800
    y_size = 600
    square_size = y_size // 8
    dot_size = square_size // 4

    button_width = (y_size - x_size) * 3 // 4
    button_height = x_size // 3
    button_offset = (y_size - x_size) // 8

    title = "Chess"

    # Buttons for starting a new game and resigning.
    new_game_button = MenuButton(
        "New Game",
        (y_size + button_offset, button_offset, button_width, button_height),
        MenuControls.NEWGAME,
    )
    resign_button = MenuButton(
        "Resign",
        (y_size + button_offset, 2 * button_offset + button_height, button_width, button_height),
        MenuControls.RESIGN,
    )

    def __init__(self):
        """Initialize pygame, load artwork, and set the starting chess position."""
        self.state = GUIStates.MENU
        pygame.init()
        self.screen = pygame.display.set_mode((self.x_size, self.y_size))
        pygame.display.set_caption(self.title)
        self.font = pygame.font.Font(None, 32)

        image_folder = os.path.join("chess_game","GUI","Images")

        self.board_img = pygame.image.load(os.path.join(image_folder, "rect-8x8.png")).convert()
        self.board_img = pygame.transform.scale(self.board_img, (self.y_size, self.y_size))
        self.dot_img = pygame.image.load(os.path.join(image_folder, "grey_dot.png")).convert_alpha()
        self.dot_img = pygame.transform.scale(self.dot_img, (self.dot_size, self.dot_size))
        self.piece_imgs = {
            "wp": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-pawn.png")).convert_alpha(),(self.square_size, self.square_size)),
            "wn": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-knight.png")).convert_alpha(),(self.square_size, self.square_size)),
            "wb": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-bishop.png")).convert_alpha(),(self.square_size, self.square_size)),
            "wr": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-rook.png")).convert_alpha(),(self.square_size, self.square_size)),
            "wq": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-queen.png")).convert_alpha(),(self.square_size, self.square_size)),
            "wk": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "white-king.png")).convert_alpha(),(self.square_size, self.square_size)),
            "bp": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-pawn.png")).convert_alpha(),(self.square_size, self.square_size)),
            "bn": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-knight.png")).convert_alpha(),(self.square_size, self.square_size)),
            "bb": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-bishop.png")).convert_alpha(),(self.square_size, self.square_size)),
            "br": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-rook.png")).convert_alpha(),(self.square_size, self.square_size)),
            "bq": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-queen.png")).convert_alpha(),(self.square_size, self.square_size)),
            "bk": pygame.transform.scale(pygame.image.load(os.path.join(image_folder, "black-king.png")).convert_alpha(),(self.square_size, self.square_size)),
        }

        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
        ]

        self.possible_moves = []

    def draw_all(self):
        """Render the board, pieces, and legal-move indicators every frame."""
        self._draw_board()
        self._draw_pieces()
        self._draw_dots()
        self._draw_menu()
        pygame.display.flip()

    def set_possible_moves(self, moves:int):
        """Store the legal target squares for the currently selected piece."""
        self.possible_moves = moves
        for move in self.possible_moves:
            if move < 0 or move > 63:
                self.possible_moves.remove(move)

    def handle_input(self, event):
        """Convert a pygame mouse event into a GUI control action."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            (x, y) = event.pos
            if x <= self.y_size:
                return self._handle_board_click((x, y))
            else:
                return self._handle_menu_click((x, y))
            
    def update_board(self, fen:str):
        """Parse a FEN string and update the internal board matrix."""
        piece_map = {
            "p": "bp",
            "n": "bn",
            "b": "bb",
            "r": "br",
            "q": "bq",
            "k": "bk",
            "P": "wp",
            "N": "wn",
            "B": "wb",
            "R": "wr",
            "Q": "wq",
            "K": "wk",
        }

        # Extract only the board layout portion from the full FEN string.
        board_part = fen.split()[0]
        rows = board_part.split("/")

        if len(rows) != 8:
            raise ValueError("Invalid FEN: must have 8 rows")

        new_board = []

        for fen_row in rows:
            board_row = []

            for char in fen_row:
                if char.isdigit():
                    empty_count = int(char)
                    for _ in range(empty_count):
                        board_row.append(None)
                elif char in piece_map:
                    board_row.append(piece_map[char])
                else:
                    raise ValueError(f"Invalid FEN character: {char}")

            if len(board_row) != 8:
                raise ValueError("Invalid FEN: each row must contain 8 squares")

            new_board.append(board_row)

        self.board = new_board

    def _draw_board(self):
        """Draw the chess board background at the origin of the window."""
        self.screen.blit(self.board_img, (0, 0))

    def _draw_pieces(self):
        """Draw each piece image in the correct board square."""
        for row in range(8):
            for column in range(8):
                x = column * self.square_size
                y = row * self.square_size
                piece = self.board[row][column]

                if piece is not None:
                    self.screen.blit(self.piece_imgs[piece], (x, y))

    def _draw_dots(self):
        """Draw move indicator dots for each legal target square."""
        for move in self.possible_moves:
            row = move // 8
            column = move % 8
            x = column * self.square_size + (self.square_size - self.dot_size) // 2
            y = row * self.square_size + (self.square_size - self.dot_size) // 2
            self.screen.blit(self.dot_img, (x, y))

    def _draw_menu(self):
        """Draw the side panel menu with buttons."""
        self.new_game_button.draw_button(self.screen, self.font)
        self.resign_button.draw_button(self.screen, self.font)
            
    def _handle_board_click(self, pos):
        """Translate a board-area click into piece selection or move selection."""
        (x, y) = pos
        column = x // self.square_size
        row = y // self.square_size

        # Ignore clicks outside the board or while the GUI is in the menu state.
        if not (0 <= row < 8 and 0 <= column < 8) or self.state == GUIStates.MENU:
            return GUIreturn(MenuControls.DONOTHING)

        if self.state == GUIStates.PIECE:
            # Piece selection stage: select the piece at the clicked square.
            piece = self.board[row][column]
            if piece is None:
                return GUIreturn(MenuControls.DONOTHING)
            else:
                self.state = GUIStates.MOVE
                square_num = row + 8 * column
                self.selected_square = square_num
                match piece:
                    case "bp":
                        FEN_piece = "p"
                    case "bn":
                        FEN_piece = "n"
                    case "bb":
                        FEN_piece = "b"
                    case "br":
                        FEN_piece = "r"
                    case "bq":
                        FEN_piece = "q"
                    case "bk":
                        FEN_piece = "k"
                    case "wp":
                        FEN_piece = "P"
                    case "wn":
                        FEN_piece = "N"
                    case "wb":
                        FEN_piece = "B"
                    case "wr":
                        FEN_piece = "R"
                    case "wq":
                        FEN_piece = "Q"
                    case "wk":
                        FEN_piece = "K"

                return GUIreturn(MenuControls.PIECESELECT, FEN_piece, square_num)

        if self.state == GUIStates.MOVE:
            # Move selection stage: choose a legal destination square.
            selected_x = self.selected_square % 8
            selected_y = self.selected_square // 8
            selected_piece = self.board[selected_y][selected_x]

            move_square = row + 8 * column

            for move in self.possible_moves:
                if move == move_square:
                    self.state = GUIStates.PIECE
                    self.selected_square = None
                    return GUIreturn(MenuControls.MOVESELECT, selected_piece, self.selected_square, move_square)

            return GUIreturn(MenuControls.DONOTHING)

    def _handle_menu_click(self, pos):
        """Handle clicks in the menu panel and return the selected menu action."""
        new_game = self.new_game_button.use_button(pos)
        resign = self.resign_button.use_button(pos)
        if new_game is not None:
            self.state = GUIStates.PIECE
            return new_game
        elif resign is not None:
            return resign
        else:
            return GUIreturn(MenuControls.DONOTHING)