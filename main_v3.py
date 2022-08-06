# 已经完成部分: 发牌， 抢地主  （2022.08.02）
#  出牌（完成）和验证（没写完）  （2022.08.03）
#  验证（完成），出牌逻辑基本完成  （2022.08.06）

# --------本版本更新说明： -----------------------
# 1. 将验证出牌出否合法的逻辑，提取到了 Comparer 类中，防止 Game 类过于臃肿
# 2. 在写 Comparer 类的过程中， 发现了更好用的牌的表示方法，更方便进行牌的统计
# 3. 为了 Game 的出牌逻辑，给 Player 学了人工控制的出牌方法 ， 输入"1 2 3"表示出三张牌， "pass" 表示选择跳过


# ----------牌用字符串表示：（改变数字规则，不再显示花色）
# 普通牌 号码3-13，
# 高级牌12: 14, 15
# 大小王: 103, 104


from random import randint as rand
from collections import Counter


class Comparer():
    def __init__(self) -> None:
        self.type_level_dict = {
            "1": 1,
            "2": 1,
            "3+1": 1,
            "lian": 1,
            "4Z": 2,
            "WZ": 3
        }

    def check_type(self, cards):
        if not cards:
            return
        if self._spe_repr(cards) == (1, 1):
            return "1"  # 单
        elif self._spe_repr(cards) == (2, 2) and all(a < 103 for a in cards):
            return "2"  # 双
        elif self._spe_repr(cards) == (2, 2) and all(a >= 103 for a in cards):
            return "WZ"  # 王炸
        elif self._spe_repr(cards) == (4, 3, 1):
            return "3+1"
        elif self._spe_repr(cards) == (4, 4):
            return "4Z"  # 4炸
        elif self._check_shunzi(cards):
            return "lian"  # 顺子

    def _check_same_type_bigger(self, now_cards, bef_cards):
        # 检验同一个类型的两次出牌，是否后面更大
        def _find_3(ls):
            c = Counter(ls)
            for k, v in c.items():
                if v >= 3:
                    return k
        t1 = self.check_type(now_cards)
        if t1 in ('1', '2', '4Z'):  # 单(11),双(22) 或者 王炸(22 ) #炸弹(44)，
            check_bigger = now_cards[0] > bef_cards[0]
        elif t1 == "3+1":
            check_bigger = _find_3(now_cards) > _find_3(bef_cards)
        elif t1 == "lian":
            check_bigger = min(now_cards) > min(
                bef_cards) and len(now_cards) >= len(bef_cards)
        # print("[check_bigger ans]", check_bigger)
        return check_bigger

    def check_bigger(self, now_cards, bef_cards):
        t1 = self.check_type(now_cards)
        t2 = self.check_type(bef_cards)
        # print("[t1, t2]", t1, t2)

        if t1 == None:  # 如果出的牌不属于任何一种形式
            return False
        if not bef_cards:  # 如果前面没有人出牌
            return True
        
        if t1 == t2:
            return self._check_same_type_bigger(now_cards, bef_cards)
        else:
            return self.type_level_dict[t1] > self.type_level_dict[t2]

    def _check_shunzi(self, cards):
        if len(cards) < 5:
            return False
        cards.sort()
        for d1, d2 in zip(cards[:-1], cards[1:]):
            if d2-d1 != 1:
                break
        else:
            return True
        return False

    def _spe_repr(self, cards):
        chu_len = len(cards)  # 数字总数
        ct = Counter(cards)   # 数字种数
        tmp = list(ct.values())
        tmp.sort(reverse=True)
        return tuple([chu_len, ] + tmp)


