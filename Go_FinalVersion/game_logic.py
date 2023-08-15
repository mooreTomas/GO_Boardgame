from PyQt5.QtCore import QObject, pyqtSignal
from itertools import chain



class Group(object):
    """Represents a group of connected stones on the board.
    Attributes:
        stones (set): list of all coordinates where the group has a stone
        border (set): list of all fields that are adjacent to the group
                      For a new group empty fields must be added manually
                      since the group does not know about the field size
        color (bool): color of the group
    Property:
        size (int): equal to len(self.stones), the number of stones in
                    the group.
    """

    def __init__(self, stones=None, color=None):
        """
        Initialise group
        """
        if stones is not None:
            self.stones = set(stones)
        else:
            self.stones = set()

        self.border = set()
        self.color = color

    def __add__(self, other):
        """To add two groups of the same color
        The new group contains all the stones of the previous groups and
        the border will be updated correctly.
        Raises:
            TypeError: The colours of the groups do not match
        """
        if self.color != other.color:
            raise ValueError('Only groups of same colour can be added!')
        grp = Group(stones=self.stones.union(other.stones))
        grp.color = self.color
        grp.border = self.border.union(other.border).difference(grp.stones)
        return grp

    @property
    def size(self):
        return len(self.stones)

# constants
BLACK = True
WHITE = False
NOPIECE = None

