# 已经完成部分: 发牌， 抢地主  （2022.08.21）

# 牌用字符串表示：
# 四种花色（ABCD），号码1-13，比如 1A，13B， 大小王 W Q  # wangquan
from random import randint as rand

class Game():
    def __init__(self):
        self.players = [Player('Z3'), Player('L4'), Player('W5')] # 三个玩家
        self.players_nums = len(self.players)  # 3
        self.dizhu_cards = []  # 三张底牌
        self.max_dizhu_cost = 8  # 加注的极限，最大值
        self.dizhu_pi = None
        self.dizhu_cost = None
        

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


    def log(self) -> str:
        for p in self.players:
            print(p)
        if self.dizhu_cards:
            print("self.dizhu_cards: ", self.dizhu_cards)
        

class Player():
    def __init__(self, name) -> None:
        self.name = name
        self.cards = []

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
            
    def __repr__(self) -> str:
        return self.name + ":" + " ".join(self.cards)


game = Game()
game.fapai()
game.qiangpai()
game.log()