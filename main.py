import pygame
import sys
from enum import Enum, auto
import random


class PieceType(Enum):
    # Types of chess pieces
    KING = auto()
    QUEEN = auto()
    ROOK = auto()
    BISHOP = auto()
    KNIGHT = auto()
    PAWN = auto()


class PieceColor(Enum):
    # Piece colors (sides)
    WHITE = auto()
    BLACK = auto()


class Piece:
    def __init__(self, piece_type, color, position):
        self.piece_type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False

    def __str__(self):
        # Return a short text like "WK" for White King
        color_char = 'W' if self.color == PieceColor.WHITE else 'B'
        piece_map = {
            PieceType.KING: "K",
            PieceType.QUEEN: "Q",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.KNIGHT: "N",
            PieceType.PAWN: "P"
        }
        return f"{color_char}{piece_map[self.piece_type]}"


class ChessBoard:
    # Handles game state and rules of chess
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = PieceColor.WHITE
        self.initialize_board()

    def initialize_board(self):
        # Set up pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK, (1, col))
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE, (6, col))

        # Set up back row pieces
        back_row = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        for col in range(8):
            self.board[0][col] = Piece(back_row[col], PieceColor.BLACK, (0, col))
            self.board[7][col] = Piece(back_row[col], PieceColor.WHITE, (7, col))

    def get_piece(self, row, col):
        # Return piece at a given position (or None)
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row, col, piece):
        # Place a piece on the board
        if piece:
            piece.position = (row, col)
        self.board[row][col] = piece

    def move_piece(self, from_pos, to_pos):
        # Move a piece if the move is valid
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.get_piece(from_row, from_col)

        if not piece:
            return False
        if piece.color != self.current_turn:
            return False
        if not self.is_valid_move(from_pos, to_pos):
            return False

        # Castling
        if piece.piece_type == PieceType.KING and abs(from_col - to_col) == 2:
            rook_col = 0 if to_col == 2 else 7
            rook_target_col = 3 if to_col == 2 else 5
            rook = self.get_piece(from_row, rook_col)
            self.set_piece(from_row, rook_col, None)
            self.set_piece(from_row, rook_target_col, rook)
            rook.has_moved = True

        # Execute move
        self.set_piece(from_row, from_col, None)
        self.set_piece(to_row, to_col, piece)
        piece.has_moved = True

        # Pawn promotion
        if piece.piece_type == PieceType.PAWN and (to_row == 0 or to_row == 7):
            piece.piece_type = PieceType.QUEEN

        # Switch turns
        self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
        return True

    def is_valid_move(self, from_pos, to_pos):
        # Check if a move is legal for a piece
        piece = self.get_piece(*from_pos)
        target = self.get_piece(*to_pos)

        if not piece:
            return False
        if target and target.color == piece.color:
            return False

        if piece.piece_type == PieceType.PAWN:
            return self._validate_pawn(from_pos, to_pos)
        if piece.piece_type == PieceType.KNIGHT:
            return self._validate_knight(from_pos, to_pos)
        if piece.piece_type == PieceType.BISHOP:
            return self._validate_bishop(from_pos, to_pos)
        if piece.piece_type == PieceType.ROOK:
            return self._validate_rook(from_pos, to_pos)
        if piece.piece_type == PieceType.QUEEN:
            return self._validate_queen(from_pos, to_pos)
        if piece.piece_type == PieceType.KING:
            return self._validate_king(from_pos, to_pos)
        return False

    def _validate_pawn(self, from_pos, to_pos):
        # Validate pawn moves including forward, double, and capture
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.get_piece(from_row, from_col)
        direction = -1 if piece.color == PieceColor.WHITE else 1

        # One square forward
        if from_col == to_col and to_row == from_row + direction:
            return self.get_piece(to_row, to_col) is None

        # Double move from starting position
        if from_col == to_col:
            if (piece.color == PieceColor.WHITE and from_row == 6 and to_row == 4) or \
               (piece.color == PieceColor.BLACK and from_row == 1 and to_row == 3):
                return self.get_piece(from_row + direction, from_col) is None and \
                       self.get_piece(to_row, to_col) is None

        # Diagonal capture
        if abs(to_col - from_col) == 1 and to_row == from_row + direction:
            target = self.get_piece(to_row, to_col)
            return target is not None and target.color != piece.color

        return False

    def _validate_knight(self, from_pos, to_pos):
        # Knight L-shaped moves
        dr, dc = abs(to_pos[0] - from_pos[0]), abs(to_pos[1] - from_pos[1])
        return (dr, dc) in [(2, 1), (1, 2)]

    def _validate_bishop(self, from_pos, to_pos):
        # Bishop diagonal moves (no jumping)
        fr, fc = from_pos
        tr, tc = to_pos
        if abs(tr - fr) != abs(tc - fc):
            return False
        row_step = 1 if tr > fr else -1
        col_step = 1 if tc > fc else -1
        r, c = fr + row_step, fc + col_step
        while (r, c) != (tr, tc):
            if self.get_piece(r, c):
                return False
            r += row_step
            c += col_step
        return True

    def _validate_rook(self, from_pos, to_pos):
        # Rook straight moves (no jumping)
        fr, fc = from_pos
        tr, tc = to_pos
        if fr != tr and fc != tc:
            return False
        if fr == tr:  # horizontal
            for c in range(min(fc, tc) + 1, max(fc, tc)):
                if self.get_piece(fr, c):
                    return False
        else:  # vertical
            for r in range(min(fr, tr) + 1, max(fr, tr)):
                if self.get_piece(r, fc):
                    return False
        return True

    def _validate_queen(self, from_pos, to_pos):
        # Queen moves like rook or bishop
        return self._validate_bishop(from_pos, to_pos) or self._validate_rook(from_pos, to_pos)

    def _validate_king(self, from_pos, to_pos):
        # King moves one square or castles
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.get_piece(fr, fc)

        # Normal one-square move
        if abs(tr - fr) <= 1 and abs(tc - fc) <= 1:
            return True

        # Castling
        if not piece.has_moved and fr == tr and abs(tc - fc) == 2:
            rook_col = 0 if tc < fc else 7
            rook = self.get_piece(fr, rook_col)
            if not rook or rook.piece_type != PieceType.ROOK or rook.has_moved:
                return False
            for c in range(min(fc, rook_col) + 1, max(fc, rook_col)):
                if self.get_piece(fr, c):
                    return False
            return True

        return False


