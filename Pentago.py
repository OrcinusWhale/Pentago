from kivy.uix.layout import Layout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.app import App
from kivy.core.window import Window
import copy
import numpy
import sys


class Minimax:
    def __init__(self, board, next=None):
        self.board = board
        self.value = 0
        self.next = next


class IntPointer:
    def __init__(self, num=0):
        self.num = num


class WidgetButton(ButtonBehavior, Widget):
    def __init__(self, pos, size, row, col, mark=None):
        Widget.__init__(self)
        ButtonBehavior.__init__(self)
        self.pos = pos
        self.size = size
        self.row = row
        self.col = col
        self.mark = mark


class Board(Layout):
    def __init__(self):
        Layout.__init__(self)
        self.rows = 8
        self.cols = 8
        self.tree = None
        self.status = "Menu"
        self.reset = Button(text="Click to play again")
        self.reset.bind(on_press=self.reset_board)
        self.menu = Button(text="Click to return to menu")
        self.menu.bind(on_press=self.go_menu)
        self.quit = Button(text="Click to quit")
        self.quit.bind(on_press=self.quit_game)
        self.rotatable = False
        self.players = 0
        self.turn = 1
        Window.bind(on_resize=self.resize)
        self.buttons = list()
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/8))):
            self.buttons.append(list())
            for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/8))):
                self.buttons[i].append(WidgetButton((x, y), (Window.size[0] / 8, Window.size[1] / 8), i, j))
                if 0 < i < self.rows-1 and 0 < j < self.cols - 1:
                    self.buttons[i][j].bind(on_press=self.place)
                    self.buttons[i][j].mark = "empty"
                elif i in [0, self.rows-1] and j in [1, self.cols-2] or i in [1, self.rows-2] and j in [0, self.cols-1]:
                    self.buttons[i][j].bind(on_press=self.rotate)
                self.draw(self.buttons[i][j])
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
        self.go_menu()

    def resize(self, window=None, width=None, height=None):
        if self.status == "Menu":
            self.go_menu()
        for i, y in enumerate(range(0, Window.size[1], int(Window.size[1]/8))):
            self.buttons.append(list())
            for j, x in enumerate(range(0, Window.size[0], int(Window.size[0]/8))):
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
                Color(1, 1, 0)
                if button.mark == "right":
                    Line(points=[button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 - button.size[1]/2 + 10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]*4/5, button.pos[0] + button.size[0]/2 + button.size[1]/2 - 10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/5], width=10)
                if button.mark == "up":
                    Line(points=[button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + 10, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2 + button.size[1]*3/10, button.pos[1] + button.size[1]/2, button.pos[0] + button.size[0]/2, button.pos[1] + button.size[1] - 10, button.pos[0] + button.size[0]/2 - button.size[1]*3/10, button.pos[1] + button.size[1]/2], width=10)

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

    def next_boards_help(self, next, temp, toRotate, x, y):
        for a in range(int((self.rows - 1) / 2) * x, int((self.rows - 1) / 2) * (x + 1)):
            for b in range(int((self.rows - 1) / 2) * y, int((self.rows - 1) / 2) * (y + 1)):
                temp[a][b] = toRotate[a - int((self.rows - 1) / 2) * x][b - int((self.rows - 1) / 2) * y]
        add = True
        for c in next:
            if c.board == temp:
                add = False
                break
        if add:
            next.append(Minimax(temp))

    def next_boards(self, m, turn):
        next = list()
        for i in range(0, self.rows-2):
            for j in range(0, self.cols-2):
                board = copy.deepcopy(m.board)
                if board[i][j] == 0:
                    board[i][j] = turn
                    for x in range(2):
                        for y in range(2):
                            temp = copy.deepcopy(board)
                            toRotate = list()
                            for a in range(int((self.rows-1)/2)*x, int((self.rows-1)/2)*(x+1)):
                                toRotate.append(list())
                                for b in range(int((self.cols-1)/2)*y, int((self.cols-1)/2)*(y+1)):
                                    toRotate[a - int((self.cols-1)/2)*x].append(temp[a][b])
                            numpy.rot90(toRotate)
                            self.next_boards_help(next, temp, toRotate, x, y)
                            numpy.rot90(toRotate, 2)
                            self.next_boards_help(next, temp, toRotate, x, y)
        return next

    def quit_game(self, touch):
        sys.exit()

    def go_menu(self, touch=None):
        self.clear_widgets()
        self.status = "Menu"
        label = Label(text="How many players?", font_size="50sp")
        label.pos = (Window.size[0]*1/2 - label.size[0]/2, Window.size[1]*2/3 - label.size[1]/2)
        self.add_widget(label)
        for i in range(1, 3):
            button = Button(text=str(i))
            button.pos = (Window.size[0]*i/3 - button.size[0]/2, Window.size[1]*1/3 - button.size[1]/2)
            button.bind(on_press=self.reset_board)
            self.add_widget(button)

    def evaluate_board_help(self, board, i, j, count, value, prev_i, prev_j):
        if board[i][j] == board[prev_i][prev_j] != 0 or board[i][j] != 0 and count.num == 0:
            count.num += 1
        else:
            if board[prev_i][prev_j] == 1:
                value.num += 2 ** count.num
            elif board[prev_i][prev_j] == 2:
                value.num -= 2 ** count.num
            count.num = 0

    def evaluate_board(self, board):
        value = IntPointer()
        sequence_count_r = IntPointer()
        sequence_count_c = IntPointer()
        sequence_count_d11 = IntPointer()
        sequence_count_d12 = IntPointer()
        sequence_count_d21 = IntPointer()
        sequence_count_d22 = IntPointer()
        for i in range(len(board)):
            for j in range(len(board[i])):
                if j != 0:
                    self.evaluate_board_help(board, i, j, sequence_count_r, value, i, j-1)
                    self.evaluate_board_help(board, j, i, sequence_count_c, value, j-1, i)
                    if i < 2 and j < 5:
                        self.evaluate_board_help(board, i+j, j, sequence_count_d11, value, i+j-1, j-1)
                        self.evaluate_board_help(board, i+j, self.cols-3-j, sequence_count_d21, value, i+j-1, self.cols-3-j-1)
                        if i != 0:
                            self.evaluate_board_help(board, j, i + j, sequence_count_d12, value, j - 1, i + j - 1)
                            self.evaluate_board_help(board, j, self.cols-3-i-j, sequence_count_d22, value, j-1, self.cols-3-i-j-1)
                else:
                    if board[i][j] != 0:
                        sequence_count_r.num = 1
                        sequence_count_c.num = 1
                    if board[i+j][j] != 0:
                        sequence_count_d11.num = 1
                    if board[j][i+j] != 0:
                        sequence_count_d12.num = 1
                    if board[i+j][self.cols-3-j] != 0:
                        sequence_count_d21.num = 1
                    if board[j][self.cols-3-i-j] != 0:
                        sequence_count_d22.num = 1
        return value.num

    def create_tree(self, turn, current, depth, alpha=float("-inf"), beta=float("inf")):
        winner = self.check_win(current.board)
        if winner == "Tie!":
            current.value = 0
        elif winner == "Player 1 wins!":
            current.value = float("inf")
        elif winner == "Player 2 wins!":
            current.value = float("-inf")
        elif depth == 0:
            current.value = self.evaluate_board(current.board)
        else:
            if turn == 1:
                current.value = float("inf")
                current.next = self.next_boards(current, 2)
            elif turn == 2:
                current.value = float("-inf")
                current.next = self.next_boards(current, 1)
            for i in current.next:
                if turn == 1:
                    self.create_tree(2, i, depth - 1, alpha, beta)
                    if current.value > i.value:
                        current.value = i.value
                    if beta > current.value:
                        beta = current.value
                    if beta <= alpha:
                        break
                else:
                    self.create_tree(1, i, depth - 1, alpha, beta)
                    if current.value < i.value:
                        current.value = i.value
                    if alpha < current.value:
                        alpha = current.value
                    if beta <= alpha:
                        break

    def reset_board(self, touch):
        if touch.text == "1":
            self.players = 1
        elif touch.text == "2":
            self.players = 2
        self.status = "Playing"
        self.clear_widgets()
        self.rotatable = False
        self.turn = 1
        for i in self.buttons:
            for j in i:
                self.disabled = False
                if j.mark == "blue" or j.mark == "red":
                    j.mark = "empty"
                    self.draw(j)
                self.add_widget(j)

    def check_win_help(self, board, i, j, count1, count2, filled=None):
        if board[i][j] == 1:
            if filled is not None:
                filled.num += 1
            count1.num += 1
            count2.num = 0
        elif board[i][j] == 2:
            if filled is not None:
                filled.num += 1
            count2.num += 1
            count1.num = 0
        else:
            count1.num = 0
            count2.num = 0

    def check_win(self, board=None):
        if board is None:
            board = self.convert_board(self.buttons)
        filled = IntPointer()
        found1 = False
        found2 = False
        for i in range(0, self.rows-2):
            count1row = IntPointer()
            count2row = IntPointer()
            count1col = IntPointer()
            count2col = IntPointer()
            count1diag11 = IntPointer()
            count2diag11 = IntPointer()
            count1diag12 = IntPointer()
            count2diag12 = IntPointer()
            count1diag21 = IntPointer()
            count2diag21 = IntPointer()
            count1diag22 = IntPointer()
            count2diag22 = IntPointer()
            for j in range(0, self.cols-2):
                self.check_win_help(board, i, j, count1row, count2row, filled)
                self.check_win_help(board, j, i, count1col, count2col)
                if i < 2 and j < 5:
                    self.check_win_help(board, i+j, j, count1diag11, count2diag11)
                    self.check_win_help(board, j, i+j, count1diag12, count2diag12)
                    self.check_win_help(board, i+j, self.cols-3-j, count1diag21, count2diag21)
                    self.check_win_help(board, j, self.cols-3-i-j, count1diag22, count2diag22)
                if count1row.num == self.cols-3 or count1col.num == self.rows-3 or count1diag11.num == self.rows-3 or count1diag12.num == self.rows-3 or count1diag21.num == self.rows-3 or count1diag22.num == self.rows-3:
                    found1 = True
                elif count2row.num == self.cols-3 or count2col.num == self.rows-3 or count2diag11.num == self.rows-3 or count2diag12.num == self.rows-3 or count2diag21.num == self.rows-3 or count2diag22.num == self.rows-3:
                    found2 = True
                if found1 and found2:
                    break
            if found1 and found2:
                break
        if found1 and found2 or filled.num == (self.rows-2) * (self.cols-2):
            return "Tie!"
        elif found1:
            return "Player 1 wins!"
        elif found2:
            return "Player 2 wins!"
        
    def win(self):
        win = self.check_win()
        if win is not None:
            label = Label(text=win, font_size="20sp")
            label.pos = (Window.size[0] / 2 - label.size[0] / 2, Window.size[1] * 2 / 3 - label.size[1] / 2)
            self.reset.pos = (Window.size[0]/2 - self.reset.size[0]/2, Window.size[1]*1/3 + self.menu.size[1]/2)
            self.menu.pos = (Window.size[0]/2 - self.menu.size[0]/2, Window.size[1]*1/3 - self.menu.size[1]/2)
            self.quit.pos = (Window.size[0]/2 - self.quit.size[0]/2, Window.size[1]*1/3 - 2*self.menu.size[1]/2)
            if self.status != "Win":
                self.status = "Win"
                for i in self.buttons:
                    for j in i:
                        j.disabled = True
                self.add_widget(label)
                self.add_widget(self.reset)
                self.add_widget(self.menu)
                self.add_widget(self.quit)
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
            if self.players == 1 and not self.win():
                self.tree = Minimax(self.convert_board(self.buttons))
                self.create_tree(self.turn, self.tree, 3)
                self.respond()

    def place(self, touch):
        if not touch.disabled and not self.rotatable:
            if self.turn == 1:
                touch.mark = "red"
                if self.players == 2:
                    self.turn = 2
            else:
                touch.mark = "blue"
                self.turn = 1
            touch.disabled = True
            self.rotatable = True
            self.draw(touch)
        self.win()

    def respond(self):
        first = True
        min_value = None
        for i in self.tree.next:
            if first:
                min_value = i
                first = False
            else:
                if i.value < min_value.value:
                    min_value = i
        self.tree = min_value
        for i in range(1, len(self.buttons)-1):
            for j in range(1, len(self.buttons[i])-1):
                if self.tree.board[i-1][j-1] == 0:
                    self.buttons[i][j].mark = "empty"
                    self.buttons[i][j].disabled = False
                elif self.tree.board[i-1][j-1] == 1:
                    self.buttons[i][j].mark = "red"
                    self.buttons[i][j].disabled = True
                elif self.tree.board[i-1][j-1] == 2:
                    self.buttons[i][j].mark = "blue"
                    self.buttons[i][j].disabled = True
                self.draw(self.buttons[i][j])
        self.win()
        

class Game(App):
    def build(self):
        self.title = "Pentago"
        return Board()


Game().run()
