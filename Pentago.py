from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.app import App
import sys


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
        self.reset = Button(text="Click to play again")
        self.reset.bind(on_press=self.reset_board)
        self.menu = Button(text="Click to return to menu")
        self.menu.bind(on_press=self.go_menu)
        self.quit = Button(text="Click to quit")
        self.quit.bind(on_press=self.quit_game)
        self.rotatable = False
        self.players = 0
        self.player = 1
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

    def quit_game(self, touch):
        sys.exit()

    def go_menu(self, touch=None):
        self.clear_widgets()
        self.add_widget(Label(text="How many players?"))
        for i in range(1, 3):
            button = Button(text=str(i))
            button.bind(on_press=self.reset_board)
            self.add_widget(button)

    def reset_board(self, touch):
        if touch.text == "1":
            self.players = 1
        elif touch.text == "2":
            self.players = 2
        self.clear_widgets()
        self.rotatable = False
        self.player = 1
        for i in range(self.rows):
            for j in range(self.cols):
                if self.buttons[i][j].source == "blue.png" or self.buttons[i][j].source == "red.png":
                    self.buttons[i][j].source = "empty.png"
                    self.buttons[i][j].disabled = False
                self.add_widget(self.buttons[i][j])

    def win(self):
        filled = 0
        found1 = False
        found2 = False
        for i in range(1, self.rows-1):
            count1row = 0
            count2row = 0
            count1col = 0
            count2col = 0
            count1diag1 = 0
            count2diag1 = 0
            count1diag2 = 0
            count2diag2 = 0
            for j in range(1, self.cols-1):
                if self.buttons[i][j].source == "red.png":
                    filled += 1
                    count1row += 1
                    count2row = 0
                elif self.buttons[i][j].source == "blue.png":
                    filled += 1
                    count2row += 1
                    count1row = 0
                else:
                    count1row = 0
                    count2row = 0
                if self.buttons[j][i].source == "red.png":
                    count1col += 1
                    count2col = 0
                elif self.buttons[j][i].source == "blue.png":
                    count2col += 1
                    count1col = 0
                else:
                    count1col = 0
                    count2col = 0
                if i < 3 and j < 7:
                    if self.buttons[i-1+j][j].source == "red.png":
                        count1diag1 += 1
                        count2diag1 = 0
                    elif self.buttons[i-1+j][j].source == "blue.png":
                        count2diag1 += 1
                        count1diag1 = 0
                    else:
                        count1diag1 = 0
                        count2diag1 = 0
                    if self.buttons[i-1+j][self.cols-2-j].source == "red.png":
                        count1diag2 += 1
                        count2diag2 = 0
                    elif self.buttons[i-1+j][self.cols-2-j].source == "blue.png":
                        count2diag2 += 1
                        count1diag2 = 0
                    else:
                        count1diag2 = 0
                        count2diag2 = 0
                if count1row == self.cols-3 or count1col == self.rows-3 or count1diag1 == self.rows-3 or count1diag2 == self.rows-3:
                    found1 = True
                elif count2row == self.cols-3 or count2col == self.rows-3 or count2diag1 == self.rows-3 or count2diag2 == self.rows-3:
                    found2 = True
                if found1 and found2:
                    break
            if found1 and found2:
                break
        if found1 and found2 or filled == (self.rows-2) * (self.cols-2):
            self.clear_widgets()
            self.add_widget(Label(text="Tie!"))
            self.add_widget(self.reset)
            self.add_widget(self.menu)
            self.add_widget(self.quit)
        elif found1:
            self.clear_widgets()
            self.add_widget(Label(text="Player 1 wins!"))
            self.add_widget(self.reset)
            self.add_widget(self.menu)
            self.add_widget(self.quit)
        elif found2:
            self.clear_widgets()
            self.add_widget(Label(text="Player 2 wins!"))
            self.add_widget(self.reset)
            self.add_widget(self.menu)
            self.add_widget(self.quit)

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
                self.respond()

    def place(self, touch):
        if not touch.disabled and not self.rotatable:
            if self.player == 1:
                touch.source = "red.png"
                self.player = 2
            else:
                touch.source = "blue.png"
                self.player = 1
            touch.disabled = True
            self.rotatable = True
        self.win()


class Game(App):
    def build(self):
        self.title = "Pentago"
        return Board()


Game().run()