class ChessGame:
    # Manages game loop, rendering, and input
    def __init__(self):
        pygame.init()
        self.screen_size = 640
        self.square_size = self.screen_size // 8
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Chess Game")

        self.board = ChessBoard()
        self.selected_piece = None
        self.images = {}
        self._load_images()

        self.game_over = False
        self.message = ""
        self.computer_player = PieceColor.BLACK

    def _load_images(self):
        # Create simple placeholders for pieces
        pieces = {
            "WK": "white_king", "WQ": "white_queen", "WR": "white_rook",
            "WB": "white_bishop", "WN": "white_knight", "WP": "white_pawn",
            "BK": "black_king", "BQ": "black_queen", "BR": "black_rook",
            "BB": "black_bishop", "BN": "black_knight", "BP": "black_pawn"
        }
        font = pygame.font.SysFont("Arial", 36)
        for key in pieces:
            fg_color = (255, 255, 255) if key.startswith("W") else (0, 0, 0)
            bg_color = (100, 100, 100) if key.startswith("W") else (200, 200, 200)
            surface = pygame.Surface((self.square_size, self.square_size))
            surface.fill(bg_color)
            text = font.render(key[1], True, fg_color)
            surface.blit(text, text.get_rect(center=(self.square_size // 2, self.square_size // 2)))
            self.images[key] = surface

    def draw_board(self):
        # Draw board, pieces, highlights, and messages
        self.screen.fill((255, 255, 255))

        for row in range(8):
            for col in range(8):
                square_color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(
                    self.screen,
                    square_color,
                    (col * self.square_size, row * self.square_size,
                     self.square_size, self.square_size)
                )

                # Highlight valid moves
                if self.selected_piece:
                    sr, sc = self.selected_piece
                    if self.board.is_valid_move((sr, sc), (row, col)):
                        highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                        highlight.fill((124, 252, 0, 128))
                        self.screen.blit(highlight, (col * self.square_size, row * self.square_size))

                # Draw piece
                piece = self.board.get_piece(row, col)
                if piece:
                    self.screen.blit(
                        self.images[str(piece)],
                        (col * self.square_size, row * self.square_size)
                    )

        # Highlight selected piece
        if self.selected_piece:
            sr, sc = self.selected_piece
            pygame.draw.rect(
                self.screen, (255, 255, 0),
                (sc * self.square_size, sr * self.square_size,
                 self.square_size, self.square_size), 3
            )

        # Show endgame message
        if self.game_over:
            font = pygame.font.SysFont("Arial", 48)
            text = font.render(self.message, True, (255, 0, 0))
            overlay = pygame.Surface((self.screen_size, 100), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, self.screen_size // 2 - 50))
            self.screen.blit(text, text.get_rect(center=(self.screen_size // 2, self.screen_size // 2)))

    def handle_click(self, pos):
        # Handle mouse clicks for selecting and moving pieces
        if self.game_over:
            return

        col, row = pos[0] // self.square_size, pos[1] // self.square_size
        if self.selected_piece:
            if self.board.move_piece(self.selected_piece, (row, col)):
                self.selected_piece = None
                self.check_game_state()
                if not self.game_over:
                    self.computer_move()
            else:
                piece = self.board.get_piece(row, col)
                self.selected_piece = (row, col) if piece and piece.color == self.board.current_turn else None
        else:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.board.current_turn:
                self.selected_piece = (row, col)

    def computer_move(self):
        # Make a random move for the computer
        moves = self.board.get_all_valid_moves(self.computer_player)
        if moves:
            from_pos, to_pos = random.choice(moves)
            self.board.move_piece(from_pos, to_pos)
            self.check_game_state()

    def check_game_state(self):
        # Detect checkmate or stalemate
        if self.board.is_checkmate():
            winner = "White" if self.board.current_turn == PieceColor.BLACK else "Black"
            self.message = f"{winner} wins by checkmate!"
            self.game_over = True
        elif self.board.is_stalemate():
            self.message = "Stalemate! It's a draw."
            self.game_over = True

    def run(self):
        # Main game loop
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw_board()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ChessGame()
    game.run()
