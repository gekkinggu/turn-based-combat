# python
"""character_core.py

Character module containing the Character class.
"""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

from action_core import Command, Action
from behaviour import Behaviour

if TYPE_CHECKING:
    from action_core import Status

class Character:
    """Character class representing a game character."""

    def __init__(self, name: str, level: int) -> None:
        
        self.name = name
        self.level = level
        
        self.is_controllable = True
        self.behaviour = Behaviour()
        self.basic_attack = Action("Attack")

        # For annotations
        self.hp: int
        self.hp_max: int
        self.mp: int
        self.mp_max: int
        self.strength: int
        self.defense: int
        self.magic: int
        self.mdefense: int
        self.speed: int
        self.ability: Command
        self.abilities: list[Action]
        self.spells: list[Action]
        self.level_modifier: float
        self.base_stats: dict[str, int]

        # Battle related
        self.limit: int
        self.atb: int
        self.statuses: list[Status]
        self.affinities: dict[str, int]
        self.commands: list[Command]
        self.pre_battle_stats: dict[str, int]

        self.define()

    def __repr__(self) -> str:
        return self.name

    def define(self) -> None:
        """Define character stats and attributes."""
        
        # Default affinities
        self.affinities = {
            "Fire": 1,
            "Ice": 1,
            "Lightning": 1,
            "Water": 1,
            "Wind": 1,
            "Earth": 1,
            "Neutral": 1
        }

        with open("definitions/battlers.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)

            self.affinities = {}
            self.abilities = []
            self.spells = []

            character_found = False
            for row in reader:
                if row["name"] == self.name:
                    character_found = True

                    self.base_stats = {
                        "hp_max": int(row["hp"]),
                        "mp_max": int(row["mp"]),
                        "strength": int(row["strength"]),
                        "defense": int(row["defense"]),
                        "magic": int(row["magic"]),
                        "mdefense": int(row["mdefense"])
                    }

                    if row["affinities"]:
                        affinities_list = row["affinities"].split(";")
                        for affinity in affinities_list:
                            element, multiplier = affinity.split(":")
                            self.affinities[element] = int(multiplier)

                    if row["abilities"]:
                        abilities_list = row["abilities"].split(";")
                        self.abilities = [Action(ability)
                                          for ability in abilities_list]

                    if row["spells"]:
                        spells_list = row["spells"].split(";")
                        self.spells = [Action(spell)
                                       for spell in spells_list]

                    # Speed is not affected by level modifier
                    self.speed = int(row["speed"])
                    self.ability = Command(row["ability"], self.abilities)
                    break
            
            if not character_found:
                print(f"Character {self.name} not found in battlers.csv")
        
        self.level_up()
        self.hp = self.hp_max
        self.mp = self.mp_max
    
    def level_up(self) -> None:
        """Level up character stats based on level modifier."""
        self.level_modifier = (self.level**2) / 10000
        for stat, value in self.base_stats.items():
            setattr(self, stat, int(value * self.level_modifier))

    def prepare_for_battle(self) -> None:
        """Prepare character for battle."""

        self.limit = 0
        self.statuses = []
        self.commands = [
            Command("Attack", [self.basic_attack], is_single = True),
            self.ability,
            Command("Magic", self.spells),
            Command("Item", [])
        ]

        self.pre_battle_stats = {
            'strength' : self.strength,
            'magic': self.magic,
            'defense' : self.defense,
            'mdefense': self.mdefense,
            'speed' : self.speed
        }
    
    def reset_stats(self) -> None:
        """Reset character stats to pre-battle values."""
        for stat, value in self.pre_battle_stats.items():
            setattr(self, stat, value)

    def rest(self) -> None:
        """Restore character's HP to maximum."""
        self.hp = self.hp_max
        self.mp = self.mp_max


class Enemy(Character):
    """Enemy class inheriting from Character."""
    def __init__(self, name: str, level: int) -> None:
        super().__init__(name, level)
        self.is_controllable = False