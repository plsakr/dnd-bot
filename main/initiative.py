from typing import List, Any


class Combatant:

    def __init__(self, name, init, is_player, mention=None, max_hp=None, current_hp=None, private=False):
        self.name = name
        self.private = private
        self.is_player = is_player
        self.init = init
        self.max_hp = max_hp
        self.mention = mention
        self.current_turn = False
        if max_hp != None:
            self.current_hp = current_hp if current_hp is not None else max_hp
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
        if self.private == False and self.max_hp is not None:
            summary += " <{0}/{1}>".format(self.current_hp, self.max_hp)
        elif self.private == True and self.max_hp is not None:
            summary += " <{0}>".format(
                "Healthy" if self.current_hp >= self.max_hp / 2 else "Bloody" if 0 < self.current_hp < self.max_hp / 2 else "Dead")
        return summary


class Initiative:

    players: List[Combatant]

    def __init__(self, players=[], current_init_index=-1, start_battle=False, battle_round=0, cached_summary=None, dungeon_master=None):
        if len(players) > 0:
            self.players = [Combatant(i.get('name'), i.get('init'), i.get('is_player'), i.get('mention'),
                                      i.get('max_hp'), i.get('current_hp'), i.get('private')) for i in players]
        else:
            self.players = players
        self.current_init_index = current_init_index
        self.start_battle = start_battle
        self.battle_round = battle_round
        self.cached_summary = cached_summary
        self.dungeon_master = dungeon_master

    def add_char(self, combatant):
        self.players.append(combatant)
        self.sort_initiative()

    def check_char_exists(self, name):
        return len(list(filter(lambda x: x.name.lower() == name.lower(), self.players))) == 1

    def get_next_name(self, name):
        current = 1
        while True:
            curr_name = name + str(current)
            if not self.check_char_exists(curr_name):
                return curr_name
            current += 1

    def remove_char(self, combatant):
        index = self.players.index(combatant)

        # make sure the initiative index is correct!
        if index < self.current_init_index:
            self.current_init_index -= 1

        self.players.remove(combatant)

    def attempt_char_removal(self, name: str):
        if self.check_char_exists(name):

            # if it is their turn, DO NOT ALLOW REMOVAL!
            combatant = self.get_combatant_from_name(name)
            if combatant.current_turn:
                return -1 # ITS THEIR TURN
            else:
                self.remove_char(combatant)
                return 0  # I DID IT!
        else:
            return -2  # I DONT KNOW WHO THAT IS

    def sort_initiative(self):
        self.players = sorted(self.players, key=lambda x: x.init, reverse=True)

    def get_full_text(self):
        outStr = "```markdown\n" + "Combat Initiative: Round {0}\n".format(
            self.battle_round if self.battle_round != 0 else "-")
        outStr = outStr + "==============================\n"

        for player in self.players:
            outStr += "# " if self.players.index(player) == self.current_init_index else "  "
            outStr += "{0} \n".format(player.get_summary())

        outStr += "```"

        return outStr

    def get_combatant_from_name(self, name):
        return list(filter(lambda x: x.name == name, self.players))[0]

    def all_players_dead(self) -> bool:
        for p in self.players:
            if p.is_player and p.current_hp is not None and p.current_hp > 0:
                return False

        return True

    def next(self) -> Combatant:
        self.players[self.current_init_index].current_turn = False
        self.current_init_index += 1

        if self.current_init_index >= len(self.players):
            self.current_init_index = 0

        if self.current_init_index == 0:
            self.battle_round += 1

        self.players[self.current_init_index].current_turn = True
        return self.players[self.current_init_index]

    def start_initiative(self):
        self.start_battle = True
        return self.next()