class Game():
    def __init__(self):
        self.players = [Player('Z3'), Player('L4'), Player('W5')]  # 三个玩家
        self.players_nums = len(self.players)  # 3
        self.dizhu_cards = []  # 三张底牌
        self.max_dizhu_cost = 8  # 加注的极限，最大值
        self.dizhu_pi = None
        self.dizhu_cost = None
        self.chu_card_error_cost = -2
        self.comparer = Comparer()

    def fapai(self):  # 1发牌
        all_cards = [103, 104]  # 所有的牌
        for i in range(3, 16):
            all_cards.extend([i] * 4)
        # print(len(all_cards))

        for i in range(17):  # 17轮发牌
            for pi in range(3):  # 3 player
                card_i = rand(0, len(all_cards)-1)  # 从已有牌堆中随机选一个索引
                tmp_card = all_cards[card_i]  # 随机牌本身

                self.players[pi].receive_card(tmp_card)  # 玩家获得 tmp_card
                all_cards.remove(tmp_card)  # 牌堆丢掉 tmp_card
        self.dizhu_cards = all_cards.copy()

    def _send_dizhu(self, player_i, cost):
        print("发放底牌给地主：", self.players[player_i].name, ",地主下注:", cost)
        self.players[player_i].get_dizhu = True
        for c in self.dizhu_cards:
            self.players[player_i].receive_card(c)
        self.dizhu_cards = []
        self.dizhu_pi = player_i
        self.dizhu_cost = cost

    def qiangpai(self):  # 2抢牌
        cost = rand(3, 6)  # 随机一个初始的代价
        player_ind = rand(0, 2)  # 随机从一个玩家开始
        last_qiang = None  # 最后抢的人
        buqiang_n = 0  # 不抢的人
        while buqiang_n < 3:
            q = self.players[player_ind].qiang_ma(
                cost, self.max_dizhu_cost)  # 问一个玩家抢不抢
            print("抢吗:", self.players[player_ind].name, q)
            if q and cost < q <= self.max_dizhu_cost:  # 如果枪且是有效的cost
                last_qiang = player_ind
                cost = q
                buqiang_n = 0
            else:
                buqiang_n += 1

            player_ind = (player_ind+1) % 3

        if last_qiang == None:  # 如果没人抢
            pi = rand(0, 2)  # 随机选一个玩家
            self._send_dizhu(pi, cost+1)
        else:
            self._send_dizhu(last_qiang, cost)

    def chupai(self):  # 3 出牌
        used_cards = []
        win_player = None
        player_ind = rand(1, 3)
        bef_cards = None  # 如 (1,1)
        chu_cards_none_times = 0 #在游戏循环中连续跳过的次数
        while len(used_cards) < (13*4+2) and not win_player:  # 当牌没有全部出, 并且没人空牌时候
            player_ind = (player_ind+1) % 3  # 
            if chu_cards_none_times >= 2:  # 如果前面连续两个人跳过，请清空上次出牌状态
                bef_cards = None
                chu_cards_none_times = 0
            print("上个玩家的出牌：", bef_cards)
            chu_cards = self.players[player_ind].try_chupai(bef_cards)  # 玩家尝试出牌

            if chu_cards is None:  # 如果玩家选择不出牌
                print("该玩家选择跳过")
                chu_cards_none_times += 1
                continue
            else:
                # print("[check_bigger]: ", chu_cards, bef_cards)
                legal = self.comparer.check_bigger(
                    chu_cards, bef_cards)   # 检查该出牌是否符合规则

            if legal:
                print("出牌成功")
                chu_cards_none_times = 0
                bef_cards = chu_cards.copy()
                used_cards.extend(chu_cards)
                he_win = self.players[player_ind].try_chupai_Ok(chu_cards)
                if he_win:
                    win_player = self.players[player_ind]
                    break
            else:
                print("出牌错误，扣分并将其跳过") # 如果出牌不合规则，就扣一定分，且跳过他一次
                chu_cards_none_times += 1 
                self.players[player_ind].score += self.chu_card_error_cost
                continue
        print("玩家{}胜利，游戏结束！".format(win_player.name))
        # 【后面结算，赢得加分，没赢减分】

    def log(self) -> str:
        for p in self.players:
            print(p)
        if self.dizhu_cards:
            print("当前底牌：", self.dizhu_cards)


class Player():
    def __init__(self, name) -> None:
        self.name = name
        self.get_dizhu = False
        self.cards = []
        self.score = 0

    def receive_card(self, p):
        self.cards.append(p)
        self.cards.sort()

    def qiang_ma(self, cost, max_cost):  # 决定是否抢牌, 随机决定
        if rand(0, 3):
            return None
        else:
            try:
                return rand(cost+1, max_cost)
            except ValueError:
                return None

    def try_chupai(self, bef_cards):  # 尝试出牌
        chu_cards = None
        while not chu_cards:
            print(self.name, "尝试出牌，现在手牌为：", self.cards)
            inp = input()
            if inp == "pass":  # 玩家输入 pass 选择跳过
                break
            chu_cards = [int(c) for c in inp.split()]
            for c in chu_cards:
                if not c in self.cards:
                    chu_cards = None
                    print(self.name, "手中没有这些牌中的某个，请重新出牌！")
                    break
        return chu_cards

    def try_chupai_Ok(self, chu_cards):  # 尝试出牌成功, 并返回它手牌数是否为零
        for c in chu_cards:
            self.cards.remove(c)
        if len(self.cards) == 0:
            return True
        else:
            return False

    def __repr__(self) -> str:
        return self.name + ":" + " ".join(str(i) for i in self.cards)


game = Game()
game.fapai()
game.log()
game.qiangpai()
game.log()
game.chupai()

# 检验 _check_chu_card 函数
# cher = Comparer()
# print(cher.check_type([1, ]))
# print(cher.check_type([1, 2, 1, 1]))
# print(cher.check_type([1, 2]))
# print(cher.check_type([6, 7, 3, 4, 5]))
# print(cher.check_bigger([6], [3]))
# print(cher.check_bigger([6, 6], [3, 3]))