import pygame
from chess.constants import SQUARE_SIZE


class Piece:
    def __init__(self, row, col, color, piece_type):
        self.row = row
        self.col = col
        self.color = color
        self.piece_type = piece_type
        self.moves = 0

        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        """Calculate position of piece
        piece_img x is scaled so, it has to be centered
        piece_img y no need to center, it takes full height of SQUARE_SIZE
        :return:
        """
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE * 0.33 // 2  # center of square, cuz 1 - 0.67 in scale == 0.33
        self.y = SQUARE_SIZE * self.row

    def pawn_promotion(self):
        self.piece_type = "queen"

    def draw_piece(self, win):
        """Draw piece on x and y using scaled image, takes color and piece type
        :param win:
        :return:
        """
        piece_img = pygame.image.load(f'assets/pieces/{self.color}_{self.piece_type}.png')
        piece_img = pygame.transform.scale(piece_img, (SQUARE_SIZE * 0.67, SQUARE_SIZE))
        win.blit(piece_img, (self.x, self.y))

    def move(self, row, col):
        """Move piece to given row, and col then calculate x and y
        :param row:
        :param col:
        :return:
        """
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return f"{self.color}_{self.piece_type}({self.row}, {self.col})"
