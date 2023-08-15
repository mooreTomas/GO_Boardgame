from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QMessageBox
from PyQt5.QtCore import Qt
from board import Board
from score_board import ScoreBoard


class Go(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def get_board(self):
        return self.board

    def get_score_board(self):
        return self.scoreBoard

    def initUI(self):
        '''initiates application UI'''

        # menu
        main_menu = self.menuBar()
        help_menu = main_menu.addMenu(" Help")

        # how to play
        help_action = QAction(QIcon("./icons/howTo.png"), "How To Play", self)
        help_action.setShortcut("Ctrl+H")
        help_menu.addAction(help_action)
        help_action.triggered.connect(self.help)

        # game rules
        rules_action = QAction(QIcon("./icons/rules.png"), "Game Rules", self)
        rules_action.setShortcut("Ctrl+R")
        help_menu.addAction(rules_action)
        rules_action.triggered.connect(self.rules)

        self.board = Board(self)
        self.board.setMinimumWidth(735)
        self.board.setMinimumHeight(735)
        self.setCentralWidget(self.board)
        self.scoreBoard = ScoreBoard()
        self.scoreBoard.setStyleSheet("margin: 200px")
        self.addDockWidget(Qt.RightDockWidgetArea, self.scoreBoard)
        self.scoreBoard.make_connection(self.board)

        self.resize(800, 800)
        self.center()
        self.setWindowTitle('Go')
        self.show()

    def help(self):
        QMessageBox.information(self, "How to Play",
                                "Press Start to begin a game\n"
                                "\nBlack goes first. Simply click the space you wish to place your piece on. \n"
                                "\nThe goal is to surround your opponents pieces to capture them and gain "
                                "territory.\n "
                                "\nTo end the game, pass your turn twice in a row. \n"
                                "\nPlayer with the most prisoners and territory wins.\n"
                                "\n\nFor a speedier version of this game where each player only has 2 mins to play,\n"
                                "begin game by pressing speed go\n")

    def rules(self):
        QMessageBox.information(self, "Game Rules", "Black goes first.\n"
                                                    "\nCapture opponents pieces by surrounding them. \n"
                                                    "\nSuicide Rule: You may not place your piece in a location where "
                                                    "your opponent will capture it immediately.\n"
                                                    "\nKO Rule: You may not place your piece in the same place as "
                                                    "last game state. \n "
                                                    "\nTo end game pass your turn twice in a row. \n"
                                                    "\nPlayer with most territory and prisoners wins.")

    def center(self):
        '''centers the window on the screen'''
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
