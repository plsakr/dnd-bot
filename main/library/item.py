from enum import Enum


class Rarity(Enum):
    NM = 0
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    VERY_RARE = 4
    LEGENDARY = 5


class DamageType(Enum):
    ACID = 1
    BLUDGEONING = 2
    COLD = 3
    FIRE = 4
    LIGHTNING = 5
    NECROTIC = 6
    PIERCING = 7
    POISON = 8
    PSYCHIC = 9
    RADIANT = 10
    SLASHING = 11
    THUNDER = 12


class Item(object):

    def __init__(self, name, desc):
        self.name = name
        self.description = desc
        self.rarity = Rarity.NM


class Weapon(Item):
    """A basic weapon with damage and possible enchanted bonus
        This can be used for both melee and ranged weapons"""

    def __init__(self, name, desc, damage, rng, bonus, dmg_type):
        """
        Create a new weapon

        :param name: The weapon name
        :type name: str
        :param desc: The weapon description
        :type desc: str
        :param damage: The damage die for the weapon
        :type damage: str
        :param rng: The range of the weapon
        :type rng: str
        :param bonus: Any enchanted magical bonus
        :type bonus: int
        :param dmg_type: The damage type the weapon inflicts
        :type dmg_type: DamageType
        """
        super().__init__(name, desc)
        self.damage = damage
        self.rng = rng
        self.bonus = bonus
        self.dmg_type = dmg_type
