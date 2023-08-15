from game_logic import GameLogic, BLACK, WHITE
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor
from piece import Piece


class Board(QFrame):  # base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int)  # signal sent when timer is updated
    clickLocationSignal = pyqtSignal(str)  # signal sent when there is a new click location
    player_turn_signal = pyqtSignal(bool)
    black_timer_signal = pyqtSignal(int)
    white_timer_signal = pyqtSignal(int)

    boardWidth = 7  # board is 7 squares wide
    boardHeight = 7  # board is 7 squares high
    timerSpeed = 1  # the timer updates every 1 second
    counter = 0  # the number the counter will count down from
    white_counter = 120000  # timer default is milliseconds
    black_counter = 120000  # timer default is milliseconds
    square_size = 70
    radius = square_size // 2 - 10

    def __init__(self, parent):
        super().__init__(parent)
        self.game = None
        self.init_board()

    def init_board(self):
        """initiates board"""
        self.is_started = False  # game is not currently started
        self.player_black_turn = True  # black always goes first
        self.timer = QBasicTimer()  # create a timer for the game
        self.speed_go = False
        self.black_timer = QBasicTimer()
        self.white_timer = QBasicTimer()

        # Creates a 2d int/Piece array to store the state of the game
        # at beginning no pieces on board
        number_of_rows = Board.boardWidth + 1
        number_of_columns = Board.boardHeight + 1
        self.board_array = []
        for x in range(number_of_rows):
            column_elements = []
            for y in range(number_of_columns):
                column_elements.append(Piece.NoPiece)
            # Append the column to the array.
            self.board_array.append(column_elements)

        self.print_board_array()

    def print_board_array(self):
        """prints the boardArray in an attractive way"""
        print("boardArray:")
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.board_array]))

    def mouse_pos_to_col_row(self, event):
        x, y = event.pos().x(), event.pos().y()
        boardSize = Board.boardWidth+1
        xSpacing = self.square_width()
        ySpacing = self.square_width()
        self.gridY = self.shift()
        self.gridX = self.shift()
        row = round((y - self.gridY) / ySpacing)
        col = round((x - self.gridX) / xSpacing)
        if row < 0 or row >= boardSize or col < 0 or col >= boardSize:
            return -1, -1, None
        return row, col, row * boardSize + col

    def square_width(self):
        """returns the width of one square in the board"""
        return self.square_size

    def square_height(self):
        """returns the height of one square of the board"""
        return self.square_size

    def shift(self):
        return self.radius

    def start(self):
        """starts game"""
        self.is_started = True  # set the boolean which determines if the game has started to TRUE
        self.timer.start(self.timerSpeed, self)  # start the timer with the correct speed
        self.game = GameLogic(self.boardWidth+1)
        print("start () - timer is started")

    def timerEvent(self, event):
        """this event is automatically called when the timer is updated. based on the timerSpeed variable """
        if self.is_started:
            if event.timerId() == self.timer.timerId():  # if the timer that has 'ticked' is the one in this class
                Board.counter += 1
                self.counter = Board.counter / 1000  # to show time in seconds
                # print('timerEvent()', self.counter)
                self.updateTimerSignal.emit(self.counter)
            else:
                super(Board, self).timerEvent(event)  # if we do not handle an event we should pass it to the super
                # class for handling otherwise pass it to the super class for handling
        if self.speed_go:
            if event.timerId() == self.black_timer.timerId():
                if Board.black_counter == 0:
                    time_remaining = 0
                else:
                    Board.black_counter -= 1
                    time_remaining = Board.black_counter / 1000
                    # print('Black timerEvent()', time_remaining)
                self.black_timer_signal.emit(time_remaining)

            if event.timerId() == self.white_timer.timerId():
                if Board.white_counter == 0:
                    time_remaining = 0
                else:
                    Board.white_counter -= 1
                    time_remaining = Board.white_counter / 1000
                    # print('White timerEvent()', time_remaining)
                self.white_timer_signal.emit(time_remaining)

    def stop_timer(self):
        self.timer.stop()

    def speed_game(self, var):
        self.speed_go = var
        self.black_timer.start(self.timerSpeed, self)

    def paintEvent(self, event):
        """paints the board and the pieces of the game"""
        painter = QPainter(self)
        self.draw_board_squares(painter)
        painter.resetTransform()
        self.draw_pieces(painter)

    def mousePressEvent(self, event):
        """this event is automatically called when the mouse is pressed"""
        if not self.is_started:
            return

        click_loc = "click location [" + str(event.x()) + "," + str(event.y()) + "]"
        row, col, point = self.mouse_pos_to_col_row(event)

        if point is None:
            return

        is_legal = self.try_move(row, col)
        if is_legal:
            self.repaint()

        self.clickLocationSignal.emit(click_loc)

        if self.player_black_turn:
            self.player_black_turn = False
            if self.speed_go:
                self.black_timer.stop()
                self.white_timer.start(self.timerSpeed, self)
        else:
            self.player_black_turn = True
            if self.speed_go:
                self.white_timer.stop()
                self.black_timer.start(self.timerSpeed, self)

        self.player_turn_signal.emit(self.player_black_turn)


    def pass_turn(self, var):
        if not self.is_started:
            return
        # check if we can pass
        is_passable = self.game.passing()
        if is_passable:
            data = self.game.get_data()
            is_game_over = data['game_over']
            if is_game_over:
                return False
            else:
                internal_turn = self.game.turn
                if internal_turn == WHITE:
                    self.player_black_turn = False
                else:
                    self.player_black_turn = True

        if self.speed_go:
            if is_passable:
                if self.white_timer.isActive():
                    self.white_timer.stop()
                self.black_timer.start(self.timerSpeed, self)
            else:
                if self.black_timer.isActive():
                    self.black_timer.stop()
                self.white_timer.start(self.timerSpeed, self)
        return True

    def end_game(self):
        """Writes the score"""
        if not self.is_started:
            return

        score, positionScored = self.game.score_game()
        if score > 0:
            print("B+{}".format(score))
        elif score < 0:
            print("W+{}".format(-score))
        else:
            print("Jigo")

    def reset_game(self):
        """clears pieces from the board"""
        number_of_rows = Board.boardWidth + 1
        number_of_columns = Board.boardHeight + 1
        self.board_array = []
        for x in range(number_of_rows):
            column_elements = []
            for y in range(number_of_columns):
                column_elements.append(Piece.NoPiece)
            self.board_array.append(column_elements)
        self.is_started = False
        self.timer.stop()
        Board.counter = 0
        Board.white_counter = 120000
        Board.black_counter = 120000
        if self.speed_go:
            if self.black_timer.isActive():
                self.black_timer.stop()
            if self.white_timer.isActive():
                self.white_timer.stop()
        self.speed_go = False
        self.game.__init__(self.boardWidth + 1)
        self.update()

    def try_move(self, new_x, new_y):
        """tries to move a piece"""
        # play the move if legal one
        is_legal = self.game.place_stone(new_y, new_x)
        # if legal, update the bord
        if is_legal:
            self.board_array = self.game._stones()
        return is_legal

    def draw_board_squares(self, painter):
        """draw all the square on the board"""

        # Sets the default colour of the brush
        colour = QColor("#FCF3CF")
        painter.setBrush(colour)
        colour_counter = 0

        painter.translate(self.shift(), self.shift())
        for row in range(0, Board.boardHeight):
            for col in range(0, Board.boardWidth):
                painter.save()
                col_transformation = self.square_width() * col
                row_transformation = self.square_height() * row
                painter.translate(col_transformation, row_transformation)
                rect = QRect(row, col, self.square_width(), self.square_width())
                color = QColor(colour)
                painter.fillRect(rect, color)
                painter.restore()
                # Changes the colour of the brush so that a checkered board is drawn
                if colour_counter == 0:
                    colour = QColor("#D0ECE7")
                    colour_counter += 1
                else:
                    colour = QColor("#FCF3CF")
                    colour_counter -= 1
                painter.setBrush(colour)

    def draw_pieces(self, painter):
        """draw the prices on the board"""

        colour = Qt.transparent

        painter.translate(self.shift() - self.radius, self.shift() - self.radius)
        for row in range(0, len(self.board_array)):
            for col in range(0, len(self.board_array)):
                painter.save()

                painter.translate((self.square_size * row) - 0, (col * self.square_size) - 0)

                piece = self.board_array[col][row]
                # Sets the painter brush to the correct colour
                if piece == Piece.NoPiece:
                    colour = Qt.transparent
                elif piece == Piece.White:
                    colour = Qt.white
                elif piece == Piece.Black:
                    colour = Qt.black
                painter.setBrush(colour)
                radius = self.radius
                center = QPoint(radius, radius)
                # Draws the pieces as ellipses
                painter.drawEllipse(center, radius, radius)
                painter.restore()
