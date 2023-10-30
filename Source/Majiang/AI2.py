import time
import copy


def print_time(f):
    """Decorator of viewing function runtime.
    eg:
        ```py
        from print_time import print_time as pt
        @pt
        def work(...):
            print('work is running')
        word()
        # work is running
        # --> RUN TIME: <work> : 2.8371810913085938e-05
        ```
    """

    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %.4f' % (f.__name__, time.time() - s))
        return res

    return fi


# @print_time
def read_hands(hands: str):
    hands_dict = {'m': [], 'p': [], 's': [], 'z': []}
    while len(hands) > 0:
        m_card = hands.split('m', 1)
        p_card = hands.split('p', 1)
        s_card = hands.split('s', 1)
        z_card = hands.split('z', 1)
        if not [False for t in ['p', 's', 'z'] if t in m_card[0]] and len(m_card) > 1:
            for num in m_card[0]:
                hands_dict['m'].append(int(num))
            hands = m_card[1]

        elif not [False for t in ['m', 's', 'z'] if t in p_card[0]] and len(p_card) > 1:
            for num in p_card[0]:
                hands_dict['p'].append(int(num))
            hands = p_card[1]

        elif not [False for t in ['m', 'p', 'z'] if t in s_card[0]] and len(s_card) > 1:
            for num in s_card[0]:
                hands_dict['s'].append(int(num))
            hands = s_card[1]

        elif not [False for t in ['m', 'p', 's'] if t in z_card[0]] and len(z_card) > 1:
            for num in z_card[0]:
                hands_dict['z'].append(int(num))
            hands = z_card[1]
    for t in ['m', 'p', 's', 'z']:
        hands_dict[t].sort()
    return hands_dict


def read_hands_from_dict(hands: list) -> dict:
    hands_dict = {'m': [], 'p': [], 's': [], 'z': []}
    for card_dict in hands:
        if card_dict['cls'] < 10:
            card = {'m': [card_dict['num']]}
        elif 10 <= card_dict['cls'] < 19:
            card = {'p': [card_dict['num']]}
        elif 19 <= card_dict['cls'] < 28:
            card = {'s': [card_dict['num']]}
        elif 28 <= card_dict['cls'] < 35:
            num = ['dong', 'nan', 'xi', 'bei', 'bai', 'fa', 'zhong'].index(card_dict['name']) + 1
            card = {'z': [num]}
        else:
            card = {'f': [card_dict['num']]}
        append_cards(hands_dict, card)
    return hands_dict


def read_cards_from_table(table: dict) -> dict:
    tables_dict = {'m': [], 'p': [], 's': [], 'z': []}
    for player in table.values():
        for card_dict in player['now_card']:
            if card_dict['cls'] < 10:
                card = {'m': [card_dict['num']]}
            elif 10 <= card_dict['cls'] < 19:
                card = {'p': [card_dict['num']]}
            elif 19 <= card_dict['cls'] < 28:
                card = {'s': [card_dict['num']]}
            elif 28 <= card_dict['cls'] < 35:
                num = ['dong', 'nan', 'xi', 'bei', 'bai', 'fa', 'zhong'].index(card_dict['name']) + 1
                card = {'z': [num]}
            else:
                card = {'f': [card_dict['num']]}
            append_cards(tables_dict, card)

        for card_dict in player['put_card']['p']:
            if card_dict['cls'] < 10:
                card = {'m': [card_dict['num']]}
            elif 10 <= card_dict['cls'] < 19:
                card = {'p': [card_dict['num']]}
            elif 19 <= card_dict['cls'] < 28:
                card = {'s': [card_dict['num']]}
            else:
                num = ['dong', 'nan', 'xi', 'bei', 'bai', 'fa', 'zhong'].index(card_dict['name']) + 1
                card = {'z': [num]}
            append_cards(tables_dict, card)

        for card_dict in player['put_card']['g']:
            if card_dict['cls'] < 10:
                card = {'m': [card_dict['num']]}
            elif 10 <= card_dict['cls'] < 19:
                card = {'p': [card_dict['num']]}
            elif 19 <= card_dict['cls'] < 28:
                card = {'s': [card_dict['num']]}
            else:
                num = ['dong', 'nan', 'xi', 'bei', 'bai', 'fa', 'zhong'].index(card_dict['name']) + 1
                card = {'z': [num]}
            append_cards(tables_dict, card)
    return tables_dict


