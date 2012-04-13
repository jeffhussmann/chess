class Piece(object):
    def __init__(self, name, color, start_pos, move_created=0):
        self.name = name
        self.color = color
        self.pos_hist = [(start_pos, 0)]
        self.curr_y, self.curr_x = start_pos
        self.is_alive = True
        self.move_created = move_created
        self.move_captured = None
        self.move_promoted = None # TODO: this can be made pawn-specific
    def __repr__(self):
        return "%s: (%i, %i)" % (self.name, self.curr_y, self.curr_x)

class Pawn(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        dy = dest_y - self.curr_y
        dx = dest_x - self.curr_x
        is_white = (self.color == 'W')
        if not is_capture and dx == 0:
            if is_white:
                if dy == 1:
                    return True
                if dy == 2 and self.curr_y == 1 and not board[2][self.curr_x]:
                    return True
            if not is_white:
                if dy == -1:
                    return True
                if dy == -2 and self.curr_y == 6 and not board[5][self.curr_x]:
                    return True
        if is_capture and abs(dx) == 1:
            if is_white and dy == 1:
                return True
            if not is_white and dy == -1:
                return True
        return False
        
class Knight(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        abs_dy = abs(dest_y - self.curr_y)
        abs_dx = abs(dest_x - self.curr_x)
        if (abs_dx == 2 and abs_dy == 1) or (abs_dx == 1 and abs_dy == 2):
            return True
        return False

class Bishop(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        dy = dest_y - self.curr_y
        dx = dest_x - self.curr_x
        if abs(dx) == abs(dy):
            y_sign = 1 if dy > 0 else -1
            x_sign = 1 if dx > 0 else -1
            path = [board[self.curr_y + y_sign*i][self.curr_x + x_sign*i] for i in range(1, abs(dy))]
            if not any(path):
                return True
        return False

class Rook(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        dy = dest_y - self.curr_y
        dx = dest_x - self.curr_x
        if abs(dx) == 0:
            # Check for pieces in the way
            path = [board[row][dest_x] for row in range(min(self.curr_y, dest_y) + 1, max(self.curr_y, dest_y))]
            if not any(path):
                return True
        if abs(dy) == 0:
            path = board[dest_y][min(self.curr_x, dest_x) + 1: max(self.curr_x, dest_x)]
            if not any(path):
                return True
        return False

class Queen(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        dy = dest_y - self.curr_y
        dx = dest_x - self.curr_x
        if abs(dx) == abs(dy):
            # Diagonal move
            y_sign = 1 if dy > 0 else -1
            x_sign = 1 if dx > 0 else -1
            path = [board[self.curr_y + y_sign*i][self.curr_x + x_sign*i] for i in range(1, abs(dy))]
            if not any(path):
                return True
        if abs(dx) == 0:
            path = [board[row][dest_x] for row in range(min(self.curr_y, dest_y) + 1, max(self.curr_y, dest_y))]
            if not any(path):
                return True
        if abs(dy) == 0:
            path = board[dest_y][min(self.curr_x, dest_x) + 1: max(self.curr_x, dest_x)]
            if not any(path):
                return True
        return False

class King(Piece):
    def can_move_to(self, dest_y, dest_x, is_capture, board):
        return True
