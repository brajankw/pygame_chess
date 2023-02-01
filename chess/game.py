import copy
import pygame
from chess.board import Board
from chess.constants import SQUARE_SIZE, HEIGHT, WIDTH


class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        """update window of game
        """
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        if self.pawn_promotion:
            self.draw_pawn_promotion()
        if self.board.checkmate_bool:
            self.draw_checkmate()
        elif self.display_check:
            self.draw_check()
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = "white"
        self.valid_moves = {}
        self.check = None
        self.display_check = False
        self.pawn_promotion = False
        self.to_promote = None

    def reset(self):
        """restart game
        :return:
        """
        self._init()

    def select(self, row, col):
        """select piece by clicking on it
        :param row:
        :param col:
        :return:
        """
        if self.pawn_promotion: # pawn promotion
            pawn = self.board.get_piece(self.to_promote[0].row, self.to_promote[0].col)
            pawn.piece_type = self.to_promote[1][row]
            self.pawn_promotion = False
            self.to_promote = None

        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece

            possible_check_bool, possible_check_moves = self.board.possible_check(piece)
            if not self.check and possible_check_bool:  # check if piece can move
                self.valid_moves = possible_check_moves
            else:
                self.valid_moves = self.board.get_valid_moves(piece, self.board.check_bool)["moves"]
            return True

        return False

    def _move(self, row, col):
        """move piece from one square to another, if something is on another square remove it
        :param row:
        :param col:
        :return:
        """
        piece = self.board.get_piece(row, col)
        if self.selected and (row, col) in self.valid_moves:
            if piece != 0:
                self.board.remove(row, col)

            if self.board.move(self.selected, row, col):
                self.pawn_promotion = True
                self.update()

            self.change_turn()
            self.board.status = self.board.get_status(self.turn)  # update status of board
            self.is_check()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        """Draw circles on allowed squares to move
        :param moves:
        :return:
        """
        for move in moves:
            col, row = move
            pygame.draw.circle(self.win, (125, 125, 125),
                               (row * SQUARE_SIZE + SQUARE_SIZE // 2, col * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def draw_pawn_promotion(self):
        """Draw pieces to choose
        :return:
        """
        if self.selected:
            self.to_promote = [copy.deepcopy(self.selected), {}]
            if self.to_promote[0].piece_type == "pawn" and self.to_promote[0].row == 7 or self.to_promote[0].row == 0:
                if self.to_promote[0].color == "black":
                    stop = self.to_promote[0].row - 4
                    step = -1
                else:
                    stop = self.to_promote[0].row + 4
                    step = 1
                types = ["queen", "rook", "knight", "bishop"]

                for row, piece_type in zip(range(self.to_promote[0].row, stop, step), types):
                    self.to_promote[1].fromkeys(range(self.to_promote[0].row, stop, step))
                    pygame.draw.rect(self.win, (125, 125, 125),
                                     (
                                     self.to_promote[0].col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    x = SQUARE_SIZE * self.to_promote[
                        0].col + SQUARE_SIZE * 0.33 // 2  # center of square, cuz 1 - 0.67 in scale == 0.33
                    y = SQUARE_SIZE * row
                    piece_img = pygame.image.load(f'assets/pieces/{self.to_promote[0].color}_{piece_type}.png')
                    piece_img = pygame.transform.scale(piece_img, (SQUARE_SIZE * 0.67, SQUARE_SIZE))
                    self.win.blit(piece_img, (x, y))
                    self.to_promote[1][row] = piece_type

    def draw_check(self):
        """display check
        :return:
        """
        font = pygame.font.Font("assets/8bit.ttf", 80)
        text = font.render('CHECK', True, (0, 0, 0))
        text_check = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.win.blit(text, text_check)

    def draw_checkmate(self):
        """display checkmate and reset
        :return:
        """
        font = pygame.font.Font("assets/8bit.ttf", 80)
        font_restart = pygame.font.Font("assets/8bit.ttf", 40)
        text = font.render(f'{self.board.winner} WINS', True, (0, 0, 0))
        text_check = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        text_r = font_restart.render('PRESS R TO RESTART', True, (0, 0, 0))
        text_restart = text_r.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.win.blit(text, text_check)
        self.win.blit(text_r, text_restart)

    def is_check(self):
        """function is used after every move, it changes booleans of check and checkmate
        :return:
        """
        checked_color = self.turn
        check = self.board.get_status(checked_color)

        self.board.status_of_game = check
        if check["check"]["king_piece"] == 0:
            self.board.check_bool = False
            self.check = None
            self.display_check = False
        else:
            self.board.checkmate(self.turn)
            self.check = check
            self.display_check = True
            self.board.check_bool = True

    def change_turn(self):
        """change color, also reset valid_moves
        :return:
        """
        self.valid_moves = {}
        if self.turn == "black":
            self.turn = "white"
        else:
            self.turn = "black"
