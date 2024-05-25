import os
import sys

# needed when you what to convert to exe file
if hasattr(sys, "_MEIPASS"):
    os.environ["KIVY_NO_CONSOLELOG"] = "1"
import random
from kivy.lang.builder import Builder
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
import json
from kivy.uix.togglebutton import ToggleButton
from functools import partial
import math


# bring our .kv design file
kv = Builder.load_file("memory.kv")

# set the app size
Window.size = (800, 800)


class StartScreen(Screen):
    """class for start screen that inherate from Screen class built in kivy"""

    # the player of game
    player_name = None
    # how many words to play with
    words_amount = 0

    def __init__(self, **kwargs):
        super().__init__(name="start", **kwargs)
        """for making the screen as part of kivy syntax"""

    def change(self):
        """changing the screen to game screen"""
        theapp.screenm.current = "game"

    def pressed(self, *arg):
        """take the name from gui and save it in a variable
        indata: the pressed object"""
        name = self.ids.player_name.text
        StartScreen.player_name = name_input(name)
        StartScreen.words_amount = int(self.ids.slider.value)

        # run the functions in GameScreen
        self.manager.get_screen("game").arrange_grid()
        self.manager.get_screen("game").arrange_cells()


class GameScreen(Screen):
    """class for game screen that inherate from Screen class built in kivy"""

    score = 0
    best_ratio = math.ceil((StartScreen.words_amount * 2) ** 0.5)

    def __init__(self, **kwargs):
        super().__init__(name="game", **kwargs)
        """for making the screen as part of kivy syntax"""

        self.all_cells = []

        # Initialize the current and previous button to None
        self.current_word = None
        self.previous_word = None

        self.current_index = None
        self.previous_index = None

        self.counter = 0
        self.count_the_matchs = 0

    def arrange_grid(self):
        """arrange the grid based on how many words user chooses"""

        best_ratio = math.ceil((StartScreen.words_amount * 2) ** 0.5)

        self.box = BoxLayout(orientation="vertical")
        self.grid = GridLayout(cols=best_ratio, rows=best_ratio)
        self.box2 = BoxLayout(size_hint=(1, 0.1), orientation="horizontal")

        self.box.add_widget(self.grid)
        self.box.add_widget(self.box2)
        self.add_widget(self.box)

        # go to score button
        self.start_button = Button(text="go to score")
        self.start_button.bind(on_press=self.go_to_score_pressed)
        self.box2.add_widget(self.start_button)

    def arrange_cells(self):
        """arrange the cells"""

        words_maker = Words()

        # all  the words in the gird
        self.words = words_maker.chosed_words

        for cell in range(len(self.words)):

            self.cell = ToggleButton(text="", color=(1, 0, 1, 1))

            # will be called whenever the size of button changes by resizing the screen
            self.cell.bind(size=self.update_after_resize)

            # when a cell is pressed
            function = partial(self.cell_pressed, cell)
            self.cell.bind(on_press=function)

            self.all_cells.append(self.cell)
            self.grid.add_widget(self.cell)

    def update_after_resize(self, instance, size):
        """function need to make dynamiclly resizing
        indata is size of button and button instance"""
        instance.font_size = size[0] / 5
        instance.text_size = (size[0], size[1])
        instance.halign = "center"
        instance.valign = "middle"

    def cell_pressed(self, cell, *arg):
        """it will save the pressed cell information for compration and show the word related to the cell
        indata: cell index and pressed cell as object"""

        word = self.words[cell]
        self.all_cells[cell].text = word

        if self.counter == 0:
            self.previous_word = word
            self.previous_index = cell
            self.counter = 1

        else:
            self.current_word = word
            self.current_index = cell
            self.counter = 0

            GameScreen.score += 1

            # wait 0.4 second before checking for match
            self.obj = Clock.schedule_once(self.check_for_match, 0.4)

    def check_for_match(self, *arg):
        """checks if two words are same or not"""

        if (
            self.previous_word == self.current_word
            and self.previous_index != self.current_index
        ):
            self.all_cells[self.previous_index].disabled = True
            self.all_cells[self.current_index].disabled = True

            self.count_the_matchs += 1

            self.last_cell_check()

        # flip over the cells
        else:
            self.all_cells[self.current_index].state = "normal"
            self.all_cells[self.previous_index].state = "normal"
            self.all_cells[self.current_index].text = ""
            self.all_cells[self.previous_index].text = ""

    def last_cell_check(self):
        """check if all cells are matched and it will finish the game and change the screen to score"""
        if self.count_the_matchs == len(self.words) / 2:

            theapp.screenm.current = "score"
            Player.maker(
                StartScreen.player_name, GameScreen.score, StartScreen.words_amount
            )
            self.manager.get_screen("score").arrange_scores()

    def go_to_score_pressed(self, *arg):
        """change the screen to score and put the player score to 0 so player will be deleted
        then it will show the top 10 players score"""

        theapp.screenm.current = "score"
        Player.maker(0, 0, StartScreen.words_amount)
        self.manager.get_screen("score").arrange_scores()


