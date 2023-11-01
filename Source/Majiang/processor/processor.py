import pygame

from pygame import Surface
from typing import List, Dict
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE
)
from sys import exit

CARD_FACE_NUMS = [
    2,   16,  30,  44,  58,  60,
    74,  88,  102, 15,  29,  43,
    57,  71,  73,  87,  101, 115,
    28,  42,  56,  70,  72,  86,
    100, 114, 128, 51,  38,  25, 
    12,  13,  26,  39,  1,   40, 
    79,  118, 14,  53,  131, 92
    ]

class Asset:

    def __init__(self, card_faces: List[Surface], card_back: Surface, fonts: Dict[str, Surface]) -> None:
        self.card_faces = card_faces
        self.card_back = card_back
        self.fonts = fonts
        
        self.card_size = (card_back.get_width(), card_back.get_height())
        self.card_width = card_back.get_width()
        self.card_height = card_back.get_height()
        
        self.font_size = (fonts[0].get_width(), fonts[0].get_height())
        self.font_width = fonts[0].get_width()
        self.font_height = fonts[0].get_height()

class Processor:
    def __init__(self,
                 card_face_image_path: str,
                 card_back_image_path: str,
                 font_image_path: str
                 ):
        
        self.card_faces_asset = pygame.image.load(card_face_image_path)
        self.card_back_asset = pygame.image.load(card_back_image_path)
        self.font_asset = pygame.image.load(font_image_path)

    def get_assets(self):
        card_face_list, card_back = self.process_card(self.card_faces_asset, self.card_back_asset)
        font_list = self.process_font(self.font_asset)

        assets = Asset(card_face_list, card_back, font_list)
        return assets

    @staticmethod
    def process_card(card_faces: Surface, card_back: Surface):
        """把麻将图片切割成一个一个的牌面"""

        card_face_list = []

        img = card_faces.subsurface((73, 139), (467, 666))
        w, h = img.get_width(), img.get_height()

        ph = h / 12
        pw = w / 12

        for i in range(12):
            for j in range(12):
                card_face = img.subsurface(pygame.Rect(j*pw, i*ph, pw, ph))
                card_face_list.append(card_face)
        
        card_face_list = list(map(lambda index: card_face_list[index], CARD_FACE_NUMS))

        card_back = card_back.subsurface(pygame.Rect(0, 0, pw, ph))

        return card_face_list, card_back

    @staticmethod
    def process_font(font_asset: Surface):
        """把字体图片切割成一个个的字"""

        w, h = font_asset.get_width(), font_asset.get_height()

        font_hu = font_asset.subsurface(pygame.Rect(0, 0, h, h))
        font_peng = font_asset.subsurface(pygame.Rect(w / 4 + 3, 0, h, h))
        font_gang = font_asset.subsurface(pygame.Rect(2 * w / 4 + 8, 0, h, h))
        font_guo = font_asset.subsurface(pygame.Rect(3 * w / 4 + 13, 0, h, h))

        return {
            "hu": font_hu, 
            "peng": font_peng,
            "gang": font_gang, 
            "guo": font_guo
            }



if __name__ == "__main__":
    path = './Assets/Majiang/img.png'
    back = './Assets/Majiang/green.png'
    font = './Assets/Majiang/font.png'
    assets = Processor(path, back, font).get_assets()
    pygame.init()
    screen = pygame.display.set_mode((584, 903), 0, 32)
    fonts = assets.card_faces
    count = 0
    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                else:
                    count += 1
                    if count >= len(fonts):
                        count = 0
        font = fonts[count]
        screen.fill((0, 0, 0))
        screen.blit(font, (0, 0))
        pygame.display.update()
