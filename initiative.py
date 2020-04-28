
class Initiative:

    def __init__(self):
        self.players = []
        self.current_init_index = -1
        self.start_battle = False
        self.battle_round = 0
        self.cached_summary = None
        self.dungeon_master = None

    def add_char(self, combatant):
        self.players.append(combatant)
        self.sort_initiative()

    def remove_char(self, name):
        self.players.remove(list(filter(lambda x: x.name == name, self.players))[0])

    def sort_initiative(self):
        self.players = sorted(self.players, key= lambda x: x.init, reverse=True)

    def get_full_text(self):
        outStr = "```markdown\n"+"Combat Initiative: Round {0}\n".format(self.battle_round if self.battle_round != 0 else "-")
        outStr = outStr + "==============================\n"

        for player in self.players:
            outStr += "# " if self.players.index(player) == self.current_init_index else "  "
            outStr += "{0} \n".format(player.get_summary())

        outStr += "```"

        return outStr

    def get_combatant_from_name(self, name):
        return (list(filter(lambda x: x.name == name, self.players))[0])

    def next(self):
        self.current_init_index += 1
        
        if self.current_init_index >= len(self.players):
            self.current_init_index = 0

        if self.current_init_index == 0:
            self.battle_round += 1
        
        return self.players[self.current_init_index]

    def start_initiative(self):
        self.start_battle = True
        return self.next()


class Combatant:

    def __init__(self, name, init, mention = None, max_hp = None, current_hp = None, private = False):
        self.name = name
        self.private = private
        self.init = init
        self.max_hp = max_hp
        self.mention = mention
        if max_hp != None:
            self.current_hp = current_hp if current_hp != None else max_hp
        else:
            self.current_hp = None

    def modify_health(self, mod):
        self.current_hp += mod
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        if self.current_hp < 0:
            self.current_hp = 0

    def get_summary(self):
        summary = "{0}: {1}".format(self.init, self.name)
        if self.private == False and self.max_hp != None:
            summary += " <{0}/{1}>".format(self.current_hp, self.max_hp)
        elif self.private == True and self.max_hp != None:
            summary += " <{0}>".format("Healthy" if self.current_hp >= self.max_hp/2 else "Bloody" if 0 < self.current_hp < self.max_hp/2 else "Dead")
        return summary