# @print_time
def sequence_extract_by_list(cards: list, seq_num: int = 3, first_card_ban: list = None):
    seq = []
    if first_card_ban is None:
        first_card_ban = []
    if len(cards) < seq_num:
        return cards, [], [], False
    for card in cards:
        first_card = card
        if card in first_card_ban:
            continue
        if seq_num == 3:
            if (first_card + 1 in cards and first_card + 2 in cards) and (
                    first_card + 1 not in first_card_ban and first_card + 2 not in first_card_ban):
                seq.append([])
                seq[-1].append(first_card)
                seq[-1].append(first_card + 1)
                seq[-1].append(first_card + 2)
                cards.remove(first_card)
                cards.remove(first_card + 1)
                cards.remove(first_card + 2)
                return cards, seq, first_card, True
        else:
            if first_card + 1 in cards:
                seq.append([])
                seq[-1].append(first_card)
                seq[-1].append(first_card + 1)
                cards.remove(first_card)
                cards.remove(first_card + 1)
                return cards, seq, first_card, True
            elif first_card + 2 in cards:
                seq.append([])
                seq[-1].append(first_card)
                seq[-1].append(first_card + 2)
                cards.remove(first_card)
                cards.remove(first_card + 2)
                return cards, seq, first_card, True
    return cards, seq, None, False


# @print_time
def pair_extract(hands: dict, pair_num: int = 2, first_card_ban: dict = None):
    sequence = {'m': [], 'p': [], 's': [], 'z': []}
    if first_card_ban is None:
        first_card_ban = {}
    for t in hands:
        cards = hands[t]
        if len(cards) < pair_num:
            continue
        for card in cards:
            first_card = card
            if t in first_card_ban and first_card in first_card_ban[t]:
                continue
            cards_copy = cards.copy()
            cards_copy.remove(first_card)
            if first_card in cards_copy:
                if pair_num > 2:
                    cards_copy.remove(first_card)
                    if pair_num > 3:
                        cards_copy.remove(first_card)
                        if first_card in cards_copy:
                            sequence[t].extend([first_card, first_card, first_card, first_card])
                            hands = remove_cards(hands, sequence)
                            return hands, sequence, {t: [first_card]}, True
                    if first_card in cards_copy:
                        sequence[t].extend([first_card, first_card, first_card])
                        hands = remove_cards(hands, sequence)
                        return hands, sequence, {t: [first_card]}, True
                if first_card in cards_copy:
                    sequence[t].extend([first_card, first_card])
                    hands = remove_cards(hands, sequence)
                    return hands, sequence, {t: [first_card]}, True
    return hands, sequence, {}, False


# @print_time
def pair_extract_by_list(cards: list, pair_num: int = 3, first_card_ban: list = None):
    seq = []
    if first_card_ban is None:
        first_card_ban = []
    if len(cards) < pair_num:
        return cards, [], [], False
    for card in cards:
        first_card = card
        if first_card in first_card_ban:
            continue
        cards_copy = cards.copy()
        cards_copy.remove(first_card)
        if first_card in cards_copy:
            if pair_num > 2:
                cards_copy.remove(first_card)
                if pair_num > 3:
                    cards_copy.remove(first_card)
                    if first_card in cards_copy:
                        seq.append([])
                        seq[-1].extend([first_card, first_card, first_card, first_card])
                        cards.remove(first_card)
                        cards.remove(first_card)
                        cards.remove(first_card)
                        cards.remove(first_card)
                        return cards, seq, first_card, True
                if first_card in cards_copy:
                    seq.append([])
                    seq[-1].extend([first_card, first_card, first_card])
                    cards.remove(first_card)
                    cards.remove(first_card)
                    cards.remove(first_card)
                    return cards, seq, first_card, True
            if first_card in cards_copy:
                seq.append([])
                seq[-1].extend([first_card, first_card])
                cards.remove(first_card)
                cards.remove(first_card)
                return cards, seq, first_card, True
    return cards, seq, [], False


