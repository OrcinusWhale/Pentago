from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.app import App
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
        self. num = num

class ImageButton(ButtonBehavior, Image):
    def __init__(self, row, col):
        Image.__init__(self)
        ButtonBehavior.__init__(self)
        self.row = row
        self.col = col


class Board(GridLayout):
    def __init__(self):
        GridLayout.__init__(self)
        self.rows = 8
        self.cols = 8
        self.buttons = list()
        self.tree = None
        self.reset = Button(text="Click to play again")
        self.reset.bind(on_press=self.reset_board)
        self.menu = Button(text="Click to return to menu")
        self.menu.bind(on_press=self.go_menu)
        self.quit = Button(text="Click to quit")
        self.quit.bind(on_press=self.quit_game)
        self.rotatable = False
        self.players = 0
        self.turn = 1
        for i in range(self.rows):
            self.buttons.append(list())
            for j in range(self.cols):
                self.buttons[i].append(ImageButton(i, j))
                if 0 < i < self.rows-1 and 0 < j < self.cols - 1:
                    self.buttons[i][j].bind(on_press=self.place)
                    self.buttons[i][j].source = "empty.png"
                elif i in [0, self.rows-1] and j in [1, self.cols-2] or i in [1, self.rows-2] and j in [0, self.cols-1]:
                    self.buttons[i][j].bind(on_press=self.rotate)
                else:
                    self.buttons[i][j].source = "board.png"
        self.buttons[0][1].source = "right.png"
        self.buttons[0][1].start_row = self.buttons[1][0].start_row = 1
        self.buttons[0][1].start_col = self.buttons[1][0].start_col = 1
        self.buttons[0][1].cw = True
        self.buttons[1][0].source = "down.png"
        self.buttons[1][0].cw = False
        self.buttons[self.rows-2][0].source = "up.png"
        self.buttons[self.rows-2][0].start_row = self.buttons[self.rows-1][1].start_row = int((self.rows-2)/2)+1
        self.buttons[self.rows-2][0].start_col = self.buttons[self.rows-1][1].start_col = 1
        self.buttons[self.rows-2][0].cw = True
        self.buttons[self.rows-1][1].source = "right.png"
        self.buttons[self.rows-1][1].cw = False
        self.buttons[self.rows-1][self.cols-2].source = "left.png"
        self.buttons[self.rows-1][self.cols-2].start_row = self.buttons[self.rows-2][self.cols-1].start_row = int((self.rows-2)/2)+1
        self.buttons[self.rows-1][self.cols-2].start_col = self.buttons[self.rows-2][self.cols-1].start_col = int((self.cols-2)/2)+1
        self.buttons[self.rows-1][self.cols-2].cw = True
        self.buttons[self.rows-2][self.cols-1].source = "up.png"
        self.buttons[self.rows-2][self.cols-1].cw = False
        self.buttons[1][self.cols-1].source = "down.png"
        self.buttons[1][self.cols-1].start_row = self.buttons[0][self.cols-2].start_row = 1
        self.buttons[1][self.cols-1].start_col = self.buttons[0][self.cols-2].start_col = int((self.cols-2)/2)+1
        self.buttons[1][self.cols-1].cw = True
        self.buttons[0][self.cols-2].source = "left.png"
        self.buttons[0][self.cols-2].cw = False
        self.go_menu()

    def convert_board(self, board=None):
        if board is None:
            board = self.buttons
        converted = list()
        for i in range(1, len(board)-1):
            converted.append(list())
            for j in range(1, len(board[i])-1):
                if board[i][j].source == "red.png":
                    converted[i-1].append(1)
                elif board[i][j].source == "blue.png":
                    converted[i-1].append(2)
                elif board[i][j].source == "empty.png":
                    converted[i-1].append(0)
        return converted

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
                            add = True
                            toRotate = list()
                            for a in range(int((self.rows-1)/2)*x, int((self.rows-1)/2)*(x+1)):
                                toRotate.append(list())
                                for b in range(int((self.cols-1)/2)*y, int((self.cols-1)/2)*(y+1)):
                                    toRotate[a - int((self.cols-1)/2)*x].append(temp[a][b])
                            numpy.rot90(toRotate)
                            for a in range(int((self.rows-1)/2)*x, int((self.rows-1)/2)*(x+1)):
                                for b in range(int((self.rows-1)/2)*y, int((self.rows-1)/2)*(y+1)):
                                    temp[a][b] = toRotate[a - int((self.rows-1)/2)*x][b - int((self.rows-1)/2)*y]
                            for c in next:
                                if c.board == temp:
                                    add = False
                                    break
                            if add:
                                next.append(Minimax(temp))
                            add = True
                            numpy.rot90(toRotate, 2)
                            for a in range(int((self.rows-1)/2)*x, int((self.rows-1)/2)*(x+1)):
                                for b in range(int((self.rows-1)/2)*y, int((self.rows-1)/2)*(y+1)):
                                    temp[a][b] = toRotate[a - int((self.rows-1)/2)*x][b - int((self.rows-1)/2)*y]
                            for c in next:
                                if c.board == temp:
                                    add = False
                                    break
                            if add:
                                next.append(Minimax(temp))
        return next

    def quit_game(self, touch):
        sys.exit()

    def go_menu(self, touch=None):
        self.clear_widgets()
        self.add_widget(Label(text="How many players?"))
        for i in range(1, 3):
            button = Button(text=str(i))
            button.bind(on_press=self.reset_board)
            self.add_widget(button)

    def evaluate_board_help(self, board, i, j, count, value):
        if board[i][j] == board[i][j - 1] != 0 or board[i][j] != 0 and count.num == 0:
            count.num += 1
        else:
            if board[i][j - 1] == 1:
                value.num += 2 ** count.num
            elif board[i][j - 1] == 2:
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
                    self.evaluate_board_help(board, i, j, sequence_count_r, value)
                    self.evaluate_board_help(board, i, j, sequence_count_c, value)
                    if i+j < 6:
                        self.evaluate_board_help(board, i+j, j, sequence_count_d11, value)
                        self.evaluate_board_help(board, j, i+j, sequence_count_d12, value)
                        self.evaluate_board_help(board, i+j, self.cols-3-j, sequence_count_d21, value)
                        self.evaluate_board_help(board, j, self.cols-3-i-j, sequence_count_d22, value)
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
        return value

    def create_tree(self, turn, current, depth):
        winner = self.win(current.board)
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
                current.next = self.next_boards(current, 2)
            if turn == 2:
                current.next = self.next_boards(current, 1)
            for i in current.next:
                if turn == 1:
                    self.create_tree(2, i, depth - 1)
                else:
                    self.create_tree(1, i, depth - 1)
            first = True
            if turn == 2:
                for i in current.next:
                    if first:
                        current.value = i.value
                        first = False
                    elif current.value < i.value:
                        current.value = i.value
            else:
                for i in current.next:
                    if first:
                        current.value = i.value
                        first = False
                    elif current.value > i.value:
                        current.value = i.value

    def reset_board(self, touch):
        if touch.text == "1":
            self.players = 1
        elif touch.text == "2":
            self.players = 2
        self.clear_widgets()
        self.rotatable = False
        self.turn = 1
        for i in range(self.rows):
            for j in range(self.cols):
                if self.buttons[i][j].source == "blue.png" or self.buttons[i][j].source == "red.png":
                    self.buttons[i][j].source = "empty.png"
                    self.buttons[i][j].disabled = False
                self.add_widget(self.buttons[i][j])

    def win_help(self, board, filled, i, j, count1, count2):
        if board[i][j] == 1:
            filled.num += 1
            count1.num += 1
            count2.num = 0
        elif board[i][j] == 2:
            filled.num += 1
            count2.num += 1
            count1.num = 0
        else:
            count1.num = 0
            count2.num = 0

    def win(self, board=None):
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
                self.win_help(board, filled, i, j, count1row, count2row)
                self.win_help(board, filled, j, i, count1col, count2col)
                if i + j < 6:
                    self.win_help(board, filled, i+j, j, count1diag11, count2diag11)
                    self.win_help(board, filled, j, i+j, count1diag12, count2diag12)
                    self.win_help(board, filled, i+j, self.cols-3-j, count1diag21, count2diag21)
                    self.win_help(board, filled, j, self.cols-3-i-j, count1diag22, count2diag22)
                if count1row == self.cols-3 or count1col == self.rows-3 or count1diag11 == self.rows-3 or count1diag12 == self.rows-3 or count1diag21 == self.rows-3 or count1diag22 == self.rows-3:
                    found1 = True
                elif count2row == self.cols-3 or count2col == self.rows-3 or count2diag11 == self.rows-3 or count2diag12 == self.rows-3 or count2diag21 == self.rows-3 or count2diag22 == self.rows-3:
                    found2 = True
                if found1 and found2:
                    break
            if found1 and found2:
                break
        if found1 and found2 or filled == (self.rows-2) * (self.cols-2):
            return "Tie!"
        elif found1:
            return "Player 1 wins!"
        elif found2:
            return "Player 2 wins!"

    def rotate(self, touch):
        if self.rotatable:
            for i in range(int((self.rows-2)/4)):
                for j in range(i, int((self.cols-2)/2)-1-i):
                    temp_s = self.buttons[touch.start_row+i][touch.start_col+i+j].source
                    temp_d = self.buttons[touch.start_row+i][touch.start_col+i+j].disabled
                    if touch.cw:
                        self.buttons[touch.start_row+i][touch.start_col+i+j].source = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].source
                        self.buttons[touch.start_row+i][touch.start_col+i+j].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].source = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].source
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].source = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].source
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].source = temp_s
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled = temp_d
                    else:
                        self.buttons[touch.start_row+i][touch.start_col+i+j].source = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].source
                        self.buttons[touch.start_row+i][touch.start_col+i+j].disabled = self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].source = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].source
                        self.buttons[touch.start_row+i+j][touch.start_col+int((self.cols-2)/2)-1-i].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].source = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].source
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i][touch.start_col+int((self.cols-2)/2)-1-i-j].disabled = self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].source = temp_s
                        self.buttons[touch.start_row+int((self.rows-2)/2)-1-i-j][touch.start_col+i].disabled = temp_d
            self.rotatable = False
            self.win()
            if self.players == 1:
                self.tree = Minimax(self.convert_board(self.buttons))
                self.create_tree(self.turn, self.tree, 2)
                self.respond()

    def place(self, touch):
        if not touch.disabled and not self.rotatable:
            if self.turn == 1:
                touch.source = "red.png"
                if self.players == 2:
                    self.turn = 2
            else:
                touch.source = "blue.png"
                self.turn = 1
            touch.disabled = True
            self.rotatable = True
        win = self.win()
        if win is not None:
            self.clear_widgets()
            self.add_widget(Label(text=win))
            self.add_widget(self.reset)
            self.add_widget(self.menu)
            self.add_widget(self.quit)

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
                    self.buttons[i][j].source = "empty.png"
                    self.buttons[i][j].disabled = False
                elif self.tree.board[i-1][j-1] == 1:
                    self.buttons[i][j].source = "red.png"
                    self.buttons[i][j].disabled = True
                elif self.tree.board[i-1][j-1] == 2:
                    self.buttons[i][j].source = "blue.png"
                    self.buttons[i][j].disabled = True


class Game(App):
    def build(self):
        self.title = "Pentago"
        return Board()


Game().run()