class ScoreScreen(Screen):
    """class for game screen that inherate from Screen class built in kivy"""

    def __init__(self, **kwargs):
        super().__init__(name="score", **kwargs)
        """for making the screen as part of kivy syntax"""

    def arrange_scores(self):
        """arrange score screen and put top 10 players on scoroe screen"""
        self.manager.get_screen("score").ids.point.text = Player.top_10_text
        self.manager.get_screen(
            "score"
        ).ids.title.text = f"TOP 10 Scoreboard for {StartScreen.words_amount} words"


class MemoApp(App):
    """class for main app that kivy will run"""

    def build(self):
        """function to build app, this is a part of kivy syntax"""

        self.screenm = ScreenManager()

        # make start screen and add it to screen manager
        self.start_screen = StartScreen()
        self.screenm.add_widget(self.start_screen)

        # make game screen and add it to screen manager
        self.game_screen = GameScreen()
        self.screenm.add_widget(self.game_screen)

        # make score screen and add it to screen manager
        self.score_screen = ScoreScreen()
        self.screenm.add_widget(self.score_screen)

        return self.screenm


class Player:
    """take care of making, reading and sorting players"""

    top_10_text = ""
    players_list = []

    @classmethod
    def maker(cls, name, score, words_amount):
        """make a player dic that have the courent player name and score as index
        and append the new player to a list with previous players
        indata: name , score and words amount"""

        cls.check_empty_file()

        # check if player finished the game or pressed the score button
        if score != 0:
            one_player = {}
            one_player["name"] = name
            one_player["score"] = score
            one_player["words_amount"] = words_amount

            cls.players_list.append(one_player)

        with open("scores.json", "w") as file2:
            json.dump(cls.players_list, file2)

        cls.top_10(cls.players_list, words_amount)

    @classmethod
    def check_empty_file(cls):
        """check if the score.json is empty and if it is empty it will not show any error
        otherwise it it will save all players to players_list"""
        try:
            with open("scores.json", "r") as file2:
                cls.players_list = json.load(file2)
        except:
            pass

    @classmethod
    def top_10(cls, p_list, words_amount):
        """get a list of players and save top 10 players in a variable in text form
        indata: player_list and words_amount"""

        filtered = cls.filter(p_list,words_amount)

        sorted_player_list = sorted(
            filtered, key=lambda player: player["score"], reverse=False
        )

        top_10 = sorted_player_list[:10]

        for player in top_10:
            cls.top_10_text += f"{player['name']}           {player['score']}\n"
        
    @classmethod
    def filter(cls,p_list,words_amount):
        """filter the player list and save all players with same words amount
        indata: player list and words_amount
        oudata: filtred list"""
        filtered = []
        for player in p_list:
            if player["words_amount"] == words_amount:
                filtered.append(player)
        return filtered



class Words:
    """take care of reading the words and adding them to a list"""

    def __init__(self):
        """make a list for words"""
        self.all_words = []
        self.chosed_words = self.read_words()

    def read_words(self):
        """read memo.tx file and get right amount of words to use in game"""
        # opens the file
        with open("memoUTF8.txt", "r", encoding="utf-8") as file:
            for _ in file:
                self.all_words.append(_)

        words = random.sample(self.all_words, StartScreen.words_amount)
        words_2 = words + words
        random.shuffle(words_2)

        return words_2


def name_input(name):
    """get the name and check if there is no name so it will
    return name as unknown player
    indata: name
    outdata: name"""
    if not name or len(name) > 30:
        name = "Unknown player"
        return name
    else:
        return name


if __name__ == "__main__":
    # instantiate our app
    theapp = MemoApp()

    # run the app
    theapp.run()
