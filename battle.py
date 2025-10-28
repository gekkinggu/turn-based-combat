# python
"""battle.py

Battle code.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character_core import Character
    from item_core import Item


class BattleState:
    """Base class for battle states."""
    def __repr__(self) -> str:
        return self.__class__.__name__
    def loop(self, battle, dt) -> None:
        """Override in subclasses to define state behavior."""
        pass


class Waiting(BattleState):
    """Handles ATB gauge filling and state transitions."""
    def loop(self, battle: Battle, dt: int) -> None:
        if battle.ready_actors:
            if len(battle.ready_actors) > 1:
                battle.state = SpeedTie()
            else:
                battle.state = PrepareActor(battle.ready_actors[0])
        for battler in battle.battlers:
            battler.atb += battler.speed * dt * 5
            if battler.atb >= battle.READY_THRESHOLD:
                battle.ready_actors.append(battler)


class SpeedTie(BattleState):
    """Handles speed ties among battlers."""
    def loop(self, battle: Battle, dt: float) -> None:
        
        if all(battler.is_controllable for battler in battle.ready_actors):
            battle.state = SelectingTieWinner(battle.ready_actors)
        
        else:
            tie_winner = random.choice(battle.ready_actors)
            battle.ready_actors = [tie_winner]
            battle.state = PrepareActor(battle.ready_actors[0])


class SelectingTieWinner(BattleState):
    def __init__(self, people_in_tie: list[Character]) -> None:
        super().__init__()
        self.people_in_tie = people_in_tie  # Instance attribute

    def loop(self, battle: Battle, dt: float) -> None:
        pass


class PrepareActor(BattleState):
    """Prepare the next actor for their turn."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

    def loop(self, battle: Battle, dt: float) -> None:
        
        # Since stat modifiers are applied every turn
        # prevent stacking by resetting at turn start
        self.actor.reset_stats()

        for status in self.actor.statuses:
            status.execute(self.actor)
        
        if self.actor.is_controllable:
            battle.state = ControlledTurn(self.actor)
        else:
            battle.state = AITurn(self.actor)


class ControlledTurn(BattleState):
    """Handles a controllable character's turn."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

    def loop(self, battle: Battle, dt: float) -> None:
        battle.state = SelectingCommands(self.actor)


class AITurn(BattleState):
    """Handles an AI-controlled character's turn."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

    def loop(self, battle: Battle, dt: float) -> None:
        self.actor.behaviour.execute(self.actor, battle)
        battle.state = CheckingDeath()


class SelectingCommands(BattleState):
    """Handles command selection for a controllable character."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

    def loop(self, battle: Battle, dt: float) -> None:
        self.actor.behaviour.execute(self.actor, battle)
        battle.state = CheckingDeath()


class CheckingDeath(BattleState):
    """Check for any defeated battlers and handle end-of-turn logic."""
    def loop(self, battle: Battle, dt: float) -> None:
        if any(battler.hp == 0 for battler in battle.battlers):
            battle.state = Burying()
        else:
            battle.state = EndingTurn()


class EndingTurn(BattleState):
    """End the current actor's turn and prepare for the next."""
    def loop(self, battle: Battle, dt: float) -> None:
        actor = battle.ready_actors.pop(0)
        actor.atb -= battle.READY_THRESHOLD
        for status in actor.statuses:
            status.reduce_duration()
        actor.statuses = [status for status in actor.statuses
                          if status.stack > 0]
        battle.state = Waiting()


class Burying(BattleState):
    """Handle defeated battlers and check for battle outcome."""
    def loop(self, battle: Battle, dt: float) -> None:
        for battler in battle.battlers:
            if battler.hp == 0:
                battler.atb = 0
                dying_battler_index = battle.battlers.index(battler)
        battle.graveyard.append(battle.battlers.pop(dying_battler_index))
        battle.state = EndingTurn()

        if all(battler in battle.graveyard for battler in battle.party):
            battle.state = Loss()
        elif all(battler in battle.graveyard for battler in battle.enemies):
            battle.state = Victory()


class Victory(BattleState):
    """Handle victory state."""
    def loop(self, battle: Battle, dt: float) -> None:
        battle.outcome = "Victory"


class Loss(BattleState):
    """Handle loss state."""
    def loop(self, battle: Battle, dt: float) -> None:
        battle.outcome = "Defeat"


class Battle:
    """Battle class."""

    inventory: list[Item] = []
    READY_THRESHOLD = 296


    def __init__(self,
                 party: list[Character],
                 enemies: list[Character],
                 can_run = True) -> None:
        
        self.party = party
        self.enemies = enemies
        self.can_run = can_run

        self.battlers = self.party + self.enemies
        self.ready_actors: list[Character] = []
        self.graveyard: list[Character] = []
        self.outcome: str | None = None

        self.state: BattleState = Waiting()
        self.prev_state: BattleState | None = None


    def preparation(self) -> None:
        """Prepare for battle."""

        for battler in self.battlers:
            battler.prepare_for_battle()
            battler.atb = random.randint(0,15)
    

    def conclude(self) -> None:
        """Conclude the battle."""
        for battler in self.battlers:
            battler.reset_stats()
    

    def loop(self, dt: float) -> None:
        """Update the battle state."""
        self.state.loop(self, dt)


if __name__ == "__main__":
    from character_core import Character, Enemy

    warrior = Character("Warrior", 50)
    mage = Enemy("Mage", 50)

    battle = Battle(party=[warrior], enemies=[mage])
    battle.preparation()

    while battle.outcome is None:
        battle.loop(0.016)

        if battle.state != battle.prev_state:
            print(f"Current State: {battle.state}")
            battle.prev_state = battle.state