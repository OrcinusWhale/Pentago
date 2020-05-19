from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
import subprocess
import time
import copy
import numpy
import sys


# Exits the program
def quit_game(touch):
    sys.exit()


class Pointer:
    def __init__(self, value=0):
        self.value = value  # The value the "pointer" points to


class WidgetButton(ButtonBehavior, Widget):
    def __init__(self, pos, size, row, col, mark=None):
        Widget.__init__(self, size_hint=(None, None), pos=pos, size=size)
        ButtonBehavior.__init__(self)
        self.row = row  # The button's row on the board
        self.col = col  # The button's column on the board
        self.mark = mark  # The mark on the button ("red"/"blue"/"empty"/"menu"/"right"/"left"/"up"/"down"/None)


class HomeMenu(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.manager = self.parent  # The screen manager
        self.layout = BoxLayout(orientation="vertical")  # The layout
        self.add_widget(self.layout)
        b = Button(text="1 player")
        b.bind(on_press=self.play)
        self.layout.add_widget(b)
        b = Button(text="2 players")
        b.bind(on_press=self.play)
        self.layout.add_widget(b)
        b = Button(text="Rules")
        b.bind(on_press=self.rules)
        self.layout.add_widget(b)
        b = Button(text="Quit")
        b.bind(on_press=quit_game)
        self.layout.add_widget(b)

    # Switches to game screen
    def play(self, touch):
        global players
        # If 1 player button is pressed
        if touch.text == "1 player":
            players = 1
        else:
            players = 2
        self.manager.current = "Game Screen"

    # Opens the "rules.pdf" file
    def rules(self, touch):
        # If OSX
        if sys.platform == "darwin":
            subprocess.Popen("open rules.pdf", shell=True)
        # If Windows
        elif sys.platform == "win32":
            subprocess.Popen("start rules.pdf", shell=True)


class GameScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.manager = self.parent  # The screen manager
        self.layout = FloatLayout()  # The layout
        self.add_widget(self.layout)
        self.rows = 8  # The amount of rows in the board
        self.cols = 8  # The amount of columns in the board
        self.status = "Playing"  # Game status ("Playing"/"Win")
        self.win_text = Label(font_size="20sp", size_hint=(None, None))  # Label displayed at the end of the game
        self.reset = Button(text="Click to play again", width=Window.size[0]/5, size_hint=(None, None))  # Button displayed at the end of the game
        self.reset.bind(on_press=self.reset_board)
        self.menu = Button(text="Click to return to menu", width=Window.size[0]/5, size_hint=(None, None))  # Button displayed at the end of the game
        self.menu.bind(on_press=self.go_menu)
        self.quit = Button(text="Click to quit", width=Window.size[0]/5, size_hint=(None, None))  # Button displayed at the end of the game
        self.quit.bind(on_press=quit_game)
        self.depth = 2  # Minimax depth
        self.start_time = 0  # Used for measuring move calculation time
        self.offset = 0  # Used to lower minimax depth in real time
        self.tooLong = False  # If calculation time is longer than 10 seoncds
        self.rotatable = False  # If a board can rotated
        self.turn = 1  # Player turn (1/2)
        Window.bind(on_resize=self.resize)
        self.buttons = list()  # Buttons displayed on screen
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/self.rows))):
            # In case loop does one extra
            if i < self.rows:
                self.buttons.append(list())
            for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/self.cols))):
                # In case loop does one extra
                if j < self.cols:
                    # First button to be added
                    if i == 0 and j == 0:
                        self.buttons[i].append(Button(text="Menu", pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8), size_hint=(None, None)))
                        self.buttons[i][j].mark = "menu"
                        self.buttons[i][j].bind(on_press=self.go_menu)
                    else:
                        self.buttons[i].append(WidgetButton((x, y), (Window.size[0] / self.cols, Window.size[1] / self.rows), i, j))
                        # If not out of bounds
                        if 0 < i < self.rows-1 and 0 < j < self.cols - 1:
                            self.buttons[i][j].bind(on_press=self.place)
                            self.buttons[i][j].mark = "empty"
                        # Arrows positions
                        elif i in [0, self.rows-1] and j in [1, self.cols-2] or i in [1, self.rows-2] and j in [0, self.cols-1]:
                            self.buttons[i][j].bind(on_press=self.rotate)
                        self.draw(self.buttons[i][j])
                    self.layout.add_widget(self.buttons[i][j])
        self.buttons[0][1].mark = "right"
        self.draw(self.buttons[0][1])
        self.buttons[0][1].start_row = self.buttons[1][0].start_row = 1
        self.buttons[0][1].start_col = self.buttons[1][0].start_col = 1
        self.buttons[0][1].cw = True
        self.buttons[1][0].mark = "up"
        self.draw(self.buttons[1][0])
        self.buttons[1][0].cw = False
        self.buttons[self.rows-2][0].mark = "down"
        self.draw(self.buttons[self.rows-2][0])
        self.buttons[self.rows-2][0].start_row = self.buttons[self.rows-1][1].start_row = int((self.rows-2)/2)+1
        self.buttons[self.rows-2][0].start_col = self.buttons[self.rows-1][1].start_col = 1
        self.buttons[self.rows-2][0].cw = True
        self.buttons[self.rows-1][1].mark = "right"
        self.draw(self.buttons[self.rows-1][1])
        self.buttons[self.rows-1][1].cw = False
        self.buttons[self.rows-1][self.cols-2].mark = "left"
        self.draw(self.buttons[self.rows-1][self.cols-2])
        self.buttons[self.rows-1][self.cols-2].start_row = self.buttons[self.rows-2][self.cols-1].start_row = int((self.rows-2)/2)+1
        self.buttons[self.rows-1][self.cols-2].start_col = self.buttons[self.rows-2][self.cols-1].start_col = int((self.cols-2)/2)+1
        self.buttons[self.rows-1][self.cols-2].cw = True
        self.buttons[self.rows-2][self.cols-1].mark = "down"
        self.draw(self.buttons[self.rows-2][self.cols-1])
        self.buttons[self.rows-2][self.cols-1].cw = False
        self.buttons[1][self.cols-1].mark = "up"
        self.draw(self.buttons[1][self.cols-1])
        self.buttons[1][self.cols-1].start_row = self.buttons[0][self.cols-2].start_row = 1
        self.buttons[1][self.cols-1].start_col = self.buttons[0][self.cols-2].start_col = int((self.cols-2)/2)+1
        self.buttons[1][self.cols-1].cw = True
        self.buttons[0][self.cols-2].mark = "left"
        self.draw(self.buttons[0][self.cols-2])
        self.buttons[0][self.cols-2].cw = False

    # Resets board and switches to home menu screen
    def go_menu(self, touch):
        self.reset_board()
        self.manager.current = "Home Menu"

    # Resizes everything on screen to fit window size
    def resize(self, window=None, width=None, height=None):
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/8))):
            # In case loop does one extra
            if i < 8:
                for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/8))):
                    # In case loop does one extra
                    if j < 8:
                        self.buttons[i][j].pos = (x, y)
                        self.buttons[i][j].size = (Window.size[0] / 8, Window.size[1] / 8)
                        self.draw(self.buttons[i][j])
        self.win()

    # Draws on button according to properties
    def draw(self, button):
        if button.mark != "menu":
            button.canvas.clear()
            with button.canvas:
                Color(84/255, 154/255, 119/255)
                Rectangle(pos=button.pos, size=button.size)
                d = button.size[1]
                # If empty spot
                if button.mark == "empty":
                    Color(84/255, 125/255, 119/255)
                    Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
                # Spot filled with red
                elif button.mark == "red":
                    Color(1, 0, 0)
                    Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
                # Spot filled with blue
                elif button.mark == "blue":
                    Color(0, 0, 1)
                    Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
                else:
                    width = 5
                    Color(1, 1, 0)
                    # Right arrow
                    if button.mark == "right":
                        Line(points=[button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 - button.size[1]/2 + width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]*4/5, button.pos[0] + button.size[0]/2 + button.size[1]/2 - width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5], width=width)
                    # Up arrow
                    elif button.mark == "up":
                        Line(points=[button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + width, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1] - width, button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2], width=width)
                    # Down arrow
                    elif button.mark == "down":
                        Line(points=[button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1] - width, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + width, button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2], width=width)
                    # Left arrow
                    elif button.mark == "left":
                        Line(points=[button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]/2 - width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]*4/5, button.pos[0] + button.size[0]/2 - button.size[1]/2 + width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5], width=width)

    # Converts a 2d list with buttons to 2d list with numbers for simplicity purposes
    def convert_board(self, board=None):
        # No board was sent as an argument
        if board is None:
            board = self.buttons
        converted = list()
        for i in range(1, len(board)-1):
            converted.append(list())
            for j in range(1, len(board[i])-1):
                # Filled with red
                if board[i][j].mark == "red":
                    converted[i-1].append(1)
                # Filled with blue
                elif board[i][j].mark == "blue":
                    converted[i-1].append(2)
                # Not filled
                elif board[i][j].mark == "empty":
                    converted[i-1].append(0)
        return converted

    # An extension to "next_boards" to reduce code duplication
    def next_boards_help(self, next, temp, rotated, x, y):
        for a in range(int((self.rows - 1) / 2) * x, int((self.rows - 1) / 2) * (x + 1)):
            for b in range(int((self.rows - 1) / 2) * y, int((self.rows - 1) / 2) * (y + 1)):
                temp[a][b] = rotated[a - int((self.rows - 1) / 2) * x][b - int((self.rows - 1) / 2) * y]
        add = True
        # If the board hasn't been added before
        if temp not in next:
            next.append(copy.deepcopy(temp))

    # Returns all the possible following moves
    def next_boards(self, board, turn):
        next = list()
        for i in range(0, self.rows-2):
            for j in range(0, self.cols-2):
                clone = copy.deepcopy(board)
                # The spot is empty
                if clone[i][j] == 0:
                    clone[i][j] = turn
                    for x in range(2):
                        for y in range(2):
                            temp = copy.deepcopy(clone)
                            toRotate = list()
                            for a in range(int((self.rows-1)/2)*x, int((self.rows-1)/2)*(x+1)):
                                toRotate.append(list())
                                for b in range(int((self.cols-1)/2)*y, int((self.cols-1)/2)*(y+1)):
                                    toRotate[a - int((self.cols-1)/2)*x].append(temp[a][b])
                            rotated = numpy.rot90(toRotate)
                            self.next_boards_help(next, temp, rotated, x, y)
                            rotated = numpy.rot90(toRotate, 3)
                            self.next_boards_help(next, temp, rotated, x, y)
        return next

    # Calculates the value of a given slice
    def evaluate_slice(self, s):
        s = s.tolist()
        # The slice's length is 5
        if len(s) == 5:
            # Only blue on slice
            if s.count(1) > 0 and s.count(2) == 0:
                return -2 ** s.count(1)
            # Only red on slice
            elif s.count(2) > 0 and s.count(1) == 0:
                return 2 ** s.count(2)
            else:
                return 0
        else:
            # If the slice to the left is closer to completion
            if max(s[0:self.rows - 3].count(1), s[0:self.rows - 3].count(2)) > max(s[1:self.rows - 2].count(1), s[1:self.rows - 2].count(2)):
                # There are no blues on the slice
                if s[0:self.rows - 3].count(2) == 0:
                    return -2 ** s[0:self.rows - 3].count(1)
                # There are no reds on the slice
                elif s[0:self.rows - 3].count(1) == 0:
                    return 2 ** s[0:self.rows - 3].count(2)
                else:
                    return 0
            # The slice to the right is closer to completion
            elif max(s[0:self.rows - 3].count(1), s[0:self.rows - 3].count(2)) < max(s[1:self.rows - 2].count(1), s[1:self.rows - 2].count(2)):
                # There are no blues on the slice
                if s[1:self.rows - 2].count(2) == 0:
                    return -2 ** s[1:self.rows - 2].count(1)
                # There are no reds on the slice
                elif s[1:self.rows - 2].count(1) == 0:
                    return 2 ** s[1:self.rows - 2].count(2)
                else:
                    return 0
            else:
                # The middle of the slice is empty
                if s[1:self.rows - 3].count(0) == self.rows - 4:
                    # Both corners are red
                    if s[0] == s[self.rows - 3] == 1:
                        return -4
                    # Both corners are blue
                    elif s[0] == s[self.rows - 3] == 2:
                        return 4
                    else:
                        return 0
                # Only red in the middle and empty corners
                elif s[1:self.rows - 3].count(1) > 0 and s[1:self.rows - 3].count(2) == 0:
                    return -2 ** s[1:self.rows - 3].count(1)
                # Only blue in the middle and empty corners
                elif s[1:self.rows - 3].count(2) > 0 and s[1:self.rows - 3].count(1) == 0:
                    return 2 ** s[1:self.rows - 3].count(2)
        return 0

    # Returns a value to a given board
    def evaluate_board(self, board):
        winner = self.check_win(board)
        board = numpy.array(board)
        value = 0
        # Red won
        if winner == "Red wins!":
            return float('-inf')
        # Blue won
        elif winner == "Blue wins!":
            return float('inf')
        # Tie
        elif winner == "Tie!":
            return 0
        value += self.evaluate_slice(numpy.diag(board))
        value += self.evaluate_slice(numpy.diag(board, 1))
        value += self.evaluate_slice(numpy.diag(board, -1))
        value += self.evaluate_slice(numpy.diag(numpy.fliplr(board)))
        value += self.evaluate_slice(numpy.diag(numpy.fliplr(board), 1))
        value += self.evaluate_slice(numpy.diag(numpy.fliplr(board), -1))
        for i in range(self.rows - 2):
            value += self.evaluate_slice(board[i])
            value += self.evaluate_slice(board[0:self.rows - 2, i:i+1])
        return value

    # Minimax function, returns a move
    def minimax(self, board, depth):
        alpha = float('-inf')
        beta = float('inf')
        moves = self.next_boards(board, 2)
        best_move = moves[0]
        best_score = float('-inf')
        for move in moves:
            clone = copy.deepcopy(move)
            score = self.min_play(clone, depth - 1, alpha, beta)
            if score > best_score:
                best_move = move
                best_score = score
            if alpha < best_score:
                alpha = best_score
            if beta <= alpha:
                break
        return best_move

    # Minimax, min player
    def min_play(self, board, depth, alpha, beta):
        # If 10 seconds have passed since calculation started and the depth is higher than 2
        if time.time() - self.start_time > 10 and self.depth > 2:
            self.tooLong = True
            self.depth -= 1
            self.offset += 1
            self.start_time = time.time()
        # Reached bottom depth or win
        if depth - self.offset == 0 or self.check_win(board) is not None:
            return self.evaluate_board(board)
        moves = self.next_boards(board, 1)
        best_score = float('inf')
        for move in moves:
            clone = copy.deepcopy(move)
            score = self.max_play(clone, depth - 1, alpha, beta)
            if score < best_score:
                best_move = move
                best_score = score
            if beta > best_score:
                beta = best_score
            if beta <= alpha:
                break
        return best_score

    # Minimax, max player
    def max_play(self, board, depth, alpha, beta):
        # If 10 seconds have passed since calculation started and the depth is higher than 2
        if time.time() - self.start_time > 10 and self.depth > 2:
            self.tooLong = True
            self.depth -= 1
            self.offset += 1
            self.start_time = time.time()
        # Reached bottom depth or win
        if depth - self.offset == 0 or self.check_win(board) is not None:
            return self.evaluate_board(board)
        moves = self.next_boards(board, 2)
        best_score = float('-inf')
        for move in moves:
            clone = copy.deepcopy(move)
            score = self.min_play(clone, depth - 1, alpha, beta)
            if score > best_score:
                best_move = move
                best_score = score
            if alpha < best_score:
                alpha = best_score
            if beta <= alpha:
                break
        return best_score

    # Resets the board
    def reset_board(self, touch=None):
        self.status = "Playing"
        self.layout.clear_widgets()
        self.rotatable = False
        self.turn = 1
        self.depth = 2
        for i in self.buttons:
            for j in i:
                j.disabled = False
                # Filled with blue or red
                if j.mark == "blue" or j.mark == "red":
                    j.mark = "empty"
                    self.draw(j)
                self.layout.add_widget(j)

    # An extension of "check_win" to reduce code duplication
    def check_win_help(self, board, i, j, count1, count2, filled=None):
        # Filled with red
        if board[i][j] == 1:
            if filled is not None:
                filled.value += 1
            count1.value += 1
            count2.value = 0
        # Filled with red
        elif board[i][j] == 2:
            if filled is not None:
                filled.value += 1
            count2.value += 1
            count1.value = 0
        else:
            count1.value = 0
            count2.value = 0

    # Checks whether there is a win in a given board
    def check_win(self, board=None):
        # No board given
        if board is None:
            board = self.convert_board(self.buttons)
        filled = Pointer()
        found1 = False
        found2 = False
        for i in range(0, self.rows-2):
            count1row = Pointer()
            count2row = Pointer()
            count1col = Pointer()
            count2col = Pointer()
            count1diag11 = Pointer()
            count2diag11 = Pointer()
            count1diag12 = Pointer()
            count2diag12 = Pointer()
            count1diag21 = Pointer()
            count2diag21 = Pointer()
            count1diag22 = Pointer()
            count2diag22 = Pointer()
            for j in range(0, self.cols-2):
                self.check_win_help(board, i, j, count1row, count2row, filled)
                self.check_win_help(board, j, i, count1col, count2col)
                # For diagonals
                if i < 2 and j < 5:
                    self.check_win_help(board, i+j, j, count1diag11, count2diag11)
                    self.check_win_help(board, j, i+j, count1diag12, count2diag12)
                    self.check_win_help(board, i+j, self.cols-3-j, count1diag21, count2diag21)
                    self.check_win_help(board, j, self.cols-3-i-j, count1diag22, count2diag22)
                if count1row.value == self.cols-3 or count1col.value == self.rows-3 or count1diag11.value == self.rows-3 or count1diag12.value == self.rows-3 or count1diag21.value == self.rows-3 or count1diag22.value == self.rows-3:
                    found1 = True
                elif count2row.value == self.cols-3 or count2col.value == self.rows-3 or count2diag11.value == self.rows-3 or count2diag12.value == self.rows-3 or count2diag21.value == self.rows-3 or count2diag22.value == self.rows-3:
                    found2 = True
                if found1 and found2:
                    break
            if found1 and found2:
                break
        if found1 and found2 or filled.value == (self.rows-2) * (self.cols-2):
            return "Tie!"
        elif found1:
            return "Red wins!"
        elif found2:
            return "Blue wins!"

    # If "check_win" doesn't return None, displays win screen.
    def win(self):
        win = self.check_win()
        if win is not None:
            self.win_text.text = win
            self.win_text.pos = (Window.size[0] / 2 - self.win_text.size[0] / 2, Window.size[1] * 2 / 3 - self.win_text.size[1] / 2)
            self.reset.pos = (Window.size[0]/2 - self.reset.size[0]/2, Window.size[1]*1/3 + self.menu.size[1]/2)
            self.menu.pos = (Window.size[0]/2 - self.menu.size[0]/2, Window.size[1]*1/3 - self.menu.size[1]/2)
            self.quit.pos = (Window.size[0]/2 - self.quit.size[0]/2, Window.size[1]*1/3 - self.menu.size[1]/2 - self.quit.size[1])
            if self.status == "Playing":
                self.status = "Win"
                for i in self.buttons:
                    for j in i:
                        j.disabled = True
                self.layout.add_widget(self.win_text)
                self.layout.add_widget(self.reset)
                self.layout.add_widget(self.menu)
                self.layout.add_widget(self.quit)
            return True
        return False

    # Rotates one of the boards based on the pressed button
    def rotate(self, touch):
        # If rotation is allowed
        if self.rotatable:
            for i in range(int((self.rows-2)/4)):
                for j in range(i, int((self.cols-2)/2)-1-i):
                    temp_s = self.buttons[touch.start_row+i][touch.start_col+i+j].mark
                    temp_d = self.buttons[touch.start_row+i][touch.start_col+i+j].disabled
                    # Clockwise
                    if touch.cw:
                        self.buttons[touch.start_row+i][touch.start_col+i+j].mark = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].mark
                        self.draw(self.buttons[touch.start_row+i][touch.start_col+i+j])
                        self.buttons[touch.start_row+i][touch.start_col+i+j].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].mark = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].mark
                        self.draw(self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i])
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].mark = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].mark
                        self.draw(self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j])
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].mark = temp_s
                        self.draw(self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i])
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled = temp_d
                    else:
                        self.buttons[touch.start_row+i][touch.start_col+i+j].mark = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].mark
                        self.draw(self.buttons[touch.start_row+i][touch.start_col+i+j])
                        self.buttons[touch.start_row+i][touch.start_col+i+j].disabled = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].mark = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].mark
                        self.draw(self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i])
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].mark = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].mark
                        self.draw(self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j])
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].mark = temp_s
                        self.draw(self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i])
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled = temp_d
            self.rotatable = False
            # One player mode and not win
            if players == 1 and not self.win():
                self.respond()

    # Fills a chosen space
    def place(self, touch):
        # Empty and allowed
        if not touch.disabled and not self.rotatable:
            # Red's turn
            if self.turn == 1:
                touch.mark = "red"
                # If there are two players
                if players == 2:
                    self.turn = 2
            else:
                touch.mark = "blue"
                self.turn = 1
            touch.disabled = True
            self.rotatable = True
            self.draw(touch)
        self.win()

    # Makes a response if in 1 player mode
    def respond(self):
        self.start_time = time.time()
        move = self.minimax(self.convert_board(self.buttons), self.depth)
        # If took less than 6 seconds to calculate move
        if time.time() - self.start_time < 6 and not self.tooLong:
            self.depth += 1
        self.tooLong = False
        self.offset = 0
        for i in range(1, len(self.buttons)-1):
            for j in range(1, len(self.buttons[i])-1):
                # If empty
                if move[i-1][j-1] == 0:
                    self.buttons[i][j].mark = "empty"
                    self.buttons[i][j].disabled = False
                # If red
                elif move[i-1][j-1] == 1:
                    self.buttons[i][j].mark = "red"
                    self.buttons[i][j].disabled = True
                # If blue
                elif move[i-1][j-1] == 2:
                    self.buttons[i][j].mark = "blue"
                    self.buttons[i][j].disabled = True
                self.draw(self.buttons[i][j])
        self.win()
        

class Game(App):
    def build(self):
        self.title = "Pentago"
        root = ScreenManager(transition=NoTransition())
        root.add_widget(HomeMenu(name="Home Menu"))
        root.add_widget(GameScreen(name="Game Screen"))
        return root


players = 0  # Number of players
Game().run()
