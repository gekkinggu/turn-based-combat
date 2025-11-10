# python
"""ui_manager.py
UI Manager module for the turn-based combat system."""

from __future__ import annotations

from typing import TYPE_CHECKING
from battle import Battle, PrepareActor, SpeedTie
from ui import BattleUI, SelectingCommand, SelectingTieWinner


class UIManager:
    """Manages different UI states."""
    def __init__(self, ui: BattleUI, battle: Battle):
        self.ui = ui
        self.battle = battle

    def loop(self) -> None:
        """Acts more like an extension of the battle code which integrates ui
        elements."""

        if isinstance(self.battle.state, PrepareActor):
            self.ui.setup_command_menu(self.battle.state.actor)
            self.ui.state = SelectingCommand()
        
        elif isinstance(self.battle.state, SpeedTie):
            self.ui.setup_tie_selection_menu(self.battle.state.tied_actors)
            self.ui.state = SelectingTieWinner
        
        if len(self.ui.state_history) > 3:
            self.ui.state_history.pop(3)
        
        if self.ui.state != self.ui.prev_state:
            self.ui.state_history.insert(0, self.ui.state)
            self.ui.prev_state = self.ui.state