# @print_time
def hu_judgment(hands: dict):
    for t in ['m', 'p', 's', 'z']:
        hands[t].sort()
    head_counter = {'m': [], 'p': [], 's': [], 'z': []}
    flag = True
    max_seqs = 0
    res_seqs = []
    res_left_hands = []
    while flag:
        left_cards = copy.deepcopy(hands)
        seq_counter = 0
        seqs = {'m': [], 'p': [], 's': [], 'z': [], 'head': {'m': [], 'p': [], 's': [], 'z': []}}
        left_hands = {'m': [], 'p': [], 's': [], 'z': []}
        left_cards, seq, head_card, flag = pair_extract(left_cards, 2, head_counter)  # find head
        if flag:
            append_cards(seqs['head'], seq)
            append_cards(head_counter, head_card)
            seq_counter += 1
            for t in left_cards:
                res = get_max_seq(left_cards[t], t)
                seqs[t] = res[1]
                seq_counter += res[2]
                left_hands[t] = res[0]
        if seq_counter >= max_seqs:
            max_seqs = seq_counter
            res_seqs.append(seqs)
            res_left_hands.append(left_hands)

    return res_left_hands, res_seqs, max_seqs, 5 - max_seqs


# @print_time
def seq_num_judgment(hands: dict) -> dict:
    for t in ['m', 'p', 's', 'z']:
        hands[t].sort()
    left_cards = copy.deepcopy(hands)
    seq_1, seq_2 = 0, 0
    pair_1, pair_2 = 0, 0
    card_num = card_counter(hands)
    card_num = card_num if (card_num - 2) % 3 == 0 else card_num + 1
    init_seq = 2 * ((card_num - 2) // 3)
    seqs = {'m': [], 'p': [], 's': [], 'z': []}
    pairs = {'m': [], 'p': [], 's': [], 'z': []}
    res_left_hands = {'m': [], 'p': [], 's': [], 'z': []}
    for t in left_cards:
        res = get_max_seq(left_cards[t], t)
        res_reverse = get_max_seq_reverse(left_cards[t], t)
        if res != res_reverse:
            if res['seq num'] > res_reverse['seq num']:
                res = res
            elif res['seq num'] == res_reverse['seq num']:
                res = res if res['pair num 2'] > res_reverse['pair num 2'] else res_reverse
            else:
                res = res_reverse
        seqs[t] = res['seq']
        seq_1 += res['seq num 1']
        seq_2 += res['seq num 2']
        res_left_hands[t] = res['left hand']

    left_hands = copy.deepcopy(res_left_hands)
    for t in left_hands:
        res = get_max_pair(left_hands[t], t)
        res_reverse = get_max_pair_reverse(left_hands[t], t)
        if res != res_reverse:
            res = res if res['pair num 2'] > res_reverse['pair num 2'] else res_reverse
        pairs[t] = res['pair']
        pair_1 += res['pair num 1']
        pair_2 += res['pair num 2']
        # res_left_hands[t] = res['left hand']

    seq = seq_1 + seq_2
    k = (14 - card_num) // 3
    if pair_2 > 0:
        if seq == 1:
            pair = (pair_1 + pair_2) if (pair_1 + pair_2) < 5 - k else 4 - k
        elif seq == 2:
            pair = (pair_1 + pair_2) if (pair_1 + pair_2) < 4 - k else 3 - k
        elif seq >= 3:
            pair = pair_1 + pair_2
        else:
            pair = (pair_1 + pair_2) if (pair_1 + pair_2) < 6 - k else 5 - k

        seq_num = init_seq - 2 * seq - pair
    else:
        if seq == 1:
            pair = pair_1 if pair_1 < 4 - k else 3 - k
        elif seq == 2:
            pair = pair_1 if pair_1 < 3 - k else 2 - k
        elif seq == 3:
            pair = pair_1 if pair_1 < 2 - k else 1 - k
        elif seq > 3:
            pair = 0
        else:
            pair = pair_1 if pair_1 < 5 - k else 4 - k

        seq_num = init_seq - 2 * seq - pair
        if seq_num < 0:
            seq_num = 0

    return {'hu num': seq_num, 'left hand': res_left_hands,
            'seq': seqs, 'seq num 1': seq_1, 'seq num 2': seq_2, 'seq num': seq_1 + seq_2,
            'pair': pairs, 'pair num 1': pair_1, 'pair num 2': pair_2, 'pair num': pair_1 + pair_2}


def card_looper(hands: dict, appear_card: dict):
    res = seq_num_judgment(hands)
    hands_copy = copy.deepcopy(hands)
    efficient_card = {'m': [], 'p': [], 's': [], 'z': []}
    for t in ['m', 'p', 's', 'z']:
        if t != 'z':
            k = 10
        else:
            k = 8
        for i in range(1, k):

            card = {t: [i]}
            append_cards(hands_copy, card)
            ap_res = seq_num_judgment(hands_copy)
            if ap_res['hu num'] < res['hu num']:
                append_cards(efficient_card, card)
            remove_cards(hands_copy, card)
    return efficient_card, left_card_counter(efficient_card, appear_card)


def card_looper_2(hands: dict, appear_card: dict, best_efficient_num: int):
    res = best_efficient_num + 1
    seq_res = seq_num_judgment(hands)
    hands_copy = copy.deepcopy(hands)
    efficient_card = {'m': [], 'p': [], 's': [], 'z': []}
    for t in ['m', 'p', 's', 'z']:
        if t != 'z':
            k = 10
        else:
            k = 8
        for i in range(1, k):

            card = {t: [i]}
            append_cards(hands_copy, card)
            ap_res = put_judgment_1(hands_copy, appear_card)
            ap_res = ap_res[0]['efficient num']
            ap_res_seq = seq_num_judgment(hands_copy)
            if ap_res_seq['hu num'] < seq_res['hu num']:
                remove_cards(hands_copy, card)
                continue
            if ap_res > res:
                append_cards(efficient_card, card)
            remove_cards(hands_copy, card)
    return efficient_card, left_card_counter(efficient_card, appear_card)


# @print_time
def put_judgment_1(hands: dict, appear_card: dict = None):
    # print(f'PUT JUDGMENT INPUT CARD: {hands} LENGTH: {card_counter(hands)}')
    if appear_card is None:
        appear_card = {'m': [], 'p': [], 's': [], 'z': []}
    if (card_counter(hands) - 2) % 3 == 0:
        before_res = seq_num_judgment(hands)
        if before_res['hu num'] == -1:
            left_hands = hands
            seq = before_res['hu num'] + 1
        else:
            left_hands = before_res['left hand']
            seq = before_res['hu num']
        after_put_hands = copy.deepcopy(hands)
        res = []
        last_put = {}
        for t in left_hands:
            if len(left_hands[t]) > 0:
                for card in left_hands[t]:
                    put_card = {t: [card]}
                    if put_card == last_put:
                        continue
                    last_put = put_card
                    remove_cards(after_put_hands, put_card)
                    after_res = seq_num_judgment(after_put_hands)
                    if after_res['hu num'] > seq:
                        append_cards(after_put_hands, put_card)
                        continue
                    loop_res = card_looper(after_put_hands, appear_card)
                    put_res = {'put': put_card, 'efficient card': loop_res[0], 'efficient num': loop_res[1]}
                    res.append(put_res)
                    append_cards(after_put_hands, put_card)
        return sorted(res, key=lambda x: x['efficient num'], reverse=True)
    return []


@print_time
def put_judgement_2(judgement_1_res: list, hands: dict, appear_card: dict) -> list:
    max_list = []
    res_list = []
    max_efficient_num = max(judgement_1_res, key=lambda x: x['efficient num'])['efficient num']
    for res in judgement_1_res:
        if res['efficient num'] == max_efficient_num:
            max_list.append(res)
        else:
            break

    if len(max_list) == 1 or seq_num_judgment(hands)['hu num'] > 2:
        return max_list
    else:
        for res in max_list:
            put_card = res['put']
            after_put = copy.deepcopy(hands)
            remove_cards(after_put, put_card)
            after_res = card_looper_2(after_put, appear_card=appear_card, best_efficient_num=max_efficient_num)
            put_res = {'put': put_card, 'efficient card': after_res[0], 'efficient num': after_res[1]}
            res_list.append(put_res)
        return sorted(res_list, key=lambda x: x['efficient num'], reverse=True)


def put_judgment(hands: dict, appear_card: dict = None):
    judgment_1 = put_judgment_1(hands, appear_card)
    judgment_2 = put_judgement_2(judgment_1, hands, appear_card)
    if len(judgment_2) == 1:
        return judgment_1
    else:
        return [judgment_2[0]]


# @print_time
def remove_cards(hands: dict, cards: dict):
    for t in cards:
        if t == 'head':
            continue
        if len(cards[t]) < 1:
            continue
        for card in cards[t]:
            hands[t].remove(card)
    return hands


# @print_time
def append_cards(hands: dict, cards: dict):
    for t in cards:
        if t == 'head':
            continue
        if len(cards[t]) < 1:
            continue
        for c in cards[t]:
            hands[t].append(c)
    return hands


def get_seq(cards: list, c_type: str, ban_card: list = None, ):
    left_cards = copy.deepcopy(cards)
    seq_counter = []
    seq_1, seq_2 = 0, 0
    first_card_counter = []
    for i in range(4):
        left_cards, seq, first_card, flag = pair_extract_by_list(left_cards, 3)
        if not flag:
            if c_type == 'z':
                flag = False
            else:
                left_cards, seq, first_card, flag = sequence_extract_by_list(left_cards, first_card_ban=ban_card)
            if flag:
                seq_counter.extend(seq)
                first_card_counter.append(first_card)
                seq_1 += 1
        else:
            seq_counter.extend(seq)
            first_card_counter.append(first_card)
            seq_2 += 1
    return {'left hand': left_cards, 'seq': seq_counter,
            'seq num 1': seq_1, 'seq num 2': seq_2, 'seq num': seq_1 + seq_2,
            'first card': first_card_counter}


def get_seq_reverse(cards: list, c_type: str, ban_card: list = None, ):
    left_cards = copy.deepcopy(cards)
    seq_counter = []
    seq_1, seq_2 = 0, 0
    first_card_counter = []
    for i in range(4):
        if c_type == 'z':
            flag = False
        else:
            left_cards, seq, first_card, flag = sequence_extract_by_list(left_cards, first_card_ban=ban_card)
        if not flag:
            left_cards, seq, first_card, flag = pair_extract_by_list(left_cards, 3)
            if flag:
                seq_counter.extend(seq)
                first_card_counter.append(first_card)
                seq_2 += 1
        else:
            seq_counter.extend(seq)
            first_card_counter.append(first_card)
            seq_1 += 1
    return {'left hand': left_cards, 'seq': seq_counter,
            'seq num 1': seq_1, 'seq num 2': seq_2, 'seq num': seq_1 + seq_2,
            'first card': first_card_counter}


def get_pair(cards: list, c_type: str, ban_card: list = None, ) -> dict:
    left_cards = copy.deepcopy(cards)
    seq_counter = []
    pair_1, pair_2 = 0, 0
    first_card_counter = []
    seq = list()
    first_card = int()
    for i in range(6):
        if c_type != 'z':
            left_cards, seq, first_card, flag = sequence_extract_by_list(left_cards, 2, first_card_ban=ban_card)
        else:
            flag = False
        if not flag:
            left_cards, seq, first_card, flag = pair_extract_by_list(left_cards, 2)
            if flag:
                seq_counter.extend(seq)
                first_card_counter.append(first_card)
                pair_2 += 1
            else:
                break
        else:
            seq_counter.extend(seq)
            first_card_counter.append(first_card)
            pair_1 += 1
    return {'left hand': left_cards, 'pair': seq_counter,
            'pair num 1': pair_1, 'pair num 2': pair_2, 'pair num': pair_1 + pair_2,
            'first card': first_card_counter}


def get_pair_reverse(cards: list, c_type: str, ban_card: list = None, ) -> dict:
    left_cards = copy.deepcopy(cards)
    seq_counter = []
    pair_1, pair_2 = 0, 0
    first_card_counter = []
    for i in range(6):
        left_cards, seq, first_card, flag = pair_extract_by_list(left_cards, 2)
        if not flag:
            if c_type == 'z':
                flag = False
            else:
                left_cards, seq, first_card, flag = sequence_extract_by_list(left_cards, 2, first_card_ban=ban_card)
            if flag:
                seq_counter.extend(seq)
                first_card_counter.append(first_card)
                pair_1 += 1
        else:
            seq_counter.extend(seq)
            first_card_counter.append(first_card)
            pair_2 += 1
    return {'left hand': left_cards, 'pair': seq_counter,
            'pair num 1': pair_1, 'pair num 2': pair_2, 'pair num': pair_1 + pair_2,
            'first card': first_card_counter}


# @print_time
def get_max_seq_reverse(cards: list, c_type: str) -> dict:
    fir_res = get_seq_reverse(cards, c_type)
    if fir_res['seq num'] == 0:
        return fir_res
    fir_card = fir_res['first card'][0]
    max_seq = fir_res['seq num']
    max_res = fir_res
    max_pair_2 = get_max_pair(fir_res['left hand'], c_type)['pair num 2']
    for i in range(fir_card, 8):
        ban_card = [i]
        res = get_seq_reverse(cards, c_type, ban_card)
        if res['seq num'] > max_seq:
            max_seq = res['seq num']
            max_res = res
            left_hand = res['left hand']
            max_pair_2 = get_max_pair(left_hand, c_type)['pair num 2']
        elif res['seq num'] == max_seq:
            left_hand = res['left hand']
            pair_2 = get_max_pair(left_hand, c_type)['pair num 2']
            if pair_2 >= max_pair_2:
                max_pair_2 = pair_2
                max_seq = res['seq num']
                max_res = res
    max_res['pair num 2'] = max_pair_2
    return max_res


def get_max_seq(cards: list, c_type: str) -> dict:
    fir_res = get_seq(cards, c_type)
    if fir_res['seq num'] == 0:
        return fir_res
    fir_card = fir_res['first card'][0]
    max_seq = fir_res['seq num']
    max_res = fir_res
    max_pair_2 = get_max_pair(fir_res['left hand'], c_type)['pair num 2']
    for i in range(fir_card, 8):
        ban_card = [i]
        res = get_seq(cards, c_type, ban_card)
        if res['seq num'] > max_seq:
            max_seq = res['seq num']
            max_res = res
            left_hand = res['left hand']
            max_pair_2 = get_max_pair(left_hand, c_type)['pair num 2']
        elif res['seq num'] == max_seq:
            left_hand = res['left hand']
            pair_2 = get_max_pair(left_hand, c_type)['pair num 2']
            if pair_2 >= max_pair_2:
                max_pair_2 = pair_2
                max_seq = res['seq num']
                max_res = res
    max_res['pair num 2'] = max_pair_2
    return max_res


def get_max_pair(cards: list, c_type: str) -> dict:
    fir_res = get_pair(cards, c_type)
    if fir_res['pair num'] == 0:
        return fir_res
    fir_card = fir_res['first card'][0]
    max_seq = fir_res['pair num']
    max_res = fir_res
    max_pair_2 = fir_res['pair num 2']
    for i in range(fir_card, 9):
        ban_card = [i]
        res = get_pair(cards, c_type, ban_card)
        if res['pair num'] > max_seq:
            max_seq = res['pair num']
            max_res = res
        elif res['pair num'] == max_seq:
            if res['pair num 2'] >= max_pair_2:
                max_pair_2 = res['pair num 2']
                max_seq = res['pair num']
                max_res = res
    return max_res


def get_max_pair_reverse(cards: list, c_type: str) -> dict:
    fir_res = get_pair_reverse(cards, c_type)
    if fir_res['pair num'] == 0:
        return fir_res
    fir_card = fir_res['first card'][0]
    max_seq = fir_res['pair num']
    max_res = fir_res
    max_pair_2 = fir_res['pair num 2']
    for i in range(fir_card, 9):
        ban_card = [i]
        res = get_pair_reverse(cards, c_type, ban_card)
        if res['pair num'] > max_seq:
            max_seq = res['pair num']
            max_res = res
        elif res['pair num'] == max_seq:
            if res['pair num 2'] >= max_pair_2:
                max_pair_2 = res['pair num 2']
                max_seq = res['pair num']
                max_res = res
    return max_res


def card_counter(cards: dict) -> int:
    counter = 0
    for t in cards:
        counter += len(cards[t])
    return counter


def left_card_counter(efficient_card: dict, appear_card: dict) -> int:
    init_count = card_counter(efficient_card) * 4
    for t in efficient_card:
        for c in efficient_card[t]:
            for a in appear_card[t]:
                if c == a:
                    init_count -= 1
    return init_count


def print_res(cards: dict, table_cards: dict, res: dict, put_res: dict, put_res_2: dict) -> str:
    hands = '输入手牌为: '
    for t in cards:
        for c in sorted(cards[t]):
            hand = str(c)
            hands += hand
        if len(cards[t]) > 0:
            hands += t
    hands += f' 共 {card_counter(cards)} 枚\n'
    table = '牌河: '
    for t in table_cards:
        for c in sorted(table_cards[t]):
            hand = str(c)
            table += hand
        if len(table_cards[t]) > 0:
            table += t
    table += f' 共 {card_counter(table_cards)} 枚\n'
    hu_num = res['hu num']
    seq_1, seq_2, seq = res['seq num 1'], res['seq num 2'], res['seq num']
    pair_1, pair_2, pair = res['pair num 1'], res['pair num 2'], res['pair num']
    seq_msg = f'向听数: {hu_num}\n' \
              f'面子数: {seq} 顺子数: {seq_1} 刻子数: {seq_2}\n' \
              f'搭子数: {pair} 两面、坎张、边张: {pair_1} 对子: {pair_2}\n'
    put_msg = ''
    if len(put_res) <= 1:
        return hands + table + seq_msg
    for item in put_res:
        c_type = [t for t in ['m', 'p', 's', 'z'] if t in item['put']][0]
        put_card = str(item['put'][c_type][0]) + c_type
        efficient_card = ''
        for t in item['efficient card']:
            for c in item['efficient card'][t]:
                card = str(c) + t
                efficient_card += card + ' '
        msg = f"打出: {put_card} 有效进张为: {efficient_card} 共 {item['efficient num']} 枚\n"
        put_msg += msg

    put_msg_2 = ''
    if len(put_res_2) <= 1:
        return hands + table + seq_msg + put_msg
    for item in put_res_2:
        c_type = [t for t in ['m', 'p', 's', 'z'] if t in item['put']][0]
        put_card = str(item['put'][c_type][0]) + c_type
        efficient_card = ''
        for t in item['efficient card 2']:
            for c in item['efficient card 2'][t]:
                card = str(c) + t
                efficient_card += card + ' '
        msg = f"打出: {put_card} 有效改良进张为: {efficient_card} 共 {item['efficient num']} 枚\n"
        put_msg_2 += msg

    return hands + table + seq_msg + put_msg + put_msg_2


if __name__ == '__main__':
    cards = read_hands('147m258p369s12345z')
    table_cards = read_hands('')
    res_1, res_2 = seq_num_judgment(cards), put_judgment_1(cards,
                                                           appear_card=append_cards(copy.deepcopy(cards), table_cards))
    #res_3 = card_looper(cards, appear_card=append_cards(copy.deepcopy(cards), table_cards))
    #res_4 = put_judgement_2(res_2, cards, appear_card=append_cards(copy.deepcopy(cards), table_cards))
    res_4 = [0]
    print(print_res(cards, table_cards, res_1, res_2, res_4))
