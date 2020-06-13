
class CharacterClass:

    def __init__(self):
        self.name = ""  # The name of the Class

        self.source = {"book": "",
                       "page": 0}  # The source of the class. book should be set to the book name and page is the page.

        self.prerequisites = []  # The prerequisites for multiclassing into this class. it is of the format:
        # [{"ability":min_score}]

        self.hit_die = 4  # The hit die of the class

        self.armor_profs = []  # Any armors that the class has proficiencies in: "light", "medium", "shields", etc.

        self.weapon_profs = []  # Any weapons that the class has proficiencies in: "simple", "martial"

        self.tool_profs = []  # Any tools that the class has proficiencies in

        self.saving_profs = []  # Any abilities that the class has proficiencies in for saving throws.
        # eg. ["Strength","Dexterity"]

        self.skill_profs = []  # Any skills that the class can have proficiencies in. Shows choices and number to choose:
        # eg. [{"skills":["Acrobatics","Insight"],"choose":1}]

        self.subclasses = []  # The subclasses that can be chosen. Of type SubClass

        self.features = []  # The features that this class has. Of type ClassFeature
        self.starting_equipment = []  # The starting equipment of the class, this will be in the following format
        # eg. [[choice1, choice2], [free]]


class ClassFeature:

    def __init__(self):
        self.name = ""  # The name of the feature

        self.source = {"book": "",
                       "page": 0}  # The source of the feature

        self.min_level = 0

        self.description = ""

        self.uses = {"type": "fixed", "uses": 1, "recharge": "lr"}  # How often you can use this. The parameters are:
        # type - inf, fixed, level. uses - an integer if fixed, an array of 21 elements if level. recharge - sr,lr,dawn

        # TODO: add needed data for spell casting
        # TODO: add needed data for increasing skill scores
        



