class Character:

    def __init__(self):
        self.name = ""  # The character name
        self.player_name = ""  # The player's name
        self.xp = 0
        self.classes = []  # [{"class": the object, "level": 1}]
        self.race = None  # The race of the player
        self.background = None  # The player's background
        self.rolled_hp = 0
        self.rolled_abilities = []

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

