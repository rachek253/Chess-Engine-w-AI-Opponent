# ==============================
# core/game_manager.py
# ==============================

from typing import List, Tuple
import requests
import os

Position = Tuple[int, int]


class GameManager:
    def __init__(self, mode="pvp"):
        """
        mode = 'pvp' or 'pvb'
        """
        self.mode = mode
        self.api_key = os.getenv("STOCKFISH_API_KEY")
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
        fen_board, self.active_color, self.castleling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number = self.fen.split()
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
        tuple_moves = self.get_legal_moves([row, col])

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

        if piece.tolower() == 'p':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.fullmove_number += 1
        
        #TODO: Add en passant handling

        #TODO: Add castling handling

        self.move((from_row, from_col), (to_row, to_col))

        return self.get_fen()

    # ==========================
    # MOVE GENERATION
    # ==========================
    def get_legal_moves(self, pos):
        board = self.get_board()
        r, c = pos
        piece = board[r][c]

        if piece == '':
            return []

        turn = self.get_turn()
        if (turn == 'w' and not self.is_white(piece)) or \
           (turn == 'b' and not self.is_black(piece)):
            return []

        moves = []

        def add_move(nr, nc):
            if not self.in_bounds(nr, nc): return
            target = board[nr][nc]
            if target == '' or not self.same_color(piece, target):
                moves.append((nr, nc))

        # PAWN
        if piece.lower() == 'p':
            direction = -1 if self.is_white(piece) else 1

            if self.in_bounds(r+direction, c) and board[r+direction][c] == '':
                moves.append((r+direction, c))

            for dc in [-1, 1]:
                nr, nc = r+direction, c+dc
                if self.in_bounds(nr, nc) and board[nr][nc] != '' and not self.same_color(piece, board[nr][nc]):
                    moves.append((nr, nc))

        # ROOK
        elif piece.lower() == 'r':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r, c
                while True:
                    nr += dr; nc += dc
                    if not self.in_bounds(nr, nc): break
                    if board[nr][nc] == '':
                        moves.append((nr, nc))
                    else:
                        if not self.same_color(piece, board[nr][nc]):
                            moves.append((nr, nc))
                        break

        # KNIGHT
        elif piece.lower() == 'n':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                add_move(r+dr, c+dc)

        # BISHOP
        elif piece.lower() == 'b':
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r, c
                while True:
                    nr += dr; nc += dc
                    if not self.in_bounds(nr, nc): break
                    if board[nr][nc] == '':
                        moves.append((nr, nc))
                    else:
                        if not self.same_color(piece, board[nr][nc]):
                            moves.append((nr, nc))
                        break

        # QUEEN
        elif piece.lower() == 'q':
            return self.get_legal_moves((r, c))  # simplified reuse

        # KING + CASTLING
        elif piece.lower() == 'k':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                add_move(r+dr, c+dc)

            # Castling (basic)
            if piece == 'K' and 'K' in self.fen:
                moves.append((7,6))  # kingside
            if piece == 'K' and 'Q' in self.fen:
                moves.append((7,2))
            if piece == 'k' and 'k' in self.fen:
                moves.append((0,6))
            if piece == 'k' and 'q' in self.fen:
                moves.append((0,2))

        return moves

    # ==========================
    # CHECK / CHECKMATE
    # ==========================
    def is_in_check(self, color):
        board = self.get_board()
        king = 'K' if color == 'w' else 'k'

        king_pos = None
        for r in range(8):
            for c in range(8):
                if board[r][c] == king:
                    king_pos = (r, c)

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != '' and ((color == 'w' and self.is_black(piece)) or (color == 'b' and self.is_white(piece))):
                    if king_pos in self.get_legal_moves((r,c)):
                        return True

        return False

    def is_checkmate(self):
        turn = self.get_turn()
        for r in range(8):
            for c in range(8):
                if self.get_legal_moves((r,c)):
                    return False
        return self.is_in_check(turn)

    # ==========================
    # MOVE EXECUTION
    # ==========================
    def move(self, start, end):
        if self.game_over:
            return False

        if end not in self.get_legal_moves(start):
            return False

        board = self.get_board()
        r1, c1 = start
        r2, c2 = end

        piece = board[r1][c1]

        # Promotion
        if piece == 'P' and r2 == 0:
            board[r2][c2] = 'Q'
        elif piece == 'p' and r2 == 7:
            board[r2][c2] = 'q'
        else:
            board[r2][c2] = piece

        board[r1][c1] = ''

        self.switch_turn()
        self.fen = self.board_to_fen(board)

        if self.is_checkmate():
            self.game_over = True

        # BOT MOVE
        if self.mode == "pvb" and not self.game_over and self.get_turn() == 'b':
            self.bot_move()

        return True

    # ==========================
    # STOCKFISH CONNECTION
    # ==========================
    def bot_move(self):
        try:
            response = requests.post(
                "https://stockfish.online/api/s/v2.php",
                params={"fen": self.fen, "depth": 10},
            )

            data = response.json()
            move = data["bestmove"].split()[1]

            start = (8 - int(move[1]), ord(move[0]) - 97)
            end = (8 - int(move[3]), ord(move[2]) - 97)

            self.move(start, end)

        except Exception:
            pass
