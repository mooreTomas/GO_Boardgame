from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QWidget, \
    QLabel, QPushButton
from PyQt5.QtCore import pyqtSlot, pyqtSignal

import __main__


class ScoreBoard(QDockWidget):
    """base the score_board on a QDockWidget"""
    pass_turn_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """initiates ScoreBoard UI"""
        self.resize(200, 200)
        self.setWindowTitle('ScoreBoard')
        self.setStyleSheet("background-color: white;")
        # create a widget to hold other widgets
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.white_pass = 0
        self.black_pass = 0
        self.speed_go = False

        # create two labels which will be updated by signals
        self.label_click_location = QLabel("Click Location: ")
        self.label_click_location.setStyleSheet("margin: 0px; padding:2px;")
        self.label_click_location.setFont(QFont('Arial', 10))
        self.label_click_location.setMinimumWidth(300)

        self.label_time_remaining = QLabel("Time Taken: ")
        self.label_time_remaining.setStyleSheet("margin: 0px; padding:2px; ")
        self.label_time_remaining.setFont(QFont('Arial', 10))

        self.start = QPushButton("Start Game", self)
        self.start.setFont(QFont('Arial', 10))
        self.start.setStyleSheet("margin: 0px; padding:5px;")
        self.start.clicked.connect(self.start_game)

        self.reset = QPushButton("Reset Board", self)
        self.reset.setFont(QFont('Arial', 10))
        self.reset.setStyleSheet("margin: 0px; padding:5px;")
        self.reset.clicked.connect(self.reset_game)

        # black always starts
        self.player = QLabel("Player Blacks turn")
        self.player.setFont(QFont('Arial', 10))
        self.player.setStyleSheet("margin: 0px; padding:2px;")

        self.pass_turn = QPushButton("Pass Turn", self)
        self.pass_turn.setFont(QFont('Arial', 10))
        self.pass_turn.setStyleSheet("margin: 0px; padding:5px;")
        self.pass_turn.clicked.connect(self.pass_a_turn)

        self.start_speed_go = QPushButton("Start Speed Go", self)
        self.start_speed_go.setFont(QFont('Arial', 10))
        self.start_speed_go.setStyleSheet("margin: 0px; padding:5px;")
        self.start_speed_go.clicked.connect(self.start_speed_game)

        self.black_time_remaining = QLabel("")
        self.black_time_remaining.setStyleSheet("margin: 0px; padding:2px; ")
        self.black_time_remaining.setFont(QFont('Arial', 10))

        self.white_time_remaining = QLabel("")
        self.white_time_remaining.setStyleSheet("margin: 0px; padding:2px; ")
        self.white_time_remaining.setFont(QFont('Arial', 10))

        # adding to the layout
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.start, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.start_speed_go, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.reset, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.pass_turn, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.player, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.label_click_location, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.label_time_remaining, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.black_time_remaining, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addWidget(self.white_time_remaining, alignment=QtCore.Qt.AlignLeft)
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)
        self.show()

    def make_connection(self, board):
        """this handles a signal sent from the board class"""
        # when the clickLocationSignal is emitted in board the setClickLocation slot receives it
        board.clickLocationSignal.connect(self.set_click_location)
        # when the updateTimerSignal is emitted in the board the setTimeRemaining slot receives it
        board.updateTimerSignal.connect(self.set_time_remaining)

        board.player_turn_signal.connect(self.player_turn)
        board.white_timer_signal.connect(self.update_white)
        board.black_timer_signal.connect(self.update_black)

    @pyqtSlot(str)  # checks to make sure that the following slot is receiving an argument of the type 'int'
    def set_click_location(self, click_loc):
        """updates the label to show the click location"""
        self.label_click_location.setText("Click Location: " + click_loc)
        # print('slot ' + click_loc)

    @pyqtSlot(int)
    def set_time_remaining(self, time_remaining):
        """updates the time remaining label to show the time remaining"""
        update = "Time Taken: " + str(time_remaining) + " seconds"
        self.label_time_remaining.setText(update)
        # print('slot ' + update)
        # self.redraw()

    @pyqtSlot(bool)
    def player_turn(self, turn):
        current_text = "Game Over"
        if self.player.text() == current_text:
            self.player.setText("Game Over")
        else:
            if turn:
                text = "Player Blacks Turn"
                if self.white_pass == 1:
                    self.white_pass -= 1
            else:
                text = "Player Whites Turn"
                if self.black_pass == 1:
                    self.black_pass -= 1

            self.player.setText(text)

    def pass_a_turn(self):
        text = self.player.text()
        if text == "Player Whites Turn":
            self.white_pass += 1
            self.player.setText("Player Blacks Turn")
            black_turn = True
        else:
            self.black_pass += 1
            self.player.setText("Player Whites Turn")
            black_turn = False

        is_game_over = not __main__.myGo.get_board().pass_turn(black_turn)
        if is_game_over:
            self.update_black(0)
            self.reset_game()
            
        if self.white_pass >= 2 or self.black_pass >= 2:
            self.player.setText("Game Over")
            __main__.myGo.get_board().stop_timer()
            if self.speed_go:
                self.speed_go = False
                __main__.myGo.get_board().speed_game(self.speed_go)

    def start_game(self):
        __main__.myGo.get_board().start()

    def start_speed_game(self):
        self.speed_go = True
        self.black_time_remaining.setText("Player Blacks Time remaining: ")
        self.white_time_remaining.setText("Player Whites Time remaining: ")
        __main__.myGo.get_board().speed_game(self.speed_go)
        self.start_game()

    def update_black(self, time):
        if time == 0:
            self.speed_go = False
            __main__.myGo.get_board().speed_game(self.speed_go)
            self.player.setText("Game Over")
            __main__.myGo.get_board().stop_timer()
            self.reset_game()

        update = "Player Blacks Time remaining: " + str(time) + " s"
        self.black_time_remaining.setText(update)

    def update_white(self, time):
        if time == 0:
            self.speed_go = False
            __main__.myGo.get_board().speed_game(self.speed_go)
            self.player.setText("Game Over")
            __main__.myGo.get_board().stop_timer()
            self.reset_game()

        update = "Player Whites Time remaining: " + str(time) + " s"
        self.white_time_remaining.setText(update)

    def reset_game(self):

        __main__.myGo.get_board().end_game()

        __main__.myGo.get_board().reset_game()
        self.player.setText("Player Blacks Turn")
        __main__.myGo.get_board().pass_turn(True)
        self.label_time_remaining.setText("Time Taken: ")
        self.black_time_remaining.setText("")
        self.white_time_remaining.setText("")
        self.white_pass = 0
        self.black_pass = 0
