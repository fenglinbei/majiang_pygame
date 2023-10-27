import copy
import random

base_list = ["wan", "tong", "suo"]
feng_list = ["dong", "nan", "xi", "bei", "zhong", "fa", "bai"]
hua_list = ["chun", "xia", "qiu", "dong", "mei", "lan", "zhu", "ju"]
PLAYER_LIST = {1: {'name': "dong", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               2: {'name': "nan", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               3: {'name': "xi", 'now_card': [], 'put_card': {'p': [], 'g': []}},
               4: {'name': "bei", 'now_card': [], 'put_card': {'p': [], 'g': []}}}


class Manager:

    def __init__(self, table=None, mode=0):
        self.mode = mode
        self.card = []
        self.player_list = PLAYER_LIST
        self.table_card = copy.deepcopy(PLAYER_LIST)
        self.last_card_id = 0
        self.table = table
        self.peng_card = None
        self.last_put = 0
        self.last_player = 0
        self.peng_player = 0
        self.pg_state_list = []
        self.ks_look_count = 0
        self.last_winner = 1

    def create_card(self):
        # 创建一副完整的牌
        id = 0
        cls = 0
        card = []
        for base in base_list:
            for i in range(1, 10):
                cls += 1
                for j in range(1, 5):
                    id += 1
                    card.append({'name': base, 'num': i, 'count': j, 'cls': cls, 'id': id})
        if self.mode == 0:
            for feng in feng_list:
                cls += 1
                for j in range(1, 5):
                    id += 1
                    card.append({'name': feng, 'num': 0, 'count': j, 'cls': cls, 'id': id})
        else:
            for feng in feng_list:
                cls += 1
                for j in range(1, 5):
                    id += 1
                    card.append({'name': feng, 'num': 0, 'count': j, 'cls': cls, 'id': id})
            for hua in hua_list:
                cls += 1
                id += 1
                card.append({'name': hua, 'num': 0, 'count': j, 'cls': cls, 'id': id})
        return card

    def reset(self):
        self.card = []
        self.card = self.create_card()
        self.player_list = copy.deepcopy(PLAYER_LIST)
        self.table_card = copy.deepcopy(PLAYER_LIST)
        self.send_card()

    def send_card(self):
        # 发牌
        if self.mode == 0:
            if len(self.card) == 136:
                random.shuffle(self.card)
                c = 13
            else:
                raise Exception("card is not reset!")
        else:
            if len(self.card) == 144:
                random.shuffle(self.card)
                c = 13
            else:
                raise Exception("card is not reset!")
        for player_id in self.player_list:
            self.player_list[player_id]["now_card"] = self.card[c - 13:c]
            c += 13
        c -= 13
        self.card = self.card[c:]
        return True

    def draw_card(self, player, printer):
        self.player_list[player]["now_card"].append(self.card[0])
        self.card.remove(self.card[0])
        printer.read_card(self.player_list, self.table_card)
        printer.load_card(14)

    def tidy_card(self, player_list):
        # 整理手牌
        for player in player_list:
            cards = player_list[player]["now_card"]
            id_list = []
            for card in cards:
                id_list.append(card['id'])
            player_list[player]["now_card"].sort(key=lambda cards: cards.get("id"))

        return player_list

    def tidy_card_player(self, card_list):
        id_list = []
        for card in card_list:
            id_list.append(card['id'])
        card_list.sort(key=lambda cards: cards.get("id"))
        return card_list

    def id_to_cls(self, card_id):
        return (card_id - 1) // 4 + 1

    def get(self, card_id):
        card_list = self.create_card()
        for card in card_list:
            if card_id == card['id']:
                return card
        return {'name': '', 'num': 0, 'count': 0, 'cls': 0, 'id': 0}

    def loop_l(self, card_list):
        l_count_cls = []
        l_count_id = []
        for card_count in range(len(card_list)):
            # 癞子统计
            if 34 < card_list[card_count]['cls'] < 43:
                l_count_id.append(card_list[card_count]['id'])
                l_count_cls.append(card_list[card_count]['cls'])
        return {'cls': l_count_cls, 'id': l_count_id}

    def loop_s(self, card_list):
        find_next = False
        s_count_cls = []
        s_count_id = []
        id_list = []

        for card_count in range(len(card_list)):

            # 跳过字牌
            if 27 < card_list[card_count]['cls'] < 35:
                continue

            cls = card_list[card_count]['cls']
            _id = card_list[card_count]['id']
            name = card_list[card_count]['name']
            s_list_cls = [cls]
            s_list_id = [_id]
            id_sum = _id  # 作为每一组顺子的标识符
            last_id = 0

            # x-2,x-1,x
            for j in [1, 2]:
                for i in range(len(card_list)):
                    now_cls = card_list[i]['cls']
                    now_id = card_list[i]['id']
                    now_name = card_list[i]['name']
                    tar_cls = cls - j
                    if (now_cls == tar_cls and now_name == name) or (
                            now_cls > 34 and now_id != last_id and now_id != _id):
                        s_list_cls.append(now_cls)
                        s_list_id.append(now_id)
                        id_sum += now_id
                        find_next = True
                        last_id = now_id
                        break
                    if not find_next:
                        break
            if len(s_list_cls) != 3:
                s_list_cls = []
                s_list_id = []
                id_sum = 0
                find_next = False
                last_id = 0
            elif len(s_list_cls) == 3 and id_sum not in id_list:
                s_count_cls.append(list(reversed(s_list_cls)))
                s_count_id.append(list(reversed(s_list_id)))
                id_list.append(id_sum)
                s_list_cls = []
                s_list_id = []
                id_sum = 0
                find_next = False
                last_id = 0
            else:
                s_list_cls = []
                s_list_id = []
                id_sum = 0
                find_next = False
                last_id = 0

            # x-1,x,x+1
            for i in range(len(card_list)):
                now_cls = card_list[i]['cls']
                now_id = card_list[i]['id']
                now_name = card_list[i]['name']
                tar_cls = cls - 1
                if (now_cls == tar_cls and now_name == name) or (now_cls > 34 and now_id not in s_list_id):
                    s_list_cls.append(now_cls)
                    s_list_id.append(now_id)
                    id_sum += now_id
                    find_next = True
                    last_id = now_id
                    break
            if find_next:
                s_list_cls.append(cls)
                s_list_id.append(_id)
                id_sum += _id
                for i in range(len(card_list)):
                    now_cls = card_list[i]['cls']
                    now_id = card_list[i]['id']
                    now_name = card_list[i]['name']
                    tar_cls = cls + 1
                    if (now_cls == tar_cls and now_name == name) or (
                            now_cls > 34 and now_id not in s_list_id):
                        s_list_cls.append(now_cls)
                        s_list_id.append(now_id)
                        id_sum += now_id
                        break
            if len(s_list_cls) != 3:
                s_list_cls = [cls]
                s_list_id = [_id]
                id_sum = _id
                last_id = 0
            elif len(s_list_cls) == 3 and id_sum not in id_list:
                s_count_cls.append(s_list_cls)
                s_count_id.append(s_list_id)
                id_list.append(id_sum)
                s_list_cls = [cls]
                s_list_id = [_id]
                id_sum = _id
                last_id = 0
            else:
                s_list_cls = [cls]
                s_list_id = [_id]
                id_sum = _id
                find_next = False
                last_id = 0

            # x,x+1,x+2
            for j in [1, 2]:
                for i in range(len(card_list)):
                    now_cls = card_list[i]['cls']
                    now_id = card_list[i]['id']
                    now_name = card_list[i]['name']
                    tar_cls = cls + j
                    if (now_cls == tar_cls and now_name == name) or (
                            now_cls > 34 and now_id not in s_list_id):
                        s_list_cls.append(now_cls)
                        s_list_id.append(now_id)
                        id_sum += now_id
                        find_next = True
                        last_id = now_id
                        break
                if not find_next:
                    break
            if len(s_list_cls) == 3 and id_sum not in id_list:
                s_count_cls.append(s_list_cls)
                s_count_id.append(s_list_id)
                id_list.append(id_sum)

        return {'cls': s_count_cls, 'id': s_count_id}

    def loop_s_2(self, card_list):
        s_2_count_id_1 = []
        s_2_count_id_2 = []
        id_list = []

        for card_count in range(len(card_list)):

            # 跳过字牌
            if 27 < card_list[card_count]['cls'] < 35:
                continue

            cls = card_list[card_count]['cls']
            _id = card_list[card_count]['id']
            name = card_list[card_count]['name']
            s_list_id = [_id]
            id_sum = _id  # 作为每一组顺子的标识符

            for i in range(len(card_list)):
                now_cls = card_list[i]['cls']
                now_id = card_list[i]['id']
                now_name = card_list[i]['name']
                tar_cls = cls - 1
                if now_cls == tar_cls and now_name == name:
                    s_list_id.append(now_id)
                    id_sum += now_id
                    break

            if len(s_list_id) == 2 and id_sum not in id_list:
                s_2_count_id_1.append(list(reversed(s_list_id)))
                id_list.append(id_sum)

        for card_count in range(len(card_list)):

            # 跳过字牌
            if 27 < card_list[card_count]['cls'] < 35:
                continue

            cls = card_list[card_count]['cls']
            _id = card_list[card_count]['id']
            name = card_list[card_count]['name']
            s_list_id = [_id]
            id_sum = _id  # 作为每一组顺子的标识符

            for i in range(len(card_list)):
                now_cls = card_list[i]['cls']
                now_id = card_list[i]['id']
                now_name = card_list[i]['name']
                tar_cls = cls - 2
                if now_cls == tar_cls and now_name == name:
                    s_list_id.append(now_id)
                    id_sum += now_id
                    break

            if len(s_list_id) == 2 and id_sum not in id_list:
                s_2_count_id_2.append(list(reversed(s_list_id)))
                id_list.append(id_sum)

        return {'cls_1': s_2_count_id_1, 'cls_2': s_2_count_id_2}

    def loop_k(self, card_list, k_count=3, l_cls=None):
        if l_cls is None:
            l_cls = list(range(35, 43))
        k_count_cls = []
        k_count_id = []
        id_list = []

        for card_count in range(len(card_list)):
            cls = card_list[card_count]['cls']
            _id = card_list[card_count]['id']
            k_list_cls = [cls]
            k_list_id = [_id]
            last_id = _id

            for j in range(k_count - 1):
                for i in range(len(card_list)):
                    now_cls = card_list[i]['cls']
                    now_id = card_list[i]['id']
                    tar_cls = cls
                    if (now_cls == tar_cls and now_id not in k_list_id) \
                            or (now_cls in l_cls and now_id not in k_list_id):
                        k_list_cls.append(now_cls)
                        k_list_id.append(now_id)
                        last_id = now_id
                        break
            if len(k_list_cls) == k_count and sum(k_list_id) not in id_list:
                k_count_cls.append(list(reversed(k_list_cls)))
                k_count_id.append(list(reversed(k_list_id)))
                id_list.append(sum(k_list_id))

        return {'cls': k_count_cls, 'id': k_count_id}

    def remove_card_by_id(self, ori_card_list, rm_card_list_by_id):
        for card_id in rm_card_list_by_id:
            for card in ori_card_list:
                if card['id'] == card_id:
                    ori_card_list.remove(card)
                    break
        return ori_card_list

    def move_card_to_table(self, move_id):
        card = self.table.get(move_id)
        flag = True
        remove_card = None
        for p in self.player_list:
            for c in self.player_list[p]['now_card']:
                if card.id == c['id']:
                    remove_card = c
                    flag = False
                    break
            if not flag:
                break
        self.player_list[card.player]['now_card'].remove(remove_card)
        self.table_card[card.player]['now_card'].append(remove_card)
        self.peng_card = remove_card

    def move_card_to_peng(self, move_id_list, player):
        for move_id in move_id_list:
            for p in self.player_list:
                for card in self.player_list[p]['now_card']:
                    if move_id == card['id']:
                        self.player_list[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['p'].append(card)
                        self.table_card[player]['put_card']['p'].append(card)

        for p in self.table_card:
            for card in self.table_card[p]['now_card']:
                if card['id'] in move_id_list:
                    self.table_card[p]['now_card'].remove(card)
                    self.player_list[player]['put_card']['p'].append(card)
                    self.table_card[player]['put_card']['p'].append(card)
                    return

    def move_card_to_gang(self, move_id_list, player):
        for move_id in move_id_list:
            for p in self.player_list:
                for card in self.player_list[p]['now_card']:
                    if move_id == card['id']:
                        self.player_list[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)

                for card in self.player_list[p]['put_card']['p']:
                    if move_id == card['id']:
                        self.player_list[p]['put_card']['p'].remove(card)
                        self.table_card[player]['put_card']['p'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)

            for p in self.table_card:
                for card in self.table_card[p]['now_card']:
                    if move_id == card['id']:
                        self.table_card[p]['now_card'].remove(card)
                        self.player_list[player]['put_card']['g'].append(card)
                        self.table_card[player]['put_card']['g'].append(card)

    def loop_ks(self, card_list):
        self.ks_look_count += 1
        k_s_count = 0

        def remove_card_by_count_id(ori_card_list):
            count_id = self.loop_s(ori_card_list)['id'] + self.loop_k(ori_card_list)['id']
            card_list_list_after_rm = []
            # 截取
            for sk_3 in count_id:
                card_list_after_rm = self.remove_card_by_id(copy.deepcopy(ori_card_list), sk_3)
                count_id_after_rm = self.loop_s(card_list_after_rm)['id'] + self.loop_k(card_list_after_rm)['id']
                if len(count_id_after_rm) > 0:
                    card_list_list_after_rm.append(card_list_after_rm)
            return card_list_list_after_rm

        count_id = self.loop_s(card_list)['id'] + self.loop_k(card_list)['id']
        if len(count_id) > 0:
            k_s_count = 1
        else:
            return k_s_count
        # 第一步提取
        first_card_list = remove_card_by_count_id(card_list)
        if len(first_card_list) > 0:
            k_s_count = 2
        else:
            return k_s_count

        # 第二步提取
        sec_card_lists = []
        sec_card_list = []
        for first_cards in first_card_list:
            sec_cards = remove_card_by_count_id(first_cards)
            if len(sec_cards) > 0:
                sec_card_lists.append(sec_cards)
        if len(sec_card_lists) > 0:
            for a in sec_card_lists:
                for b in a:
                    sec_card_list.append(b)
            k_s_count = 3
        else:
            return k_s_count
        # 第三步提取
        third_card_lists = []
        third_card_list = []
        for sec_cards in sec_card_list:
            third_cards = remove_card_by_count_id(sec_cards)
            if len(third_cards) > 0:
                third_card_lists.append(third_cards)
        if len(third_card_lists) > 0:
            for a in third_card_lists:
                for b in a:
                    third_card_list.append(b)
            k_s_count = 4
        return k_s_count

    def judge(self, card_list):
        # 胡牌判定
        eye_count = self.loop_k(card_list, k_count=2)
        max_count = 0
        is_win = False
        judgement = {'is_win': False, 'type': 0, 'count': max_count}
        for eyes in eye_count['id']:
            card_list_after_rm_eye = self.remove_card_by_id(copy.deepcopy(card_list), eyes)
            all_count = self.loop_ks(copy.deepcopy(card_list_after_rm_eye))
            if all_count >= max_count:
                max_count = all_count
            if all_count * 3 == len(card_list_after_rm_eye):
                is_win = True
                judgement = {'is_win': True, 'type': 1, 'count': all_count}
                break

        if is_win:
            return judgement
        else:
            judgement = {'is_win': False, 'type': 0, 'count': max_count}
            return judgement

    def check_state(self, card_id, card_list):
        state_list = []
        card = self.get(card_id)
        card_list['now_card'].append(card)
        k_count = self.loop_k(card_list['now_card'] + card_list['put_card']['p'], k_count=4, l_cls=[])
        if len(k_count['cls']) > 0:
            state_list.append('gang')
        if self.judge(card_list['now_card'])['is_win']:
            state_list.append('hu')
        return state_list

    def set_turn(self, put_id, player_id):
        self.pg_state_list = ['guo']
        self.last_put = put_id
        self.last_player = player_id
        put_cls = self.id_to_cls(put_id)
        for player in self.player_list:
            if player == player_id:
                continue
            k_2_list = self.loop_k(self.player_list[player]['now_card'], k_count=2, l_cls=[])['cls']
            k_3_list = self.loop_k(self.player_list[player]['now_card'], k_count=3, l_cls=[])['cls']
            for counts_k_2 in k_2_list:
                if put_cls in counts_k_2:
                    for count_k_3 in k_3_list:
                        if put_cls in count_k_3:
                            self.pg_state_list.append('peng')
                            self.pg_state_list.append('gang')
                            self.peng_player = player
                            return
                    self.pg_state_list.append('peng')
                    self.peng_player = player
                    return
