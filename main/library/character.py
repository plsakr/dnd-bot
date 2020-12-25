class Character:

    def __init__(self):
        self.name = ""  # The character name
        self.player_name = ""  # The player's name
        self.xp = 0
        self.classes = []  # [{"class": the object, "level": 1}]
        self.race = None  # The race of the player
        self.background = None  # The player's background
        self.rolled_hp = 0
        self.rolled_abilities = {"cha": 0, "con": 0, "dex": 0,
                                 "int": 0, "str": 0, "wis": 0}

    def get_ability(self, ability_name):
        pass

    def get_proficiency(self, skill_name):
        pass

    def get_ability_mod(self, ability_name):
        pass

    def get_skill_mod(self, skill_name):
        pass

    def get_weapon_profs(self):
        res = []
        for i in self.classes:
            res.extend(i.weapon_profs)
        return res

    def get_armor_profs(self):
        res = []
        for i in self.classes:
            res.extend(i.armor_profs)
        return res

    def get_tool_profs(self):
        res = []
        for i in self.classes:
            res.extend(i.tool_profs)
        return res

        # TODO: The rest of the attributes like equipment, and spells!


class CharacterBuilder:

    def __init__(self):
        self.character = Character()

    def set_name(self, name):
        self.character.name = name
        return self

    def set_player_name(self, player_name):
        self.character.player_name = player_name
        return self

