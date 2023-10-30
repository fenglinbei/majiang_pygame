import copy
import Source.Majiang.AI2 as AI2
import sys
import Source.Majiang.mj_manager as mj_manager

L_SCORE = 1000
S_3_SCORE = 1000
K_3_SCORE = 4000
S_2_1_SCORE = 500
S_2_2_SCORE = 250
K_2_SCORE = 500
EYE_SCORE = 8
WIN_SCORE = 10000
SCORE_LIST = {
    'win_type': 100000,
    'ks': 30000,
    'l': 5000,
    'k_2': 1000,
    'k_3': 20000,
    'k_4': 25000,
    's_2_1': 4000,
    's_2_2': 2000,
    's_3': 4000
}


def get_type_score(type_list):
    card_score = 0
    for card_type in type_list.keys():
        card_score += type_list[card_type] * SCORE_LIST[card_type]
    return card_score


def get_id(card_list: list, card: dict) -> int:
    c_type = list(card.keys())[0]
    if c_type != 'z':
        card_name = {'m': 'wan', 'p': 'tong', 's': 'suo'}[c_type]
    else:
        card_name = ['dong', 'nan', 'xi', 'bei', 'bai', 'fa', 'zhong'][card[c_type][0] - 1]
    for card_dict in card_list:
        if card_dict['name'] == card_name:
            if card_name in ['wan', 'tong', 'suo']:
                if card[c_type][0] == card_dict['num']:
                    return card_dict['id']
            else:
                return card_dict['id']


