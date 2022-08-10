# 已经完成部分: 发牌， 抢地主  （2022.08.02）
#  出牌（完成）和验证（没写完）  （2022.08.03）
#  验证（完成），出牌逻辑基本完成  （2022.08.06）
#  添加自动玩家类 （2022.08.07）

# --------本版本更新说明： -----------------------
# 1. 在游戏中加入了两个 自动化陪玩 AutuPlayer。  -- ok
# 2. 优化了出牌阶段的控制台输出等细节。  -- ok
# 3. AutuPlayer还要添加炸弹逻辑。  --有4炸了
# 4. 最终结算  -- ok
# AutuPlayer可以对队友下手轻一点，另外做了其他关于队友逻辑的细节。  --未做
# 项目一期基本完成。

# ----------牌用字符串表示：（改变数字规则，不再显示花色）
# 普通牌 号码3-13，
# 高级牌12: 14, 15
# 大小王: 103, 104

# 目前每次出牌的类型：  [还没有对对蹦]
# "1": 1,
# "2": 1,
# "3+1": 1,  # [三带一目前必须有带个一，后续根据情况再改]
# "lian": 1,
# "4Z": 2,
# "WZ": 3

from random import randint as rand
from collections import Counter

CHU_CARD_ERROR_COST = -2  #　出牌错误的罚分设置
START_COST_MIN = 50  # 最小起拍
START_COST_MAX = 60  # 最大起拍
MAX_DIZHU_COST = 100  # 加注的极限，最大值

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
        elif self._spe_repr(cards) == (2, 1, 1) and all(a >= 103 for a in cards):
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
        if t1 in ('1', '2', '4Z'):  # 单(11),双(22) 或者 #炸弹(44)，
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
        # 返回 数字位数， 最多的数字的个数， 第二个的数字的个数， 依次类推
        chu_len = len(cards)  # 数字总数
        ct = Counter(cards)   # 数字种数
        tmp = list(ct.values())
        tmp.sort(reverse=True)
        return tuple([chu_len, ] + tmp)


class Game():
    def __init__(self):
        self.players = [AutoPlayer('=张三='), AutoPlayer('=李四='), Player('=我=')]  # 三个玩家
        self.players_nums = len(self.players)  # 3
        self.dizhu_cards = []  # 三张底牌
        self.dizhu_pi = None
        self.dizhu_cost = None
        self.comparer = Comparer()
        self.win_player = None

    def fapai(self):  # 1发牌
        print("================1发牌======================")
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
        self.players[player_i].name =  self.players[player_i].name + "(地主)"
        for c in self.dizhu_cards:
            self.players[player_i].receive_card(c)
        self.dizhu_cards = []
        self.dizhu_pi = player_i
        self.dizhu_cost = cost

    def qiangpai(self):  # 2抢牌
        print("================2抢牌======================")
        cost = rand(START_COST_MIN, START_COST_MAX+1)  # 随机一个初始的代价
        player_ind = rand(0, 2)  # 随机从一个玩家开始
        last_qiang = None  # 最后抢的人
        buqiang_n = 0  # 不抢的人
        while buqiang_n < 3:
            q = self.players[player_ind].qiang_ma(
                cost, MAX_DIZHU_COST)  # 问一个玩家抢不抢
            print("抢吗:", self.players[player_ind].name, q)
            if q and cost < q <= MAX_DIZHU_COST:  # 如果枪且是有效的cost
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
        print("================3出牌======================")
        used_cards = []
        win_player = None
        for i in range(3):  # 地主先出牌
            if self.players[i].get_dizhu:
                player_ind = i
        bef_cards = None  # 如 (1,1)
        bef_c_player = None
        chu_cards_none_times = 0  # 在游戏循环中连续跳过的次数
        while len(used_cards) < (13*4+2) and not win_player:  # 当牌没有全部出, 并且没人空牌时候
            if chu_cards_none_times >= 2:  # 如果前面连续两个人跳过，请清空上次出牌状态
                bef_cards = None
                bef_c_player = None
                chu_cards_none_times = 0

            tmp_player = self.players[player_ind]
            player_ind = (player_ind+1) % 3

            print("< - - - - - - - - - - - ^ - - - - - - - - - - - > ")
            if bef_c_player:
                print("      # 上个玩家{}的出牌：".format(bef_c_player.name), bef_cards)
            else:
                print("      # 你刚出的牌没人接，本次随意出牌~")
            chu_cards = tmp_player.try_chupai(
                bef_cards)  # 玩家尝试出牌

            if chu_cards is None:  # 如果玩家选择不出牌
                print(tmp_player.name, "该玩家选择跳过", ",余牌{}张".format(len(tmp_player.cards)), "\n")
                chu_cards_none_times += 1
                continue
            else:
                # print("[check_bigger]: ", chu_cards, bef_cards)
                legal = self.comparer.check_bigger(
                    chu_cards, bef_cards)   # 检查该出牌是否符合规则

            if legal:
                chu_cards_none_times = 0
                bef_cards = chu_cards.copy()
                bef_c_player = tmp_player
                used_cards.extend(chu_cards)
                he_win = tmp_player.try_chupai_Ok(chu_cards)
                print(tmp_player.name, "      出牌成功:", chu_cards, ",余牌{}张".format(len(tmp_player.cards)), "\n")
                if he_win:
                    win_player = tmp_player
                    break
            else:
                print("出牌错误，扣分并将其跳过")  # 如果出牌不合规则，就扣一定分，且跳过他一次
                chu_cards_none_times += 1
                tmp_player.score += CHU_CARD_ERROR_COST
                continue
        print("玩家{}胜利，游戏结束！".format(win_player.name))
        self.win_player = win_player

    def jiesuan(self):  # 4结算
        print("================4结算======================")
        if self.win_player.get_dizhu: # 如果胜利的玩家是地主
            for p in self.players:
                if p.get_dizhu:
                    p.score += self.dizhu_cost * 2
                else:
                    p.score -= self.dizhu_cost
        else:
            for p in self.players:
                if p.get_dizhu:
                    p.score -= self.dizhu_cost * 2
                else:
                    p.score += self.dizhu_cost

        print("计算结果：")
        print("本局胜利玩家: ", self.win_player.name)
        print("本局分数： ")
        for p in self.players:
            print("   " + p.name, ":", p.score)

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
            try:
                chu_cards = [int(c) for c in inp.split()]
            except ValueError:
                print("输入错误，请重新输入")
                continue
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


