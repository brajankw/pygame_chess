import pygame
import copy
from chess.constants import BLACK, WHITE, ROWS, COLS, SQUARE_SIZE
from chess.piece import Piece


class Board:
    def __init__(self):
        """
        board is representing every row and column, pieces are there
        pawn_promotion bool goes true if pawn black pawn is on 7 row or white on 0
        status have all information about game, updates after every move
        """
        self.board = []
        self.col_start_pos = {  # starting position of pieces on first and last row
            0: "rook",
            1: "knight",
            2: "bishop",
            3: "queen",
            4: "king",
            5: "bishop",
            6: "knight",
            7: "rook"
        }
        self.pawn_promotion = False
        self.status = {
            "on_move": 0,
            "white_pieces": {},
            "white_moves": [],
            "white_pieces_defended": [],
            "black_pieces": {},
            "black_moves": [],
            "black_pieces_defended": [],
            "check": {
                "king_piece": 0,
                "checking_pieces": [],
            },

        }
        self.create_board()
        self.check_bool = False
        self.checkmate_bool = False

    @staticmethod
    def draw_squares(win):
        """ Draw squares of board, firstly white color generates on screen,
        then makes every 2 square black squares from image
        :param win:
        :return:
        """
        win.fill(WHITE)
        black_square = pygame.image.load('assets/black_boardv2.png')
        black_square = pygame.transform.scale(black_square, (SQUARE_SIZE, SQUARE_SIZE))
        for row in range(ROWS):
            for col in range(row % 2 - 1, ROWS, 2):
                win.blit(black_square, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        """Create pieces and put them on proper squares
        also put 0, on blank squares
        """
        for row in range(ROWS):
            color = "black" if row < 2 else "white"  # color of pieces, rows 0, 1 are black
            self.board.append([])  # creates row in board
            for col in range(COLS):
                if row == 1 or row == 6:
                    self.board[row].append(Piece(row, col, color, "pawn"))
                elif row == 0 or row == 7:
                    self.board[row].append(Piece(row, col, color, self.col_start_pos[col]))
                else:
                    self.board[row].append(0)

    def draw(self, win):
        """Draw first squares, then draw pieces
        :param piece:
        :param win:
        :return:
        """
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw_piece(win)

    def move(self, piece, row, col):
        """Move the piece, simply change current position of piece with another piece or 0 in board[],
        checks if pawn is on promotion square, and if king is in check, or castle is allowed
        :param win:
        :param piece:
        :param row:
        :param col:
        """
        if piece.piece_type == "king":  # castle
            if piece.col == col + 2:
                long_castle_rook = self.board[row][0]
                self.board[row][0], self.board[row][3] = self.board[row][0], self.board[row][3]
                long_castle_rook.move(row, 3)
                long_castle_rook.moves += 1
            if piece.col == col - 2:
                short_castle_rook = self.board[row][7]
                self.board[row][7], self.board[row][5] = self.board[row][5], self.board[row][7]
                short_castle_rook.move(row, 5)
                short_castle_rook.moves += 1
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        piece.moves += 1

        if (row == 7 or row == 0) and piece.piece_type == "pawn":
            return True

    def get_piece(self, row, col):
        """Get position of piece
        :param row:
        :param col:
        """
        return self.board[row][col]

    def remove(self, row, col):
        """Remove pawn from board
        :param row:
        :param col:
        :return:
        """
        self.board[row][col] = 0

    def attacked_squares(self):
        """Take status, and return attacked squares including ones behind king
        list attacked_squares is used by check and checkmate method
        :return:
        """
        checking_piece = self.status["check"]["checking_pieces"][0]
        king = self.status["check"]["king_piece"]
        attacked_squares = []

        if checking_piece.piece_type == "knight":
            attacked_squares.append((checking_piece.row, checking_piece.col))

        else:
            if king.col == checking_piece.col:  # rook, queen
                row = checking_piece.row
                step = 1 if king.row > checking_piece.row else -1
                while row != king.row + step:
                    row += step
                    attacked_squares.append((row, king.col))

            if king.row == checking_piece.row:  # rook, queen
                col = checking_piece.col
                step = 1 if king.col > checking_piece.col else -1
                while col != king.col + step:
                    col += step
                    attacked_squares.append((king.row, col))

            if king.row != checking_piece.row and king.row != checking_piece.row:  # bishop, queen
                if king.row < checking_piece.row:
                    step_row = -1
                else:
                    step_row = 1
                if king.col < checking_piece.col:
                    step_col = -1
                else:
                    step_col = 1
                start_row, end_row = sorted([king.row + step_row, checking_piece.row])
                start_col, end_col = sorted([king.col + step_col, checking_piece.col])
                for i, j in zip(range(start_row, end_row), range(start_col, end_col)):
                    attacked_squares.append((i, j))
            attacked_squares.append((checking_piece.row, checking_piece.col))

        return attacked_squares

    def check(self, piece, moves):
        """Function returns valid moves after king being checked,
        so if piece.type != "king" these pieces can only block or attack checking pieces
        :param piece:
        :param moves:
        :return:
        """
        enemy_color = "white" if piece.color == "black" else "black"
        check_moves = copy.deepcopy(moves)
        attacked_squares = self.attacked_squares()

        if piece.piece_type != "king":  # block or attack checking piece
            check_moves["moves"] = {move: val for move, val in moves["moves"].items() if move in attacked_squares}
            return check_moves
        if piece.piece_type == "king":
            checking_piece = self.status["check"]["checking_pieces"][0]
            if not (checking_piece in self.status[f"{enemy_color}_pieces_defended"]) and (checking_piece.row,
                                                                                          checking_piece.col) in attacked_squares:  # allows to kill not defended piece while check
                attacked_squares.pop(attacked_squares.index((checking_piece.row, checking_piece.col)))
            check_moves["moves"] = {move: val for move, val in moves["moves"].items() if move not in attacked_squares}
            return check_moves

    def checkmate(self, color):
        """Check if it is checkmate
        :param color:
        :return:
        """
        enemy_color = "white" if color == "black" else "black"
        checking_piece = self.status["check"]["checking_pieces"][0]
        attacked_squares = self.attacked_squares()
        kings_moves = []
        print(self.status)
        for piece, piece_moves in self.status[ f"{color}_pieces"].items():  # iterate over king moves, if move is not in attacked_squares(including the ones behind king) then add it to list
            if f"{color}_king" in piece:
                for move in piece_moves.keys():
                    if move not in attacked_squares and move not in self.status[f"{enemy_color}_moves"]:
                        kings_moves.append(move)
        if checking_piece in self.status[f"{enemy_color}_pieces_defended"]:  # if piece is defended, if not it is not a checkmate
            if checking_piece not in self.status[f"{color}_moves"] and not any(move in attacked_squares for move in
                                                                               self.status[
                                                                                   f"{color}_moves"]) and not kings_moves:  # if checking piece cant be attacked and ally cant block it and king has no other moves it is checkmate
                self.winner = enemy_color
                self.checkmate_bool = True

    def get_valid_moves(self, piece, check=False, board=None):
        """Generate valid moves of piece, these moves are used in almost every function and in self.status
        :param piece:
        :param check:
        :param board:
        :return:
        """

        moves = {
            "moves": {},
            "defended_pieces": {},
        }

        traversals = {
            "pawn": "_traverse_pawn",
            "knight": "_traverse_knight",
            "bishop": "_traverse_bishop",
            "rook": "_traverse_rook",
            "queen": "_traverse_queen",
            "king": "_traverse_king"
        }
        move_func = getattr(self, traversals[piece.piece_type])
        move_result = move_func(piece.row, piece.col, piece.color, board)
        moves["moves"].update(move_result["moves"])
        moves["defended_pieces"].update(move_result["defended_pieces"])

        if check:
            check_moves = self.check(piece, moves)
            return check_moves

        return moves

    def get_status(self, color, piece_row=None, piece_column=None):
        """Generate status of game
        piece_row and piece_column are None default because they are only used in possible_check
        :param color:
        :param piece_row:
        :param piece_column:
        :return:
        """
        status = {
            "on_move": color,
            "white_pieces": {},
            "white_moves": [],
            "white_pieces_defended": [],
            "black_pieces": {},
            "black_moves": [],
            "black_pieces_defended": [],
            "check": {
                "king_piece": 0,
                "checking_pieces": [],
            },

        }
        board = self.board
        if piece_row is not None:
            board = copy.deepcopy(self.board)
            board[piece_row][piece_column] = 0
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece != 0:
                    piece_moves = self.get_valid_moves(piece, board=board)
                    status[f"{piece.color}_pieces"].update({f"{piece}": piece_moves["moves"]})
                    status[f"{piece.color}_moves"] += piece_moves["moves"].keys()
                    status[f"{piece.color}_pieces_defended"] += piece_moves["defended_pieces"].values()
                    for i in piece_moves["moves"].keys():
                        if piece_moves["moves"][i] != 0 and piece_moves["moves"][i].piece_type == "king" and \
                                piece_moves["moves"][i].color != piece.color:
                            status["check"]["king_piece"] = piece_moves["moves"][i]
                            status["check"]["checking_pieces"].append(piece)
        return status

    def possible_check(self, piece):
        """Prevent of piece movement when king is behind this piece
        :param piece:
        :return:
        """
        valid_moves = {}
        possible_check_bool = False
        possible_check = self.get_status(piece.color, piece.row, piece.col)
        piece_moves = self.get_valid_moves(piece)["moves"]
        if possible_check["check"]["king_piece"] != 0 and piece.color == possible_check["check"]["king_piece"].color:
            possible_check_bool = True
            for checking_piece in possible_check["check"]["checking_pieces"]:
                for piece_move in piece_moves.keys():
                    if piece_move == (checking_piece.row, checking_piece.col):
                        valid_moves = {piece_move}
        return possible_check_bool, valid_moves

    def castle(self, color, row):
        """allows to do castle with rook and king
        :param color:
        :param row:
        :return:
        """
        short_castle = False
        long_castle = False
        if self.status["check"]["king_piece"] == 0:  # castle is not allowed while check
            if self.board[row][0] != 0:
                if self.board[row][0].color == color and self.board[row][0].piece_type == "rook" and self.board[row][
                    0].moves == 0 and self.board[row][1] == self.board[row][2] == self.board[row][3] == 0:
                    long_castle = True
            if self.board[row][7] != 0:
                if self.board[row][7].color == color and self.board[row][0].piece_type == "rook" and self.board[row][
                    7].moves == 0 and self.board[row][5] == self.board[row][6] == 0:
                    short_castle = True
        return long_castle, short_castle

    def possibly_pawn_pos(self, color, row, col):
        """Not allowing king to go on pawn protected squares, because pawn direction attack is not like his movement
        :param color:
        :param row:
        :param col:
        :return:
        """
        pawn_attacked_squares = []
        var = 1
        if color == "black":
            var = -1
        possibly_pawn_pos = [(row, col - 2), (row, col - 1), (row, col + 1), (row, col + 2), (row - 1 * var, col - 2),
                             (row - 1 * var, col), (row - 1 * var, col + 2),
                             (row - 2 * var, col - 2), (row - 2 * var, col - 1), (row - 2 * var, col),
                             (row - 2 * var, col + 1), (row - 2 * var, col + 2)]
        for possibly_pawn in possibly_pawn_pos:
            pawn_row, pawn_col = possibly_pawn
            if 0 <= pawn_row <= 7 and 0 <= pawn_col <= 7:
                if self.board[pawn_row][pawn_col] != 0 and self.board[pawn_row][pawn_col].piece_type == "pawn" and \
                        self.board[pawn_row][pawn_col].color != color:
                    pawn_row = pawn_row + 1 if color == "white" else pawn_row - 1
                    pawn_attacked_squares.append((pawn_row, pawn_col + 1))
                    pawn_attacked_squares.append((pawn_row, pawn_col - 1))
        return pawn_attacked_squares

    def possibly_king_pos(self, color, row, col):
        """Not allowing kings to go each other zones
        :param color:
        :param row:
        :param col:
        :return:
        """
        enemy_king_attacked_squares = []

        possibly_enemy_king_pos = {(row + 2, col - 2): [(row + 1, col - 1)],
                                   (row + 2, col - 1): [(row + 1, col - 1), (row + 1, col)],
                                   (row + 2, col): [(row + 1, col - 1), (row + 1, col), (row + 1, col + 1)],
                                   (row + 2, col + 1): [(row + 1, col), (row + 1, col + 1)],
                                   (row + 2, col + 2): [(row + 1, col)],
                                   (row + 1, col - 2): [(row + 1, col - 1), (row, col - 1)],
                                   (row + 1, col + 2): [(row + 1, col + 1), (row, col + 1)],
                                   (row, col - 2): [(row + 1, col - 1), (row, col - 1), (row - 1, col - 1)],
                                   (row, col + 2): [(row + 1, col + 1), (row, col + 1), (row - 1, col + 1)],
                                   (row - 1, col - 2): [(row - 1, col - 1), (row, col - 1)],
                                   (row - 1, col + 2): [(row - 1, col + 1), (row, col + 1)],
                                   (row - 2, col - 2): [(row - 1, col - 1)],
                                   (row - 2, col - 1): [(row - 1, col - 1), (row - 1, col)],
                                   (row - 2, col): [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1)],
                                   (row - 2, col + 1): [(row - 1, col + 1), (row - 1, col)],
                                   (row - 2, col + 2): [(row - 1, col + 1)]
                                   }

        for possibly_enemy_king in possibly_enemy_king_pos:
            enemy_king_row, enemy_king_col = possibly_enemy_king
            if 0 <= enemy_king_row <= 7 and 0 <= enemy_king_col <= 7:
                if self.board[enemy_king_row][enemy_king_col] != 0 and self.board[enemy_king_row][enemy_king_col].piece_type == "king" and self.board[enemy_king_row][enemy_king_col].color != color:
                    enemy_king_attacked_squares += possibly_enemy_king_pos[(enemy_king_row, enemy_king_col)]
        return enemy_king_attacked_squares

    def _traverse_pawn(self, row, col, color, board=None):
        """Generate movement and pieces defended by pawn
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        if not board:
            board = self.board
        moves = {
            "moves": {},
            "defended_pieces": {},
        }

        piece_moves = board[row][col].moves
        col_left, col_right = col - 1, col + 1  # used to calculate attacking direction
        start, stop, step = (row + 1, row + 3, 1) if color == "black" else (row - 1, row - 3, -1)
        if piece_moves > 0:
            stop -= step  # if not first move, it goes just 1 square
        if stop == 9:  # if black pawn promotion do nothing, just promote(it is fix of bug)
            return moves
        for r in range(start, stop, step):
            if board[r][col] == 0:
                moves["moves"][(r, col)] = board[r][col]
            if r == start:
                if col_left >= 0 and board[r][col_left] != 0 and color != board[r][col_left].color:
                    moves["moves"][(r, col_left)] = board[r][col_left]
                if col_left >= 0 and board[r][col_left] != 0 and color == board[r][col_left].color:
                    moves["defended_pieces"][(r, col_left)] = board[r][col_left]
                if col_right <= 7 and board[r][col_right] != 0 and color != board[r][col_right].color:
                    moves["moves"][(r, col_right)] = board[r][col_right]
                if col_right <= 7 and board[r][col_right] != 0 and color == board[r][col_right].color:
                    moves["defended_pieces"][(r, col_right)] = board[r][col_right]
        if piece_moves == 0 and board[start][
            col] != 0:  # it removes 2nd square in front of pawn if on 1st square is anything
            if (start + step, col) in moves["moves"].keys():
                moves["moves"].pop((start + step, col))
        return moves

    def _traverse_knight(self, row, col, color, board=None):
        """Generate movement and pieces defended by knight
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        if not board:
            board = self.board
        moves = {
            "moves": {},
            "defended_pieces": {},
        }
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]  # way that knight jumps

        for direction in directions:
            r, c = direction
            if 0 <= row + r <= 7 and 0 <= col + c <= 7:
                piece = board[row + r][col + c]
                if piece == 0 or piece.color != color:
                    moves["moves"][(row + r, col + c)] = piece
                else:
                    moves["defended_pieces"][(row + r, col + c)] = piece

        return moves

    def _traverse_bishop(self, row, col, color, board=None):
        """ Generate movement and pieces defended by bishop
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        if not board:
            board = self.board
        moves = {
            "moves": {},
            "defended_pieces": {},
        }

        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for direction in directions:
            r_step, c_step = direction
            for i in range(1, 8):
                r, c = row + i * r_step, col + i * c_step
                if 0 <= r <= 7 and 0 <= c <= 7:
                    piece = board[r][c]
                    if piece == 0 or piece.color != color:
                        moves["moves"][(r, c)] = piece
                    if piece != 0:
                        moves["defended_pieces"][(r, c)] = piece
                        break

        return moves

    def _traverse_rook(self, row, col, color, board=None):
        """Generate movement and pieces defended by rook
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        if not board:
            board = self.board
        moves = {
            "moves": {},
            "defended_pieces": {},
        }

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for direction in directions:
            r_step, c_step = direction
            r, c = row, col
            for i in range(1, 8):
                r += r_step
                c += c_step
                if not (0 <= r <= 7) or not (0 <= c <= 7):
                    break
                piece = board[r][c]
                if piece == 0:
                    moves["moves"][(r, c)] = piece
                elif piece.color != color:
                    moves["moves"][(r, c)] = piece
                    break
                else:
                    moves["defended_pieces"][(r, c)] = piece
                    break

        return moves

    def _traverse_queen(self, row, col, color, board=None):
        """Generate movement and pieces defended by queen, using rook and bishop traverse
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        if not board:
            board = self.board

        moves = {
            "moves": {},
            "defended_pieces": {},
        }
        moves["moves"].update(self._traverse_bishop(row, col, color, board)["moves"])
        moves["defended_pieces"].update(self._traverse_bishop(row, col, color, board)["defended_pieces"])
        moves["moves"].update(self._traverse_rook(row, col, color, board)["moves"])
        moves["defended_pieces"].update(self._traverse_rook(row, col, color, board)["defended_pieces"])

        return moves

    def _traverse_king(self, row, col, color, board=None):
        enemy_color = "white" if color == "black" else "black"
        """Generate movement of king, includes also illegal moves
        :param row:
        :param col:
        :param color:
        :param board:
        :return:
        """
        moves = {
            "moves": {},
            "defended_pieces": {},
        }
        illegal_moves = []

        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        illegal_moves += self.possibly_pawn_pos(row=row, col=col, color=color)
        illegal_moves += self.possibly_king_pos(row=row, col=col, color=color)
        illegal_moves += self.status[f"{enemy_color}_moves"]
        illegal_moves += [(piece.row, piece.col) for piece in self.status[f"{enemy_color}_pieces_defended"]]

        for direction in directions:
            r_step, c_step = direction
            r, c = row + r_step, col + c_step
            if not (0 <= r <= 7) or not (0 <= c <= 7) or (r, c) in illegal_moves:
                continue
            piece = self.board[r][c]
            if piece == 0:
                moves["moves"][(r, c)] = piece
            elif piece.color != color:
                moves["moves"][(r, c)] = piece
            else:
                moves["defended_pieces"][(r, c)] = piece

        if self.board[row][col].moves == 0:
            long_castle, short_castle = self.castle(color, row)
            if long_castle:
                moves["moves"][(row, col - 2)] = 0
            if short_castle:
                moves["moves"][(row, col + 2)] = 0

        return moves
