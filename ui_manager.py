# python
"""ui_manager.py
UI Manager module for the turn-based combat system."""

from __future__ import annotations

from typing import TYPE_CHECKING
from battle import Battle, ControlledTurn, WaitingForTie
from ui import BattleUI, SelectingCommand, SelectingTieWinner

if TYPE_CHECKING:
    from battle import BattleState

class UIManager:
    """Manages different UI states."""
    def __init__(self, ui: BattleUI, battle: Battle):
        self.ui = ui
        self.battle = battle
        self.last_battle_state: BattleState | None = None

    def loop(self) -> None:
        """Acts more like an extension of the battle code which integrates ui
        elements."""

        if self.battle.state != self.last_battle_state:
            self._on_battle_state_enter(self.battle.state)
            self.last_battle_state = self.battle.state
        
        # Track UI state changes
        if self.ui.state != self.ui.prev_state:
            self.ui.state_history.insert(0, self.ui.state)
            if len(self.ui.state_history) > 3:
                self.ui.state_history.pop()
            self.ui.prev_state = self.ui.state
            print(f"UI State changed to: {self.ui.state}")
        
    def _on_battle_state_enter(self, state) -> None:
        """Called once when battle state changes - this is your 'run once' hook"""
        if isinstance(state, ControlledTurn):
            self.ui.setup_command_menu(state.actor)
            self.ui.state = SelectingCommand()
        
        elif isinstance(state, WaitingForTie):
            self.ui.setup_tie_selection_menu(state.people_in_tie)
            self.ui.state = SelectingTieWinner()