# ==============================
# core/game_manager.py
# ==============================

from typing import List, Tuple
from enum import Enum
import requests
import os
from API.stockfish_bot import StockfishBot

Position = Tuple[int, int]

class GameState(Enum):
    ONGOING = 1
    STALEMATE = 2
    BLACKWINS = 3
    WHITEWINS = 4
    BLACKPROMO = 5
    WHITEPROMO = 6

class GameManager:
    def __init__(self, mode="pvp"):
        """
        mode = 'pvp' or 'pvb'
        """
        self.mode = mode
        self.api_key = os.getenv("STOCKFISH_API_KEY")
        self.bot = StockfishBot() if mode == "pvb" else None
        self.game_state = GameState.ONGOING
        self.new_game()

    def new_game(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.active_color = 'w'
        self.castleling_rights = 'KQkq'
        self.en_passant = '-'
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.game_over = False

    # ==========================
    # FEN ↔ BOARD
    # ==========================
    def fen_to_board(self):
        fen_board, self.active_color, self.castleling_rights, self.en_passant, halfmove_clock, fullmove_number = self.fen.split()
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
        rows = fen_board.split('/')
        board = []

        for row in rows:
            new_row = []
            for char in row:
                if char.isdigit():
                    new_row.extend([''] * int(char))
                else:
                    new_row.append(char)
            board.append(new_row)

        return board

    def board_to_fen(self, board):
        fen_rows = []

        for row in board:
            empty = 0
            fen_row = ""
            for cell in row:
                if cell == '':
                    empty += 1
                else:
                    if empty:
                        fen_row += str(empty)
                        empty = 0
                    fen_row += cell
            if empty:
                fen_row += str(empty)

            fen_rows.append(fen_row)

        return f"{'/'.join(fen_rows)} {self.active_color} {self.castleling_rights} {self.en_passant} {self.halfmove_clock} {self.fullmove_number}"

    def get_turn(self):
        return self.active_color

    def switch_turn(self):
        if self.active_color == 'w':
            self.active_color = 'b'
        else:
            self.active_color = 'w'
            self.fullmove_number += 1

    def get_board(self):
        return self.fen_to_board()

    def get_fen(self):
        return self.fen

    # ==========================
    # HELPER FUNCTIONS
    # ==========================
    def is_white(self, p): return p.isupper()
    def is_black(self, p): return p.islower()

    def same_color(self, p1, p2):
        return (self.is_white(p1) and self.is_white(p2)) or \
               (self.is_black(p1) and self.is_black(p2))

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8
    
    def handle_piece_selection(self, coords: int):
        row = coords // 8
        col = coords % 8
        tuple_moves = self.get_legal_moves([row, col], self.get_turn())

        moves = []

        for move in tuple_moves:
            int_move = move[0] * 8 + move[1]
            moves.append(int_move)

        return moves
    
    def handle_move_selection(self, piece, from_coords: int, to_coords: int):
        from_row = from_coords // 8
        from_col = from_coords % 8
        to_row = to_coords // 8
        to_col = to_coords % 8

        self.move((from_row, from_col), (to_row, to_col))

        return self.get_fen()
    
    def get_status(self):
        self.is_in_checkmate(self.get_turn())
        self.is_in_stalemate()

        return self.game_state
    
    def resign(self):
        if self.active_color == 'w':
            self.game_state = GameState.BLACKWINS
        elif self.active_color == 'b':
            self.game_state = GameState.WHITEWINS
        self.game_over = True

    def promote(self, piece):
        if self.game_state == GameState.WHITEPROMO and piece in ['q', 'r', 'b', 'n']:
            board = self.get_board()
            for c in range(8):
                if board[0][c] == 'P':
                    board[0][c] = piece.upper()
            self.switch_turn()
            self.fen = self.board_to_fen(board)
            self.game_state = GameState.ONGOING
        elif self.game_state == GameState.BLACKPROMO and piece in ['q', 'r', 'b', 'n']:
            board = self.get_board()
            for c in range(8):
                if board[7][c] == 'p':
                    board[7][c] = piece.lower()
            self.switch_turn()
            self.fen = self.board_to_fen(board)
            self.game_state = GameState.ONGOING

    # ==========================
    # MOVE GENERATION
    # ==========================
    def get_legal_moves(self, pos, turn):
        board = self.get_board()
        r, c = pos
        piece = board[r][c]

        if piece == '':
            return []

        if (turn == 'w' and not self.is_white(piece)) or \
           (turn == 'b' and not self.is_black(piece)):
            return []

        moves = []

        def add_move(r, c, nr, nc):
            if not self.in_bounds(nr, nc): return False
            target = board[nr][nc]
            potential_board = [row.copy() for row in board]
            potential_board[nr][nc] = piece
            potential_board[r][c] = ''
            in_check = self.is_in_check(potential_board, self.get_turn())
            if target == '':
                if not in_check: moves.append((nr, nc))
                return True
            if target != '' and not self.same_color(piece, target):
                if not in_check: moves.append((nr, nc))
                return False
            return False

        # PAWN
        if piece.lower() == 'p':
            direction = -1 if self.is_white(piece) else 1
            first_move_legal = False

            if self.en_passant != "-":
                file = self.en_passant[0]
                rank = self.en_passant[1]
                ep_c = ord(file) - ord('a')
                ep_r = 8 - int(rank)
            else:
                ep_c = None
                ep_r = None
 
            if board[r+direction][c] == '':
                first_move_legal = add_move(r, c, r+direction, c)

            if ((self.is_white(piece) and r == 6) or (self.is_black(piece) and r == 1)) and first_move_legal == True and board[r+2*direction][c] == '':
                add_move(r, c, r+2*direction, c)

            for dc in [-1, 1]:
                nr, nc = r+direction, c+dc
                if self.in_bounds(nr, nc) and (board[nr][nc] != '' and not self.same_color(piece, board[nr][nc])) or (nr == ep_r and nc == ep_c):
                    add_move(r, c, nr, nc)

        # ROOK
        elif piece.lower() == 'r':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r, c
                legal_move_returned = True
                while legal_move_returned:
                    nr += dr; nc += dc
                    if not self.in_bounds(nr, nc): legal_move_returned = False
                    legal_move_returned = add_move(r, c, nr, nc)

        # KNIGHT
        elif piece.lower() == 'n':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                add_move(r, c, r+dr, c+dc)

        # BISHOP
        elif piece.lower() == 'b':
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r, c
                legal_move_returned = True
                while legal_move_returned:
                    nr += dr; nc += dc
                    if not self.in_bounds(nr, nc): legal_move_returned = False
                    legal_move_returned = add_move(r, c, nr, nc)

        # QUEEN
        elif piece.lower() == 'q':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r, c
                legal_move_returned = True
                while legal_move_returned:
                    nr += dr; nc += dc
                    if not self.in_bounds(nr, nc): legal_move_returned = False
                    legal_move_returned = add_move(r, c, nr, nc)

        # KING + CASTLING
        elif piece.lower() == 'k':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                add_move(r, c, r+dr, c+dc)

            # Castling TODO: add check for castling across check
            if not self.is_in_check(board, self.active_color):
                if piece == 'K' and 'K' in self.castleling_rights and board[7][5] == '' and board[7][6] == '' and not self.square_under_attack(board, (7,5),"w"):
                    add_move(r, c, 7, 6)
                if piece == 'K' and 'Q' in self.castleling_rights and board[7][3] == '' and board[7][2] == '' and board[7][1] == '' and not self.square_under_attack(board, (7,3),"w"):
                    add_move(r, c, 7, 2)
                if piece == 'k' and 'k' in self.castleling_rights and board[0][5] == '' and board[0][6] == '' and not self.square_under_attack(board, (0,5),"b"):
                    add_move(r, c, 0, 6)
                if piece == 'k' and 'q' in self.castleling_rights and board[0][3] == '' and board[0][2] == '' and board[0][1] == '' and not self.square_under_attack(board, (0,3),"b"):
                    add_move(r, c, 0, 2)

        return moves

    # ==========================
    # CHECK / CHECKMATE
    # ==========================

    def square_under_attack(self, board, square, active_color):
        r, c = square
        opponent_color = 'b' if active_color == 'w' else 'w'

        #check knight attacks
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr, nc = r+dr, c+dc
            if self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece.lower() == 'n' and ((opponent_color == 'w' and self.is_white(piece)) or (opponent_color == 'b' and self.is_black(piece))):
                    return True
                
        #check pawn attacks
        direction = 1 if opponent_color == 'w' else -1
        for dc in [-1, 1]:
            nr, nc = r+direction, c+dc
            if self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece.lower() == 'p' and ((opponent_color == 'w' and self.is_white(piece)) or (opponent_color == 'b' and self.is_black(piece))):
                    return True
        
        #check rook/queen horizontal attacks
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r, c
            legal_move_returned = True
            while legal_move_returned:
                nr += dr; nc += dc
                if not self.in_bounds(nr, nc): legal_move_returned = False
                else:
                    piece = board[nr][nc]
                    if piece != '':
                        if piece.lower() in ['r', 'q'] and ((opponent_color == 'w' and self.is_white(piece)) or (opponent_color == 'b' and self.is_black(piece))):
                            return True
                        legal_move_returned = False

        #check bishop/queen diagonal attacks
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r, c
            legal_move_returned = True
            while legal_move_returned:
                nr += dr; nc += dc
                if not self.in_bounds(nr, nc): legal_move_returned = False
                else:
                    piece = board[nr][nc]
                    if piece != '':
                        if piece.lower() in ['b', 'q'] and ((opponent_color == 'w' and self.is_white(piece)) or (opponent_color == 'b' and self.is_black(piece))):
                            return True
                        legal_move_returned = False

        #check king attacks
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r+dr, c+dc
            if self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece.lower() == 'k' and ((opponent_color == 'w' and self.is_white(piece)) or (opponent_color == 'b' and self.is_black(piece))):
                    return True
                
        return False
    
    def is_in_check(self, board, color):
        king = 'K' if color == 'w' else 'k'

        for r, c in [(r,c) for r in range(8) for c in range(8)]:
            if board[r][c] == king:
                return self.square_under_attack(board, (r,c), color)

    def is_in_checkmate(self, color):
        if not self.is_in_check(self.get_board(), color):
            return False
        for r, c in [(r,c) for r in range(8) for c in range(8)]:
            piece = self.get_board()[r][c]
            if (piece != '') and ((color == 'w' and self.is_white(piece)) or (color == 'b' and self.is_black(piece))):
                moves = self.get_legal_moves((r,c), color)
                if moves:
                    return False
        if self.active_color == 'w':
            self.game_state = GameState.BLACKWINS
        elif self.active_color == 'b':
            self.game_state = GameState.WHITEWINS
        self.game_over = True
        return True
    
    def is_in_stalemate(self):
        if self.is_in_check(self.get_board(), self.active_color):
            return False
        if self.halfmove_clock >= 100:
            self.game_state = GameState.STALEMATE
            self.game_over = True
            return True
        for r, c in [(r,c) for r in range(8) for c in range(8)]:
            piece = self.get_board()[r][c]
            if (piece != '') and ((self.active_color == 'w' and self.is_white(piece)) or (self.active_color == 'b' and self.is_black(piece))):
                moves = self.get_legal_moves((r,c), self.active_color)
                if moves:
                    return False
        self.game_state = GameState.STALEMATE
        self.game_over = True
        return True


    # ==========================
    # MOVE EXECUTION
    # ==========================
    def move(self, start, end):
        if self.game_over:
            return False

        if end not in self.get_legal_moves(start, self.get_turn()):
            return False

        board = self.get_board()
        r1, c1 = start
        r2, c2 = end

        piece = board[r1][c1]

        # Promotion
        if piece == 'P' and r2 == 0:
            self.game_state = GameState.WHITEPROMO
        elif piece == 'p' and r2 == 7:
            self.game_state = GameState.BLACKPROMO
        
        board[r2][c2] = piece
        board[r1][c1] = ''

        #updating castling rights
        if piece == 'R' and r1 == 7 and c1 == 0:
            castleling_rights = self.castleling_rights.replace('Q', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'
        if piece == 'r' and r1 == 0 and c1 == 0:
            castleling_rights = self.castleling_rights.replace('q', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'
        if piece == 'R' and r1 == 7 and c1 == 7:
            castleling_rights = self.castleling_rights.replace('K', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'
        if piece == 'r' and r1 == 0 and c1 == 7:
            castleling_rights = self.castleling_rights.replace('k', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'

        if piece == 'K' and r1 == 7 and c1 == 4:
            castleling_rights = self.castleling_rights.replace('K', '').replace('Q', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'
        if piece == 'k' and r1 == 0 and c1 == 4:
            castleling_rights = self.castleling_rights.replace('k', '').replace('q', '')
            self.castleling_rights = castleling_rights if castleling_rights else '-'

        #make rook move if castling
        if piece == 'K' and r1 == 7 and c1 == 4 and r2 == 7 and c2 == 6:
            board[7][5] = 'R'
            board[7][7] = ''
        if piece == 'K' and r1 == 7 and c1 == 4 and r2 == 7 and c2 == 2:
            board[7][3] = 'R'
            board[7][0] = ''
        if piece == 'k' and r1 == 0 and c1 == 4 and r2 == 0 and c2 == 6:
            board[0][5] = 'r'
            board[0][7] = ''
        if piece == 'k' and r1 == 0 and c1 == 4 and r2 == 0 and c2 == 2:
            board[0][3] = 'r'
            board[0][0] = ''

        #en passant handling
        if self.en_passant != "-":
            file = self.en_passant[0]
            rank = self.en_passant[1]
            ep_c = ord(file) - ord('a')
            ep_r = 8 - int(rank)
        else:
            ep_c = None
            ep_r = None

        if ep_c == c2 and ep_r == r2:
            if self.is_white(piece):
                board[r2+1][c2] = ''
            else:
                board[r2-1][c2] = ''

        self.en_passant = "-"
        if piece == 'p' and r1 == 1 and r2 == 3:
            match c2:
                case 0:
                    self.en_passant = "a6"
                case 1:
                    self.en_passant = "b6"
                case 2:
                    self.en_passant = "c6"
                case 3:
                    self.en_passant = "d6"
                case 4:
                    self.en_passant = "e6"
                case 5:
                    self.en_passant = "f6"
                case 6:
                    self.en_passant = "g6"
                case 7:
                    self.en_passant = "h6"
                case _:
                    self.en_passant = "-"

        if piece == "P" and r1 == 6 and r2 == 4:
            match c2:
                case 0:
                    self.en_passant = "a3"
                case 1:
                    self.en_passant = "b3"
                case 2:
                    self.en_passant = "c3"
                case 3:
                    self.en_passant = "d3"
                case 4:
                    self.en_passant = "e3"
                case 5:
                    self.en_passant = "f3"
                case 6:
                    self.en_passant = "g3"
                case 7:
                    self.en_passant = "h3"
                case _:
                    self.en_passant = "-"

        if self.game_state == GameState.ONGOING:
            if piece.lower() == 'p' or self.is_in_check(board, 'w' if self.active_color == 'b' else 'b'):
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1

            self.switch_turn()
            self.fen = self.board_to_fen(board)

            if self.is_in_checkmate(self.get_turn()):
                self.game_over = True

            # BOT MOVE
            if self.mode == "pvb" and not self.game_over and self.get_turn() == 'b':
                self.bot_move()
        else:
            self.fen = self.board_to_fen(board)

        return True

    # ==========================
    # STOCKFISH CONNECTION
    # ==========================
    print("[DEBUG] About to connect to bot...")
    def bot_move(self):
        if not self.bot: 
            return
        try:
            move_str = self.bot.choose_moves(self.fen)

            if not move_str: 
                return

            print(f"[DEBUG] FEN sent to bot: {self.fen}")
            move_str = self.bot.choose_moves(self.fen)
            print(f"[DEBUG] Bot returned: {move_str}")
            
            start = (8 - int(move_str[1]), ord(move_str[0]) - 97)
            end = (8 - int(move_str[3]), ord(move_str[2]) - 97)

            self.move(start, end)

        except Exception as e:
            print(f"[GameManager Bot Error] {e}")
