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


def quit_game(touch):
    sys.exit()


class Pointer:
    def __init__(self, value=0):
        self.value = value


class WidgetButton(ButtonBehavior, Widget):
    def __init__(self, pos, size, row, col, mark=None):
        Widget.__init__(self, size_hint=(None, None), pos=pos, size=size)
        ButtonBehavior.__init__(self)
        self.row = row
        self.col = col
        self.mark = mark


class HomeMenu(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.manager = self.parent
        self.layout = BoxLayout(orientation="vertical")
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

    def play(self, touch):
        global players
        if touch.text == "1 player":
            players = 1
        else:
            players = 2
        self.manager.current = "Game Screen"

    def rules(self, touch):
        if sys.platform == "darwin":
            subprocess.Popen("open rules.pdf", shell=True)
        elif sys.platform == "win32":
            subprocess.Popen("start rules.pdf", shell=True)


class GameScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.manager = self.parent
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.rows = 8
        self.cols = 8
        self.status = "Playing"
        self.win_text = Label(font_size="20sp", size_hint=(None, None))
        self.reset = Button(text="Click to play again", width=Window.size[0]/5, size_hint=(None, None))
        self.reset.bind(on_press=self.reset_board)
        self.menu = Button(text="Click to return to menu", width=Window.size[0]/5, size_hint=(None, None))
        self.menu.bind(on_press=self.go_menu)
        self.quit = Button(text="Click to quit", width=Window.size[0]/5, size_hint=(None, None))
        self.quit.bind(on_press=quit_game)
        self.depth = 2
        self.offset = 0
        self.tooLong = False
        self.rotatable = False
        self.players = 0
        self.turn = 1
        Window.bind(on_resize=self.resize)
        self.buttons = list()
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/8))):
            if i < 8:
                self.buttons.append(list())
            for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/8))):
                if j < 8:
                    if i == 0 and j == 0:
                        self.buttons[i].append(Button(text="Menu", pos=(x, y), size=(Window.size[0] / 8, Window.size[1] / 8), size_hint=(None, None)))
                        self.buttons[i][j].mark = "menu"
                        self.buttons[i][j].bind(on_press=self.go_menu)
                    else:
                        self.buttons[i].append(WidgetButton((x, y), (Window.size[0] / 8, Window.size[1] / 8), i, j))
                        if 0 < i < self.rows-1 and 0 < j < self.cols - 1:
                            self.buttons[i][j].bind(on_press=self.place)
                            self.buttons[i][j].mark = "empty"
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

    def go_menu(self, touch):
        self.reset_board()
        self.manager.current = "Home Menu"

    def resize(self, window=None, width=None, height=None):
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/8))):
            if i < 8:
                for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/8))):
                    if j < 8:
                        self.buttons[i][j].pos = (x, y)
                        self.buttons[i][j].size = (Window.size[0] / 8, Window.size[1] / 8)
                        self.draw(self.buttons[i][j])
        self.win()

    def draw(self, button):
        button.canvas.clear()
        with button.canvas:
            Color(84/255, 154/255, 119/255)
            Rectangle(pos=button.pos, size=button.size)
            d = button.size[1]
            if button.mark == "empty":
                Color(84/255, 125/255, 119/255)
                Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
            elif button.mark == "red":
                Color(1, 0, 0)
                Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
            elif button.mark == "blue":
                Color(0, 0, 1)
                Ellipse(pos=(button.pos[0] + button.size[0] / 2 - d / 2, button.pos[1]), size=(d, d))
            else:
                width = 5
                Color(1, 1, 0)
                if button.mark == "right":
                    Line(points=[button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 - button.size[1]/2 + width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]*4/5, button.pos[0] + button.size[0]/2 + button.size[1]/2 - width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5], width=width)
                elif button.mark == "up":
                    Line(points=[button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + width, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1] - width, button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2], width=width)
                elif button.mark == "down":
                    Line(points=[button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1] - width, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + width, button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2], width=width)
                elif button.mark == "left":
                    Line(points=[button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]/2 - width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]*4/5, button.pos[0] + button.size[0]/2 - button.size[1]/2 + width, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5], width=width)

    def convert_board(self, board=None):
        if board is None:
            board = self.buttons
        converted = list()
        for i in range(1, len(board)-1):
            converted.append(list())
            for j in range(1, len(board[i])-1):
                if board[i][j].mark == "red":
                    converted[i-1].append(1)
                elif board[i][j].mark == "blue":
                    converted[i-1].append(2)
                elif board[i][j].mark == "empty":
                    converted[i-1].append(0)
        return converted

    def next_boards_help(self, next, temp, rotated, x, y):
        for a in range(int((self.rows - 1) / 2) * x, int((self.rows - 1) / 2) * (x + 1)):
            for b in range(int((self.rows - 1) / 2) * y, int((self.rows - 1) / 2) * (y + 1)):
                temp[a][b] = rotated[a - int((self.rows - 1) / 2) * x][b - int((self.rows - 1) / 2) * y]
        add = True
        if temp not in next:
            next.append(copy.deepcopy(temp))

    def next_boards(self, board, turn):
        next = list()
        for i in range(0, self.rows-2):
            for j in range(0, self.cols-2):
                clone = copy.deepcopy(board)
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

    def evaluate_slice(self, s):
        s = s.tolist()
        if len(s) == 5:
            if s.count(1) > 0 and s.count(2) == 0:
                return -2 ** s.count(1)
            elif s.count(2) > 0 and s.count(1) == 0:
                return 2 ** s.count(2)
            else:
                return 0
        else:
            if max(s[0:self.rows - 3].count(1), s[0:self.rows - 3].count(2)) > max(s[1:self.rows - 2].count(1), s[1:self.rows - 2].count(2)):
                if s[0:self.rows - 3].count(2) == 0:
                    return -2 ** s[0:self.rows - 3].count(1)
                elif s[0:self.rows - 3].count(1) == 0:
                    return 2 ** s[0:self.rows - 3].count(2)
                else:
                    return 0
            elif max(s[0:self.rows - 3].count(1), s[0:self.rows - 3].count(2)) < max(s[1:self.rows - 2].count(1), s[1:self.rows - 2].count(2)):
                if s[1:self.rows - 2].count(2) == 0:
                    return -2 ** s[1:self.rows - 2].count(1)
                elif s[1:self.rows - 2].count(1) == 0:
                    return 2 ** s[1:self.rows - 2].count(2)
                else:
                    return 0
            else:
                if s[1:self.rows - 3].count(0) == self.rows - 2:
                    if s[0] == s[self.rows - 2] == 1:
                        return -2
                    elif s[0] == s[self.rows - 2] == 2:
                        return 2
                    else:
                        return 0
        return 0

    def evaluate_board(self, board):
        winner = self.check_win(board)
        board = numpy.array(board)
        value = 0
        if winner == "Red wins!":
            return float('-inf')
        elif winner == "Blue wins!":
            return float('inf')
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

    def min_play(self, board, depth, alpha, beta):
        if time.time() - self.start_time > 10 and self.depth > 2:
            self.tooLong = True
            self.offset += 1
            self.depth -= 1
            self.start_time = time.time()
        if depth - self.offset < 1 or self.check_win(board) is not None:
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

    def max_play(self, board, depth, alpha, beta):
        if time.time() - self.start_time > 10 and self.depth > 2:
            self.tooLong = True
            self.offset += 1
            self.depth -= 1
            self.start_time = time.time()
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

    def reset_board(self, touch=None):
        self.status = "Playing"
        self.layout.clear_widgets()
        self.rotatable = False
        self.turn = 1
        for i in self.buttons:
            for j in i:
                j.disabled = False
                if j.mark == "blue" or j.mark == "red":
                    j.mark = "empty"
                    self.draw(j)
                self.layout.add_widget(j)

    def check_win_help(self, board, i, j, count1, count2, filled=None):
        if board[i][j] == 1:
            if filled is not None:
                filled.value += 1
            count1.value += 1
            count2.value = 0
        elif board[i][j] == 2:
            if filled is not None:
                filled.value += 1
            count2.value += 1
            count1.value = 0
        else:
            count1.value = 0
            count2.value = 0

    def check_win(self, board=None):
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

    def rotate(self, touch):
        if self.rotatable:
            for i in range(int((self.rows-2)/4)):
                for j in range(i, int((self.cols-2)/2)-1-i):
                    temp_s = self.buttons[touch.start_row+i][touch.start_col+i+j].mark
                    temp_d = self.buttons[touch.start_row+i][touch.start_col+i+j].disabled
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
            if players == 1 and not self.win():
                self.respond()

    def place(self, touch):
        if not touch.disabled and not self.rotatable:
            if self.turn == 1:
                touch.mark = "red"
                if players == 2:
                    self.turn = 2
            else:
                touch.mark = "blue"
                self.turn = 1
            touch.disabled = True
            self.rotatable = True
            self.draw(touch)
        self.win()

    def respond(self):
        self.start_time = time.time()
        move = self.minimax(self.convert_board(self.buttons), self.depth)
        if time.time() - self.start_time < 6 and not self.tooLong:
            self.depth += 1
        self.offset = 0
        self.tooLong = False
        for i in range(1, len(self.buttons)-1):
            for j in range(1, len(self.buttons[i])-1):
                if move[i-1][j-1] == 0:
                    self.buttons[i][j].mark = "empty"
                    self.buttons[i][j].disabled = False
                elif move[i-1][j-1] == 1:
                    self.buttons[i][j].mark = "red"
                    self.buttons[i][j].disabled = True
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


players = 0
Game().run()