class AI(object):
    def __init__(self, manager, player_num):
        self.last_put = 0
        self.manager = manager
        self.player = player_num

    def get_available_card(self, card_list, table_card):
        new_card = self.manager.create_card()

        for p in table_card:
            for card_put in table_card[p]['now_card']:
                new_card.remove(card_put)
            for card_peng in table_card[p]['put_card']['p']:
                new_card.remove(card_peng)
            for card_gang in table_card[p]['put_card']['g']:
                new_card.remove(card_gang)
        for card_mine in card_list:
            new_card.remove(card_mine)
        return new_card

    def put_card(self, card_list, table_card, player_num=0):
        card_dict = AI2.read_hands_from_dict(card_list)
        table_dict = AI2.read_cards_from_table(table_card)
        best_card = AI2.put_judgment(card_dict,
                                     appear_card=AI2.append_cards(copy.deepcopy(card_dict), table_dict))
        best_card_id = get_id(card_list, best_card[0]['put'])
        return best_card_id, best_card

    def get_tips(self, card_list, table_card):
        card_dict = AI2.read_hands_from_dict(card_list)
        table_dict = AI2.read_cards_from_table(table_card)
        best_card = AI2.put_judgment(card_dict,
                                     appear_card=AI2.append_cards(copy.deepcopy(card_dict), table_dict))
        c_type = list(best_card[0]['put'].keys())[0]
        card = str(best_card[0]['put'][c_type][0]) + c_type
        tips = [f"best card: {card}", f"efficient num: {best_card[0]['efficient num']}"]
        return tips

    def choice(self, card_list, table_card, put_card, state_list):
        print(f"CHOICE CARD: {AI2.read_hands_from_dict(card_list)}")
        if 'hu' in state_list:
            return 'hu'
        if 'peng' in state_list:
            peng_card_id_list = []
            card_dict = AI2.read_hands_from_dict(card_list)
            table_dict = AI2.read_cards_from_table(table_card)
            before_res = AI2.card_looper(card_dict, table_dict)
            before_efficient_card, before_efficient_num = before_res
            before_hu_num = AI2.seq_num_judgment(card_dict)['hu num']

            # 提取碰牌列表
            k_2_list = self.manager.loop_k(card_list, k_count=2, l_cls=[])
            for k_2_cls_num in range(len(k_2_list['cls'])):
                if put_card['cls'] in k_2_list['cls'][k_2_cls_num]:
                    peng_card_id_list = k_2_list['id'][k_2_cls_num]
                    break
            peng_card_id_list.append(put_card['id'])

            # 获取碰牌后手牌
            new_card_list = copy.deepcopy(card_list)
            new_table_card = copy.deepcopy(table_card)  # 没碰牌之前的牌河
            new_player_list = copy.deepcopy(self.manager.player_list)
            new_card_list = self.manager.remove_card_by_id(new_card_list, peng_card_id_list)
            new_card_dict = AI2.read_hands_from_dict(new_card_list)
            new_table_dict = AI2.read_cards_from_table(self.manager.table_card)
            self.manager.move_card_to_peng(peng_card_id_list, 1)
            after_res = AI2.put_judgment(new_card_dict,
                                         appear_card=AI2.append_cards(copy.deepcopy(new_card_dict), new_table_dict))
            # print(new_card_dict, AI2.card_counter(new_card_dict))
            after_efficient_num = after_res[0]['efficient num']
            after_hu_num = AI2.seq_num_judgment(new_card_dict)['hu num']
            print(f'BEFORE: {before_hu_num}, BEFORE NUM: {before_efficient_num}')
            print(f'AFTER PENG: {after_hu_num}, AFTER PENG: {after_efficient_num}')
            self.manager.table_card = new_table_card  # 使manager牌河返回到没碰之前的状态
            self.manager.player_list = new_player_list

            # 获取碰牌后分数

            if 'gang' in state_list:  # 如果可碰可杠，则进行模拟杠牌后分数计算
                # 提取杠牌列表
                gang_card_id_list = []
                k_3_list = self.manager.loop_k(card_list, k_count=3, l_cls=[])
                for k_3_cls_num in range(len(k_3_list['cls'])):
                    if put_card['cls'] in k_3_list['cls'][k_3_cls_num]:
                        gang_card_id_list = k_3_list['id'][k_3_cls_num]
                        break
                gang_card_id_list.append(put_card['id'])

                # 获取杠牌后的分数
                new_card_list = copy.deepcopy(card_list)
                new_table_card = copy.deepcopy(table_card)  # 没碰牌之前的牌河
                new_player_list = copy.deepcopy(self.manager.player_list)
                new_card_list = self.manager.remove_card_by_id(new_card_list, gang_card_id_list)
                new_card_dict = AI2.read_hands_from_dict(new_card_list)
                new_table_dict = AI2.read_cards_from_table(self.manager.table_card)
                self.manager.move_card_to_gang(gang_card_id_list, 1)
                after_res = AI2.card_looper(new_card_dict,
                                            appear_card=AI2.append_cards(copy.deepcopy(new_card_dict), new_table_dict))
                after_efficient_num_2 = after_res[1]
                after_hu_num_2 = AI2.seq_num_judgment(new_card_dict)['hu num']
                print(f'AFTER GANG: {after_hu_num_2}, AFTER GANG: {after_efficient_num_2}')
                self.manager.table_card = new_table_card  # 使manager牌河返回到没碰之前的状态
                self.manager.player_list = new_player_list

                if after_hu_num < before_hu_num:
                    return 'peng'
                elif after_hu_num == before_hu_num:
                    if after_efficient_num > before_efficient_num:
                        return 'peng'

                if after_hu_num_2 > before_hu_num:
                    return 'guo'
                elif after_hu_num_2 == before_hu_num:
                    if after_efficient_num_2 >= before_efficient_num:
                        return 'gang'
                    else:
                        return 'guo'

            if after_hu_num < before_hu_num:
                return 'peng'
            elif after_hu_num == before_hu_num:
                if after_efficient_num >= before_efficient_num:
                    return 'peng'
                else:
                    return 'guo'
            else:
                return 'guo'
        else:  # 自己摸出杠牌
            card_dict = AI2.read_hands_from_dict(card_list)
            print(f"GANG CHOICE: {card_dict} GANG CARD: {card_list[-1]}")
            table_dict = AI2.read_cards_from_table(table_card)
            before_res = AI2.put_judgment(card_dict,
                                          appear_card=AI2.append_cards(copy.deepcopy(card_dict), table_dict))
            before_efficient_num = before_res[0]['efficient num']
            before_hu_num = AI2.seq_num_judgment(card_dict)['hu num']
            print(f'BEFORE: {before_hu_num}, BEFORE NUM: {before_efficient_num}')

            # 提取杠牌列表
            gang_card_id_list = []
            k_4_list = self.manager.loop_k(card_list, k_count=4, l_cls=[])
            for k_4_cls_num in range(len(k_4_list['cls'])):
                gang_card_id_list = k_4_list['id'][k_4_cls_num]
                break

            # 获取杠牌后分数
            new_card_list = copy.deepcopy(card_list)
            new_table_card = copy.deepcopy(table_card)  # 没碰牌之前的牌河
            new_player_list = copy.deepcopy(self.manager.player_list)
            new_card_list = self.manager.remove_card_by_id(new_card_list, gang_card_id_list)
            new_card_dict = AI2.read_hands_from_dict(new_card_list)
            new_table_dict = AI2.read_cards_from_table(self.manager.table_card)
            self.manager.move_card_to_gang(gang_card_id_list, 1)
            after_res = AI2.card_looper(new_card_dict,
                                        appear_card=AI2.append_cards(copy.deepcopy(new_card_dict), new_table_dict))
            after_efficient_num_2 = after_res[1]
            after_hu_num_2 = AI2.seq_num_judgment(new_card_dict)['hu num']
            print(f'AFTER GANG: {after_hu_num_2}, AFTER GANG: {after_efficient_num_2}')
            self.manager.table_card = new_table_card  # 使manager牌河返回到没碰之前的状态
            self.manager.player_list = new_player_list

            if after_hu_num_2 > before_hu_num:
                return 'guo'
            elif after_hu_num_2 == before_hu_num:
                if after_efficient_num_2 >= before_efficient_num:
                    return 'gang'
                else:
                    return 'guo'

    def get_type_count(self, card_list):
        type_list = {
            'win_type': self.manager.judge(card_list)['type'],
            'ks': self.manager.loop_ks(card_list),
            'l': len(self.manager.loop_l(card_list)['cls']),
            'k_2': len(self.manager.loop_k(card_list, k_count=2, l_cls=[])['cls']),
            'k_3': len(self.manager.loop_k(card_list, k_count=3, l_cls=[])['cls']),
            'k_4': len(self.manager.loop_k(card_list, k_count=4, l_cls=[])['cls']),
            's_2_1': len(self.manager.loop_s_2(card_list)['cls_1']),
            's_2_2': len(self.manager.loop_s_2(card_list)['cls_2']),
            's_3': len(self.manager.loop_s(card_list)['cls'])
        }
        return type_list

    def get_score(self, card_list, table_card):
        available_card_list = self.get_available_card(card_list, table_card)
        score_a = 0
        type_list = self.get_type_count(card_list)
        score_1 = get_type_score(type_list)
        last_avi_cls = 0
        for avi_card in available_card_list:
            if avi_card['cls'] == last_avi_cls:
                score_a += score_2 - score_1
                continue
            card_list.append(avi_card)
            type_list_2 = self.get_type_count(card_list)
            score_2 = get_type_score(type_list_2)

            score_a += score_2 - score_1
            card_list.remove(avi_card)
            last_avi_cls = avi_card['cls']
        score = score_a / len(available_card_list)
        return score