class GameLogic(QObject):
    """ This class takes care of all the calculations and the game logic"""
    def __init__(self, n=8):
        super().__init__(parent=None)
        """This function initializes a new """
        # gameplay attributes
        self.size = n
        self.turn = BLACK

        # used for ko-rule
        self.blocked_field = None

        # used to detect if bother players pass
        self.has_passed = False

        # game over flag
        self.game_over = False

        # the board is represented by a size x size - matrix. 
        self.board = [[None for i in range(self.size)] for j in range(self.size)]   
        self.territory = [[None for i in range(self.size)] for j in range(self.size)]
        self.neighbors = []
        self.initializeNeighbors()
        # score from empty fields at the end of the game.
        self.score = [0, 0]

        # stones killed during the game
        self.captured = [0, 0] 

    def passing(self):
        """Action when a player passes his turn.

        Variables changed by this function:
            self.game_over
            self.turn
            self.has_passed
            self.blocked_field
        """

        # do nothing if game is over
        if self.game_over:
            return False
        
        # both players pass => game over
        if self.has_passed:
            self.game_over = True
            return True
        
        # invert the turn & set passed to true
        self.turn = WHITE if (self.turn == BLACK) else BLACK     
        self.has_passed = True
        self.blocked_field = None

        return True

    def _stones(self):
        """Returns a nested list (same shape as board) containing the colors of each stone.

        Returns:
            list (boolean) : multidimensional list containing the colors of the stones on the board.
        """
        # initialize a new empty list with the size of the playing board
        colors = [[None for i in range(self.size)] for j in range(self.size)]

        for j in range(0, self.size):
            for i in range(0, self.size):
                if self.board[j][i] is None:
                    colors[j][i] = None
                else:
                    colors[j][i] = self.board[j][i].color
                            
        return colors

    def _add(self, grp):
        """Adds a group of stones to the game

        Arguments:
            grp (Group): The group that shall be added
        
        Attributes updated by this function:
            self.board
        """
        for (x, y) in grp.stones:
            self.board[y][x] = grp
    
    def _remove(self, grp):
        """Removes a group of stones from the game

        Arguments:
            grp (Group): The group that shall be removed
        
        Attributes updated by this function:
            self.board
        """
        for (x, y) in grp.stones:
            self.board[y][x] = None

    def _kill(self, grp):
        """Removes a group of stones from the game and increases the
        counter of captured stones.

        Arguments:
            grp (Group): The group that has been killed/captured - needs to be removed

        Attributes updated by this function:
            self.board
            self.captured
            self.group
        """
        # increase the caputured counter of the opposite color by the nr. of stones in the grp 
        self.captured[not grp.color] += grp.size

        # remove the group
        self._remove(grp)

    def _liberties(self, grp):
        """Counts the number of empty fields adjacent to the group.

        Arguments:
            grp (Group): a group of stones.

        Returns:
            (int): nr. of liberties of that group
        """
        return sum([1 for u, v in grp.border if self.board[v][u] is None])     

    def get_data(self):
        """Returns the data object containing all relevant information"""
        data = {
            'size'      : self.size,
            'stones'    : self._stones(),
            'game_over' : self.game_over,
            'color'     : self.turn
        }

        return data

    def place_stone(self, x, y):
        """Attempts to place a new stone"""
        # check if the game is finished
        if self.game_over:
            return False
        
        # check if the position is free
        if self.board[y][x] is not None:
            return False

        # check if the field is already blocked
        if self.blocked_field == (x, y):
            return False

        # create new group with the given coordinates
        new_group = Group(stones=[(x, y)], color=self.turn)

        # create two lists to remember the groups to remove / kill
        groups_to_remove = []
        groups_to_kill = []

        # Move Validation
        # set the move validity initially to False
        is_valid = False

        # All direct neighbors of (x, y)
        for (u, v) in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:

            # Check if the neighbor is on the board
            if u < 0 or v < 0 or u >= self.size or v >= self.size:
                continue
            
            # Add the neighbor to the border of the new group
            new_group.border.add((u, v))

            other_group = self.board[v][u]
            
            # check if neighbor is None
            if other_group is None:
                is_valid = True
                continue

            # same color
            if new_group.color == other_group.color:
                # merge the two groups
                new_group = new_group + other_group

                # remember to delte the old grp (other_group)
                groups_to_remove.append(other_group)

            # groups have different colors
            # check that there is only one free adjacent field to other_group
            elif self._liberties(other_group) == 1:
                is_valid = True
                
                # remember to kill the other_group
                if other_group not in groups_to_kill: 
                    groups_to_kill.append(other_group)

        # new_group must have at least one free adjacent field
        if self._liberties(new_group) >= 1:
            is_valid = True

        # Move  (only if valid)

        # the move is valid
        if is_valid:
            # remove groups
            for grp in groups_to_remove:
                self._remove(grp)

            # kill groups
            for grp in groups_to_kill:
                self._kill(grp)

            # add the new group
            self._add(new_group)
        
        # the move is invalid
        else:
            return False

        # ko-rule: block the field where the stone has just been placed
        # conditions
        # 1. the new group has only one stone
        # 2. only one group has been killed
        # 3. the killed group has only had one stone
        if new_group.size == 1 and len(groups_to_kill) == 1 and groups_to_kill[0].size == 1:
            for (x, y) in groups_to_kill[0].stones:
                self.blocked_field = (x, y)
        else:
            self.blocked_field = None
        
        # switch the color (turn)
        self.turn = WHITE if (self.turn == BLACK) else BLACK
        self.has_passed = False

        return True

    def initializeNeighbors(self):
        """Caching the neighbors to quickly get them when necessary"""
        for point in range(self.size * self.size):
            row, col = point // self.size, point % self.size
            neighbors = [(row - 1, col), (row + 1, col),
                        (row, col - 1), (row, col + 1)]
            neighbors = [n for n in neighbors if n[0] >= 0 and n[0] < self.size
                                            and n[1] >= 0 and n[1] < self.size]
            self.neighbors.append([n[0] * self.size + n[1] for n in neighbors])

    def reachesColor(self, position, point):
        """Checking if the flood of empty space from a point reaches a color or not"""
        stack = [point]
        pointSet = set([point])
        reachesBlack, reachesWhite = False, False
        
        while len(stack) > 0:
            currentPoint = stack.pop()
            for n in self.neighbors[currentPoint]:
                if position[n] == BLACK:
                    reachesBlack = True

                if position[n] == WHITE:
                    reachesWhite = True
                    
                if position[n] == NOPIECE and n not in pointSet:
                    stack.append(n)
                    pointSet.add(n)
            
        return (reachesBlack, reachesWhite, pointSet)

    def score_game(self):
        """Calculating the score by considering territories of certain color as actual pieces of it, then
        get the difference
        """
        board = self._stones()[:] 
        positionScored = list(chain.from_iterable(board))
        position = positionScored[:]

        for i in range(self.size * self.size):
            if positionScored[i] != NOPIECE:
                continue

            reachesBlack, reachesWhite, points = self.reachesColor(position, i)
            if reachesBlack and not reachesWhite:
              color = BLACK
            elif reachesWhite and not reachesBlack:
                color = WHITE
            else:
                color = NOPIECE

            for p in points:
                positionScored[p] = color
        
        score = 0
        for i in range(self.size * self.size):
            if positionScored[i] == BLACK:
                score +=1
            elif positionScored[i] == WHITE:
                score -=1
            # else:
            #     positionScored[i] = NOPIECE
        return score, positionScored
