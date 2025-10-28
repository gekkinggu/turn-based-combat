# python
"""behaviour_core.py

Behaviour module containing the Behaviour class.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character
    from battle import Battle

class Behaviour:
    """Class representing the behaviour of a character."""

    def __init__(self, name = "Random Attack") -> None:
        self.name = name
        self.log_messages: list[str] = []
    
    def execute(self, actor: Character, battle: Battle) -> list[str]:
        """Execute the behaviour based on its name."""

        match self.name:

            case "Random Attack":
                self.random_attack(actor, battle)
            
            case _:
                self.random_attack(actor, battle)
        
        return self.log_messages
    
    def random_attack(self, actor: Character, battle: Battle) -> None:
        """Execute a random attack behaviour."""
        
        if actor in battle.party:
            opposing = battle.enemies
        else:
            opposing = battle.party
        
        targets = [target for target in opposing if target.hp > 0]
        target = random.choice(targets)
        
        self.log_messages.extend(actor.basic_attack.execute(actor, [target],
                                                            battle))