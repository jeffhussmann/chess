import re
from pieces import *

move_pattern = re.compile(r"""
    (?:
    (?P<type>[KQRBN]?)          # The piece moving, or nothing if a pawn
    (?P<start_file>[abcdefgh]?) # The starting file, if specified
    (?P<start_rank>[12345678]?) # The starting rank, if specified
    (?P<capture>x?)             # Whether a capture occured
    (?P<dest_file>[abcdefgh])   # Destination file
    (?P<dest_rank>[12345678])   # Destination rank
    =?(?P<promotion>[KQRBN]?)   # Pawn promotion
    |
    (?P<castle_queen_side>O-O-O) 
    |
    (?P<castle_king_side>O-O)
    )
    (?P<outcome>[+#]?)         # Check or checkmate
                          """, re.VERBOSE)

class Game(object):    
    def __init__(self, parse_moves=True):
        self.info = {}
        if parse_moves:
            self.pieces = {'W':     {'':    [Pawn('w_a_p', 'W', (1, 0)),
                                             Pawn('w_b_p', 'W', (1, 1)),
                                             Pawn('w_c_p', 'W', (1, 2)),
                                             Pawn('w_d_p', 'W', (1, 3)),
                                             Pawn('w_e_p', 'W', (1, 4)),
                                             Pawn('w_f_p', 'W', (1, 5)),
                                             Pawn('w_g_p', 'W', (1, 6)),
                                             Pawn('w_h_p', 'W', (1, 7))],
                                     'N':   [Knight('w_b_n', 'W', (0, 1)),
                                             Knight('w_g_n', 'W', (0, 6))],
                                     'B':   [Bishop('w_c_b', 'W', (0, 2)),
                                             Bishop('w_f_b', 'W', (0, 5))],
                                     'R':   [Rook('w_a_r', 'W', (0, 0)),
                                             Rook('w_h_r', 'W', (0, 7))],
                                     'Q':   [Queen('w_d_q', 'W', (0, 3))],
                                     'K':   [King('w_e_k', 'W', (0, 4))],
                                     'promoted': {'': [],
                                                  'N': [],
                                                  'B': [],
                                                  'R': [],
                                                  'Q': [],
                                                  'K': []}},
                            'B':    {'':    [Pawn('b_a_p', 'B', (6, 0)),
                                             Pawn('b_b_p', 'B', (6, 1)),
                                             Pawn('b_c_p', 'B', (6, 2)),
                                             Pawn('b_d_p', 'B', (6, 3)),
                                             Pawn('b_e_p', 'B', (6, 4)),
                                             Pawn('b_f_p', 'B', (6, 5)),
                                             Pawn('b_g_p', 'B', (6, 6)),
                                             Pawn('b_h_p', 'B', (6, 7))],
                                     'N':   [Knight('b_b_n', 'B', (7, 1)),
                                             Knight('b_g_n', 'B', (7, 6))],
                                     'B':   [Bishop('b_c_b', 'B', (7, 2)),
                                             Bishop('b_f_b', 'B', (7, 5))],
                                     'R':   [Rook('b_a_r', 'B', (7, 0)),
                                             Rook('b_h_r', 'B', (7, 7))],
                                     'Q':   [Queen('b_d_q', 'B', (7, 3))],
                                     'K':   [King('b_e_k', 'B', (7, 4))],
                                     'promoted': {'': [],
                                                  'N': [],
                                                  'B': [],
                                                  'R': [],
                                                  'Q': [],
                                                  'K': []}}}
            self.board = [[self.pieces['W']['R'][0],
                           self.pieces['W']['N'][0],
                           self.pieces['W']['B'][0],
                           self.pieces['W']['Q'][0],
                           self.pieces['W']['K'][0],
                           self.pieces['W']['B'][1],
                           self.pieces['W']['N'][1],
                           self.pieces['W']['R'][1]], 
                          [pawn for pawn in self.pieces['W']['']],
                          [None]*8,
                          [None]*8,
                          [None]*8,
                          [None]*8,
                          [pawn for pawn in self.pieces['B']['']],
                          [self.pieces['B']['R'][0],
                           self.pieces['B']['N'][0],
                           self.pieces['B']['B'][0],
                           self.pieces['B']['Q'][0],
                           self.pieces['B']['K'][0],
                           self.pieces['B']['B'][1],
                           self.pieces['B']['N'][1],
                           self.pieces['B']['R'][1]]]
    
    def parse_move(self, m, color, move_num):
        dest_y = int(m.group('dest_rank')) - 1
        dest_x = ord(m.group('dest_file')) - ord('a')
        piece_type = m.group('type')
        curr_x = ord(m.group('start_file')) - ord('a') if m.group('start_file') else None
        curr_y = int(m.group('start_rank')) - 1 if m.group('start_rank') else None
        is_capture = bool(m.group('capture'))
        promotion = m.group('promotion')
        if curr_x != None and curr_y != None:
            piece_to_move = self.board[curr_y][curr_x]
        else:
            candidates = filter(lambda p: p.is_alive, self.pieces[color][piece_type] + self.pieces[color]['promoted'][piece_type])
            if curr_x != None and curr_y == None:
                candidates = filter(lambda p: p.curr_x == curr_x, candidates)
            elif curr_x == None and curr_y != None:
                candidates = filter(lambda p: p.curr_y == curr_y, candidates)
            candidates = filter(lambda p: p.can_move_to(dest_y, dest_x, is_capture, self.board), candidates)
            if len(candidates) == 1:
                piece_to_move = candidates[0]
            else:
                print "not exactly one eligible piece, need to check for check-avoidance"
                print self.pieces[color]
                print m.groups()
                print "moving to (%i, %i)" % (dest_y, dest_x) 
                print candidates
                self.print_board()
                sys.stdout.flush()
                sys.stdin.readline()
        return piece_to_move, dest_y, dest_x, move_num, is_capture, promotion
    
    def move(self, move_string, move_num, color):
        is_white = (color == 'W')
        m = move_pattern.match(move_string)
        if m.group('castle_king_side'):
            self.perform_move(self.pieces[color]['K'][0], 0 if is_white else 7, 6, move_num, False, '')
            self.perform_move(self.pieces[color]['R'][1], 0 if is_white else 7, 5, move_num, False, '')
        elif m.group('castle_queen_side'):
            self.perform_move(self.pieces[color]['K'][0], 0 if is_white else 7, 2, move_num, False, '')
            self.perform_move(self.pieces[color]['R'][0], 0 if is_white else 7, 3, move_num, False, '')
        else:
            self.perform_move(*self.parse_move(m, color, move_num))

    def perform_move(self, piece_to_move, dest_y, dest_x, move_num, is_capture, promotion):
        if is_capture:
            piece_to_capture = self.board[dest_y][dest_x]
            if not piece_to_capture:
                # Assuming a legal game, must be en passant
                if dest_y == 5:
                    piece_to_capture = self.board[dest_y - 1][dest_x]
                    self.board[dest_y - 1][dest_x] = None
                elif dest_y == 2:
                    piece_to_capture = self.board[dest_y + 1][dest_x]
                    self.board[dest_y + 1][dest_x] = None
            piece_to_capture.curr_y = -1
            piece_to_capture.curr_x = -1
            piece_to_capture.is_alive = False
            piece_to_capture.move_captured = move_num
        self.board[piece_to_move.curr_y][piece_to_move.curr_x] = None
        if promotion:
            color = piece_to_move.color
            if promotion == 'Q':
                constructor = Queen
            elif promotion == 'R':
                constructor = Rook
            elif promotion == 'B':
                constructor = Bishop
            elif promotion == 'N':
                constructor = Knight
            new_piece = constructor(piece_to_move.name + '_promoted', color, (dest_y, dest_x), move_num)
            self.pieces[color]['promoted'][promotion].append(new_piece)
            self.board[dest_y][dest_x] = new_piece
            piece_to_move.move_promoted = move_num
            piece_to_move.curr_y = -1
            piece_to_move.curr_x = -1
        else:
            self.board[dest_y][dest_x] = piece_to_move
            piece_to_move.curr_y = dest_y
            piece_to_move.curr_x = dest_x
        piece_to_move.pos_hist.append(((dest_y, dest_x), move_num))

    def print_board(self):
        for row in range(7, -1, -1):
            line = []
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    symbol = piece.name[4] #TODO: doesn't handle promoted pieces well
                    if 'promoted' in piece.name:
                        symbol = 'z'
                    if piece.name[0] == 'w':
                        symbol = symbol.upper()
                    line.append(symbol)
                else:
                    line.append(' ')
            print ''.join(line)
