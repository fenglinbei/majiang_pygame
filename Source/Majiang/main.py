import pygame
from pygame import QUIT, KEYDOWN, K_ESCAPE, K_n, K_s, K_j, K_w, KEYUP, K_p

from config import render_config, base_config
from entity.entities import Table
from render.render import Render
from game_state import GameState

def run():
    pygame.init()

    table = Table()
    state = GameState(table)
    render = Render(table)
    

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                elif event.key == K_n:
                    state.init_game()
                elif event.key == K_s:
                    show_flag = not show_flag
                    if show_flag:
                        show_player_list = [1, 2, 3, 4]
                    else:
                        show_player_list = [1]
                elif event.key == K_j:
                    pass
                elif event.key == K_w:
                    last_j = not last_j

            elif event.type == KEYUP:
                if event.key == K_s:
                    pass
                
        for player in state.players:
            player.brain.think(state)

            if not last_j and player.brain.active_state.name != 'hu':
                state.table.text = ''
            elif last_j and player.brain.active_state.name != 'hu':
                # state.table.text = tips[0]
                # printer.text_2 = tips[1]
                pass
            if player.player_type == 1 and player.brain.active_state.name == 'putting' and not tips_change and last_j:
                tips_change = True
                # tips = player_1.AI.get_tips(manager.player_list[1]['now_card'], manager.table_card)
                # printer.text = tips[0]
                # printer.text_2 = tips[1]
            elif player.player_type == 1 and player.brain.active_state.name != 'putting':
                tips_change = False

        
        render.render()
        pygame.display.update()
