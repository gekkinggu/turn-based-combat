# python
"""action_core.py

Action core module containing Command, Status, and Action classes.
"""

from __future__ import annotations
import random
import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character
    from battle import Battle
    from item import Item


class Command:
    """A command contains one or more actions."""

    def __init__(self, name: str, actions: list[Action], is_single = False
                 ) -> None:
        self.name = name
        self.actions = actions
        # Selecting this command immediately executes its
        # single action rather than open a menu
        self.is_single = is_single

    def __repr__(self) -> str:
        return self.name

    def __getitem__(self, index) -> Action | list[Action] | None:
        # Support slicing and integer indexing;
        # return None for invalid indexes
        if isinstance(index, slice):
            return self.actions[index]
        try:
            return self.actions[index]
        except (IndexError, TypeError):
            return None

    def __len__(self) -> int:
        return len(self.actions)


class Status:
    """A status effect applied to a character."""


    def __init__(self, name: str) -> None:
        self.name = name

        # Defaults for undefined statuses
        self.stack: int = 1
        self.starting_stacks: int = 1
        self.max_stacks: int = 1

        self.duration: int = 3
        self.applied_duration: int = 3
        self.max_duration: int = 3

        self.stat_modifiers: dict[str, float] = {}

        # For annotations
        self.patient: Character

        self.define()


    def __repr__(self) -> str:
        if self.max_stacks == 1:
            return f"{self.name}: {self.duration}"
        else:
            return f"{self.name} x {self.stack}: {self.duration}"


    def define(self) -> None:
        """Define status attributes from CSV file."""

        with open("definitions/statuses.csv", newline="", encoding='utf-8'
                  ) as file:
            library = csv.DictReader(file)
            
            name_found = False
            for row in library:
                if self.name == row["name"]:
                    name_found = True
                    self.starting_stacks = int(row["starting_stacks"])
                    self.max_stacks = int(row["max_stacks"])
                    self.applied_duration = int(row["applied_duration"])
                    self.max_duration = int(row["max_duration"])
                    if row["stat_modifiers"]:
                        self.stat_modifiers = eval(row["stat_modifiers"])
                    else:
                        self.stat_modifiers = {}
            
            if not name_found:
                print(f"Status {self.name} not defined")

            self.stack = self.starting_stacks
            self.duration = self.applied_duration


    def execute(self, patient:Character) -> None:
        """Execute status effect on the patient character."""
        
        self.patient = patient

        # Make sure to do the code before reducing the duration
        match self.name:
            case "Poison":
                pass
        
        # Could be before or after the execute code depending on design
        self.modify_stat()


    def end(self) -> None:
        """For statuses that do something when they end."""


    def modify_stat(self) -> None:
        """Apply stat modifiers to the patient character."""
        for stat, modifier in self.stat_modifiers.items():
            current_value = getattr(self.patient, stat.lower())
            setattr(self.patient, stat.lower(), int(current_value * modifier))


    def reduce_duration(self) -> None:
        """Reduce duration by 1, remove status if duration reaches 0.
        This function is called from the battle code when ending a turn
        instead of in execute so that statuses last the full duration."""
        self.duration -= 1
        if self.duration == 0:
            self.stack -= 1
            if self.stack == 0:
                self.end()
            else:
                self.duration = self.applied_duration


    def reapply(self) -> None:
        """Reapply the status, increasing stacks and duration."""
        self.duration = min(self.duration+self.applied_duration,
                            self.max_duration)
        self.stack = min(self.stack + 1, self.max_stacks)


