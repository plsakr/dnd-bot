from enum import Enum, auto

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

class FeatureType(Enum):
    CUSTOM = auto
    PROFICIENCY = auto
    SPELL_CASTING = auto
    SKILL_BONUS = auto


class ClassFeature:

    def __init__(self, name, type=FeatureType.CUSTOM, source=None, min_level=1, description="", uses=None, **kwargs):
        if source is None:
            source = {"book": "", "page": 0}
        if uses is None:
            uses = {"type": "inf", "uses": 1, "recharge": "lr"}
        self.name = ""  # The name of the feature
        self.type = type
        self.source = source # The source of the feature

        self.min_level = min_level
        self.description = description
        self.uses = uses  # How often you can use this. The parameters are:
        # type - inf, fixed, level. uses - an integer if fixed, an array of 21 elements if level. recharge - sr,lr,dawn

        def __init_custom():
            # All data in description
            pass

        def __init_proficiency():

            pass

        def __init_spellcasting():
            pass

        def __init_skill_bonus():
            pass

        switcher = {
            FeatureType.CUSTOM: __init_custom,
            FeatureType.PROFICIENCY: __init_proficiency,
            FeatureType.SPELL_CASTING: __init_spellcasting,
            FeatureType.SKILL_BONUS: __init_skill_bonus
        }

        switcher[type]()
        # TODO: add needed data for spell casting
        # TODO: add needed data for increasing skill scores