class AutoPlayer(Player):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.name = self.name + "(ATUO_P)"
        self.comparer = Comparer()

    def _smallest_repeat_cards(self, n_tar=None, bef_cards=None):
        # 只会出单、双、炸弹
        # n_tar 表示限定了几次相同的牌， bef_cards 表示必须大过的之前的牌
        self.cards.sort()
        for c in self.cards:
            n = self.cards.count(c)
            if n == 3:  # 如果有3张相同的牌， 但是这里只能出两张
                n = 2
            if n_tar != None:  # 判断 n_tar 条件
                if n != n_tar:
                    continue
            if bef_cards == None or c > bef_cards[0]:  # 判断 bef_cards 条件
                return [c] * n
        return None

    def _smallest_3plus1(self, bef_cards):
        counter = Counter(bef_cards)
        # 将三带一的两种牌分离，分别是 c3 和 c1
        for c in counter.keys():
            if counter[c] == 1:
                c1 = c
            if counter[c] == 3:
                c3 = c
        c3_new = self. _smallest_repeat_cards(3, [c3])
        c1_new = self. _smallest_repeat_cards(1, [c1])
        if c1_new and c3_new:
            c3_new.extend(c1_new)
        return c3_new

    def _smallest_lian(self, bef_cards):
        bef_n = len(bef_cards)
        for c in self.cards:
            need_cards = [c+i for i in range(1, bef_n)]
            for nc in need_cards:
                if not nc in self.cards:
                    continue
            else:
                need_cards.append(c)
                return need_cards

    def try_chupai(self, bef_cards):  # 尝试出牌
        if bef_cards == None:
            chu_cards = self._smallest_repeat_cards()
        else:
            bef_type = self.comparer.check_type(bef_cards)
            if bef_type in ("1", "2", "4Z"):
                type_n = int(bef_type[0])
                chu_cards = self._smallest_repeat_cards(type_n, bef_cards)
            elif bef_type == 'lian':
                chu_cards = self._smallest_lian(bef_cards)
            elif bef_type == '3+1':
                chu_cards = self._smallest_3plus1(bef_cards)
        if chu_cards==None:
            chu_cards = self._smallest_repeat_cards(4, bef_cards)  # 当相同类型压不住的时候，尝试用4炸弹

        return chu_cards


game = Game()
game.fapai()
game.log()
game.qiangpai()
game.log()
game.chupai()
game.jiesuan()

# # 检验 _check_chu_card 函数
# cher = Comparer()
# print(cher.check_type([103, 104]))
# print(cher.check_type([1, 2, 1, 1]))
# print(cher.check_type([1, 2]))
# print(cher.check_type([6, 7, 3, 4, 5]))
# print(cher.check_bigger([6], [3]))
# print(cher.check_bigger([6, 6], [3, 3]))
