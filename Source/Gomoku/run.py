import pygame

from pygame import Surface
from typing import List

from config import config
from map.game_map import Map
from ai.chess_ai import ChessAI
from utils.constants import Player, Color

from utils.utils import reverse_player

class Button:
    def __init__(self, screen: Surface, text: str, x: int, y: int, color, enable: bool):
        self.screen = screen
        self.width = config.BUTTON_WIDTH
        self.height = config.BUTTON_HEIGHT
        self.button_color = color
        self.text_color = (255, 255, 255)
        self.enable = enable
        self.font = pygame.font.SysFont(None, config.BUTTON_HEIGHT * 2 // 3)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.topleft = (x, y)
        self.text = text

        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])

        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
    
    def click(self):
        pass


class StartButton(Button):
    def __init__(self, screen: Surface, text: str, x: int, y: int):
        super().__init__(screen, text, x, y, [(26, 173, 25), (158, 217, 157)], True)

    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class GiveUpButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(230, 67, 64), (236, 139, 137)], False)

    def click(self, game):
        if self.enable:
            game.playing = False
            if game.winner is None:
                game.winner = reverse_player(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class Game:
    def __init__(self, caption: str):
        pygame.init()
        self.screen = pygame.display.set_mode([config.SCREEN_WIDTH, config.SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.buttons: List[Button] = []
        self.buttons.append(StartButton(self.screen, 'Start', config.MAP_WIDTH + 30, 15))
        self.buttons.append(GiveUpButton(self.screen, 'Give up', config.MAP_WIDTH + 30, config.BUTTON_HEIGHT + 45))
        self.playing = False

        self.map = Map(config.LOGIC_MAP_WIDTH, config.LOGIC_MAP_HIGHT)
        self.player = config.PLAYER_USED
        self.first_hand = config.FIRST_HAND
        self.action = None
        self.AI = ChessAI(config.CHESS_LEN)
        self.useAI = config.USE_AI
        self.winner = None

    def start(self):
        self.playing = True

        if self.first_hand:
            self.useAI = False
            self.player = config.PLAYER_USED
        else:
            self.useAI = True
            self.player = reverse_player(config.PLAYER_USED)

        self.map.reset()

    def play(self):
        self.clock.tick(60)

        pygame.draw.rect(self.screen, Color.LIGHT_YELLOW, pygame.Rect(0, 0, config.MAP_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, Color.WHITE, pygame.Rect(config.MAP_WIDTH, 0, config.INFO_WIDTH, config.SCREEN_HEIGHT))

        for button in self.buttons:
            button.draw()

        if self.playing and not self.isOver():

            if self.useAI:
                x, y = self.AI.findBestChess(self.map.map, self.player)
                self.checkClick(x, y, True)
                self.useAI = False

            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.action = None

            if not self.isOver():
                self.changeMouseShow()


        if self.isOver():
            self.showWinner()

        self.map.drawBackground(self.screen)
        self.map.drawChess(self.screen)

    def changeMouseShow(self):
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            light_red = (213, 90, 107)
            pos, radius = (map_x, map_y), config.CHESS_RADIUS
            pygame.draw.circle(self.screen, light_red, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    def checkClick(self, x, y, isAI=False):
        self.map.click(x, y, self.player)
        if self.AI.isWin(self.map.map, self.player):
            self.winner = self.player
            self.click_button(self.buttons[1])
        else:
            self.player = reverse_player(self.player)
            if not isAI:
                self.useAI = True

    def mouseClick(self, map_x: int, map_y: int):

        if self.playing and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)
        

    def isOver(self) -> bool:
        return self.winner is not None

    def showWinner(self):
        def showFont(screen, text, location_x, locaiton_y, height):
            font = pygame.font.SysFont(None, height)
            font_image = font.render(text, True, (0, 0, 255), (255, 255, 255))
            font_image_rect = font_image.get_rect()
            font_image_rect.x = location_x
            font_image_rect.y = locaiton_y
            screen.blit(font_image, font_image_rect)

        if self.winner == Player.WHITE:
            str = 'Winner is White'
        else:
            str = 'Winner is Black'
        showFont(self.screen, str, config.MAP_WIDTH + 25, config.SCREEN_HEIGHT - 60, 30)
        pygame.mouse.set_visible(True)

    def click_button(self, button: Button):
        if button.click(self):
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick()

    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break


if __name__ == "__main__":
    print(config.__dict__)
    game = Game("FIVE CHESS " + config.GAME_VERSION)
    while True:
        game.play()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                game.mouseClick(mouse_x, mouse_y)
                game.check_buttons(mouse_x, mouse_y)