class Action:
    """Any action that can be performed in battle."""

    def __init__(self, name: str) -> None:
        self.name = name

        # Defaults for undefined actions
        self.type: str = "Damage Single"
        self.potency: int = 100
        self.is_physical: bool = True
        self.element: str = "None"
        self.targetting: str = "Single"
        self.mp_cost: int = 0
        self.status_for_actor: list[str] = []
        self.status_for_target: list[str] = []
        self.status_costs: dict[str, int] = {}

        self.modifiers: list[float] = []
        self.log_messages: list[str] = []

        # For annotations
        self.actor: Character
        self.battle: Battle
        self.party: list[Character]
        self.enemies: list[Character]
        self.targets: list[Character]

        self.define()

    def __repr__(self) -> str:
        return self.name

    def define(self) -> None:
        """Define action attributes from CSV file."""

        with open("definitions/actions.csv", newline="", encoding='utf-8'
                  ) as file:
            library = csv.DictReader(file)
            
            name_found = False
            for row in library:
                if self.name == row["name"]:
                    name_found = True
                    self.type = row["type"]
                    self.potency = int(row["potency"])
                    self.is_physical = row["is_physical"].lower() == "true"
                    self.element = row["element"]
                    self.targetting = row["targetting"]
                    self.mp_cost = int(row["mp_cost"])

                    if row["status_for_actor"]:
                        self.status_for_actor = eval(row["status_for_actor"])
                    else:
                        self.status_for_actor = []

                    if row["status_for_target"]:
                        self.status_for_target = eval(row["status_for_target"])
                    else:
                        self.status_for_target = []

                    if row["status_costs"]:
                        self.status_costs = eval(row["status_costs"])
                    else:
                        self.status_costs = {}

            if not name_found:
               print(f"Action {self.name} not defined")

    def execute(self, actor: Character, targets: list[Character],
                battle: Battle) -> list[str]:
        """Execute the action in the context of a battle.
        Returns log messages generated during execution."""
        self.log_messages = [f"{actor} used {self}!"]

        self.actor = actor
        self.targets = targets

        self.battle = battle
        self.party = battle.party
        self.enemies = battle.enemies

        self.modifiers = []

        match self.type:
            case "Damage Single":
                self.damage_single(self.targets[0])
            case "Damage All":
                self.damage_all()
            case "Heal Single":
                self.heal_single(self.targets[0])
            case "Heal All":
                self.heal_all()
            case "Item Heal":
                self.dealHeal(self.potency, self.targets[0])
            case "Buff Only":
                pass
            case "Limit Gain":
                actor.limit = 100
            case _:
                print("Error: Action Type not found")
        
        self.statusing()
        self.apply_costs(battle.inventory)

        return self.log_messages

    def damage_single(self, target: Character, flavor_text: str | None = None,
                      custom_potency: int | None = None) -> None:
        """Damage a single target."""

        if flavor_text:
            pass

        if self.is_physical:
            damage = self.damageFormula(self.actor.strength,
                                        target.defense,
                                        custom_potency)
        else:
            damage = self.damageFormula(self.actor.magic,
                                        target.mdefense,
                                        custom_potency)
        
        self.dealDamage(damage, target)

    def damage_all(self, flavor_text: str | None = None,
                   custom_potency: int | None = None) -> None:
        """Damage all targets."""

        if flavor_text:
            pass

        for target in self.targets:
            self.damage_single(target, custom_potency = custom_potency)

    def heal_single(self, target: Character, flavor_text: str | None = None,
                    custom_potency: int | None = None) -> None:
        """Heal a single target."""

        if flavor_text:
            pass
        if custom_potency:
            self.dealHeal(self.healFormula(self.actor.magic, custom_potency),
                          target)
        else:
            self.dealHeal(self.healFormula(self.actor.magic), target)

    def heal_all(self, flavor_text: str | None = None,
                 custom_potency: int | None = None) -> None:
        """Heal all targets."""
        if flavor_text:
            pass
        
        for target in self.targets:
            self.heal_single(target, custom_potency = custom_potency)

    def statusing(self) -> None:
        """Apply statuses to actor and target(s)."""

        for status in self.status_for_actor:
            self.apply_status(self.actor, status)
            for thing in self.actor.statuses:
                if thing.name == status:
                    thing.duration += 1
                    # This is because when applying a status to self,
                    # the duration gets decreased the same turn that
                    # it is applied. So we add 1 to offset that.
        
        for status in self.status_for_target:
            for target in self.targets:
                self.apply_status(target, status)

    def apply_status(self, patient: Character, status_name: str) -> None:
        """Apply a status to a character, reapplying if already present."""

        apply_me = None
        for status in patient.statuses:
            if status.name == status_name:
                apply_me = status
        if apply_me:
            apply_me.reapply()
        else:
            patient.statuses.append(Status(status_name))

    def check_costs(self, actor: Character) -> str | None:
        """Check if the actor can afford the costs of
        the action. This code can be run outside of execute
        so it needs the actor argument."""

        if actor.mp < self.mp_cost:
            return "Not enough MP"
        
        if self.status_costs:
            for name, stack in self.status_costs.items():

                this_status = next((status for status in actor.statuses
                                    if status.name == name), None)

                if not this_status:
                    return f"Need {name}"
                elif this_status.stack < stack:
                    return f"Need {stack} more {name}"
        
        return None

    def apply_costs(self, inventory: list[Item]) -> str | None:
        """Apply the costs of the action to the actor and inventory.
        Inventory isn't optional because only execute calls this function."""

        if self.status_costs:
            for name, stack in self.status_costs.items():
                for status in self.actor.statuses:
                    if status.name == name:
                        status.stack -= stack

        if self.mp_cost > 0:
            self.actor.mp -= self.mp_cost
        
        elif isinstance(self, Item_Action):

            used_item = next((item for item in inventory
                              if item.name == self.name), None)
            
            if not used_item:
                return f"No {self.name} in inventory"
            
            used_item.quantity -= 1
            if used_item.quantity == 0:
                inventory.remove(used_item)
        
        elif isinstance(self, Limit):
            self.actor.limit = 0
        
        return None

    def damageFormula(self, attack: int, defense: int,
                      custom_potency: int | None = None) -> int:
        """Calculate damage based on attack, defense, and potency."""
        if custom_potency:
            damage = attack/(2**(defense/attack)) * (custom_potency/100)
        else:
            damage = attack/(2**(defense/attack)) * (self.potency/100)
        return int(damage)

    def dealDamage(self, damage: int, target: Character) -> None:
        """Apply damage to the target,
        considering modifiers and critical hits."""

        # Apply random variance
        self.modifiers.append(random.randint(85,115)/100)

        if self.element in target.affinities:
            self.modifiers.append(target.affinities[self.element])

        if random.randint(1, 100) <= 15:
            self.modifiers.append(2)
            self.log_messages.append("A critical hit!")

        damage_temp = float(damage)
        for modifier in self.modifiers:
            damage_temp *= modifier

        damage = int(damage_temp)
        if damage > target.hp:
            damage = target.hp
        target.hp -= damage
        self.log_messages.append(f"{target} took {damage} damage!")

    def healFormula(self, attack: int, custom_potency: int | None = None
                    ) -> int:
        """Calculate healing based on magic and potency."""
        heal = attack/2 * (self.potency/100)
        if custom_potency:
            heal = attack/2 * (custom_potency/100)
        heal = heal * random.randint(85,115)/100
        return int(heal)

    def dealHeal(self, heal: int, target: Character) -> None:
        """Apply healing to the target."""
        if target.hp + heal > target.hp_max:
            heal = target.hp_max - target.hp
        target.hp += heal
        self.log_messages.append(f"{target} healed {heal} HP!")

class Limit(Action):
    pass


class Item_Action(Action):
    pass