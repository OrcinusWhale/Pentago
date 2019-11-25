from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.app import App


class ImageButton(ButtonBehavior, Image):
    def __init__(self):
        Image.__init__(self)
        ButtonBehavior.__init__(self)


class Board(GridLayout):
    def __init__(self):
        GridLayout.__init__(self)
        self.rows = 8
        self.cols = 8
        self.buttons = list()
        self.rotatable = False
        self.player = 0
        for i in range(self.rows):
            self.buttons.append(list())
            for j in range(self.cols):
                self.buttons[i].append(ImageButton())
                if 0 < i < self.rows-1 and 0 < j < self.cols - 1:
                    self.buttons[i][j].bind(on_press=self.place)
                    self.buttons[i][j].source = "empty.png"
                elif i in [0, self.rows-1] and j in [1, self.cols-2] or i in [1, self.rows-2] and j in [0, self.cols-1]:
                    self.buttons[i][j].bind(on_press=self.rotate)
                else:
                    self.buttons[i][j].source = "board.png"
                self.add_widget(self.buttons[i][j])
        self.buttons[0][1].source = "right.png"
        self.buttons[1][0].source = "down.png"
        self.buttons[self.rows-2][0].source = "up.png"
        self.buttons[self.rows-1][1].source = "right.png"
        self.buttons[self.rows-1][self.cols-2].source = "left.png"
        self.buttons[self.rows-2][self.cols-1].source = "up.png"
        self.buttons[1][self.cols-1].source = "down.png"
        self.buttons[0][self.cols-2].source = "left.png"

    def rotate(self, touch):
        if self.rotatable:

            self.rotatable = False

    def place(self, touch):
        if not touch.disabled and not self.rotatable:
            if self.player == 0:
                touch.source = "red.png"
                self.player = 1
            else:
                touch.source = "blue.png"
                self.player = 0
            touch.disabled = True
            self.rotatable = True


class Game(App):
    def build(self):
        self.title = "Pentago"
        return Board()


Game().run()
