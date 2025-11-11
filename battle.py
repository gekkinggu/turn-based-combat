# python
"""battle.py

Battle code.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character
    from item import Item
    from action_core import Action


class BattleState:
    """Base class for battle states."""
    def __init__(self):
        pass
    def __repr__(self) -> str:
        return self.__class__.__name__
    def loop(self, battle, dt) -> None:
        """Override in subclasses to define state behavior."""
        pass


class Waiting(BattleState):
    """Handles ATB gauge filling and state transitions."""
    def __init__(self):
        super().__init__()
    def loop(self, battle: Battle, dt: int) -> None:

        if battle.ready_actors:
            if len(battle.ready_actors) > 1:
                battle.state = SpeedTie(battle.ready_actors)
            else:
                battle.state = PrepareActor(battle.ready_actors[0])
            return
            
        for battler in battle.battlers:
            battler.atb += battler.speed * dt * 5
            if battler.atb >= battle.READY_THRESHOLD:
                battle.ready_actors.append(battler)


class SpeedTie(BattleState):
    """Handles speed ties among battlers."""
    def __init__(self, tied_actors: list[Character]):
        super().__init__()
        self.tied_actors = tied_actors
    def loop(self, battle: Battle, dt: float) -> None:
        battle.log_messages.append("Speed tie!")

        if all(battler.is_controllable for battler in battle.ready_actors):
            battle.state = WaitingForTie(battle.ready_actors)
        
        else:
            tie_winner = random.choice(battle.ready_actors)
            battle.log_messages.append(f"{tie_winner} wins the speed tie!")
            battle.state = PrepareActor(tie_winner)


class WaitingForTie(BattleState):
    def __init__(self, people_in_tie: list[Character]) -> None:
        super().__init__()
        self.people_in_tie = people_in_tie  # Instance attribute
        self.tie_winner: Character | None = None

    def loop(self, battle: Battle, dt: float) -> None:
        # Waits for player input to select tie winner
        if self.tie_winner:
            battle.log_messages.append(f"{self.tie_winner} wins the speed tie!"
                                       )
            battle.state = PrepareActor(self.tie_winner)


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
    """Handles command selection for a controllable character."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

        # These will be set via UI input
        self.action: Action | None = None
        self.targets: list[Character] = []

    def loop(self, battle: Battle, dt: float) -> None:
        # This state now waits for UI input
        if self.action and self.targets:
            battle.log_messages.extend(
                self.action.execute(
                    self.actor, self.targets, battle))
            battle.state = CheckingDeath(self.actor)


class AITurn(BattleState):
    """Handles an AI-controlled character's turn."""
    def __init__(self, actor: Character) -> None:
        super().__init__()
        self.actor = actor

    def loop(self, battle: Battle, dt: float) -> None:
        battle.log_messages.extend(self.actor.behaviour.execute(
                                    self.actor, battle))
        battle.state = CheckingDeath(self.actor)


class CheckingDeath(BattleState):
    """Check for any defeated battlers and handle end-of-turn logic."""
    def __init__(self, actor: Character):
        super().__init__()
        self.actor = actor
    def loop(self, battle: Battle, dt: float) -> None:
        if any(battler.hp == 0 for battler in battle.battlers):
            battle.state = Burying(self.actor)
        else:
            battle.state = EndingTurn(self.actor)


class EndingTurn(BattleState):
    """End the current actor's turn and prepare for the next."""
    def __init__(self, actor: Character):
        super().__init__()
        self.actor = actor
    def loop(self, battle: Battle, dt: float) -> None:
        actor = self.actor
        battle.ready_actors.remove(actor)
        actor.atb -= battle.READY_THRESHOLD
        for status in actor.statuses:
            status.reduce_duration()
        actor.statuses = [status for status in actor.statuses
                          if status.stack > 0]
        battle.state = Waiting()


class Burying(BattleState):
    """Handle defeated battlers and check for battle outcome."""
    def __init__(self, actor: Character):
        super().__init__()
        self.actor = actor
    def loop(self, battle: Battle, dt: float) -> None:
        for battler in battle.battlers:
            if battler.hp == 0:
                battler.atb = 0
                dying_battler_index = battle.battlers.index(battler)
        battle.graveyard.append(battle.battlers.pop(dying_battler_index))
        battle.state = EndingTurn(self.actor)

        if all(battler in battle.graveyard for battler in battle.party):
            battle.state = Loss()
        elif all(battler in battle.graveyard for battler in battle.enemies):
            battle.state = Victory()


class Victory(BattleState):
    """Handle victory state."""
    def __init__(self):
        super().__init__()
    def loop(self, battle: Battle, dt: float) -> None:
        battle.outcome = "Victory"


class Loss(BattleState):
    """Handle loss state."""
    def __init__(self):
        super().__init__()
    def loop(self, battle: Battle, dt: float) -> None:
        battle.outcome = "Defeat"


class Battle:
    """Battle class."""

    inventory: list[Item] = []
    READY_THRESHOLD = 296

    def __init__(self, party: list[Character], enemies: list[Character],
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
        self.log_messages: list[str] = []

        self.preparation()

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
        
        if self.state != self.prev_state:
            self.prev_state = self.state
            print(f"Battle State changed to: {self.state}")
        
        self.state.loop(self, dt)
        