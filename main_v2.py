# 已经完成部分: 发牌， 抢地主  （2022.08.02）
#  出牌（完成）和验证（没写完）  （2022.08.03）

# 牌用字符串表示：
# 四种花色（ABCD），号码1-13，比如 1A，13B， 大小王 W Q  # wangquan
from random import randint as rand
from collections import Counter

class Game():
    def __init__(self):
        self.players = [Player('Z3'), Player('L4'), Player('W5')] # 三个玩家
        self.players_nums = len(self.players)  # 3
        self.dizhu_cards = []  # 三张底牌
        self.max_dizhu_cost = 8  # 加注的极限，最大值
        self.dizhu_pi = None
        self.dizhu_cost = None
        self.chu_card_error_cost = -2
    

    def fapai(self):  # 1发牌
        all_cards = ['W', 'Q'] # 所有的牌
        for i in range(1, 14):
            for k in "ABCD":
                all_cards.append(str(i) + k)
        # print(len(all_cards))

        for i in range(17): # 17轮发牌
            for pi in range(3): # 3 player
                card_i = rand(0, len(all_cards)-1)  # 从已有牌堆中随机选一个索引
                tmp_card = all_cards[card_i]  # 随机牌本身

                self.players[pi].receive_card(tmp_card)  # 玩家获得 tmp_card
                all_cards.remove(tmp_card)  # 牌堆丢掉 tmp_card
        self.dizhu_cards = all_cards.copy()

    def _send_dizhu(self, player_i, cost):
        print("_send_dizhu", player_i, cost)
        for c in self.dizhu_cards:
            self.players[player_i].receive_card(c)
        self.dizhu_cards = []
        self.dizhu_pi = player_i
        self.dizhu_cost = cost

    def qiangpai(self):  # 2抢牌
        cost = rand(3, 6)  # 随机一个初始的代价
        player_ind = rand(0, 2)  # 随机从一个玩家开始 
        last_qiang = None # 最后抢的人
        buqiang_n = 0  # 不抢的人
        while buqiang_n<3:
            q = self.players[player_ind].qiang_ma(cost, self.max_dizhu_cost)  # 问一个玩家抢不抢
            print("抢吗:", self.players[player_ind].name, q)
            if q and cost < q <= self.max_dizhu_cost: # 如果枪且是有效的cost
                last_qiang = player_ind
                cost = q
                buqiang_n = 0
            else:
                buqiang_n += 1
            
            player_ind = (player_ind+1) % 3
            
        if last_qiang == None: #如果没人抢
            pi = rand(0, 2) # 随机选一个玩家
            self._send_dizhu(pi, cost+1)
        else:
            self._send_dizhu(last_qiang, cost)

    def _check_chu_card(self, chu_cards, bef_cards):
        # 分情况， 单(11)， 双(22)， 三带一(431)， 顺子(>=5 11111 等)， 炸弹(44)， 王炸(22 ,和双一样)。
        # 定义每种牌的表示方法。 （长度，第1多的牌的数量，第二多的牌的数量，第三多的牌的数量）
        chu_len = len(chu_cards)
        ct = Counter(chu_cards)
        check_xingshi = False  # 是否符合某一种形式
        chu_repr = tuple([chu_len] + list(ct.vals()).sort(reverse=True))
        if chu_repr == (1, 1):  # 单(11)
            check_xingshi = True
        elif chu_repr == (2, 2):  # 双(22) 或者 王炸(22 )
            check_xingshi = True
        elif chu_repr == (4, 3, 1):  #三带一(431)， 
            check_xingshi = True
        elif chu_repr == (4, 4):  #炸弹(44)，
            check_xingshi = True
        elif chu_repr[0]>=5 and all(a==1 for a in chu_repr[1:]):  #三带一(431)，   
            check_xingshi = True
        # 【顺子的逻辑还没加】
        if not check_xingshi:
            return False

        check_bigger = False    # 比较它是不是更大
        if bef_cards != None:  # 如果前面有人出牌，就需要比较它是不是更大
            if chu_repr == (1, 1):  # 单(11)
                check_bigger = chu_cards[0] > bef_cards[0]
            elif chu_repr == (2, 2):  # 双(22) 或者 王炸(22 )
                check_bigger = chu_cards[0] > bef_cards[0]
            elif chu_repr == (4, 3, 1):  #三带一(431)， 
                check_bigger = None  # 【这里还没写】
            elif chu_repr == (4, 4):  #炸弹(44)，
                check_bigger = chu_cards[0] > bef_cards[0]
            elif chu_repr[0]>=5 and all(a==1 for a in chu_repr[1:]):  #三带一(431)， 
                check_bigger = True
            # 【顺子的逻辑还没加】
            # 【后面还没写】



    def chupai(self):
        used_cards = []
        win_player = None
        player_ind = rand(1, 3)
        bef_cards = None  #  如 (1,1)

        while len(used_cards)<(13*4+2) and not win_player:  # 当牌没有全部出, 并且没人空牌时候
            player_ind = (player_ind+1)%3  # 每轮更新玩家序号，轮流出牌
            chu_cards = self.players[player_ind].try_chupai(bef_cards)  # 玩家尝试出牌
            if chu_cards is None:  # 如果玩家选择不出牌
                continue
            else:
                legal = self._check_chu_card(chu_cards, bef_cards)   # 检查该出牌是否符合规则
                if not legal:  # 如果出牌不合规则，就扣一定分，且跳过他一次
                    self.players[player_ind].score += self.chu_card_error_cost
                    continue
                else:
                    bef_cards = chu_cards
                    used_cards.extend(chu_cards)
                    he_win = self.players[player_ind].try_chupai_Ok(chu_cards)
                    if he_win:
                        win_player = self.players[player_ind]

        # 后面结算，赢得加分，没赢减分



    def log(self) -> str:
        for p in self.players:
            print(p)
        if self.dizhu_cards:
            print("self.dizhu_cards: ", self.dizhu_cards)
        

class Player():
    def __init__(self, name) -> None:
        self.name = name
        self.cards = []
        self.score = 0

    def receive_card(self, p):
        self.cards.append(p)

    def qiang_ma(self, cost, max_cost): # 决定是否抢牌, 随机决定
        if rand(0, 3):
            return None
        else:
            try:
                return rand(cost+1, max_cost)
            except ValueError:
                return None

    def try_chupai(self, bef_cards):  # 尝试出牌
        pass

    def try_chupai_Ok(self, chu_cards):  # 尝试出牌成功, 并返回它手牌数是否为零
        for c in chu_cards:
            self.cards.remove(c)
        if len(self.cards) == 0:
            return True
        else:
            return False
            
    def __repr__(self) -> str:
        return self.name + ":" + " ".join(self.cards)


game = Game()
game.fapai()
game.qiangpai()
# game.log()