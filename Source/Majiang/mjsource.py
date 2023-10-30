import pygame
from pygame.locals import *
from sys import exit


class Processor:
    def __init__(self,
                 card_front_image_path: str,
                 card_back_image_path: str,
                 font_image_path: str
                 ):
        self.card_front = pygame.image.load(card_front_image_path)
        self.card_back = pygame.image.load(card_back_image_path)
        self.font = pygame.image.load(font_image_path)
        self.img_list = self.convert()
        self.font_list = self.convert_font()
        self.num_list = [2, 16, 30, 44, 58, 60, 74, 88, 102,
                         15, 29, 43, 57, 71, 73, 87, 101, 115,
                         28, 42, 56, 70, 72, 86, 100, 114, 128,
                         51, 38, 25, 12, 13, 26, 39, 1, 40, 79, 118, 14, 53, 131, 92]

    def convert(self):
        img_list = []
        img = self.card_front.subsurface((73, 139), (467, 666))
        w, h = img.get_width(), img.get_height()
        ph = h / 12
        pw = w / 12
        for i in range(12):
            for j in range(12):
                img_cut = img.subsurface(pygame.Rect(j*pw, i*ph, pw, ph))
                img_list.append(img_cut)
        img_list.append(self.green.subsurface(pygame.Rect(0, 0, pw, ph)))
        return img_list

    def convert_font(self):
        fonts = self.font
        w, h = fonts.get_width(), fonts.get_height()
        font_hu = fonts.subsurface(pygame.Rect(0, 0, h, h))
        font_peng = fonts.subsurface(pygame.Rect(w / 4 + 3, 0, h, h))
        font_gang = fonts.subsurface(pygame.Rect(2 * w / 4 + 8, 0, h, h))
        font_guo = fonts.subsurface(pygame.Rect(3 * w / 4 + 13, 0, h, h))
        return [font_hu, font_peng, font_gang, font_guo]

    def __getitem__(self, index):
        if index != 0:
            return self.img_list[self.num_list[index - 1]].convert()
        else:
            return self.img_list[-1].convert()



if __name__ == "__main__":
    path = './data/image/img.png'
    back = './data/image/green.png'
    font = './data/image/font.png'
    mj = mjPic(path, back, font)
    pygame.init()
    screen = pygame.display.set_mode((584, 903), 0, 32)
    img = mj.font_list[0]
    count = 0
    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                else:
                    count += 1
                    if count >= len(mj.font_list):
                        count = 0
        img = mj.font_list[count]
        screen.fill((0, 0, 0))
        screen.blit(img, (0, 0))
        pygame.display.update()
