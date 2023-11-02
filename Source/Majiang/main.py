import pygame

from config import render_config, base_config
from Source.Majiang.entity.entities import Table
from Source.Majiang.logic.referee import Logic
from render.render import Render

def run():
    pygame.init()
    screen = pygame.display.set_mode((render_config.SCREEN_WIDTH, render_config.SCREEN_HEIGHT), 0, 32)
    font = pygame.font.SysFont("arial", render_config.FONT_SIZE)


    table = Table()
    logic = Logic(table, card_mode=base_config.CARD_MODE)
    render = Render(table)

    w, h = screen.get_width(), screen.get_height()
    text = ''
    count = 1
    step = 1
    last_j = False
    tips_change = False
    tips = ['', '']
    flag = False
    card_is_choice = False
    card_is_draw = {1: True, 2: False, 3: False, 4: False}
    put_card = 0
    win_count = 0
    show_player_list = [1]
    show_flag = False

    logic.init_game()
    render.load_all_cards(logic.all_cards)
    
    clock = pygame.time.Clock()
    
    player = logic.players[base_config.INIT_PLAYER]
    
    player_1 = Player(1, manager, printer, use_ai=False)
    player_1.brain.set_state('drawing')
    players = [player_1]

    for i in range(3):
        player_i = Player(i + 2, manager, printer, use_ai=True)
        player_i.brain.set_state('waiting')
        players.append(player_i)


    def get_text(judgement):
        return str(judgement['is_win']) + '  ' + str(
            judgement['type']) + '  ks: ' + str(judgement['count'])


    def restart():
        printer.table.reset_entity()
        manager.reset()
        manager.tidy_card(manager.player_list)
        printer.read_card(manager.player_list, manager.table_card)
        manager.last_player = 0
        manager.peng_player = 0
        for player in players:
            if player.player == manager.last_winner:
                player.brain.set_state('drawing')
            else:
                player.brain.set_state('waiting')
            player.peng_cls_list = []
        printer.text = ''


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()
                elif event.key == K_n:
                    restart()
                    step = 1
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
                    # show_player_list = [1, 2, 3, 4]
                elif event.key == K_p:
                    type_list, score, best_card, best_score, all_score = \
                        players[0].AI.do_score(manager.player_list[1]['now_card'],
                                               manager.table_card)
                    print(type_list, score, best_card, best_score, all_score)
        if step <= 14:
            time_passed = clock.tick(10)
            printer.load_card(step)
            printer.table.render(screen, show_player_list)
            step += 1
        else:
            for player in players:
                player.brain.think()

                if not last_j and player.brain.active_state.name != 'hu':
                    printer.text = ''
                    printer.text_2 = ''
                elif last_j and player.brain.active_state.name != 'hu':
                    printer.text = tips[0]
                    printer.text_2 = tips[1]
                if player.player == 1 and player.brain.active_state.name == 'putting' and not tips_change and last_j:
                    tips_change = True
                    tips = player_1.AI.get_tips(manager.player_list[1]['now_card'], manager.table_card)
                    printer.text = tips[0]
                    printer.text_2 = tips[1]
                elif player.player == 1 and player.brain.active_state.name != 'putting':
                    tips_change = False

            time_passed = clock.tick(60)
            printer.table.process(time_passed)
            printer.table.render(screen, show_player_list)
            font_text_1 = font.render(printer.text, True, (0, 0, 0))
            font_text_2 = font.render(printer.text_2, True, (0, 0, 0))
            screen.blit(font_text_1, (w / 2 - 100, h / 2 - 24))
            screen.blit(font_text_2, (w / 2 - 100, h / 2 + 10))
        pygame.display.update()
